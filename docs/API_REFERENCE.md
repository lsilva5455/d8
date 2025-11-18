# Congress System - API Quick Reference

## Base URL
```
http://localhost:5000/api/congress
```

## Endpoints Summary

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/status` | GET | System status |
| `/council/members` | GET | Council members |
| `/council/decisions` | GET | Recent decisions |
| `/council/okrs` | GET | Active OKRs |
| `/council/stats` | GET | Council statistics |
| `/discovery/candidates` | GET | Niche candidates |
| `/discovery/validated` | GET | Validated niches |
| `/discovery/stats` | GET | Discovery stats |
| `/roi/summary` | GET | ROI summary |
| `/roi/niche/{id}` | GET | Niche ROI history |
| `/roi/agent/{id}` | GET | Agent ROI history |
| `/roi/top-niches` | GET | Top niches |
| `/roi/top-agents` | GET | Top agents |

---

## Quick Examples

### Check System Status
```bash
curl http://localhost:5000/api/congress/status
```

### Get Validated Niches
```bash
curl http://localhost:5000/api/congress/discovery/validated
```

### Get ROI Summary
```bash
curl http://localhost:5000/api/congress/roi/summary
```

### Get Top Performers
```bash
# Top niches
curl "http://localhost:5000/api/congress/roi/top-niches?limit=5"

# Top agents
curl "http://localhost:5000/api/congress/roi/top-agents?limit=5"
```

### Get Council Decisions
```bash
curl "http://localhost:5000/api/congress/council/decisions?limit=10"
```

---

## Response Format

All endpoints return JSON:

**Success:**
```json
{
  "data": {...},
  "total": 10
}
```

**Error:**
```json
{
  "error": "Description of error"
}
```

---

## Query Parameters

### Common Parameters

- `limit` (integer): Max results to return (default varies)
- `status` (string): Filter by status

### Examples

```bash
# Limit results
curl "http://localhost:5000/api/congress/discovery/candidates?limit=5"

# Filter by status
curl "http://localhost:5000/api/congress/discovery/candidates?status=validated"

# Combined
curl "http://localhost:5000/api/congress/discovery/candidates?status=analyzed&limit=10"
```

---

## Authentication

**Current:** No authentication required (development mode)

**Production:** Add API key authentication:
```bash
curl -H "X-API-Key: your_key" http://localhost:5000/api/congress/status
```

---

## Rate Limiting

**Current:** No rate limits (development mode)

**Recommended for Production:**
- 100 requests/minute per IP
- 1000 requests/hour per IP

---

## Webhooks (Future)

Subscribe to events:
- New niche validated
- Decision made
- ROI threshold reached
- OKR milestone completed

---

## Testing

### Health Check
```bash
curl http://localhost:5000/
```

Should return:
```json
{
  "status": "online",
  "project": "The Hive",
  "version": "0.2.0",
  "congress_system": {
    "supreme_council_ready": true,
    "niche_discovery_ready": true,
    "roi_tracker_ready": true
  }
}
```

### Full Test Script

```bash
#!/bin/bash

BASE_URL="http://localhost:5000/api/congress"

echo "Testing Congress API..."

# Status
echo "\n1. Status:"
curl -s "$BASE_URL/status" | jq .

# Council
echo "\n2. Council Members:"
curl -s "$BASE_URL/council/members" | jq .

# Discovery
echo "\n3. Discovery Stats:"
curl -s "$BASE_URL/discovery/stats" | jq .

# ROI
echo "\n4. ROI Summary:"
curl -s "$BASE_URL/roi/summary" | jq .

echo "\nDone!"
```

---

## Integration Examples

### Python
```python
import requests

BASE_URL = "http://localhost:5000/api/congress"

# Get validated niches
response = requests.get(f"{BASE_URL}/discovery/validated")
niches = response.json()

for niche in niches["validated_niches"]:
    print(f"Niche: {niche['name']}")
    print(f"  ROI Potential: {niche['monetization_potential']}")
```

### JavaScript
```javascript
const BASE_URL = "http://localhost:5000/api/congress";

// Get ROI summary
fetch(`${BASE_URL}/roi/summary`)
  .then(res => res.json())
  .then(data => {
    console.log("System ROI:", data.system_roi.roi_percentage + "%");
  });
```

### cURL
```bash
# Save to file
curl -s http://localhost:5000/api/congress/discovery/validated \
  | jq . > validated_niches.json
```

---

## Error Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 400 | Bad request |
| 404 | Not found |
| 500 | Server error |

---

## Support

- Documentation: `/docs/CONGRESS_SYSTEM.md`
- GitHub: https://github.com/lsilva5455/d8
- Issues: https://github.com/lsilva5455/d8/issues
