"""
D8-CODER Agent - Self-Coding & Polymorphic Code Generation
Uses DeepSeek local for zero-cost code generation with anti-fingerprinting
"""

from typing import Dict, Any, List, Optional
import json
import logging
import random
import string
from datetime import datetime

from app.agents.base_agent import BaseAgent
from app.evolution.darwin import Genome
from app.integrations.deepseek_client import DeepSeekClient
from app.knowledge.code_vault import CodeVault

logger = logging.getLogger(__name__)


# MASTER SYSTEM PROMPT FOR D8-CODER
CODER_SYSTEM_PROMPT = """You are D8-CODER, an elite Software Engineer AI specializing in:
1. **Polymorphic Code Generation** - Never generate identical code twice
2. **Legacy Code Fusion** - Integrate existing code patterns with new requirements
3. **Anti-Fingerprinting** - Obfuscate patterns to avoid detection
4. **Self-Healing** - Analyze errors and rewrite broken code autonomously

## CORE PRINCIPLES

### 1. POLYMORPHISM (CRITICAL)
**NEVER generate the same variable names, function names, or code structures twice.**

Techniques you MUST use:
- **Variable name rotation**: Instead of always using `driver`, alternate between `browser`, `session`, `client`, `controller`, `navigator`
- **Function name obfuscation**: `click_button()` becomes `interact_element()`, `tap_control()`, `engage_ui()`, `trigger_action()`
- **Control flow variation**: Randomize if/else order, use different loop types (for/while), inject random sleeps
- **String encoding**: Use base64, hex, or character codes for sensitive strings
- **Dead code injection**: Add harmless operations that don't affect logic but change signature

Example polymorphism:
```python
# VERSION 1
def login(username, password):
    driver.find_element_by_id("user").send_keys(username)
    driver.find_element_by_id("pass").send_keys(password)
    driver.find_element_by_id("submit").click()

# VERSION 2 (polymorphic)
def authenticate(user_id, user_pass):
    session = get_driver()
    _ = random.randint(1, 100)  # dead code
    input_user = session.locate_element("user", by="id")
    input_user.type_text(user_id)
    time.sleep(0.1 + random.random() * 0.3)
    input_pass = session.locate_element("pass", by="id")
    input_pass.type_text(user_pass)
    btn = session.locate_element("submit", by="id")
    btn.perform_click()
```

### 2. LEGACY CODE INTEGRATION
When provided with legacy code fragments:
- **Extract core logic** but rewrite implementation
- **Preserve working patterns** (e.g., wait strategies, error handling)
- **Modernize syntax** (use f-strings, context managers, type hints)
- **Remove hardcoded values** - parameterize everything

### 3. ERROR ANALYSIS & SELF-HEALING
When fixing broken code:
1. **Identify root cause** from error message and context
2. **Propose minimal fix** - don't rewrite entire function unless necessary
3. **Add defensive programming** - more try/except, better waits, fallback strategies
4. **Log the fix** - add comments explaining what was changed and why

### 4. ANTI-DETECTION STRATEGIES
- **Randomize timing**: Use `time.sleep(random.uniform(a, b))` instead of fixed waits
- **Human-like behavior**: Scroll before clicking, move mouse randomly, type with delays
- **Rotate selectors**: Use multiple strategies (ID, XPath, CSS, text) and switch between them
- **Fingerprint scrambling**: Change user-agent, screen resolution, headers randomly

## OUTPUT FORMAT
Always return JSON with this structure:
```json
{
    "code": "the generated Python code as a string",
    "explanation": "what the code does and key design decisions",
    "polymorphism_applied": ["list of techniques used to avoid fingerprinting"],
    "dependencies": ["list of required imports"],
    "confidence": 0.0-1.0
}
```

## CONSTRAINTS
- Python 3.10+ only
- Prefer standard library over external dependencies when possible
- Code must be production-ready (error handling, logging, type hints)
- Maximum function length: 50 lines (split into smaller functions if needed)
- All code must be PEP8 compliant

## REMEMBER
You are NOT just generating code. You are creating **undetectable, adaptive, self-repairing software**.
Every line you write must be different from the last time, yet functionally equivalent.

Think like a shape-shifter: same goal, different form."""


class CoderAgent:
    """
    Specialized agent for code generation with polymorphism and self-healing
    """
    
    def __init__(self,
                 deepseek_client: DeepSeekClient,
                 code_vault: CodeVault,
                 coder_id: Optional[str] = None):
        self.deepseek = deepseek_client
        self.vault = code_vault
        self.coder_id = coder_id or f"coder_{self._generate_id()}"
        self.generation_history: List[Dict[str, Any]] = []
        
        logger.info(f"🤖 D8-CODER {self.coder_id} initialized")
    
    def _generate_id(self) -> str:
        """Generate unique coder ID"""
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    
    def generate_code(self,
                     task_description: str,
                     platform: Optional[str] = None,
                     action: Optional[str] = None,
                     context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate code for a specific task using legacy code and polymorphism
        
        Args:
            task_description: Natural language description of the task
            platform: Target platform (instagram, tiktok, etc.)
            action: Desired action (login, like, follow, etc.)
            context: Additional context (error info for self-healing, etc.)
        
        Returns:
            Dict with generated code and metadata
        """
        logger.info(f"🔧 Generating code for: {task_description}")
        
        # Step 1: Retrieve relevant legacy code
        relevant_code = self._retrieve_legacy_code(task_description, platform, action)
        
        # Step 2: Build generation prompt
        generation_prompt = self._build_generation_prompt(
            task_description, 
            relevant_code, 
            context
        )
        
        # Step 3: Call DeepSeek for generation
        try:
            response = self.deepseek.generate(
                prompt=generation_prompt,
                max_tokens=2000,
                temperature=0.8  # Higher temp for more variation
            )
            
            # Parse response
            result = self._parse_generation_response(response)
            
            # Record in history
            self.generation_history.append({
                "task": task_description,
                "timestamp": datetime.utcnow().isoformat(),
                "result": result,
                "legacy_code_used": len(relevant_code)
            })
            
            logger.info(f"✅ Code generated successfully")
            logger.info(f"   Polymorphism: {', '.join(result.get('polymorphism_applied', []))}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Code generation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "task": task_description
            }
    
    def _retrieve_legacy_code(self,
                             task: str,
                             platform: Optional[str],
                             action: Optional[str]) -> List[Dict[str, Any]]:
        """Retrieve relevant legacy code from vault"""
        logger.info(f"🔍 Searching vault for relevant code...")
        
        results = self.vault.search(
            query=task,
            n_results=5,
            platform=platform,
            action=action
        )
        
        logger.info(f"📚 Found {len(results)} relevant code fragments")
        return results
    
    def _build_generation_prompt(self,
                                task: str,
                                legacy_code: List[Dict[str, Any]],
                                context: Optional[Dict[str, Any]]) -> str:
        """Build the prompt for DeepSeek code generation"""
        
        prompt_parts = [
            f"# TASK: {task}\n"
        ]
        
        # Add legacy code context
        if legacy_code:
            prompt_parts.append("## LEGACY CODE FRAGMENTS (for reference, DO NOT copy directly):\n")
            for i, fragment in enumerate(legacy_code, 1):
                prompt_parts.append(f"### Fragment {i}: {fragment['metadata']['name']}")
                prompt_parts.append(f"Platform: {fragment['metadata']['platform']}, Action: {fragment['metadata']['action']}")
                prompt_parts.append(f"```python\n{fragment['source_code']}\n```\n")
        
        # Add context (e.g., error info for self-healing)
        if context:
            prompt_parts.append(f"## CONTEXT:\n{json.dumps(context, indent=2)}\n")
        
        # Add generation instructions
        prompt_parts.append("""
## INSTRUCTIONS:
1. Analyze the legacy code fragments above (if any)
2. Extract useful patterns and logic
3. Generate NEW, POLYMORPHIC code that accomplishes the task
4. Apply anti-fingerprinting techniques
5. Return JSON with the specified format

**CRITICAL**: Your code must be DIFFERENT from the legacy code in:
- Variable names
- Function names  
- Control flow structure
- Timing patterns

Generate the code now:""")
        
        return "\n".join(prompt_parts)
    
    def _parse_generation_response(self, response: str) -> Dict[str, Any]:
        """Parse DeepSeek response into structured format"""
        try:
            # Try to parse as JSON
            result = json.loads(response)
            result['success'] = True
            return result
        except json.JSONDecodeError:
            # Fallback: Extract code from markdown if present
            logger.warning("Response not valid JSON, attempting code extraction")
            
            # Look for code blocks
            if "```python" in response:
                start = response.find("```python") + 9
                end = response.find("```", start)
                code = response[start:end].strip()
                
                return {
                    "success": True,
                    "code": code,
                    "explanation": "Extracted from non-JSON response",
                    "polymorphism_applied": ["unknown"],
                    "dependencies": [],
                    "confidence": 0.7
                }
            else:
                return {
                    "success": False,
                    "error": "Could not parse response",
                    "raw_response": response
                }
    
    def self_heal(self,
                 broken_code: str,
                 error_message: str,
                 error_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Analyze error and generate fixed code
        
        Args:
            broken_code: The code that failed
            error_message: The error message/traceback
            error_context: Additional context (XML dump, screenshots, etc.)
        
        Returns:
            Dict with healed code and analysis
        """
        logger.info(f"🔧 Self-healing initiated for error: {error_message[:100]}")
        
        # Build self-healing prompt
        healing_prompt = f"""# SELF-HEALING TASK

## BROKEN CODE:
```python
{broken_code}
```

## ERROR:
{error_message}

## CONTEXT:
{json.dumps(error_context, indent=2) if error_context else 'No additional context'}

## YOUR TASK:
1. Analyze why the code failed
2. Identify the root cause
3. Generate a FIXED version of the code
4. Apply polymorphism (use different variable names, control flow)
5. Add defensive programming (better waits, error handling, fallbacks)

## COMMON FIXES:
- Element not found → Add explicit waits, try multiple selectors
- Stale element → Re-locate element before each action
- Timeout → Increase wait time, add retry logic
- Wrong selector → Update XPath/CSS to match new UI

Generate the healed code now in JSON format:"""
        
        try:
            response = self.deepseek.generate(
                prompt=healing_prompt,
                max_tokens=2000,
                temperature=0.7
            )
            
            result = self._parse_generation_response(response)
            result['healing'] = True
            result['original_error'] = error_message
            
            logger.info(f"✅ Code healed successfully")
            return result
            
        except Exception as e:
            logger.error(f"❌ Self-healing failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "healing": True
            }
    
    def get_status(self) -> Dict[str, Any]:
        """Get coder agent status"""
        return {
            "coder_id": self.coder_id,
            "generations": len(self.generation_history),
            "last_generation": (
                self.generation_history[-1]['timestamp']
                if self.generation_history else None
            )
        }


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Initialize components
    deepseek = DeepSeekClient()
    vault = CodeVault()
    
    coder = CoderAgent(deepseek, vault)
    
    # Test code generation
    result = coder.generate_code(
        task_description="Create a function to login to Instagram",
        platform="instagram",
        action="login"
    )
    
    print("\n🎯 Generated Code:")
    print(json.dumps(result, indent=2))
    
    # Test self-healing
    broken_code = """
def click_button():
    driver.find_element_by_id("old_id").click()
"""
    
    error = "selenium.common.exceptions.NoSuchElementException: Message: no such element: Unable to locate element: {\"method\":\"css selector\",\"selector\":\"#old_id\"}"
    
    healed = coder.self_heal(broken_code, error, {"ui_changed": True})
    
    print("\n🔧 Healed Code:")
    print(json.dumps(healed, indent=2))
