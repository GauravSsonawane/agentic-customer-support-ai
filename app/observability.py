from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

def setup_observability(app):
    """
    Configures OpenTelemetry tracing for the FastAPI application.
    Exports traces to Console by default (for demo purposes).
    """
    # 1. Define Resource (Service Name)
    resource = Resource(attributes={
        SERVICE_NAME: "agentic-customer-support-backend"
    })

    # 2. Set up Tracer Provider
    provider = TracerProvider(resource=resource)
    
    # 3. Add Exporter (Console for local, easy to swap for OTLP)
    processor = BatchSpanProcessor(ConsoleSpanExporter())
    provider.add_span_processor(processor)
    
    # 4. Set global provider
    trace.set_tracer_provider(provider)

    # 5. Instrument FastAPI
    FastAPIInstrumentor.instrument_app(app)
