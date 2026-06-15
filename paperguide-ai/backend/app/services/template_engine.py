"""Template engine for conference-aware LaTeX package generation."""

import os
import re
from typing import Dict, Optional
from ..core import get_logger

logger = get_logger(__name__)

PLACEHOLDER_PATTERN = re.compile(r'\{\{(\w+)\}\}')


class TemplateEngine:
    """Loads and renders conference-specific templates with fallback to default."""

    def __init__(self, templates_dir: Optional[str] = None):
        self.templates_dir = templates_dir or os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "templates",
        )
        logger.info(f"Template engine directory: {self.templates_dir}")

    def _load_template(self, conference_id: str, filename: str) -> Optional[str]:
        """Load a template file, with fallback to default."""
        paths_to_try = [
            os.path.join(self.templates_dir, conference_id, filename),
            os.path.join(self.templates_dir, "default", filename),
        ]
        for path in paths_to_try:
            if os.path.exists(path):
                logger.debug(f"Template loaded: {path}")
                with open(path, "r", encoding="utf-8") as f:
                    return f.read()
        logger.warning(f"No template found for {conference_id}/{filename}")
        return None

    def render(self, template_content: str, variables: Dict[str, str]) -> str:
        """Replace {{placeholders}} with variable values."""
        def replacer(match):
            key = match.group(1)
            return variables.get(key, match.group(0))
        return PLACEHOLDER_PATTERN.sub(replacer, template_content)

    def render_main_tex(self, conference_id: str, variables: Dict[str, str]) -> str:
        """Load and render main.tex template for the given conference."""
        content = self._load_template(conference_id, "main.tex")
        if content is None:
            raise FileNotFoundError(
                f"No main.tex template for conference: {conference_id}"
            )
        return self.render(content, variables)

    def render_readme(self, conference_id: str, variables: Dict[str, str]) -> str:
        """Load and render readme.md template for the given conference."""
        content = self._load_template(conference_id, "readme.md")
        if content is None:
            raise FileNotFoundError(
                f"No readme.md template for conference: {conference_id}"
            )
        return self.render(content, variables)

    @staticmethod
    def escape_latex(text: str) -> str:
        """Escape special LaTeX characters in dynamic text."""
        replacements = {
            '\\': r'\textbackslash{}',
            '&': r'\&',
            '%': r'\%',
            '$': r'\$',
            '#': r'\#',
            '_': r'\_',
            '{': r'\{',
            '}': r'\}',
            '~': r'\textasciitilde{}',
            '^': r'\textasciicircum{}',
        }
        return ''.join(replacements.get(char, char) for char in text)
