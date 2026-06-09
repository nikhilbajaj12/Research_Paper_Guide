"""ZIP utilities for package creation."""

import os
import zipfile
from pathlib import Path
from typing import List, Dict
from ..core import get_logger

logger = get_logger(__name__)


class ZipUtils:
    """Utility for creating ZIP packages safely."""

    @staticmethod
    def create_package_zip(
        files_dict: Dict[str, str],
        output_path: str,
        package_name: str = "overleaf_package"
    ) -> str:
        """
        Create ZIP package from file dictionary.
        
        Args:
            files_dict: Dict mapping file_name -> file_content
            output_path: Directory to save ZIP
            package_name: Name for the ZIP file
            
        Returns:
            Full path to created ZIP file
        """
        logger.info(f"Creating ZIP package: {package_name}")
        
        os.makedirs(output_path, exist_ok=True)
        
        zip_filename = f"{package_name}.zip"
        zip_path = os.path.join(output_path, zip_filename)
        
        try:
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file_name, file_content in files_dict.items():
                    if isinstance(file_content, str):
                        zipf.writestr(file_name, file_content)
                    elif isinstance(file_content, bytes):
                        zipf.writestr(file_name, file_content)
                    else:
                        logger.warning(f"Skipping file {file_name}: unsupported type")
            
            logger.info(f"ZIP package created: {zip_path}")
            return zip_path
        
        except Exception as e:
            logger.error(f"Error creating ZIP package: {str(e)}")
            raise

    @staticmethod
    def add_files_to_zip(
        zip_path: str,
        files_dict: Dict[str, str]
    ) -> None:
        """Add files to existing ZIP."""
        logger.info(f"Adding files to ZIP: {zip_path}")
        
        try:
            with zipfile.ZipFile(zip_path, 'a', zipfile.ZIP_DEFLATED) as zipf:
                for file_name, file_content in files_dict.items():
                    if isinstance(file_content, str):
                        zipf.writestr(file_name, file_content)
                    elif isinstance(file_content, bytes):
                        zipf.writestr(file_name, file_content)
        except Exception as e:
            logger.error(f"Error adding files to ZIP: {str(e)}")
            raise

    @staticmethod
    def get_zip_size(zip_path: str) -> int:
        """Get ZIP file size in bytes."""
        try:
            return os.path.getsize(zip_path)
        except Exception as e:
            logger.error(f"Error getting ZIP size: {str(e)}")
            return 0

    @staticmethod
    def validate_zip_safety(file_path: str) -> bool:
        """Validate ZIP doesn't contain suspicious paths."""
        try:
            with zipfile.ZipFile(file_path, 'r') as zipf:
                for name in zipf.namelist():
                    if name.startswith('/') or '..' in name or '\\' in name:
                        logger.warning(f"Suspicious path in ZIP: {name}")
                        return False
            return True
        except Exception as e:
            logger.error(f"Error validating ZIP: {str(e)}")
            return False
