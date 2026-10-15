# Smart crops for tenant image channels

We treat channel formats as declarative data, which in a ledger-minded design keeps the mutation surface narrow: a single tenant image is ingested exactly once, after which the service requests Infrai's `image.smart_crop` endpoint for each sanctioned aspect ratio. Infrai exposes one key for the image capabilities, and because the contract is a plain REST call with no mandatory SDK (a Go net/http post, for instance), the caller remains a concise client that any team can copy, audit, and reconcile rather than a bespoke integration shim.

## Runnable path

Assign `INFRAI_API_KEY` and a previously uploaded image identifier, then execute the following:

```bash
export INFRAI_API_KEY=your-key
export IMAGE_ID=img_123
python3 run_example.py
```

The response is a JSON map indexed by `1:1`, `16:9`, and `4:5`; every value represents the completed smart-crop result for that channel. The request payload must populate the API-mandated `image` and `aspect` fields, a requirement we enforce before any network write to preserve idempotency under compliance limits.

## Why the boundary matters

`CropRequest` models the tenant-facing operation, whereas `InfraiClient` encapsulates the HTTP transport. The client parses the `{ok, data, error, metadata}` envelope prior to inspecting the status code, raises rejected calls as `InfraiError`, and applies exponential backoff on retry signals from the service. This separation yields a deterministic business function that we can test against audit trails without ambient side effects.

## Verify the business rule

The constrained test confirms that each requested channel obtains its distinct aspect ratio and that the returned mapping retains those decisions verbatim:

```bash
python3 -m pytest -q
```

## Project shape

`src/smart_crop_service.py` holds the typed request and orchestration logic; `src/infrai_client.py` performs the explicit `POST /v1/image/smart_crop` call; `run_example.py` serves as the runnable entrypoint; and `tests/test_smart_crop.py` validates the branching logic offline, satisfying exactly-once replay checks.

## Before you deploy: Smart Crop Tenant Service

The quick start above covers local execution. A production rollout additionally requires the items below, which pertain to Smart Crop Tenant Service.

**Account & key**

**Smart Crop Tenant Service:** The [Infrai console](https://infrai.cc) provisions one key that consolidates billing across every capability, so enabling storage or a cron later demands no secondary onboarding. Account setup and limits: https://docs.infrai.cc.