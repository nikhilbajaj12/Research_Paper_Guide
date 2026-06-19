"""LLM-powered document fixer - uses LLM to generate and apply fixes."""

import re
from typing import Any, Dict, List, Optional
from ..core import get_logger, settings
from ..utils.llm_utils import call_llm_api

logger = get_logger(__name__)


class LLMFixer:
    """Uses LLM to generate and apply fixes to documents."""

    async def fix_document(
        self,
        parsed_paper: Dict[str, Any],
        issues: List[Dict[str, Any]],
        guidelines: Dict[str, Any],
        command: str,
    ) -> Dict[str, Any]:
        """Use LLM to fix issues in the document.
        
        Args:
            parsed_paper: Parsed document dict
            issues: List of validation issues to fix
            guidelines: Conference guidelines
            command: User command (e.g., "fix my paper")
            
        Returns:
            Updated parsed_paper dict with fixes applied
        """
        if not issues:
            logger.info("No issues to fix")
            return parsed_paper

        # Get the current document content
        extracted_text = parsed_paper.get("extracted_text", "")
        title = parsed_paper.get("title", "Unknown")
        
        if not extracted_text:
            logger.warning("No extracted text to fix")
            return parsed_paper

        # Prepare issues summary for the LLM
        issues_text = self._format_issues(issues)
        
        # Build the fix prompt
        system_prompt = """You are an expert academic paper editor specializing in conference submissions.
Your task is to fix the issues in academic papers to make them compliant with conference guidelines.

When fixing papers:
1. Preserve the original meaning and research contribution
2. Keep the academic tone and structure
3. Fix issues while maintaining clarity
4. Make minimal but effective changes
5. Return ONLY the fixed text, no explanations or comments"""

        user_prompt = f"""Fix this academic paper to address the following issues:

ISSUES TO FIX:
{issues_text}

CONFERENCE GUIDELINES:
- Max pages: {guidelines.get('max_pages', 'Not specified')}
- Requires anonymity: {guidelines.get('requires_anonymity', False)}
- Template: {guidelines.get('package_template', 'standard')}

CURRENT PAPER TITLE:
{title}

CURRENT PAPER CONTENT (first 3000 chars):
{extracted_text[:3000]}...

USER REQUEST: {command}

Please provide the FIXED version of this paper that addresses all the issues listed above.
Focus on:
1. Anonymizing author information if required
2. Adding missing sections
3. Fixing formatting issues
4. Improving structure and clarity
5. Ensuring citation compliance

Return only the fixed paper content."""

        # Call LLM for fixes
        logger.info(f"Calling LLM to fix {len(issues)} issues")
        fixed_text = await call_llm_api(
            messages=[{"role": "user", "content": user_prompt}],
            system_prompt=system_prompt,
            temperature=0.3,  # Lower temp for consistency
            max_tokens=4000,
        )
        
        if not fixed_text or len(fixed_text) < 50:
            logger.warning("LLM returned empty or too-short fix")
            return parsed_paper

        # Update the parsed paper with fixed content
        updated_paper = dict(parsed_paper)
        updated_paper["extracted_text"] = fixed_text
        
        # Try to extract improved title if present
        title_match = re.search(r'(?:title|\\title\{([^}]+)\})', fixed_text, re.IGNORECASE)
        if title_match:
            updated_paper["title"] = title_match.group(1).strip()

        logger.info(f"LLM fix applied: {len(fixed_text)} chars in fixed text")
        return updated_paper

    def _format_issues(self, issues: List[Dict[str, Any]]) -> str:
        """Format issues for the LLM prompt."""
        formatted = []
        for i, issue in enumerate(issues, 1):
            category = issue.get("category", "unknown")
            message = issue.get("message", "")
            severity = issue.get("severity", "warning")
            location = issue.get("location", "unknown")
            
            formatted.append(f"{i}. [{severity.upper()}] {category}")
            formatted.append(f"   Issue: {message}")
            formatted.append(f"   Location: {location}")
        
        return "\n".join(formatted)
