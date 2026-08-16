# Observability conventions

Every request can be followed through logs, metrics and traces using a single
identifier. That property is easy to break accidentally, so the conventions
below are load-bearing.

## Request correlation

`RequestIdMiddleware` assigns a `request_id` — taken from the `X-Request-ID`
header when the client supplies one, generated otherwise — stores it in a
`ContextVar`, and puts it on every response.

`RequestContextFilter` attaches it to every log record, so nothing needs to
pass it around explicitly.

That middleware also catches unhandled exceptions. This is not stylistic:
Starlette routes a FastAPI `Exception` handler to `ServerErrorMiddleware`,
which sits outside every user-added middleware, so a handler registered there
can never see this middleware's request id or attach its header. Catching in
the middleware is what keeps the error envelope and the header consistent.

## Logging

Logs are structured JSON via `JSONFormatter`. Put values in `extra`, not in the
message:

```python
# Correct: queryable fields, stable message.
access_logger.info(
    "request_handled",
    extra={"http_status_code": response.status_code, "duration_ms": ms},
)

# Wrong: the values are trapped in a string.
access_logger.info(f"handled with {response.status_code} in {ms}ms")
```

The message is an event name, not a sentence. `auth_failed` is greppable across
every request; "Authentication failed for user" is not.

**Never log credentials** — no passwords, tokens, or hashes, in the message or
in `extra`. A test asserts this for the login path; adding a new authentication
path means adding that assertion too.

Levels carry meaning here:

| Level | For |
|---|---|
| `INFO` | normal request handling |
| `WARNING` | domain errors — a rejected request is not a system failure |
| `ERROR` | unhandled exceptions only, always with `exc_info` |

Domain errors deliberately log below `ERROR`. Logging expected rejections as
errors is how alerting becomes noise that people stop reading.

## Metrics

Prometheus metrics are exposed at `/metrics` via
`prometheus-fastapi-instrumentator`, which covers HTTP metrics automatically.

Business counters live in `app/infrastructure/metrics.py`. Add one only when
someone would actually act on the number.

**Never label a metric with anything unbounded** — user id, transaction id,
email. Each distinct label value creates a new time series, and high-cardinality
labels are the standard way to bring down a metrics backend.

## Tracing

OpenTelemetry exports to an OTLP collector, with FastAPI and SQLAlchemy
instrumented automatically. `_current_trace_id()` links a log line to its trace.

`configure_tracing` returns immediately when `OTEL_ENABLED` is false.

**This matters for tests.** With export enabled and no collector listening, the
exporter retries with escalating backoff — the suite goes from about 43 seconds
to roughly four minutes and buries the result in retry warnings. The quality
gate sets `OTEL_ENABLED=false` for exactly this reason, and any test that
depends on a real tracer must establish its own provider rather than relying on
the application's global configuration.
