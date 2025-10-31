# Grafana Dashboard Setup for Health Endpoint Metrics

## Overview
This guide explains how to view the health endpoint metrics in Grafana after setting up the OpenTelemetry Collector.

## Prerequisites
1. All services running via `docker-compose up`
2. Grafana accessible at http://localhost:3000 (admin/admin)

## Setup Steps

### 1. Add Prometheus as Data Source in Grafana

1. Log into Grafana at http://localhost:3000
2. Go to **Configuration** → **Data Sources**
3. Click **Add data source**
4. Select **Prometheus**
5. Set the URL to: `http://prometheus:9090` (from within Docker network)
   - Or `http://localhost:9090` if accessing from host machine
6. Click **Save & Test**

### 2. Import Dashboard or Create Custom Queries

#### Option A: Create Custom Dashboard

1. Go to **Dashboards** → **New Dashboard**
2. Add a new panel
3. Use the following PromQL queries:

**Total Health Endpoint Calls:**
```promql
health_endpoint_calls_total
```

**Health Endpoint Calls Rate (per second):**
```promql
rate(health_endpoint_calls_total[5m])
```

**Health Endpoint Calls with Labels:**
```promql
rate(health_endpoint_calls_total{endpoint="/health"}[1m])
```

#### Option B: Query Available Metrics

OpenTelemetry Collector exports metrics with specific naming conventions. To see all available metrics:

1. Go to Prometheus UI: http://localhost:9090
2. Click **Graph** tab
3. Type `health_endpoint` and see autocomplete suggestions
4. The metric might be named:
   - `health_endpoint_calls` (as defined)
   - `health_endpoint_calls_total` (Prometheus convention)
   - Or prefixed with service name like `fastapi_app_health_endpoint_calls`

### 3. Verify Metrics are Flowing

1. Make several requests to the health endpoint:
   ```bash
   curl http://localhost:8000/health
   ```

2. Check Prometheus:
   - Go to http://localhost:9090
   - Query: `health_endpoint_calls` or `health_endpoint_calls_total`
   - You should see the metric with increasing values

3. Check OpenTelemetry Collector logs:
   ```bash
   docker logs otel-collector
   ```
   You should see metrics being exported

### 4. Create Visualization Panels

Suggested panel configurations:

**Panel 1: Total Calls Counter**
- Type: Stat
- Query: `health_endpoint_calls_total`
- Visualization: Shows total number of calls

**Panel 2: Calls Rate**
- Type: Time Series
- Query: `rate(health_endpoint_calls_total[5m])`
- Visualization: Line chart showing calls per second

**Panel 3: Calls by Status (if using labels)**
- Type: Time Series
- Query: `rate(health_endpoint_calls_total{status="healthy"}[1m])`
- Visualization: Multiple series for different status values

## Troubleshooting

### Metrics Not Appearing in Grafana

1. **Check if metrics are reaching the collector:**
   ```bash
   docker logs otel-collector | grep -i metric
   ```

2. **Verify Prometheus is scraping the collector:**
   - Go to Prometheus: http://localhost:9090/targets
   - Check that `otel-collector` target is UP

3. **Check metric name format:**
   - OpenTelemetry metrics may be transformed by the collector
   - Check Prometheus metrics endpoint: http://localhost:9090/api/v1/label/__name__/values
   - Look for metrics starting with `health_endpoint`

4. **Verify FastAPI app is exporting metrics:**
   - Check API container logs for metric export errors
   - Ensure `OTEL_EXPORTER_OTLP_ENDPOINT` environment variable is set correctly

### Metric Name Variations

Depending on how OpenTelemetry transforms metrics, you might need to use:
- `health_endpoint_calls`
- `health_endpoint_calls_total`
- `fastapi_app_health_endpoint_calls`
- `otel_health_endpoint_calls`

Use Prometheus autocomplete to find the exact metric name.

## Example PromQL Queries

```promql
# Total calls
sum(health_endpoint_calls_total)

# Calls per second (rate)
rate(health_endpoint_calls_total[5m])

# Calls per minute
rate(health_endpoint_calls_total[1m]) * 60

# Calls in the last hour
increase(health_endpoint_calls_total[1h])

# Calls with specific labels
health_endpoint_calls_total{endpoint="/health", status="healthy"}
```

