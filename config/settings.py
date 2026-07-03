import os
import yaml

# Determine the absolute path to default.yaml relative to this file's location
DEFAULT_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "default.yaml")

class AutoFixSettings:
    """
    Handles loading, parsing, and providing access to the auto-fix configuration.
    Acts as the single abstraction layer between the application and the raw configuration data.
    """
    def __init__(self, config_path: str = DEFAULT_CONFIG_PATH):
        self.config_path = config_path
        self._config = self._load_config()

    def _load_config(self) -> dict:
        """Reads and safely parses the YAML configuration file."""
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Configuration file not found at: {self.config_path}")
            
        with open(self.config_path, "r", encoding="utf-8") as f:
            try:
                config_data = yaml.safe_load(f)
                return config_data if isinstance(config_data, dict) else {}
            except yaml.YAMLError as e:
                raise RuntimeError(f"Failed to parse YAML configuration: {e}")

    def get(self, key: str, default=None):
        """Generic fallback helper to fetch top-level configuration blocks."""
        return self._config.get(key, default)

    # -------------------------------------------------------------------------
    # Rich Configuration API Layer (Encapsulated properties with defaults)
    # -------------------------------------------------------------------------
    @property
    def max_iterations(self) -> int:
        """Returns the configured maximum pipeline loop iterations (Default: 20)."""
        return self.pipeline_settings.get("max_iterations", 20)

    @property
    def ai_enabled(self) -> bool:
        """Returns whether AI capabilities and fallbacks are toggled on (Default: False)."""
        return self.ai_settings.get("enable_ai", False)

    @property
    def ruff_enabled(self) -> bool:
        """Returns whether the Ruff analyzer run is enabled (Default: True)."""
        return self.analyzer_settings.get("ruff", {}).get("enabled", True)

    @property
    def bandit_enabled(self) -> bool:
        """Returns whether the Bandit analyzer run is enabled (Default: True)."""
        return self.analyzer_settings.get("bandit", {}).get("enabled", True)

    @property
    def semgrep_enabled(self) -> bool:
        """Returns whether the Semgrep analyzer run is enabled (Default: True)."""
        return self.analyzer_settings.get("semgrep", {}).get("enabled", True)

    @property
    def semgrep_config_path(self) -> str:
        """Returns the local rule configuration file path for Semgrep (Default: 'semgrep_test_rule.yml')."""
        return self.analyzer_settings.get("semgrep", {}).get("config_path", "semgrep_test_rule.yml")

    @property
    def logging_level(self) -> str:
        """Returns the threshold log level configuration (Default: 'INFO')."""
        return self.logging_settings.get("level", "INFO")

    @property
    def logging_file(self) -> str:
        """Returns the tracking path destination for engine logs (Default: 'logs/agent.log')."""
        return self.logging_settings.get("file_path", "logs/agent.log")

    @property
    def console_logging_enabled(self) -> bool:
        """Returns whether engine stdout logs are printed to standard output (Default: True)."""
        return self.logging_settings.get("enable_console", True)

    # -------------------------------------------------------------------------
    # Backward Compatibility & Structural Subgroups
    # -------------------------------------------------------------------------
    @property
    def ai_settings(self) -> dict:
        """Returns the AI configuration sub-dictionary."""
        return self._config.get("ai_settings", {})

    @property
    def pipeline_settings(self) -> dict:
        """Returns the execution pipeline settings."""
        return self._config.get("pipeline_settings", {})

    @property
    def analyzer_settings(self) -> dict:
        """Returns the tool enablement and setup settings for analyzers."""
        return self._config.get("analyzer_settings", {})

    @property
    def rule_priorities(self) -> dict:
        """Returns the priority configuration mapping for rules."""
        return self._config.get("rule_priorities", {})

    @property
    def disabled_rules(self) -> list:
        """Returns the list of rules excluded from automatic fixing."""
        return self._config.get("disabled_rules", [])

    @property
    def logging_settings(self) -> dict:
        """Returns the logging configuration sub-dictionary."""
        return self._config.get("logging_settings", {})


# Instantiate a singleton-style instance for seamless cross-module imports
settings = AutoFixSettings()