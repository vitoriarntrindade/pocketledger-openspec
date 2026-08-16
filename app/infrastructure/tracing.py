from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
    OTLPSpanExporter,
)
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from app.core.config import settings
from app.infrastructure.database import engine


def configure_tracing(app: FastAPI) -> None:
    if not settings.otel_enabled:
        return

    resource = Resource.create({SERVICE_NAME: settings.service_name})
    provider = TracerProvider(resource=resource)
    exporter = OTLPSpanExporter(
        endpoint=settings.otel_exporter_otlp_endpoint, insecure=True
    )
    provider.add_span_processor(BatchSpanProcessor(exporter))
    trace.set_tracer_provider(provider)

    FastAPIInstrumentor.instrument_app(app)
    SQLAlchemyInstrumentor().instrument(engine=engine)
