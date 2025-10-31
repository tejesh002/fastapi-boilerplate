"""
OpenTelemetry configuration for FastAPI application
Handles traces, metrics, and instrumentation setup
"""
import os
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry import trace, metrics
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader, ConsoleMetricExporter
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter


def setup_telemetry(app, service_name: str = "fastapi-app", enable_console: bool = True):
    """
    Configure OpenTelemetry for the FastAPI application.

    Args:
        app: FastAPI application instance
        service_name: Name of the service for telemetry
        enable_console: Whether to enable console exporters for debugging

    Returns:
        tuple: (meter, health_endpoint_counter) - Meter instance and health counter metric
    """
    # Configure OpenTelemetry Resource
    resource = Resource.create({"service.name": service_name})

    # Configure Traces
    trace_provider = TracerProvider(resource=resource)

    # Determine OTLP endpoints based on environment
    environment = os.getenv("ENVIRONMENT", "local").lower()

    if environment == "local":
        # Use docker endpoints for local development
        otlp_traces_endpoint = "http://otel-collector:4318/v1/traces"
        otlp_metrics_endpoint = "http://otel-collector:4318/v1/metrics"
    else:
        # Use environment variables for other environments
        otlp_base_url = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://otel-collector:4318")

        otlp_traces_endpoint = os.getenv("OTEL_TRACES_ENDPOINT", f"{otlp_base_url}/v1/traces")
        otlp_metrics_endpoint = os.getenv("OTEL_METRICS_ENDPOINT", f"{otlp_base_url}/v1/metrics")

    # Export spans to console (for local debugging) and OTLP collector
    if enable_console:
        console_processor = BatchSpanProcessor(ConsoleSpanExporter())
        trace_provider.add_span_processor(console_processor)

    # OTLP exporter for traces
    otlp_traces_exporter = OTLPSpanExporter(endpoint=otlp_traces_endpoint)
    otlp_traces_processor = BatchSpanProcessor(otlp_traces_exporter)
    trace_provider.add_span_processor(otlp_traces_processor)

    trace.set_tracer_provider(trace_provider)

    # Configure Metrics
    # Create OTLP metrics exporter
    otlp_metrics_exporter = OTLPMetricExporter(endpoint=otlp_metrics_endpoint)

    # Get export interval from environment or use default (5 seconds)
    export_interval = int(os.getenv("OTEL_METRIC_EXPORT_INTERVAL", "5000"))

    # Create metric reader that exports to OTLP
    metric_reader = PeriodicExportingMetricReader(
        export_interval_millis=export_interval, exporter=otlp_metrics_exporter
    )

    # Create meter provider
    metrics_provider = MeterProvider(resource=resource, metric_readers=[metric_reader])
    metrics.set_meter_provider(metrics_provider)

    # Get meter and create health endpoint counter
    meter = metrics.get_meter(__name__)
    health_endpoint_counter = meter.create_counter(
        name="health_endpoint_calls",
        description="Number of times the health endpoint has been called",
        unit="1",
    )

    # Instrument FastAPI application
    FastAPIInstrumentor.instrument_app(app)

    return meter, health_endpoint_counter
