# Functional Architecture: Observability Stack Guide

This document explains the complete observability setup, data flow, and practical usage of Jaeger, Prometheus, Loki, and Grafana in this FastAPI application.

## 📊 Architecture Overview

This boilerplate implements a complete observability stack using the OpenTelemetry (OTel) standard:

```
┌─────────────────┐
│   FastAPI App   │
│  (Port 8000)    │
└────────┬────────┘
         │
         │ OTLP (Traces, Metrics, Logs)
         │
┌────────▼─────────────────┐
│  OTel Collector          │
│  (Port 4317/4318/8889)   │
└────────┬─────────────────┘
         │
    ┌────┴────┬──────────────┬────────────┐
    │         │              │            │
┌───▼───┐ ┌──▼──────┐  ┌────▼────┐  ┌────▼────┐
│Jaeger │ │Prometheus│ │  Loki  │  │ Grafana │
│:16686 │ │  :9090   │ │ :3100  │  │  :3000  │
└───────┘ └──────────┘ └─────────┘  └─────────┘
```

## 🔄 Complete Data Flow

### 1. Trace Data Flow (Distributed Tracing)

```
FastAPI Request
    │
    ├─→ FastAPIInstrumentor captures HTTP request
    │   - Creates trace spans for each endpoint
    │   - Records timing, HTTP method, status codes
    │
    ├─→ OTLPSpanExporter sends traces
    │   - Endpoint: otel-collector:4317 (gRPC)
    │
    ├─→ OpenTelemetry Collector
    │   - Receives via OTLP receiver (port 4317)
    │   - Processes through batch processor
    │   - Routes to exporters
    │
    ├─→ Debug Exporter (logs to stdout)
    │   - For debugging and development
    │
    └─→ Jaeger Exporter (OTLP)
        - Endpoint: jaeger:4317
        - Stores traces for visualization
        - UI accessible at http://localhost:16686
```

**What You Can Track:**
- Request latency (time taken for each endpoint)
- Request/response headers and status codes
- Service dependencies and call chains
- Error traces and stack traces
- Custom spans for business logic

### 2. Metrics Data Flow

```
FastAPI Application
    │
    ├─→ Custom Metrics (health_endpoint_calls)
    │   - Counters, gauges, histograms
    │   - Exported via OTLPMetricExporter
    │
    ├─→ Automatic Metrics
    │   - HTTP request duration
    │   - Request count
    │   - Active requests
    │
    ├─→ OpenTelemetry Collector
    │   - Receives metrics via OTLP
    │   - Exposes Prometheus metrics at :8889
    │
    ├─→ Prometheus
    │   - Scrapes metrics from otel-collector:8889
    │   - Stores time-series data
    │   - Queryable via PromQL
    │
    └─→ Grafana
        - Connects to Prometheus as data source
        - Visualizes metrics in dashboards
        - Creates alerts based on thresholds
```

**What You Can Track:**
- Request rate (requests per second)
- Response times (p50, p95, p99 percentiles)
- Error rates
- Custom business metrics
- System resource usage

### 3. Log Data Flow

```
FastAPI Application
    │
    ├─→ Application Logs
    │   - Python logging statements
    │   - FastAPI request logs
    │
    ├─→ OpenTelemetry Collector
    │   - Receives logs via OTLP
    │   - Processes and batches logs
    │
    └─→ Loki
        - Stores logs (similar to Prometheus for metrics)
        - Indexes by labels
        - Queryable via LogQL
        - Visualized in Grafana
```

**What You Can Track:**
- Application errors and exceptions
- Request/response logs
- Business event logs
- Correlate logs with traces via trace IDs

---

## 🛠️ Tool-by-Tool Usage Guide

### 1. 🔍 Jaeger - Distributed Tracing

**Purpose:** View and analyze distributed traces to understand request flow and performance bottlenecks.

**Access:** http://localhost:16686

**Key Features:**
- Trace visualization with timeline
- Service dependency graphs
- Trace search and filtering
- Performance analysis

#### Example Use Cases:

**A. Finding Slow Endpoints**
1. Open Jaeger UI: http://localhost:16686
2. Select service: `fastapi-app`
3. Click "Find Traces"
4. Sort by duration to see slowest requests
5. Click on a trace to see detailed span breakdown

**B. Debugging Failed Requests**
1. Filter by operation: `/health` or `/status`
2. Filter by tags: `error=true`
3. View trace details to see where failure occurred
4. Check span logs for error messages

**C. Understanding Request Flow**
1. Click on any trace
2. View the timeline to see:
   - Total request duration
   - Time spent in each function/span
   - Database query times (if added)
   - External API call times (if added)

**D. Service Dependency Analysis**
1. Navigate to "Dependencies" tab
2. See visual graph of service interactions
3. Understand system architecture at runtime

#### Practical Example:

```bash
# Make some requests to generate traces
curl http://localhost:8000/health
curl http://localhost:8000/status
curl http://localhost:8000/

# Then:
# 1. Open http://localhost:16686
# 2. Select service: "fastapi-app"
# 3. Time range: Last 15 minutes
# 4. Click "Find Traces"
# 5. You'll see 3 traces, one for each endpoint
```

**What You'll See in Jaeger:**
- Service name: `fastapi-app`
- Operation: `GET /health`, `GET /status`, `GET /`
- Duration: Request processing time
- Tags: HTTP method, status code, URL path
- Logs: Request/response details

---

### 2. 📈 Prometheus - Metrics Storage & Querying

**Purpose:** Store time-series metrics and query them using PromQL.

**Access:** http://localhost:9090

**Key Features:**
- Time-series database
- Powerful query language (PromQL)
- Alerting rules
- Data source for Grafana

#### Example Use Cases:

**A. Query Custom Metrics**
```promql
# Total health endpoint calls
health_endpoint_calls_total

# Health endpoint call rate (per second)
rate(health_endpoint_calls_total[5m])

# Health endpoint calls in last hour
increase(health_endpoint_calls_total[1h])
```

**B. Query HTTP Metrics (Auto-instrumented)**
```promql
# Request rate per endpoint
rate(http_server_request_duration_seconds_count[5m])

# Average response time
rate(http_server_request_duration_seconds_sum[5m]) / 
rate(http_server_request_duration_seconds_count[5m])

# 95th percentile latency
histogram_quantile(0.95, 
  rate(http_server_request_duration_seconds_bucket[5m])
)
```

**C. Error Rate Monitoring**
```promql
# Error rate (status code >= 500)
rate(http_server_request_duration_seconds_count{status_code=~"5.."}[5m])

# Success rate
rate(http_server_request_duration_seconds_count{status_code=~"2.."}[5m])
```

#### Practical Example:

```bash
# Generate some load
for i in {1..10}; do
  curl http://localhost:8000/health
  sleep 1
done

# Then in Prometheus UI:
# 1. Go to http://localhost:9090
# 2. Click "Graph" tab
# 3. Type: rate(health_endpoint_calls_total[1m])
# 4. Click "Execute"
# 5. See the graph showing calls per second
```

**Available Metrics:**
- `health_endpoint_calls_total` - Your custom counter
- `http_server_request_duration_seconds` - Request duration histogram
- `http_server_request_duration_seconds_count` - Total request count
- `http_server_request_duration_seconds_sum` - Sum of all durations

---

### 3. 📝 Loki - Log Aggregation

**Purpose:** Store and query logs efficiently, similar to Prometheus but for logs.

**Access:** Via Grafana (http://localhost:3000) or direct API (http://localhost:3100)

**Key Features:**
- Label-based indexing (like Prometheus)
- LogQL query language
- Efficient storage
- Integrated with Grafana

#### Example Use Cases:

**A. Finding Error Logs**
```logql
{job="fastapi-app"} |= "error"
{job="fastapi-app"} | json | level="ERROR"
```

**B. Searching by Trace ID**
```logql
{job="fastapi-app"} |= "trace_id_here"
```

**C. Filtering by Time Range**
```logql
{job="fastapi-app"} [5m] | line_format "{{.message}}"
```

#### Practical Example:

```python
# Add logging to your FastAPI app
import logging

logger = logging.getLogger(__name__)

@app.get("/health")
async def health_check():
    logger.info("Health check requested")
    health_endpoint_counter.add(1, {"endpoint": "/health", "status": "healthy"})
    return JSONResponse(content={
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    })
```

**Note:** Loki is configured but logs need to be sent via OTLP. Currently, the collector is configured to receive logs but the FastAPI app only sends traces and metrics.

---

### 4. 📊 Grafana - Unified Visualization

**Purpose:** Single dashboard to visualize traces, metrics, and logs together.

**Access:** http://localhost:3000 (admin/admin)

**Key Features:**
- Unified observability dashboard
- Alerting rules
- Multiple data source support
- Beautiful visualizations

#### Example Use Cases:

**A. Creating a Request Rate Dashboard**
1. Go to Dashboards → New Dashboard
2. Add Panel → Time Series
3. Data Source: Prometheus
4. Query: `rate(http_server_request_duration_seconds_count[1m])`
5. Panel Title: "Request Rate"

**B. Creating a Latency Dashboard**
1. Add Panel → Time Series
2. Query: `histogram_quantile(0.95, rate(http_server_request_duration_seconds_bucket[5m]))`
3. Panel Title: "95th Percentile Latency"

**C. Creating a Health Endpoint Dashboard**
1. Add Panel → Stat
2. Query: `health_endpoint_calls_total`
3. Panel Title: "Total Health Checks"
4. Add another panel:
   - Query: `rate(health_endpoint_calls_total[5m])`
   - Panel Title: "Health Checks per Second"

**D. Correlating Logs with Traces**
1. Add Panel → Logs
2. Data Source: Loki
3. Query: `{job="fastapi-app"}`
4. Use trace ID from Jaeger to filter logs

#### Practical Example:

**Step 1: Add Prometheus Data Source**
1. Configuration → Data Sources → Add data source
2. Select Prometheus
3. URL: `http://prometheus:9090`
4. Save & Test

**Step 2: Create Dashboard**
1. Dashboards → New Dashboard → Add Visualization
2. Query: `rate(health_endpoint_calls_total[1m])`
3. Visualization: Time Series
4. Save dashboard

**Step 3: Add Multiple Panels**
- Request Rate Panel
- Error Rate Panel
- Response Time Panel
- Health Check Counter Panel

---

## 🎯 Real-World Scenarios

### Scenario 1: Debugging Slow API Endpoints

**Problem:** `/status` endpoint is taking too long

**Solution:**
1. **Jaeger**: 
   - Open http://localhost:16686
   - Filter by operation: `GET /status`
   - Sort by duration
   - Identify which span takes longest time

2. **Prometheus**:
   - Query: `histogram_quantile(0.95, rate(http_server_request_duration_seconds_bucket{http_target="/status"}[5m]))`
   - Compare with other endpoints

3. **Grafana**:
   - Create dashboard comparing all endpoint latencies
   - Set up alert if p95 latency > 500ms

### Scenario 2: Monitoring API Health

**Problem:** Want to ensure API is healthy and track health check frequency

**Solution:**
1. **Prometheus Alert**:
   ```yaml
   - alert: HealthCheckStopped
     expr: rate(health_endpoint_calls_total[5m]) == 0
     for: 5m
     annotations:
       summary: "Health checks have stopped"
   ```

2. **Grafana Dashboard**:
   - Panel 1: Health check count over time
   - Panel 2: Health check rate (should be constant if monitored)
   - Panel 3: Last health check timestamp

### Scenario 3: Understanding Traffic Patterns

**Problem:** Need to understand when API is most used

**Solution:**
1. **Grafana Dashboard**:
   - Panel: Request rate by hour of day
   - Query: `sum(rate(http_server_request_duration_seconds_count[1h])) by (hour)`
   
2. **Prometheus**:
   - Query peak hours: `topk(3, rate(http_server_request_duration_seconds_count[1h]))`

### Scenario 4: Error Tracking

**Problem:** Want to track and alert on errors

**Solution:**
1. **Jaeger**:
   - Filter traces with `error=true` tag
   - See full error context and stack traces

2. **Prometheus Alert**:
   ```yaml
   - alert: HighErrorRate
     expr: rate(http_server_request_duration_seconds_count{status_code=~"5.."}[5m]) > 0.1
     for: 2m
     annotations:
       summary: "Error rate is {{ $value }} errors/second"
   ```

3. **Grafana**:
   - Error rate panel with threshold line
   - Alert when error rate crosses threshold

---

## 🚀 Quick Start Examples

### Example 1: View All Traces

```bash
# 1. Start services
docker-compose up -d

# 2. Generate some requests
curl http://localhost:8000/health
curl http://localhost:8000/status
curl http://localhost:8000/

# 3. View in Jaeger
# Open http://localhost:16686
# Select service: fastapi-app
# Click "Find Traces"
```

### Example 2: Query Metrics

```bash
# 1. Generate load
for i in {1..20}; do
  curl http://localhost:8000/health
  sleep 0.5
done

# 2. Query in Prometheus
# Open http://localhost:9090
# Type: rate(health_endpoint_calls_total[1m])
# See the graph showing ~2 requests/second
```

### Example 3: Create Grafana Dashboard

```bash
# 1. Access Grafana
# Open http://localhost:3000
# Login: admin/admin

# 2. Add Prometheus data source
# Configuration → Data Sources → Prometheus
# URL: http://prometheus:9090

# 3. Create dashboard
# Dashboards → New Dashboard
# Add visualization with query: health_endpoint_calls_total
```

### Example 4: Correlate Trace with Logs

```bash
# 1. Get trace ID from Jaeger
# Open http://localhost:16686
# Click on any trace
# Copy the Trace ID

# 2. Search logs by trace ID in Grafana
# Open Grafana → Explore
# Select Loki data source
# Query: {job="fastapi-app"} |= "trace_id_here"
```

---

## 📋 Configuration Files Reference

### otel-collector-config.yaml
- **Receivers**: OTLP (gRPC and HTTP)
- **Processors**: Batch (for efficient processing)
- **Exporters**: 
  - Debug (for development)
  - OTLP/Jaeger (traces)
  - Prometheus (metrics)
- **Pipelines**: Traces, Metrics, Logs

### docker-compose.yml
- **Port Mappings**:
  - FastAPI: 8000
  - Jaeger UI: 16686
  - Prometheus: 9090
  - Grafana: 3000
  - Loki: 3100
  - OTel Collector: 4317 (gRPC), 4318 (HTTP), 8889 (Prometheus)

---

## 🔧 Troubleshooting

### No Traces in Jaeger

1. **Check collector logs:**
   ```bash
   docker-compose logs otel-collector
   ```

2. **Verify endpoint configuration:**
   - FastAPI → Collector: `OTEL_EXPORTER_OTLP_ENDPOINT=otel-collector:4317`
   - Collector → Jaeger: `endpoint: "http://jaeger:4317"` in otel-collector-config.yaml

3. **Test connectivity:**
   ```bash
   docker-compose exec api curl otel-collector:4317
   ```

### No Metrics in Prometheus

1. **Check Prometheus targets:**
   - Open http://localhost:9090/targets
   - Verify `otel-collector` target is UP

2. **Check collector metrics endpoint:**
   ```bash
   curl http://localhost:8889/metrics
   ```

3. **Verify metric names:**
   - In Prometheus, go to Graph tab
   - Start typing metric name to see autocomplete

### Grafana Not Showing Data

1. **Verify data source connection:**
   - Configuration → Data Sources
   - Test connection to Prometheus

2. **Check time range:**
   - Ensure time range in Grafana includes recent data
   - Default: Last 15 minutes

3. **Verify query syntax:**
   - Test query in Prometheus first
   - Then use same query in Grafana

---

## 📚 Additional Resources

- **OpenTelemetry Documentation**: https://opentelemetry.io/docs/
- **Jaeger Documentation**: https://www.jaegertracing.io/docs/
- **Prometheus Documentation**: https://prometheus.io/docs/
- **Grafana Documentation**: https://grafana.com/docs/
- **Loki Documentation**: https://grafana.com/docs/loki/

---

## 🎓 Learning Path

1. **Start Simple**: Make requests and view in Jaeger
2. **Add Metrics**: Query custom metrics in Prometheus
3. **Visualize**: Create dashboards in Grafana
4. **Alert**: Set up alerts for critical metrics
5. **Advanced**: Correlate traces, metrics, and logs together

---

## 💡 Best Practices

1. **Always use batch processors** - Reduces overhead
2. **Set appropriate sample rates** - For high-traffic applications
3. **Use meaningful service names** - Makes filtering easier
4. **Add custom spans** - For important business logic
5. **Set up alerts** - Don't just visualize, act on data
6. **Keep dashboards focused** - One dashboard per use case
7. **Correlate data sources** - Use trace IDs to link traces with logs

---

## 🎯 Summary

This observability stack provides:

- **Traces** (Jaeger): See request flow and identify bottlenecks
- **Metrics** (Prometheus): Track performance and business KPIs
- **Logs** (Loki): Debug issues with detailed logs
- **Dashboards** (Grafana): Unified view of all observability data

All tools work together to give you complete visibility into your FastAPI application's behavior, performance, and health.

