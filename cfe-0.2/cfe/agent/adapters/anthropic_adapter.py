"""
CFE Anthropic Adapter – translates CFE messages to the Anthropic Messages API.

Version: 3.0
Author: Generated for aidev
Change rationale: Phase 9a – Anthropic vendor adapter using the Messages
                  endpoint with session history support.

Security:
  - API key is passed from AgentConfig (resolved from env var at load time).
  - No secrets are logged or stored beyond the config object's lifetime.
  - Request payloads are data only; no executable code is sent.
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Tuple
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from ..config import AgentConfig
from ..message import Message, Response
from .base import BaseAdapter

ANTHROPIC_MESSAGES_URL = "https://api.anthropic.com/v1/messages"
ANTHROPIC_API_VERSION = "2023-06-01"


class AnthropicAdapter(BaseAdapter):
    """Adapter for the Anthropic Messages API."""

    def send(
        self,
        message: Message,
        config: AgentConfig,
        history: List[Tuple[str, str]],
    ) -> Response:
        messages = self._build_messages(message, history)
        request_body: Dict[str, Any] = {
            "model": config.model or "claude-sonnet-4-20250514",
            "max_tokens": config.max_tokens,
            "messages": messages,
        }
        if config.system_prompt:
            request_body["system"] = config.system_prompt
        if config.temperature is not None:
            request_body["temperature"] = config.temperature

        try:
            raw = self._http_post(config.api_key, request_body)
        except Exception as exc:
            return Response(
                payload="",
                status="error",
                tokens=0,
                model=config.model,
                error=str(exc),
            )

        return self._parse_response(raw, config.model)

    def validate_config(self, config: AgentConfig) -> bool:
        if not config.api_key:
            return False
        if not config.model:
            return False
        return True

    def _build_messages(
        self,
        message: Message,
        history: List[Tuple[str, str]],
    ) -> List[Dict[str, str]]:
        msgs: List[Dict[str, str]] = []

        for role, content in history:
            api_role = "assistant" if role == "assistant" else "user"
            msgs.append({"role": api_role, "content": content})

        prompt = message.to_prompt()
        if prompt:
            msgs.append({"role": "user", "content": prompt})

        return msgs

    def _http_post(
        self, api_key: str, body: Dict[str, Any],
    ) -> Dict[str, Any]:
        data = json.dumps(body).encode("utf-8")
        req = Request(
            ANTHROPIC_MESSAGES_URL,
            data=data,
            headers={
                "Content-Type": "application/json",
                "x-api-key": api_key,
                "anthropic-version": ANTHROPIC_API_VERSION,
            },
            method="POST",
        )
        try:
            with urlopen(req, timeout=60) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except HTTPError as exc:
            error_body = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(
                f"Anthropic API error {exc.code}: {error_body}"
            ) from exc
        except URLError as exc:
            raise RuntimeError(
                f"Anthropic API connection error: {exc.reason}"
            ) from exc

    def _parse_response(
        self, raw: Dict[str, Any], model_name: str,
    ) -> Response:
        try:
            content_blocks = raw.get("content", [])
            text_parts = []
            for block in content_blocks:
                if block.get("type") == "text":
                    text_parts.append(block.get("text", ""))
            content = "\n".join(text_parts)

            usage = raw.get("usage", {})
            input_tokens = usage.get("input_tokens", 0)
            output_tokens = usage.get("output_tokens", 0)
            total_tokens = input_tokens + output_tokens
            model = raw.get("model", model_name)

            return Response(
                payload=content.strip(),
                status="success",
                tokens=total_tokens,
                model=model,
                error=None,
            )
        except (KeyError, IndexError, TypeError) as exc:
            return Response(
                payload="",
                status="error",
                tokens=0,
                model=model_name,
                error=f"Failed to parse Anthropic response: {exc}",
            )
