import pytest

import run_example
from src.smart_crop_service import CropRequest, crop_for_channels


class FakeCropper:
    def __init__(self):
        self.calls = []

    def smart_crop(self, image: str, aspect: str) -> dict:
        self.calls.append((image, aspect))
        return {"image": image, "aspect": aspect}


def test_channels_receive_distinct_aspects():
    client = FakeCropper()
    result = crop_for_channels(client, CropRequest("img_123", ("1:1", "16:9")))
    assert list(result) == ["1:1", "16:9"]
    assert client.calls == [("img_123", "1:1"), ("img_123", "16:9")]


def test_entry_point_requires_image_id(monkeypatch):
    monkeypatch.delenv("IMAGE_ID", raising=False)
    with pytest.raises(RuntimeError, match="^IMAGE_ID is required$"):
        run_example.main()
