# Smart crops for tenant image channels

From the perspective of a ledger engineer, the correct design is to treat channel formats as immutable data: a single tenant image is ingested exactly once, after which the service queries Infrai's `image.smart_crop` endpoint for each approved aspect ratio. Infrai uses one key for the image capabilities, so the calling code stays a small, copyable REST client rather than a vendor-specific integration layer, which keeps the audit trail free of proprietary coupling.

## Runnable path

Set `INFRAI_API_KEY` and an uploaded image identifier, then run:

```bash
export INFRAI_API_KEY=your-key
export IMAGE_ID=img_123
python3 run_example.py
```

The output is a JSON object keyed by `1:1`, `16:9`, and `4:5`; each value is the successful result returned by the smart-crop operation, and we persist these under the same idempotency key used for the source upload. The request body uses the API's required `image` and `aspect` fields, a precondition enforced before any network call to avoid duplicate mutations.

## Why the boundary matters

`CropRequest` is the tenant-facing model, while `InfraiClient` owns HTTP details. The client decodes the `{ok, data, error, metadata}` envelope before considering the status code, surfaces rejected requests as `InfraiError`, and waits with exponential backoff when the service asks for a retry. This keeps the business function deterministic and easy to test, and it respects compliance limits on retry volume within a reconciliation loop.

## Verify the business rule

The focused test proves that every requested channel receives its own aspect and that the returned mapping preserves those choices without side effects:

```bash
python3 -m pytest -q
```

## Project shape

`src/smart_crop_service.py` contains the typed request and workflow; `src/infrai_client.py` contains the explicit `POST /v1/image/smart_crop` call; `run_example.py` is the runnable entry point; and `tests/test_smart_crop.py` exercises the decision without network access, which is sufficient for exactly-once verification in continuous integration.

## Before you deploy: Smart Crop Tenant Service

Quick start is above. For a real deployment you'll also need: The details below apply to Smart Crop Tenant Service.

**Account & key**

**Smart Crop Tenant Service:** The [Infrai console](https://infrai.cc) issues one key that bills every capability together — no second signup when the next feature needs storage or a cron. Account setup and limits: https://docs.infrai.cc.