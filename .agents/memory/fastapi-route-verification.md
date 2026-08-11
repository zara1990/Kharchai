---
name: FastAPI route verification
description: Route inspection behavior in the current FastAPI runtime.
---

In the current FastAPI runtime, `include_router()` stores included routers as
internal lazy entries rather than flattening every operation into concrete
`APIRoute` objects in `app.routes`.

**Why:** A direct `app.routes` scan can falsely report that included endpoints
are missing even when OpenAPI and live requests expose them correctly.

**How to apply:** Verify public route registration through `app.openapi()` or an
actual ASGI/HTTP request. Do not change router inclusion code solely because a
concrete-`APIRoute` scan misses lazily included routes.