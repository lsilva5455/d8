"""
Self-Healing System - Autonomous Error Detection and Code Repair
Continuously monitors executions and automatically fixes broken code
"""

from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import traceback
import logging
import json
import time

from app.agents.coder_agent import CoderAgent

logger = logging.getLogger(__name__)


class ErrorSeverity(Enum):
    """Error severity levels"""
    LOW = "low"  # Recoverable, retry might work
    MEDIUM = "medium"  # Needs code fix
    HIGH = "high"  # Critical, blocks execution
    FATAL = "fatal"  # System-level failure


@dataclass
class ExecutionError:
    """Represents an error during code execution"""
    error_type: str
    error_message: str
    traceback: str
    code_snippet: str
    context: Dict[str, Any]
    severity: ErrorSeverity
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    fix_attempted: bool = False
    fix_successful: bool = False
    fix_code: Optional[str] = None


class SelfHealingOrchestrator:
    """
    Orchestrates the self-healing loop:
    1. Detect errors
    2. Analyze root cause
    3. Generate fix via CoderAgent
    4. Deploy hot patch
    5. Verify fix
    """
    
    def __init__(self, coder_agent: CoderAgent, max_healing_attempts: int = 3):
        self.coder = coder_agent
        self.max_attempts = max_healing_attempts
        self.error_history: List[ExecutionError] = []
        self.healing_stats = {
            "total_errors": 0,
            "healed": 0,
            "failed": 0,
            "success_rate": 0.0
        }
        
        logger.info(f"🔧 Self-Healing Orchestrator initialized (max attempts: {max_attempts})")
    
    def execute_with_healing(self,
                            func: Callable,
                            *args,
                            **kwargs) -> Dict[str, Any]:
        """
        Execute a function with automatic self-healing on errors
        
        Args:
            func: Function to execute
            *args, **kwargs: Arguments for the function
        
        Returns:
            Execution result with healing info
        """
        attempt = 0
        last_error = None
        
        while attempt < self.max_attempts:
            try:
                logger.info(f"🚀 Executing {func.__name__} (attempt {attempt + 1}/{self.max_attempts})")
                
                result = func(*args, **kwargs)
                
                if attempt > 0:
                    logger.info(f"✅ Execution successful after {attempt} healing attempts")
                
                return {
                    "success": True,
                    "result": result,
                    "healing_applied": attempt > 0,
                    "healing_attempts": attempt
                }
                
            except Exception as e:
                last_error = e
                self.healing_stats["total_errors"] += 1
                
                logger.error(f"❌ Execution failed: {str(e)}")
                
                # Record error
                error_record = self._record_error(e, func, args, kwargs)
                
                # Check if we should attempt healing
                if attempt >= self.max_attempts - 1:
                    logger.error(f"💥 Max healing attempts reached, giving up")
                    self.healing_stats["failed"] += 1
                    break
                
                # Attempt self-healing
                healing_result = self._heal_error(error_record)
                
                if healing_result["success"]:
                    logger.info(f"🔧 Healing successful, retrying execution...")
                    self.healing_stats["healed"] += 1
                    
                    # Update function with healed code
                    func = self._deploy_healed_code(healing_result["code"], func)
                    
                    attempt += 1
                    time.sleep(1)  # Brief pause before retry
                else:
                    logger.error(f"❌ Healing failed: {healing_result.get('error')}")
                    self.healing_stats["failed"] += 1
                    break
        
        # Update success rate
        total = self.healing_stats["healed"] + self.healing_stats["failed"]
        if total > 0:
            self.healing_stats["success_rate"] = self.healing_stats["healed"] / total
        
        return {
            "success": False,
            "error": str(last_error),
            "healing_applied": attempt > 0,
            "healing_attempts": attempt,
            "healing_failed": True
        }
    
    def _record_error(self,
                     exception: Exception,
                     func: Callable,
                     args: tuple,
                     kwargs: dict) -> ExecutionError:
        """Record error with full context"""
        
        # Determine severity
        severity = self._classify_error_severity(exception)
        
        # Extract code snippet (if available)
        code_snippet = self._extract_code_snippet(func)
        
        error_record = ExecutionError(
            error_type=type(exception).__name__,
            error_message=str(exception),
            traceback=traceback.format_exc(),
            code_snippet=code_snippet,
            context={
                "function_name": func.__name__,
                "args": str(args),
                "kwargs": str(kwargs)
            },
            severity=severity
        )
        
        self.error_history.append(error_record)
        
        logger.info(f"📝 Error recorded: {error_record.error_type} (severity: {severity.value})")
        
        return error_record
    
    def _classify_error_severity(self, exception: Exception) -> ErrorSeverity:
        """Classify error severity based on type"""
        
        # High severity errors (need immediate fix)
        high_severity = [
            "NoSuchElementException",
            "ElementNotInteractableException",
            "TimeoutException",
            "StaleElementReferenceException"
        ]
        
        # Medium severity (retry might work)
        medium_severity = [
            "AttributeError",
            "KeyError",
            "IndexError"
        ]
        
        # Fatal errors (system-level)
        fatal_severity = [
            "MemoryError",
            "SystemError",
            "ConnectionError"
        ]
        
        error_name = type(exception).__name__
        
        if error_name in fatal_severity:
            return ErrorSeverity.FATAL
        elif error_name in high_severity:
            return ErrorSeverity.HIGH
        elif error_name in medium_severity:
            return ErrorSeverity.MEDIUM
        else:
            return ErrorSeverity.LOW
    
    def _extract_code_snippet(self, func: Callable) -> str:
        """Extract source code of function"""
        try:
            import inspect
            return inspect.getsource(func)
        except Exception as e:
            logger.warning(f"Could not extract source code: {e}")
            return f"# Function: {func.__name__}\n# Source unavailable"
    
    def _heal_error(self, error: ExecutionError) -> Dict[str, Any]:
        """
        Use CoderAgent to heal the error
        """
        logger.info(f"🔧 Attempting to heal error: {error.error_type}")
        
        # Build context for self-healing
        healing_context = {
            "error_type": error.error_type,
            "severity": error.severity.value,
            "function_context": error.context
        }
        
        # Call CoderAgent's self_heal method
        healing_result = self.coder.self_heal(
            broken_code=error.code_snippet,
            error_message=f"{error.error_type}: {error.error_message}",
            error_context=healing_context
        )
        
        # Update error record
        error.fix_attempted = True
        error.fix_successful = healing_result.get("success", False)
        error.fix_code = healing_result.get("code")
        
        return healing_result
    
    def _deploy_healed_code(self, healed_code: str, original_func: Callable) -> Callable:
        """
        Deploy healed code as a hot patch
        
        NOTE: In production, this would dynamically compile and replace the function.
        For this implementation, we return a modified version.
        """
        try:
            # Create new function from healed code
            namespace = {}
            exec(healed_code, namespace)
            
            # Find the function in namespace (assumes same name)
            func_name = original_func.__name__
            if func_name in namespace:
                new_func = namespace[func_name]
                logger.info(f"✅ Hot patch deployed for {func_name}")
                return new_func
            else:
                logger.warning(f"⚠️ Function {func_name} not found in healed code, using original")
                return original_func
                
        except Exception as e:
            logger.error(f"❌ Failed to deploy hot patch: {e}")
            return original_func
    
    def get_stats(self) -> Dict[str, Any]:
        """Get self-healing statistics"""
        return {
            "total_errors": self.healing_stats["total_errors"],
            "healed_successfully": self.healing_stats["healed"],
            "healing_failed": self.healing_stats["failed"],
            "success_rate": f"{self.healing_stats['success_rate']:.1%}",
            "error_history_size": len(self.error_history)
        }
    
    def get_error_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent error history"""
        recent_errors = self.error_history[-limit:]
        
        return [
            {
                "timestamp": err.timestamp,
                "type": err.error_type,
                "message": err.error_message[:100],
                "severity": err.severity.value,
                "fix_attempted": err.fix_attempted,
                "fix_successful": err.fix_successful
            }
            for err in recent_errors
        ]


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    from app.integrations.deepseek_client import DeepSeekClient
    from app.knowledge.code_vault import CodeVault
    from app.agents.coder_agent import CoderAgent
    
    # Initialize components
    deepseek = DeepSeekClient()
    vault = CodeVault()
    coder = CoderAgent(deepseek, vault)
    
    # Initialize self-healing orchestrator
    healer = SelfHealingOrchestrator(coder, max_healing_attempts=3)
    
    # Test function that will fail
    def broken_function():
        # Simulates a NoSuchElementException
        raise Exception("NoSuchElementException: Unable to locate element with id 'old_button'")
    
    # Execute with self-healing
    result = healer.execute_with_healing(broken_function)
    
    print("\n📊 Execution Result:")
    print(json.dumps(result, indent=2))
    
    print("\n📈 Self-Healing Stats:")
    print(json.dumps(healer.get_stats(), indent=2))
    
    print("\n📜 Error History:")
    print(json.dumps(healer.get_error_history(), indent=2))
