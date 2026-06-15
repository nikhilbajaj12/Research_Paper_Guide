"""LaTeX ZIP parser for extracting content and metadata."""

import re
import zipfile
from pathlib import PurePosixPath
from typing import Dict, List, Optional, Any
from ..core import get_logger, settings

logger = get_logger(__name__)

CITATION_PATTERNS = [
    r'\\cite\{[^}]+\}',
    r'\[[0-9]+\]',
    r'\([A-Z][a-z]+,\s*\d{4}\)',
]

PERCENTAGE_PATTERN = r'(\d+\.?\d*)\s*%'
DECIMAL_PATTERN = r'\b0\.\d+\b'
SPEEDUP_PATTERN = r'(\d+\.?\d*)\s*x(?:times)?|(\d+\.?\d*)×'
BENCHMARK_KEYWORDS = [
    'accuracy', 'loss', 'perplexity', 'speedup', 'throughput',
    'latency', 'improvement', 'outperforms', 'state-of-the-art',
    'achieves', 'metric', 'benchmark', 'baseline', 'performance'
]


class LatexZipParser:
    """Parse LaTeX ZIP files."""

    def parse(self, file_path: str) -> Dict[str, Any]:
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

                tex_file_names = [info.filename for info in archive_files if info.filename.lower().endswith('.tex')]
                bib_file_names = [info.filename for info in archive_files if info.filename.lower().endswith('.bib')]
                sty_file_names = [info.filename for info in archive_files if info.filename.lower().endswith('.sty')]

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
                            if source_file in tex_file_names:
                                content = file_content.decode('utf-8', errors='ignore')
                                tex_contents[source_file] = content
                                text += content + "\n"
                                if 'checklist' in content.lower():
                                    has_checklist = True
                    except Exception as e:
                        logger.warning(f"Error reading {source_file}: {str(e)}")

                sections = self._detect_sections(text)
                has_bibliography = self._find_bibliography(text)
                main_tex_path = self._select_main_tex(tex_file_names, tex_contents)
                main_tex_content = tex_contents.get(main_tex_path)
                abstract = self._extract_abstract(text)
                citation_patterns = self._find_citation_patterns(text)
                numeric_claims = self._find_numeric_claims(text)

                return {
                    "page_count": None,
                    "extracted_text": text,
                    "sections": sections,
                    "title": self._extract_title(text),
                    "abstract": abstract,
                    "abstract_found": abstract is not None,
                    "references_found": has_bibliography,
                    "citation_patterns_found": len(citation_patterns) > 0,
                    "citation_patterns": citation_patterns,
                    "numeric_claims": numeric_claims,
                    "source_type": "latex",
                    "source_files": source_files,
                    "authors": [],
                    "bib_files": bib_file_names,
                    "sty_files": sty_file_names,
                    "main_tex_content": main_tex_content,
                    "has_checklist": has_checklist,
                }
        except Exception as e:
            logger.error(f"Error parsing LaTeX ZIP: {str(e)}")
            return {
                "page_count": None,
                "extracted_text": None,
                "sections": [],
                "title": None,
                "abstract": None,
                "abstract_found": False,
                "references_found": False,
                "citation_patterns_found": False,
                "citation_patterns": [],
                "numeric_claims": [],
                "source_type": "latex",
                "source_files": {},
                "authors": [],
                "bib_files": [],
                "sty_files": [],
                "main_tex_content": None,
                "has_checklist": False,
                "error": str(e),
            }

    def _is_safe_archive_path(self, path: str) -> bool:
        normalized = path.replace('\\', '/')
        archive_path = PurePosixPath(normalized)
        return not archive_path.is_absolute() and '..' not in archive_path.parts

    def _select_main_tex(self, tex_files: List[str], tex_contents: Dict[str, str]) -> Optional[str]:
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
        sections = []
        patterns = [
            r'\\section\{([^}]+)\}',
            r'\\subsection\{([^}]+)\}',
        ]
        for pattern in patterns:
            matches = re.findall(pattern, text)
            sections.extend(matches)
        return sections

    def _extract_title(self, text: str) -> Optional[str]:
        match = re.search(r'\\title\{(.+?)\}', text, re.DOTALL)
        if match:
            return match.group(1).strip()[:200]
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        return lines[0][:200] if lines else None

    def _extract_abstract(self, text: str) -> Optional[str]:
        match = re.search(r'\\begin\{abstract\}(.*?)\\end\{abstract\}', text, re.DOTALL)
        if match:
            return match.group(1).strip()[:500]
        return None

    def _find_abstract(self, text: str) -> bool:
        return bool(re.search(r'\\begin\{abstract\}', text))

    def _find_bibliography(self, text: str) -> bool:
        patterns = [r'\\bibliography\{', r'\\cite\{', r'\\bibitem']
        for pattern in patterns:
            if re.search(pattern, text):
                return True
        return False

    def _find_citation_patterns(self, text: str) -> List[str]:
        found = []
        for pattern in CITATION_PATTERNS:
            matches = re.findall(pattern, text)
            found.extend(matches)
        return found

    def _find_numeric_claims(self, text: str) -> List[Dict[str, Any]]:
        claims = []
        text_lower = text.lower()
        percentages = re.findall(PERCENTAGE_PATTERN, text)
        for pct in percentages[:10]:
            claims.append({"type": "percentage", "value": f"{pct}%", "severity": "warning"})
        decimals = re.findall(DECIMAL_PATTERN, text)
        for dec in set(decimals):
            idx = text.lower().find(dec)
            if idx >= 0:
                surrounding = text_lower[max(0, idx - 100):min(len(text_lower), idx + 100)]
                if any(kw in surrounding for kw in BENCHMARK_KEYWORDS):
                    claims.append({"type": "metric", "value": dec, "severity": "warning"})
        speedups = re.findall(SPEEDUP_PATTERN, text)
        for sp in speedups[:5]:
            val = sp[0] if sp[0] else sp[1]
            if val:
                claims.append({"type": "speedup", "value": f"{val}x", "severity": "warning"})
        return claims
