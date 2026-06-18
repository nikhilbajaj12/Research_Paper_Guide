"""Unit tests for AI Assistant features."""

import pytest
from unittest.mock import AsyncMock, patch

from app.utils.deduplication import deduplicate_recommendations
from app.services.context_builder import ContextBuilder
from app.services.prompt_builder import PromptBuilder
from app.services.assistant_service import AssistantService


# ============ Deduplication Tests ============

class TestDeduplication:
    def test_no_duplicates_returns_same(self):
        recommendations = [
            {
                "issue_id": "method_missing",
                "category": "structure",
                "issue": "Method section missing",
            },
            {
                "issue_id": "page_limit_exceeded",
                "category": "page_limit",
                "issue": "Paper exceeds page limit",
            },
        ]
        result = deduplicate_recommendations(recommendations)
        assert len(result) == 2
        assert result == recommendations

    def test_duplicates_removed_keeps_first(self):
        recommendations = [
            {
                "issue_id": "method_missing",
                "category": "structure",
                "issue": "Method section missing",
            },
            {
                "issue_id": "method_missing",
                "category": "structure",
                "issue": "Method section missing",
            },
            {
                "issue_id": "method_missing",
                "category": "structure",
                "issue": "Method section missing",
            },
        ]
        result = deduplicate_recommendations(recommendations)
        assert len(result) == 1
        assert result[0]["issue_id"] == "method_missing"

    def test_duplicates_with_different_messages_kept(self):
        recommendations = [
            {
                "issue_id": "method_missing",
                "category": "structure",
                "issue": "Method section missing",
            },
            {
                "issue_id": "results_missing",
                "category": "structure",
                "issue": "Results section missing",
            },
        ]
        result = deduplicate_recommendations(recommendations)
        assert len(result) == 2

    def test_duplicates_with_different_categories_kept(self):
        recommendations = [
            {
                "issue_id": "method_missing",
                "category": "structure",
                "issue": "Method section missing",
            },
            {
                "issue_id": "method_missing",
                "category": "content",
                "issue": "Method section missing",
            },
        ]
        result = deduplicate_recommendations(recommendations)
        assert len(result) == 2

    def test_empty_list_returns_empty(self):
        result = deduplicate_recommendations([])
        assert result == []

    def test_uses_message_field_as_fallback(self):
        recommendations = [
            {
                "issue_id": "test",
                "category": "test",
                "message": "Some message",
            },
            {
                "issue_id": "test",
                "category": "test",
                "message": "Some message",
            },
        ]
        result = deduplicate_recommendations(recommendations)
        assert len(result) == 1


# ============ Context Builder Tests ============

class TestContextBuilder:
    def test_build_with_all_fields(self):
        builder = ContextBuilder()
        context = builder.build(
            conference={"id": "neurips-2025", "name": "NeurIPS 2025"},
            compliance_score=45,
            critical_issues=[{"issue_id": "test", "message": "Critical issue"}],
            warnings=[{"issue_id": "warn", "message": "Warning"}],
            passed_checks=["anonymity", "references"],
            recommendations=[{"issue_id": "rec1", "suggested_action": "Fix it"}],
        )
        assert context["compliance_score"] == 45
        assert len(context["critical_issues"]) == 1
        assert len(context["warnings"]) == 1
        assert len(context["passed_checks"]) == 2
        assert len(context["recommendations"]) == 1
        assert context["conference"]["id"] == "neurips-2025"

    def test_build_with_empty_fields(self):
        builder = ContextBuilder()
        context = builder.build()
        assert context["compliance_score"] == 0
        assert context["critical_issues"] == []
        assert context["warnings"] == []
        assert context["passed_checks"] == []
        assert context["recommendations"] == []
        assert context["conference"] == {}


# ============ Prompt Builder Tests ============

class TestPromptBuilder:
    def test_build_system_prompt_contains_all_sections(self):
        builder = PromptBuilder()
        prompt = builder.build_system_prompt(
            conference={"id": "neurips-2025"},
            compliance_score=45,
            critical_issues=[{"issue": "Missing method section"}],
            warnings=[{"issue": "Page count close to limit"}],
            passed_checks=["references"],
            recommendations=[{"issue": "Add method section", "category": "structure", "severity": "critical"}],
            user_message="Fix all issues",
        )
        assert "Conference Information" in prompt
        assert "Compliance Score" in prompt
        assert "Critical Issues" in prompt
        assert "Warnings" in prompt
        assert "Passed Checks" in prompt
        assert "Recommendations" in prompt
        assert "User Question" in prompt
        assert "Fix all issues" in prompt
        assert "Missing method section" in prompt

    def test_build_context_format(self):
        builder = PromptBuilder()
        context = builder.build_context(
            conference={"id": "test-conf"},
            compliance_score=80,
            critical_issues=[],
            warnings=[{"issue": "Test warning"}],
            passed_checks=["check1"],
            recommendations=[{"issue": "Rec 1", "category": "general", "severity": "info"}],
        )
        assert "Conference Information" in context
        assert "80" in context
        assert "Test warning" in context
        assert "check1" in context
        assert "Rec 1" in context


# ============ Assistant Service Tests ============

class TestAssistantService:
    @pytest.mark.asyncio
    async def test_chat_returns_answer(self):
        service = AssistantService()
        result = await service.chat(
            compliance_score=75,
            critical_issues=[],
            warnings=[],
            passed_checks=["references"],
            recommendations=[],
            user_message="How is my paper?",
        )
        assert "answer" in result
        assert isinstance(result["answer"], str)
        assert len(result["answer"]) > 0

    @pytest.mark.asyncio
    async def test_chat_with_critical_issues(self):
        service = AssistantService()
        result = await service.chat(
            compliance_score=30,
            critical_issues=[{"issue": "Missing method section", "message": "Method section missing"}],
            warnings=[],
            passed_checks=[],
            recommendations=[{"issue": "Add method", "category": "structure", "severity": "critical"}],
            user_message="What's wrong?",
        )
        assert "Critical Issues" in result["answer"]
        assert "Missing method section" in result["answer"] or "Method section missing" in result["answer"]

    @pytest.mark.asyncio
    async def test_chat_deduplicates_recommendations(self):
        service = AssistantService()
        duplicate_recs = [
            {"issue_id": "test", "category": "structure", "issue": "Test issue", "suggested_action": "Fix"},
            {"issue_id": "test", "category": "structure", "issue": "Test issue", "suggested_action": "Fix"},
        ]
        with patch.object(service, "_generate_response", new_callable=AsyncMock) as mock:
            mock.return_value = "Response"
            result = await service.chat(
                compliance_score=50,
                recommendations=duplicate_recs,
                user_message="Help",
            )
            assert result["answer"] == "Response"
            # Verify that only 1 recommendation was passed to generate
            call_context = mock.call_args[0][1]
            assert len(call_context["recommendations"]) == 1

    @pytest.mark.asyncio
    async def test_chat_empty_message(self):
        service = AssistantService()
        result = await service.chat(
            compliance_score=100,
            user_message="",
        )
        assert "answer" in result
        assert isinstance(result["answer"], str)
