"""
Robust HTTP Connection with retry, timeout, exponential backoff
"""

import requests
import time
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class RobustConnection:
    """
    Wrapper para requests con:
    - Retry automático (3 intentos)
    - Timeout configurable (30s default)
    - Exponential backoff (2^attempt segundos)
    - Circuit breaker pattern
    """
    
    def __init__(self, max_retries: int = 3, timeout: int = 30):
        self.max_retries = max_retries
        self.timeout = timeout
        self.session = requests.Session()
        
        # Circuit breaker state
        self.failure_threshold = 5
        self.failure_count = 0
        self.circuit_open_until = 0
    
    def _is_circuit_open(self) -> bool:
        """Verifica si el circuit breaker está abierto"""
        if self.circuit_open_until > time.time():
            return True
        
        # Reset si pasó el tiempo
        if self.circuit_open_until > 0:
            logger.info("🔓 Circuit breaker cerrado, reintentando...")
            self.circuit_open_until = 0
            self.failure_count = 0
        
        return False
    
    def _open_circuit(self):
        """Abre el circuit breaker por 60 segundos"""
        self.circuit_open_until = time.time() + 60
        logger.warning("🔴 Circuit breaker abierto por 60 segundos")
    
    def _record_failure(self):
        """Registra un fallo"""
        self.failure_count += 1
        if self.failure_count >= self.failure_threshold:
            self._open_circuit()
    
    def _record_success(self):
        """Registra un éxito"""
        self.failure_count = max(0, self.failure_count - 1)
    
    def get(self, url: str, **kwargs) -> Optional[requests.Response]:
        """GET request con retry"""
        return self._request("GET", url, **kwargs)
    
    def post(self, url: str, **kwargs) -> Optional[requests.Response]:
        """POST request con retry"""
        return self._request("POST", url, **kwargs)
    
    def _request(self, method: str, url: str, **kwargs) -> Optional[requests.Response]:
        """
        Ejecuta request con retry y exponential backoff
        
        Args:
            method: HTTP method (GET, POST, etc.)
            url: URL destino
            **kwargs: Argumentos adicionales para requests
        
        Returns:
            Response object o None si falla
        """
        # Circuit breaker check
        if self._is_circuit_open():
            logger.error(f"🔴 Circuit breaker abierto, rechazando request a {url}")
            return None
        
        # Set timeout si no está especificado
        if "timeout" not in kwargs:
            kwargs["timeout"] = self.timeout
        
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                # Log attempt
                if attempt > 0:
                    logger.info(f"🔄 Retry {attempt + 1}/{self.max_retries} para {url}")
                
                # Make request
                response = self.session.request(method, url, **kwargs)
                
                # Success
                if response.status_code < 500:
                    self._record_success()
                    return response
                
                # Server error (5xx) - retry
                last_error = f"HTTP {response.status_code}"
                logger.warning(f"⚠️ {last_error} en {url}, reintentando...")
                
            except requests.exceptions.Timeout as e:
                last_error = f"Timeout después de {self.timeout}s"
                logger.warning(f"⏱️ {last_error} en {url}")
            
            except requests.exceptions.ConnectionError as e:
                last_error = f"Connection error: {str(e)}"
                logger.warning(f"🔌 {last_error}")
            
            except Exception as e:
                last_error = f"Unexpected error: {str(e)}"
                logger.error(f"❌ {last_error}")
                break  # No retry en errores inesperados
            
            # Exponential backoff
            if attempt < self.max_retries - 1:
                backoff_time = 2 ** attempt
                logger.info(f"⏳ Esperando {backoff_time}s antes de reintentar...")
                time.sleep(backoff_time)
        
        # Todos los intentos fallaron
        self._record_failure()
        logger.error(f"❌ Request falló después de {self.max_retries} intentos: {last_error}")
        return None
    
    def close(self):
        """Cierra la sesión"""
        self.session.close()
