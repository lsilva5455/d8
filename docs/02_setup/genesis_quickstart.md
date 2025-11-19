# D8-GENESIS Quick Start Guide

This guide walks you through testing the D8-GENESIS self-coding and self-healing capabilities.

---

## Prerequisites

1. **The Hive is running:**
   ```bash
   python app/main.py
   ```

2. **Ollama + DeepSeek installed:**
   ```bash
   ollama pull deepseek-coder:33b
   ollama serve
   ```

3. **Legacy code directory exists:**
   ```bash
   mkdir legacy_code
   ```

---

## Step 1: Create Sample Legacy Code

Create a simple legacy bot script to ingest:

```bash
# legacy_code/instagram_bot.py
```

```python
from selenium import webdriver
import time

def instagram_login(username, password):
    """Login to Instagram"""
    driver = webdriver.Chrome()
    driver.get("https://instagram.com")
    time.sleep(2)
    
    # Old selectors (will break)
    username_field = driver.find_element_by_name("username")
    password_field = driver.find_element_by_name("password")
    
    username_field.send_keys(username)
    password_field.send_keys(password)
    
    login_button = driver.find_element_by_xpath("//button[@type='submit']")
    login_button.click()
    
    return driver

def like_post(driver, post_url):
    """Like a post"""
    driver.get(post_url)
    time.sleep(2)
    
    like_button = driver.find_element_by_xpath("//span[@aria-label='Like']")
    like_button.click()
    
    return True
```

---

## Step 2: Ingest Legacy Code

```bash
curl -X POST http://localhost:5000/api/genesis/ingest \
  -H "Content-Type: application/json" \
  -d '{"path": "./legacy_code", "recursive": true}'
```

**Expected response:**
```json
{
  "success": true,
  "fragments_ingested": 2,
  "stats": {
    "total_fragments": 2,
    "by_platform": {
      "instagram": 2
    },
    "by_action": {
      "login": 1,
      "like": 1
    }
  }
}
```

---

## Step 3: Generate Polymorphic Code

Request code generation for a similar task:

```bash
curl -X POST http://localhost:5000/api/genesis/generate \
  -H "Content-Type: application/json" \
  -d '{
    "task": "Create a function to login to Instagram with anti-detection measures",
    "platform": "instagram",
    "action": "login"
  }'
```

**Expected response:**
```json
{
  "code": "def authenticate_platform(account_name, secret): ...",
  "polymorphism_applied": [
    "variable_name_rotation",
    "timing_randomization",
    "control_flow_variation"
  ],
  "legacy_patterns_used": [
    "instagram_login"
  ],
  "anti_detection_features": [
    "random_delays",
    "user_agent_rotation"
  ]
}
```

The generated code will be **different each time** (polymorphic).

---

## Step 4: Test Self-Healing

Simulate a broken function and request healing:

```bash
curl -X POST http://localhost:5000/api/genesis/heal \
  -H "Content-Type: application/json" \
  -d '{
    "code": "def click(): driver.find_element_by_id(\"old_button\").click()",
    "error": "NoSuchElementException: Element with id \"old_button\" not found",
    "context": "Instagram updated their UI and button ID changed"
  }'
```

**Expected response:**
```json
{
  "healed_code": "def perform_click(): browser.find_element(By.CSS_SELECTOR, '[data-testid=\"like-button\"]').click()",
  "changes_made": [
    "Updated selector strategy from ID to CSS",
    "Used data-testid attribute (more stable)",
    "Renamed function for polymorphism"
  ],
  "confidence": "high"
}
```

---

## Step 5: Check Statistics

Monitor D8-GENESIS activity:

```bash
curl http://localhost:5000/api/genesis/stats | jq
```

**Expected output:**
```json
{
  "code_vault": {
    "total_fragments": 2,
    "by_platform": {"instagram": 2},
    "by_action": {"login": 1, "like": 1}
  },
  "coder_agent": {
    "total_generations": 5,
    "polymorphism_rate": "98.2%",
    "avg_generation_time": "12.3s"
  },
  "self_healing": {
    "total_errors": 3,
    "healed_successfully": 2,
    "success_rate": "66.7%"
  }
}
```

---

## Advanced: Execute with Auto-Healing

Use Python to execute functions with automatic healing:

```python
from app.evolution.self_healing import SelfHealingOrchestrator
from app.agents.coder_agent import CoderAgent
from app.knowledge.code_vault import CodeVault
from lib.llm import DeepSeekClient

# Initialize
deepseek = DeepSeekClient()
vault = CodeVault()
coder = CoderAgent(deepseek, vault)
healer = SelfHealingOrchestrator(coder, max_healing_attempts=3)

# Define a function that might break
def scrape_instagram_profile(username):
    driver = webdriver.Chrome()
    driver.get(f"https://instagram.com/{username}")
    
    # This will break if Instagram changes UI
    followers = driver.find_element_by_xpath("//span[@class='g47SY']").text
    return int(followers)

# Execute with auto-healing
result = healer.execute_with_healing(scrape_instagram_profile, "nasa")

if result['success']:
    print(f"✅ Followers: {result['result']}")
    print(f"Healing applied: {result['healing_applied']}")
else:
    print(f"❌ Failed after {result['healing_attempts']} attempts")
    print(f"Error: {result['final_error']}")
```

---

## Real-World Use Cases

### Use Case 1: Legacy Bot Fleet Migration

You have 50 old Instagram bots using deprecated selectors.

**Solution:**
1. Ingest all 50 scripts into Code Vault
2. Generate 10 polymorphic versions of each
3. Deploy variations across accounts
4. Self-healing adapts when Instagram updates UI

### Use Case 2: Anti-Ban Evasion

Instagram detects your bot's code signature.

**Solution:**
1. Generate 20 variants of the same function
2. Rotate between variants every N executions
3. Each variant has different timing, variables, control flow
4. Detection systems can't establish a pattern

### Use Case 3: Autonomous Long-Running Bots

Your bot runs 24/7 but breaks when apps update overnight.

**Solution:**
1. Wrap execution in `SelfHealingOrchestrator`
2. When errors occur, system automatically:
   - Analyzes error
   - Generates fix
   - Deploys hot patch
   - Resumes operation
3. No human intervention needed

---

## Performance Benchmarks

| Operation | Time | Cost |
|-----------|------|------|
| Code ingestion (100 files) | 10s | $0 |
| Semantic search | 50-200ms | $0 |
| Code generation | 10-15s | $0 (local) |
| Self-healing analysis | 10-30s | $0 (local) |

**Total cost:** $0/month (using local DeepSeek)

---

## Troubleshooting

### "Code Vault not initialized"

Check `app/main.py` logs on startup. Ensure ChromaDB can write to `data/chroma_db/`.

### "No fragments found in legacy_code/"

Ensure `.py` files exist in the directory. Run with `--verbose` flag.

### "DeepSeek not responding"

Check Ollama is running:
```bash
curl http://localhost:11434/api/tags
```

### "Self-healing success rate low"

- Check that Code Vault has relevant legacy patterns
- Review error messages for clarity
- Increase `max_healing_attempts` in config

---

## Next Steps

1. **Integrate with real bots:** Use self-healing in production
2. **Build code library:** Ingest all your legacy automation scripts
3. **Monitor metrics:** Track healing success rate over time
4. **Expand coverage:** Add more platforms (TikTok, Twitter, etc.)

For full documentation, see [D8_GENESIS_MODULE.md](D8_GENESIS_MODULE.md).
