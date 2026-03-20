"""
CFE Agent Configuration Loader – reads agents.yaml and resolves credentials.

Version: 3.0
Author: Generated for aidev
Change rationale: Phase 9a – load agent definitions from external YAML config,
                  resolve API keys from environment variables, validate required
                  fields.

Security:
  - API keys are stored as environment variable *names* in YAML, never as
    literal secrets.
  - Missing env vars produce a clear error at load time.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional

try:
    import yaml  # type: ignore[import-untyped]
    _HAS_YAML = True
except ImportError:
    _HAS_YAML = False


class ConfigError(Exception):
    """Raised when agent configuration is invalid or incomplete."""


SUPPORTED_VENDORS = frozenset({
    "openai", "anthropic", "google", "local", "http",
})


@dataclass
class AgentConfig:
    """Validated configuration for a single agent."""

    name: str
    vendor: str
    model: str = ""
    api_key: str = ""
    system_prompt: str = ""
    max_tokens: int = 1024
    temperature: float = 0.7
    extra: Dict[str, Any] = field(default_factory=dict)


def _resolve_env(env_name: str, agent_name: str) -> str:
    """Resolve an environment variable name to its value."""
    val = os.environ.get(env_name, "")
    if not val:
        raise ConfigError(
            f"Agent '{agent_name}': environment variable '{env_name}' "
            f"is not set or empty"
        )
    return val


def _parse_agent(name: str, raw: Dict[str, Any]) -> AgentConfig:
    """Parse and validate a single agent entry from the config dict."""
    vendor = raw.get("vendor", "")
    if not vendor:
        raise ConfigError(f"Agent '{name}': missing required field 'vendor'")
    if vendor not in SUPPORTED_VENDORS:
        raise ConfigError(
            f"Agent '{name}': unsupported vendor '{vendor}'. "
            f"Supported: {', '.join(sorted(SUPPORTED_VENDORS))}"
        )

    api_key = ""
    api_key_env = raw.get("api_key_env", "")
    if api_key_env:
        api_key = _resolve_env(api_key_env, name)

    model = raw.get("model", "")
    system_prompt = raw.get("system_prompt", "")
    max_tokens = int(raw.get("max_tokens", 1024))
    temperature = float(raw.get("temperature", 0.7))

    known = {"vendor", "model", "api_key_env", "system_prompt",
             "max_tokens", "temperature"}
    extra = {k: v for k, v in raw.items() if k not in known}

    return AgentConfig(
        name=name,
        vendor=vendor,
        model=model,
        api_key=api_key,
        system_prompt=system_prompt,
        max_tokens=max_tokens,
        temperature=temperature,
        extra=extra,
    )


def load_config(path: Optional[str] = None) -> Dict[str, AgentConfig]:
    """Load agent configs from a YAML file.

    Parameters
    ----------
    path : str or None
        Path to the YAML config file.  Defaults to ``agents.yaml`` in the
        current working directory.

    Returns
    -------
    dict[str, AgentConfig]
        Mapping from agent name to its validated configuration.
    """
    if not _HAS_YAML:
        raise ConfigError(
            "PyYAML is required for agent configuration. "
            "Install it with: pip install pyyaml"
        )

    config_path = Path(path) if path else Path("agents.yaml")
    if not config_path.exists():
        raise ConfigError(f"Agent config file not found: {config_path}")

    with open(config_path) as f:
        data = yaml.safe_load(f)

    if not isinstance(data, dict) or "agents" not in data:
        raise ConfigError(
            f"Config file {config_path} must contain a top-level 'agents' key"
        )

    agents_raw = data["agents"]
    if not isinstance(agents_raw, dict):
        raise ConfigError("'agents' must be a mapping of name → config")

    result: Dict[str, AgentConfig] = {}
    for name, raw in agents_raw.items():
        if not isinstance(raw, dict):
            raise ConfigError(f"Agent '{name}': config must be a mapping")
        result[name] = _parse_agent(str(name), raw)

    return result


def load_config_from_dict(data: Dict[str, Any]) -> Dict[str, AgentConfig]:
    """Load agent configs from an in-memory dict (useful for testing)."""
    agents_raw = data.get("agents", data)
    result: Dict[str, AgentConfig] = {}
    for name, raw in agents_raw.items():
        if not isinstance(raw, dict):
            raise ConfigError(f"Agent '{name}': config must be a mapping")
        result[name] = _parse_agent(str(name), raw)
    return result
