"""MCP (Model Context Protocol) integration for file system operations."""

import os
import json
import shutil
from typing import Any, Dict, List, Optional
from ..core import get_logger, settings

logger = get_logger(__name__)


class MCPService:
    """Lightweight MCP tool integration for filesystem operations.

    Provides file read/write/create operations that the planner agent
    can invoke during the fix pipeline.
    """

    def __init__(self):
        self.base_path = settings.LOCAL_STORAGE_PATH
        self.edit_base = os.path.join(settings.GENERATED_DIR, "edits")
        os.makedirs(self.edit_base, exist_ok=True)

    async def read_file(self, path: str) -> Optional[str]:
        """Read a file from the filesystem."""
        full_path = self._resolve_path(path)
        if not full_path or not os.path.exists(full_path):
            logger.warning(f"MCP read_file: path not found {path}")
            return None
        try:
            with open(full_path, "r", encoding="utf-8", errors="replace") as f:
                return f.read()
        except Exception as e:
            logger.error(f"MCP read_file error: {e}")
            return None

    async def write_file(self, path: str, content: str) -> bool:
        """Write content to a file."""
        full_path = self._resolve_path(path)
        if not full_path:
            return False
        try:
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(content)
            logger.info(f"MCP write_file: {full_path}")
            return True
        except Exception as e:
            logger.error(f"MCP write_file error: {e}")
            return False

    async def list_files(self, directory: str) -> List[str]:
        """List files in a directory."""
        full_path = self._resolve_path(directory)
        if not full_path or not os.path.isdir(full_path):
            return []
        return os.listdir(full_path)

    async def copy_file(self, source: str, dest: str) -> bool:
        """Copy a file."""
        src_path = self._resolve_path(source)
        dst_path = self._resolve_path(dest)
        if not src_path or not dst_path:
            return False
        try:
            os.makedirs(os.path.dirname(dst_path), exist_ok=True)
            shutil.copy2(src_path, dst_path)
            return True
        except Exception as e:
            logger.error(f"MCP copy_file error: {e}")
            return False

    async def create_directory(self, path: str) -> bool:
        """Create a directory."""
        full_path = self._resolve_path(path)
        if not full_path:
            return False
        try:
            os.makedirs(full_path, exist_ok=True)
            return True
        except Exception as e:
            logger.error(f"MCP create_directory error: {e}")
            return False

    def _resolve_path(self, path: str) -> Optional[str]:
        """Resolve a path, ensuring it stays within allowed directories."""
        allowed = [
            os.path.abspath(self.base_path),
            os.path.abspath(self.edit_base),
            os.path.abspath(settings.GENERATED_DIR),
        ]
        abs_path = os.path.abspath(path) if os.path.isabs(path) else os.path.abspath(
            os.path.join(self.base_path, path)
        )
        for allowed_dir in allowed:
            if abs_path.startswith(allowed_dir):
                return abs_path
        logger.warning(f"MCP path resolution denied: {path} (outside allowed dirs)")
        return None

    async def create_package_zip(
        self,
        source_dir: str,
        output_path: str,
        files: List[str],
    ) -> bool:
        """Create a ZIP package from specified files."""
        import zipfile

        full_output = self._resolve_path(output_path)
        if not full_output:
            return False
        try:
            os.makedirs(os.path.dirname(full_output), exist_ok=True)
            with zipfile.ZipFile(full_output, "w", zipfile.ZIP_DEFLATED) as zf:
                for fname in files:
                    src = os.path.join(source_dir, fname)
                    if os.path.exists(src):
                        zf.write(src, fname)
            logger.info(f"MCP created package: {full_output}")
            return True
        except Exception as e:
            logger.error(f"MCP create_package_zip error: {e}")
            return False
