"""Package generation service."""

import os
import uuid
from datetime import datetime
from typing import Dict, Optional, Tuple
from ..core import get_logger, settings
from ..services.report_generator import ReportGenerator
from ..services.latex_package_generator import LatexPackageGenerator
from ..utils.zip_utils import ZipUtils

logger = get_logger(__name__)

PACKAGE_STORAGE = {}


class PackageService:
    """Service for generating and managing packages."""

    def __init__(self):
        """Initialize service."""
        self.report_gen = ReportGenerator()
        self.latex_gen = LatexPackageGenerator()
        self.zip_utils = ZipUtils()

    def generate_package(
        self,
        paper_id: str,
        conference_id: str,
        parsed_paper: Dict,
        compliance_report: Dict,
        conference_config: Optional[Dict] = None,
        project_id: Optional[str] = None,
        package_type: str = "overleaf"
    ) -> Tuple[str, Dict]:
        """
        Generate Overleaf package.
        
        Returns: (package_id, package_metadata)
        """
        logger.info(f"Generating package for paper: {paper_id}")
        
        package_id = str(uuid.uuid4())
        project_id = project_id or paper_id
        
        try:
            os.makedirs(settings.PACKAGE_DIR, exist_ok=True)
            
            has_citations = parsed_paper.get('citation_patterns_found', False)
            has_references = parsed_paper.get('references_found', False)
            
            files_dict = {}
            generated_files = []

            for source_file, source_content in parsed_paper.get('source_files', {}).items():
                files_dict[source_file] = source_content
                generated_files.append({
                    'file_name': source_file,
                    'file_type': os.path.splitext(source_file)[1].lstrip('.') or 'file',
                    'file_path': source_file
                })
            
            main_tex = self.latex_gen.generate_main_tex(
                parsed_paper,
                has_citations=has_citations,
                has_references=has_references,
                conference_config=conference_config,
            )
            files_dict['main.tex'] = main_tex
            if not any(item['file_path'] == 'main.tex' for item in generated_files):
                generated_files.append({
                    'file_name': 'main.tex',
                    'file_type': 'tex',
                    'file_path': 'main.tex'
                })
            
            if not parsed_paper.get('bib_files'):
                references_bib = self.latex_gen.generate_references_bib()
                files_dict['references.bib'] = references_bib
                generated_files.append({
                    'file_name': 'references.bib',
                    'file_type': 'bib',
                    'file_path': 'references.bib'
                })
            
            readme = self.latex_gen.generate_readme(
                conference_config=conference_config,
                compliance_data=compliance_report,
            )
            files_dict['README_OVERLEAF_INSTRUCTIONS.md'] = readme
            generated_files.append({
                'file_name': 'README_OVERLEAF_INSTRUCTIONS.md',
                'file_type': 'md',
                'file_path': 'README_OVERLEAF_INSTRUCTIONS.md'
            })
            
            readiness_score = compliance_report.get('readiness_score', 0)
            overall_status = compliance_report.get('overall_status', 'unknown')
            critical_count = compliance_report.get('critical_count', 0)
            warnings_count = compliance_report.get('warnings_count', 0)
            
            compliance_note = self.latex_gen.generate_compliance_report_note(
                readiness_score,
                overall_status,
                critical_count,
                warnings_count
            )
            
            compliance_report_json = self.report_gen.generate_json_report(compliance_report)
            files_dict['compliance_report.json'] = compliance_report_json
            generated_files.append({
                'file_name': 'compliance_report.json',
                'file_type': 'json',
                'file_path': 'compliance_report.json'
            })
            
            files_dict['COMPLIANCE_SUMMARY.txt'] = compliance_note
            generated_files.append({
                'file_name': 'COMPLIANCE_SUMMARY.txt',
                'file_type': 'txt',
                'file_path': 'COMPLIANCE_SUMMARY.txt'
            })
            
            recommendations = compliance_report.get('recommendations', [])
            recommendations_md = self.latex_gen.generate_recommendations_md(recommendations)
            if recommendations:
                files_dict['recommendations.md'] = recommendations_md
                generated_files.append({
                    'file_name': 'recommendations.md',
                    'file_type': 'md',
                    'file_path': 'recommendations.md'
                })
            
            zip_path = self.zip_utils.create_package_zip(
                files_dict,
                settings.PACKAGE_DIR,
                f"overleaf_{package_id}"
            )
            
            zip_size = self.zip_utils.get_zip_size(zip_path)
            
            package_metadata = {
                'package_id': package_id,
                'project_id': project_id,
                'paper_id': paper_id,
                'conference_id': conference_id,
                'package_type': package_type,
                'zip_file_path': zip_path,
                'generated_files': generated_files,
                'status': 'completed',
                'message': 'Package generated successfully',
                'zip_size_bytes': zip_size,
                'created_at': datetime.utcnow().isoformat(),
            }
            
            PACKAGE_STORAGE[package_id] = package_metadata
            
            logger.info(f"Package created: {package_id}")
            return package_id, package_metadata
        
        except Exception as e:
            logger.error(f"Error generating package: {str(e)}")
            raise

    def get_package(self, package_id: str) -> Optional[Dict]:
        """Get package metadata."""
        return PACKAGE_STORAGE.get(package_id)

    def get_package_zip_path(self, package_id: str) -> Optional[str]:
        """Get ZIP file path for package."""
        package = PACKAGE_STORAGE.get(package_id)
        if package:
            return package.get('zip_file_path')
        return None
