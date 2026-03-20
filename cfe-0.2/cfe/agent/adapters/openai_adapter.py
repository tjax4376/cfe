"""
CFE OpenAI Adapter – translates CFE messages to OpenAI Chat Completions API.

Version: 3.0
Author: Generated for aidev
Change rationale: Phase 9a – OpenAI vendor adapter using the Chat Completions
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

OPENAI_CHAT_URL = "https://api.openai.com/v1/chat/completions"


class OpenAIAdapter(BaseAdapter):
    """Adapter for the OpenAI Chat Completions API."""

    def send(
        self,
        message: Message,
        config: AgentConfig,
        history: List[Tuple[str, str]],
    ) -> Response:
        messages = self._build_messages(message, config, history)
        request_body: Dict[str, Any] = {
            "model": config.model or "gpt-4o",
            "messages": messages,
            "max_tokens": config.max_tokens,
            "temperature": config.temperature,
        }

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
        config: AgentConfig,
        history: List[Tuple[str, str]],
    ) -> List[Dict[str, str]]:
        msgs: List[Dict[str, str]] = []

        if config.system_prompt:
            msgs.append({"role": "system", "content": config.system_prompt})

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
            OPENAI_CHAT_URL,
            data=data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
            },
            method="POST",
        )
        try:
            with urlopen(req, timeout=60) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except HTTPError as exc:
            error_body = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(
                f"OpenAI API error {exc.code}: {error_body}"
            ) from exc
        except URLError as exc:
            raise RuntimeError(
                f"OpenAI API connection error: {exc.reason}"
            ) from exc

    def _parse_response(
        self, raw: Dict[str, Any], model_name: str,
    ) -> Response:
        try:
            choice = raw["choices"][0]
            content = choice["message"]["content"] or ""
            usage = raw.get("usage", {})
            total_tokens = usage.get("total_tokens", 0)
            model = raw.get("model", model_name)

            return Response(
                payload=content.strip(),
                status="success",
                tokens=total_tokens,
                model=model,
                error=None,
            )
        except (KeyError, IndexError) as exc:
            return Response(
                payload="",
                status="error",
                tokens=0,
                model=model_name,
                error=f"Failed to parse OpenAI response: {exc}",
            )
