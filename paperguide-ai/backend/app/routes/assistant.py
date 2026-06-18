"""AI Assistant routes."""

from fastapi import APIRouter, HTTPException
from ..schemas import AssistantChatRequest, AssistantChatResponse
from ..services.assistant_service import AssistantService
from ..core import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/api/v1/assistant", tags=["assistant"])

assistant_service = AssistantService()


@router.post("/chat", response_model=AssistantChatResponse)
async def chat_with_assistant(request: AssistantChatRequest):
    """Chat with the AI Submission Assistant.

    The assistant provides guidance based on compliance results.
    It does NOT modify files, re-run validators, or trigger package generation.
    """
    logger.info(
        f"Assistant chat request received: score={request.compliance_score}, "
        f"critical_issues={len(request.critical_issues)}, "
        f"recommendations={len(request.recommendations)}"
    )

    try:
        result = await assistant_service.chat(
            conference=request.conference,
            compliance_score=request.compliance_score,
            critical_issues=request.critical_issues,
            warnings=request.warnings,
            passed_checks=request.passed_checks,
            recommendations=request.recommendations,
            user_message=request.user_message,
        )
        return AssistantChatResponse(**result)
    except Exception as e:
        logger.error(f"Assistant chat error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to process assistant request",
        )
