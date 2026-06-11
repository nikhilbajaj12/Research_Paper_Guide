"""LaTeX ZIP parser for extracting content and metadata."""

import re
import zipfile
from pathlib import PurePosixPath
from typing import Dict, List, Optional
from ..core import get_logger, settings

logger = get_logger(__name__)


class LatexZipParser:
    """Parse LaTeX ZIP files."""

    def parse(self, file_path: str) -> Dict:
        """Extract LaTeX files and content from ZIP."""
        try:
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                archive_files = [info for info in zip_ref.infolist() if not info.is_dir()]
                max_uncompressed_size = settings.MAX_PACKAGE_SIZE_MB * 1024 * 1024
                total_uncompressed_size = sum(info.file_size for info in archive_files)
                if total_uncompressed_size > max_uncompressed_size:
                    raise ValueError(
                        f"LaTeX project exceeds {settings.MAX_PACKAGE_SIZE_MB}MB uncompressed size limit"
                    )

                tex_files = [info.filename for info in archive_files if info.filename.lower().endswith('.tex')]
                bib_files = [info.filename for info in archive_files if info.filename.lower().endswith('.bib')]
                sty_files = [info.filename for info in archive_files if info.filename.lower().endswith('.sty')]
                
                text = ""
                has_checklist = False
                source_files = {}
                tex_contents = {}
                
                for file_info in archive_files:
                    source_file = file_info.filename
                    try:
                        with zip_ref.open(source_file) as f:
                            file_content = f.read()
                            if self._is_safe_archive_path(source_file):
                                source_files[source_file] = file_content
                            if source_file in tex_files:
                                content = file_content.decode('utf-8', errors='ignore')
                                tex_contents[source_file] = content
                                text += content + "\n"
                                if 'checklist' in content.lower():
                                    has_checklist = True
                    except Exception as e:
                        logger.warning(f"Error reading {source_file}: {str(e)}")
                
                sections = self._detect_sections(text)
                has_bibliography = self._find_bibliography(text)
                main_tex_path = self._select_main_tex(tex_files, tex_contents)
                main_tex_content = tex_contents.get(main_tex_path)
                
                return {
                    "page_count": None,
                    "extracted_text": text,
                    "sections": sections,
                    "abstract_found": self._find_abstract(text),
                    "references_found": has_bibliography,
                    "tex_files": tex_files,
                    "bib_files": bib_files,
                    "sty_files": sty_files,
                    "has_checklist": has_checklist,
                    "source_type": "latex",
                    "source_files": source_files,
                    "main_tex_path": main_tex_path,
                    "main_tex_content": main_tex_content,
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

    def _is_safe_archive_path(self, path: str) -> bool:
        """Check that a source file can be safely copied into a generated ZIP."""
        normalized = path.replace('\\', '/')
        archive_path = PurePosixPath(normalized)
        return not archive_path.is_absolute() and '..' not in archive_path.parts

    def _select_main_tex(self, tex_files: List[str], tex_contents: Dict[str, str]) -> Optional[str]:
        """Select the most likely project entry point deterministically."""
        if "main.tex" in tex_contents:
            return "main.tex"
        for tex_file in tex_files:
            if PurePosixPath(tex_file).name.lower() == "main.tex":
                return tex_file
        for tex_file in tex_files:
            if r'\documentclass' in tex_contents.get(tex_file, ''):
                return tex_file
        return tex_files[0] if tex_files else None

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
