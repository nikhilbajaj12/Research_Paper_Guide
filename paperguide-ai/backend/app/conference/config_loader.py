"""Conference config loader — loads, validates, and caches JSON config files."""

import json
import os
from typing import Dict, List, Optional, Any
from ..schemas import ConferenceConfig
from ..core import get_logger, settings

logger = get_logger(__name__)

REQUIRED_FIELDS = [
    "conference_name",
    "max_pages",
    "blind_review",
    "reference_style",
    "required_sections",
]

SCHEMA_EXAMPLE = {
    "conference_name": "NeurIPS",
    "conference_year": 2026,
    "max_pages": 9,
    "min_pages": 1,
    "blind_review": True,
    "reference_style": "bibtex",
    "required_sections": ["abstract", "introduction", "methodology", "results"],
    "optional_sections": ["appendix"],
    "required_keywords": [],
    "margin_rules": {"top_cm": 2.5, "bottom_cm": 2.5, "left_cm": 2.5, "right_cm": 2.5},
    "package_template": "neurips",
    "scoring_weights": {"critical": 20, "warning": 8, "info": 2},
}


class ConferenceConfigLoader:
    """Loads conference configs from JSON files with caching.

    Adding conference #21 requires only creating conference_configs/21.json.
    No code changes needed.
    """

    _cache: Dict[str, ConferenceConfig] = {}
    _config_dir: str = ""

    def __init__(self, config_dir: Optional[str] = None):
        self._config_dir = config_dir or os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "conference_configs",
        )
        logger.info(f"Conference config dir: {self._config_dir}")

    def load(self, conference_id: str) -> Optional[ConferenceConfig]:
        """Load a conference config by ID (e.g., 'neurips', 'icml')."""
        if conference_id in self._cache:
            logger.debug(f"Config cache HIT: {conference_id}")
            return self._cache[conference_id]

        file_path = os.path.join(self._config_dir, f"{conference_id}.json")
        if not os.path.exists(file_path):
            logger.warning(f"Config file not found: {file_path}")
            return None

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                raw = json.load(f)

            raw["conference_id"] = conference_id
            config = ConferenceConfig.from_dict(raw)
            self._cache[conference_id] = config
            logger.info(f"Config loaded and cached: {conference_id}")
            return config
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            logger.error(f"Failed to load config {conference_id}: {e}")
            return None

    def list_available(self) -> List[Dict[str, Any]]:
        """List all available conference configs (id + name)."""
        available = []
        if not os.path.isdir(self._config_dir):
            logger.warning(f"Config directory not found: {self._config_dir}")
            return available

        for fname in sorted(os.listdir(self._config_dir)):
            if fname.endswith(".json"):
                conf_id = fname[:-5]
                config = self.load(conf_id)
                if config:
                    available.append({
                        "conference_id": conf_id,
                        "conference_name": config.conference_name,
                        "conference_year": config.conference_year,
                    })
        return available

    def validate_config(self, conference_id: str) -> Dict[str, Any]:
        """Validate a conference config and return errors/missing fields."""
        file_path = os.path.join(self._config_dir, f"{conference_id}.json")
        errors = []
        warnings = []

        if not os.path.exists(file_path):
            return {
                "conference_id": conference_id,
                "valid": False,
                "errors": [f"Config file not found: {file_path}"],
                "warnings": [],
            }

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                raw = json.load(f)
        except json.JSONDecodeError as e:
            return {
                "conference_id": conference_id,
                "valid": False,
                "errors": [f"Invalid JSON: {e}"],
                "warnings": [],
            }

        for field in REQUIRED_FIELDS:
            if field not in raw:
                errors.append(f"Missing required field: '{field}'")

        if "max_pages" in raw and not isinstance(raw["max_pages"], int):
            errors.append("'max_pages' must be an integer")

        if "required_sections" in raw and not isinstance(raw["required_sections"], list):
            errors.append("'required_sections' must be a list")

        if "margin_rules" in raw:
            mr = raw["margin_rules"]
            for axis in ["top_cm", "bottom_cm", "left_cm", "right_cm"]:
                if axis not in mr:
                    warnings.append(f"Missing margin rule: 'margin_rules.{axis}' — will use default 2.54cm")

        return {
            "conference_id": conference_id,
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
        }

    def validate_all(self) -> List[Dict[str, Any]]:
        """Validate all available conference configs."""
        results = []
        for entry in self.list_available():
            result = self.validate_config(entry["conference_id"])
            results.append(result)
        return results

    def reload(self, conference_id: str) -> Optional[ConferenceConfig]:
        """Force-reload a config (clear cache, reload)."""
        self._cache.pop(conference_id, None)
        return self.load(conference_id)

    def clear_cache(self) -> None:
        """Clear all cached configs."""
        self._cache.clear()
        logger.info("Conference config cache cleared")


# Singleton for convenience
config_loader = ConferenceConfigLoader()
