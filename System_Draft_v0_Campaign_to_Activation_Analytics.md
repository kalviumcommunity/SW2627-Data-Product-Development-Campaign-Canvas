# System Draft v0 – Campaign-to-Activation Analytics Platform

---

# 1. Problem Framing

The Campaign-to-Activation Analytics Platform helps Growth Marketing teams understand which marketing campaigns generate users who successfully activate within the product rather than only measuring clicks or signups. It integrates campaign data from Google Ads and Meta Ads with customer information from HubSpot and product activity stored in PostgreSQL to generate downstream activation metrics through interactive dashboards.

The system **does not** create or manage marketing campaigns, process advertising payments, or modify user behavior inside the product.

Success is measured by:

- Improved visibility into downstream activation.
- Reduced spending on low-performing campaigns.
- Dashboard response time below **3 seconds**.

Compared to the original system promise, the project evolved from simple campaign reporting to measuring the complete customer journey from acquisition to activation because stakeholder discussions identified activation—not traffic—as the real business KPI.

---

# 2. Workflow Model (IPO)

| Stage | Description |
|--------|-------------|
| **Input** | Marketing campaign data (Google Ads, Meta Ads), CRM signups (HubSpot), and product usage events (PostgreSQL). |
| **Process** | Validate incoming data → Standardize campaign identifiers → Join marketing and product datasets → Calculate activation metrics → Store processed analytics → Generate dashboard response. |
| **Output** | Dashboard displaying Campaign Name, Total Signups, Activated Users, Activation Rate, Cost per Activation, and ROI. |

## Critical Failure Point

If campaign identifiers (UTM parameters) are missing or inconsistent between HubSpot and product data, the system cannot correctly attribute users to campaigns.

Instead of generating incorrect analytics, the API returns an attribution error and excludes incomplete records from activation calculations.

---

# 3. API Contract

## Endpoint

```http
POST /api/v1/campaigns/activation
```

## Contract Style

### Selected: REST

REST was selected because the system exposes resource-oriented HTTP endpoints that integrate naturally with web dashboards and external marketing platforms.

### Rejected GraphQL

GraphQL was rejected because the dashboard requires predefined aggregated reports rather than flexible client-driven queries. Introducing GraphQL would increase complexity without providing meaningful benefits.

### Rejected gRPC

gRPC was rejected because communication mainly occurs with HTTP-based systems such as Google Ads, HubSpot, and dashboard clients. The performance improvements do not justify additional Protocol Buffer tooling.

---

## Request Shape

### Required Fields

```json
{
  "campaign_id": "cmp_101",
  "start_date": "2026-07-01",
  "end_date": "2026-07-31"
}
```

### Justification

| Field | Reason |
|--------|--------|
| campaign_id | Identifies the campaign to analyze |
| start_date | Beginning of reporting period |
| end_date | End of reporting period |

---

### Optional Fields

```json
{
  "channel": "Google Ads",
  "group_by": "week"
}
```

### Default Values

| Field | Default |
|--------|----------|
| channel | all |
| group_by | day |

---

## Response Shape

```json
{
  "campaign_id": "cmp_101",
  "campaign_name": "Summer Launch",
  "total_signups": 520,
  "activated_users": 348,
  "activation_rate": 66.9,
  "cost_per_activation": 14.50,
  "roi": 3.4
}
```

---

## Failure Codes

### 400 Bad Request

**Condition**

Missing required request field.

```json
{
  "error": "missing_required_field",
  "message": "campaign_id is required"
}
```

---

### 404 Not Found

**Condition**

Campaign does not exist.

```json
{
  "error": "campaign_not_found",
  "message": "Campaign does not exist"
}
```

---

### 422 Unprocessable Entity

**Condition**

Invalid reporting date range.

```json
{
  "error": "invalid_date_range",
  "message": "End date must be after start date"
}
```

---

## Versioning

The API uses URL versioning (`/api/v1/`).

A new version will be introduced only when:

- Required request fields change.
- Existing response fields are removed.
- Backward compatibility cannot be maintained.

---

# 4. Reliability Notes

## Error Handling

The API returns explicit HTTP status codes (400, 404, and 422) instead of generic server errors, making debugging easier for clients.

---

## Retry Safety

The endpoint performs read-only analytics. Repeated requests with the same parameters safely return the same results without modifying data.

---

## Duplicate Request Handling

Duplicate requests return identical analytics results and do not create duplicate records because no write operation occurs.

---

## Rate Limiting

Rate limiting has intentionally been left open during the prototype stage because only internal dashboard users consume the API.

Production deployment will introduce request throttling to prevent abuse.

---

## Versioning

URL versioning (`/v1/`) preserves backward compatibility while allowing future breaking changes.

---

## Remaining Reliability Gap

The system assumes synchronization between HubSpot and PostgreSQL is complete.

If synchronization is delayed, dashboard metrics may temporarily display incomplete activation results.

This limitation is acceptable during the prototype phase but should be resolved before production deployment.

---

# 5. Open Questions

## Rejected Alternative

GraphQL was considered because dashboards often require different datasets.

It was rejected because predefined analytics reports satisfy the current business requirements, making REST simpler to implement and easier to integrate with existing marketing platforms.

---

## Remaining Production Risk

Incorrect or missing UTM campaign identifiers may reduce attribution accuracy and produce incomplete campaign performance metrics.

---

## Unresolved Design Question

Should activation metrics be calculated:

- in real time whenever new product events arrive, or
- using scheduled batch processing every few hours?

The answer will influence infrastructure cost, caching strategy, and dashboard latency.

---

# 6. Repository Trace

## Design Decision

Validation of required request parameters.

---

## File

```text
backend/app/api/routes/campaigns.py
```

---

## Entry Point

```http
POST /api/v1/campaigns/activation
```

---

## Processing Flow

```
Request
    ↓
Validate campaign_id
    ↓
Validate start_date & end_date
    ↓
Fetch campaign analytics
    ↓
Calculate activation metrics
    ↓
Return dashboard response
```

---

## Status Code Handling

| Status Code | Condition |
|--------------|-----------|
| 200 OK | Successful analytics generation |
| 400 Bad Request | Missing or invalid request fields |
| 404 Not Found | Campaign ID does not exist |

---

## Delta (Design vs Implementation)

**API Contract**

The design specifies that invalid date ranges should return:

```
422 Unprocessable Entity
```

**Current Implementation**

The implementation currently returns:

```
400 Bad Request
```

for all validation errors, including invalid date ranges.

### Delta

The API contract and implementation are inconsistent.

To maintain consistency, either:

- update the implementation to return **422 Unprocessable Entity** for invalid date ranges, or
- revise the API contract to document **400 Bad Request** as the intended behavior.

This difference is documented as the **repository trace delta**.