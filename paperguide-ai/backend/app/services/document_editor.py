"""Document Editor service - applies edits to DOCX/TEX/PDF files."""

import os
import shutil
from datetime import datetime
from typing import Any, Dict, List, Optional
from ..core import get_logger, settings

logger = get_logger(__name__)


class DocumentEditor:
    """Edits uploaded documents based on fix agent instructions.

    Supported file types:
    - DOCX: python-docx paragraph manipulation
    - TEX (LaTeX ZIP): source file modification
    - PDF: limited support (create annotated copy)

    Always creates original backup before editing.
    """

    EDITS_DIR = os.path.join(settings.GENERATED_DIR, "edits")

    def __init__(self):
        os.makedirs(self.EDITS_DIR, exist_ok=True)

    def backup_original(self, storage_path: str, paper_id: str) -> str:
        """Create timestamped backup of original file."""
        backup_dir = os.path.join(self.EDITS_DIR, paper_id, "backups")
        os.makedirs(backup_dir, exist_ok=True)
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        ext = os.path.splitext(storage_path)[1]
        backup_path = os.path.join(backup_dir, f"original_{timestamp}{ext}")
        shutil.copy2(storage_path, backup_path)
        logger.info(f"Backup created: {backup_path}")
        return backup_path

    def edit_docx(self, storage_path: str, edits: List[Dict[str, Any]]) -> str:
        """Apply edits to a DOCX file. Returns path to edited file."""
        from docx import Document

        doc = Document(storage_path)
        for edit in edits:
            action = edit.get("action", "")
            if action == "replace_text":
                for paragraph in doc.paragraphs:
                    if edit.get("old_text") in paragraph.text:
                        for run in paragraph.runs:
                            if edit["old_text"] in run.text:
                                run.text = run.text.replace(edit["old_text"], edit["new_text"])
            elif action == "add_paragraph":
                doc.add_paragraph(edit.get("text", ""))
            elif action == "remove_paragraph":
                for paragraph in doc.paragraphs:
                    if edit.get("text", "") in paragraph.text:
                        p_element = paragraph._element
                        p_element.getparent().remove(p_element)

        edited_path = self._edited_path(storage_path)
        doc.save(edited_path)
        logger.info(f"DOCX edits saved to: {edited_path}")
        return edited_path

    def edit_tex_content(self, main_tex_content: str, edits: List[Dict[str, Any]], file_type: str = "") -> str:
        """Apply edits to LaTeX content string. Returns modified content."""
        content = main_tex_content
        for edit in edits:
            action = edit.get("action", "")
            if action == "replace_text":
                content = content.replace(edit.get("old_text", ""), edit.get("new_text", ""))
            elif action == "insert_before":
                target = edit.get("target", "")
                if target in content:
                    idx = content.index(target)
                    content = content[:idx] + edit.get("text", "") + "\n" + content[idx:]
            elif action == "insert_after":
                target = edit.get("target", "")
                if target in content:
                    idx = content.index(target) + len(target)
                    content = content[:idx] + "\n" + edit.get("text", "") + content[idx:]
            elif action == "remove_line":
                lines = content.split("\n")
                content = "\n".join(
                    l for l in lines if edit.get("text", "") not in l
                )
            elif action == "add_preamble":
                if r"\begin{document}" in content:
                    idx = content.index(r"\begin{document}")
                    content = content[:idx] + edit.get("text", "") + "\n" + content[idx:]
        return content

    def edit_tex_file(self, storage_path: str, edits: List[Dict[str, Any]]) -> str:
        """Apply edits directly to a .tex file."""
        with open(storage_path, "r", encoding="utf-8") as f:
            content = f.read()
        modified = self.edit_tex_content(content, edits)
        edited_path = self._edited_path(storage_path)
        with open(edited_path, "w", encoding="utf-8") as f:
            f.write(modified)
        logger.info(f"TEX edits saved to: {edited_path}")
        return edited_path

    def _edited_path(self, storage_path: str) -> str:
        base, ext = os.path.splitext(os.path.basename(storage_path))
        edited_dir = os.path.join(self.EDITS_DIR, "latest")
        os.makedirs(edited_dir, exist_ok=True)
        return os.path.join(edited_dir, f"{base}_fixed{ext}")

    def replace_source_files(self, parsed_paper: Dict[str, Any], file_name: str, new_content: str) -> Dict[str, Any]:
        """Replace a source file in parsed_paper['source_files']."""
        if "source_files" not in parsed_paper:
            return parsed_paper
        parsed_paper["source_files"][file_name] = new_content.encode("utf-8")
        if file_name == "main.tex" or file_name.endswith(".tex"):
            parsed_paper["main_tex_content"] = new_content
        return parsed_paper
