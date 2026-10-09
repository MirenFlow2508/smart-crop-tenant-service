"""Business workflow: produce the requested image renditions."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


class Cropper(Protocol):
    def smart_crop(self, image: str, aspect: str) -> dict:
        raise NotImplementedError


@dataclass(frozen=True)
class CropRequest:
    image: str
    aspects: tuple[str, ...]


def crop_for_channels(client: Cropper, request: CropRequest) -> dict[str, dict]:
    if not request.image:
        raise ValueError("image is required")
    if not request.aspects:
        raise ValueError("at least one aspect is required")
    return {aspect: client.smart_crop(request.image, aspect) for aspect in request.aspects}
