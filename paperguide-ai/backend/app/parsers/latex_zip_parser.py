"""LaTeX ZIP parser for extracting content and metadata."""

import re
import zipfile
import os
from typing import Dict, List
from ..core import get_logger

logger = get_logger(__name__)


class LatexZipParser:
    """Parse LaTeX ZIP files."""

    def parse(self, file_path: str) -> Dict:
        """Extract LaTeX files and content from ZIP."""
        try:
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                tex_files = [f for f in zip_ref.namelist() if f.endswith('.tex')]
                bib_files = [f for f in zip_ref.namelist() if f.endswith('.bib')]
                sty_files = [f for f in zip_ref.namelist() if f.endswith('.sty')]
                
                text = ""
                has_checklist = False
                checklist_file = None
                
                for tex_file in tex_files[:1]:
                    try:
                        with zip_ref.open(tex_file) as f:
                            content = f.read().decode('utf-8', errors='ignore')
                            text += content
                            if 'checklist' in content.lower():
                                has_checklist = True
                    except Exception as e:
                        logger.warning(f"Error reading {tex_file}: {str(e)}")
                
                sections = self._detect_sections(text)
                has_bibliography = self._find_bibliography(text)
                
                return {
                    "page_count": None,
                    "extracted_text": text[:5000],
                    "sections": sections,
                    "abstract_found": self._find_abstract(text),
                    "references_found": has_bibliography,
                    "tex_files": tex_files,
                    "bib_files": bib_files,
                    "sty_files": sty_files,
                    "has_checklist": has_checklist,
                }
        except Exception as e:
            logger.error(f"Error parsing LaTeX ZIP: {str(e)}")
            return {
                "page_count": None,
                "extracted_text": None,
                "sections": [],
                "abstract_found": False,
                "references_found": False,
                "error": str(e),
            }

    def _detect_sections(self, text: str) -> List[str]:
        """Detect sections from LaTeX commands."""
        sections = []
        patterns = [
            r'\\section\{([^}]+)\}',
            r'\\subsection\{([^}]+)\}',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text)
            sections.extend(matches)
        
        return sections

    def _find_abstract(self, text: str) -> bool:
        """Check if abstract environment exists."""
        return bool(re.search(r'\\begin\{abstract\}', text))

    def _find_bibliography(self, text: str) -> bool:
        """Check if bibliography is referenced."""
        patterns = [
            r'\\bibliography\{',
            r'\\cite\{',
            r'\\bibitem',
        ]
        for pattern in patterns:
            if re.search(pattern, text):
                return True
        return False
