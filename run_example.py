"""Run smart crops for a small set of channel formats."""
from __future__ import annotations

import json
import os

from src.infrai_client import InfraiClient
from src.smart_crop_service import CropRequest, crop_for_channels


def main() -> None:
    image = os.environ.get("IMAGE_ID")
    if not image:
        raise RuntimeError("IMAGE_ID is required")
    request = CropRequest(image=image, aspects=("1:1", "16:9", "4:5"))
    result = crop_for_channels(InfraiClient(), request)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
