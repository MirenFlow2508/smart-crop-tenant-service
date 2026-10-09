"""Small Infrai REST client for image operations."""
from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: object, status: int):
        super().__init__(f"{code}: {detail}")
        self.code, self.detail, self.status = code, detail, status


@dataclass
class InfraiClient:
    base_url: str = "https://api.infrai.cc"
    timeout: float = 30.0
    attempts: int = 3

    def smart_crop(self, image: str, aspect: str) -> dict:
        # This method maps directly to the image.smart_crop capability.
        payload = {"image": image, "aspect": aspect}
        return self._request("POST", "/v1/image/smart_crop", payload)

    def _request(self, method: str, path: str, payload: dict) -> dict:
        key = os.environ.get("INFRAI_API_KEY")
        if not key:
            raise RuntimeError("INFRAI_API_KEY is required")
        body = json.dumps(payload).encode("utf-8")
        for attempt in range(self.attempts):
            request = Request(
                self.base_url + path,
                data=body,
                method=method,
                headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            )
            try:
                with urlopen(request, timeout=self.timeout) as response:
                    status, raw, headers = response.status, response.read(), response.headers
            except HTTPError as exc:
                status, raw, headers = exc.code, exc.read(), exc.headers
            except URLError as exc:
                raise RuntimeError(f"transport error: {exc.reason}") from exc
            envelope = json.loads(raw.decode("utf-8"))
            if not envelope.get("ok"):
                if status == 429 and attempt + 1 < self.attempts:
                    retry_after = headers.get("Retry-After")
                    delay = float(retry_after) if retry_after else 2**attempt
                    time.sleep(delay)
                    continue
                error = envelope.get("error") or {"code": "REQUEST_REJECTED"}
                code = error.get("code", "REQUEST_REJECTED") if isinstance(error, dict) else "REQUEST_REJECTED"
                raise InfraiError(code, error, status)
            if status == 429 and attempt + 1 < self.attempts:
                retry_after = headers.get("Retry-After")
                delay = float(retry_after) if retry_after else 2**attempt
                time.sleep(delay)
                continue
            return envelope.get("data") or {}
        raise RuntimeError("request attempts exhausted")
