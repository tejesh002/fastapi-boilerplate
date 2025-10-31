"""
FastAPI Boilerplate
Main application file with health and status routes
"""
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from datetime import datetime
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry import trace, metrics
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader, ConsoleMetricExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter

import os
from urllib.parse import urlparse

app = FastAPI(
    title="FastAPI Boilerplate",
    description="A production-ready FastAPI boilerplate",
    version="1.0.0"
)


# Configure OpenTelemetry
resource = Resource.create({"service.name": "fastapi-app"})

# Configure Traces
trace_provider = TracerProvider(resource=resource)

# Export spans to console and OTLP collector
processor = BatchSpanProcessor(ConsoleSpanExporter()) # For local debugging
otlp_endpoint_env = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "localhost:4317")
# Extract host:port from URL if it's a full URL
if otlp_endpoint_env.startswith("http://") or otlp_endpoint_env.startswith("https://"):
    parsed = urlparse(otlp_endpoint_env)
    otlp_endpoint = f"{parsed.hostname}:{parsed.port}" if parsed.port else parsed.hostname
else:
    otlp_endpoint = otlp_endpoint_env
otlp_exporter = OTLPSpanExporter(endpoint=otlp_endpoint, insecure=True)
otlp_processor = BatchSpanProcessor(otlp_exporter)

trace_provider.add_span_processor(processor)
trace_provider.add_span_processor(otlp_processor)
trace.set_tracer_provider(trace_provider)

# Configure Metrics
# Create OTLP metrics exporter
otlp_metrics_exporter = OTLPMetricExporter(endpoint=otlp_endpoint, insecure=True)
console_metrics_exporter = ConsoleMetricExporter()

# Create metric reader that exports to OTLP
metric_reader = PeriodicExportingMetricReader(
    export_interval_millis=5000,  # Export every 5 seconds
    exporter=otlp_metrics_exporter
)

# Create meter provider
metrics_provider = MeterProvider(
    resource=resource,
    metric_readers=[metric_reader]
)
metrics.set_meter_provider(metrics_provider)

# Get meter and create health endpoint counter
meter = metrics.get_meter(__name__)
health_endpoint_counter = meter.create_counter(
    name="health_endpoint_calls",
    description="Number of times the health endpoint has been called",
    unit="1"
)

FastAPIInstrumentor.instrument_app(app)


@app.get("/")
async def root():
    """Root endpoint"""
    return JSONResponse(content={
        "message": "Welcome to FastAPI Boilerplate",
        "docs": "/docs",
        "health": "/health",
        "status": "/status"
    })


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    # Increment the health endpoint counter metric
    health_endpoint_counter.add(1, {"endpoint": "/health", "status": "healthy"})
    
    return JSONResponse(content={
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    })


@app.get("/status")
async def status_check():
    """Detailed status endpoint"""
    return JSONResponse(content={
        "status": "operational",
        "application": "FastAPI Boilerplate",
        "version": "1.0.0",
        "environment": os.getenv("ENVIRONMENT", "development"),
        "timestamp": datetime.utcnow().isoformat()
    })


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

