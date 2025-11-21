"""
Overbooking Optimizer - Aprendizaje Adaptativo de Capacidad
============================================================
Aprende cuántos agentes puede manejar cada tipo de dispositivo.
Factor inicial 1.5x, se ajusta según carga histórica.
Replica aprendizaje entre devices similares.

Author: D8 System
Date: 2025-11-21
"""

import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json
from pathlib import Path
import statistics

logger = logging.getLogger(__name__)


@dataclass
class LoadSample:
    """Muestra de carga en un momento dado"""
    timestamp: float
    agents_registered: int
    agents_active: int
    cpu_percent: float
    memory_percent: float
    latency_ms: float = 0.0  # Latencia promedio de requests


@dataclass
class DeviceProfile:
    """Perfil de un tipo de dispositivo"""
    device_type: str
    overbooking_factor: float = 1.5  # Factor inicial
    samples: List[LoadSample] = field(default_factory=list)
    adjustments_count: int = 0
    last_adjustment: Optional[float] = None


class OverbookingOptimizer:
    """
    Optimiza factor de overbooking por tipo de dispositivo
    
    Lógica:
    - Factor inicial: 1.5x (8 slots → 12 agentes)
    - Tracking histórico de carga por hora del día
    - Ajuste dinámico basado en métricas reales
    - Replicación de aprendizaje entre devices similares
    """
    
    def __init__(self, data_dir: Optional[Path] = None):
        # Profiles por tipo de dispositivo
        self.profiles: Dict[str, DeviceProfile] = {}
        
        # Data directory
        self.data_dir = data_dir or (Path.home() / "Documents" / "d8_data" / "orchestrator")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Configuración
        self.min_samples_for_adjustment = 100  # Mínimo de samples antes de ajustar
        self.adjustment_interval_hours = 24  # Ajustar máximo cada 24h
        self.max_samples_per_profile = 10000  # Límite de memoria
        
        # Load state
        self._load_state()
        
        logger.info("📊 OverbookingOptimizer initialized")
        logger.info(f"   Device profiles: {len(self.profiles)}")
    
    def get_overbooking_factor(self, device_type: str) -> float:
        """Obtener factor de overbooking actual para un device"""
        if device_type not in self.profiles:
            # Crear profile con factor por defecto
            self.profiles[device_type] = DeviceProfile(device_type=device_type)
            self._save_state()
        
        return self.profiles[device_type].overbooking_factor
    
    def record_sample(
        self,
        device_type: str,
        agents_registered: int,
        agents_active: int,
        cpu_percent: float,
        memory_percent: float,
        latency_ms: float = 0.0
    ):
        """Registrar muestra de carga"""
        if device_type not in self.profiles:
            self.profiles[device_type] = DeviceProfile(device_type=device_type)
        
        profile = self.profiles[device_type]
        
        sample = LoadSample(
            timestamp=datetime.utcnow().timestamp(),
            agents_registered=agents_registered,
            agents_active=agents_active,
            cpu_percent=cpu_percent,
            memory_percent=memory_percent,
            latency_ms=latency_ms
        )
        
        profile.samples.append(sample)
        
        # Limitar tamaño de samples
        if len(profile.samples) > self.max_samples_per_profile:
            # Remover los más viejos
            profile.samples = profile.samples[-self.max_samples_per_profile:]
        
        # Check si es momento de ajustar
        self._maybe_adjust_factor(device_type)
    
    def _maybe_adjust_factor(self, device_type: str):
        """Evaluar si es momento de ajustar el factor"""
        profile = self.profiles[device_type]
        
        # Verificar condiciones para ajuste
        if len(profile.samples) < self.min_samples_for_adjustment:
            return  # No hay suficientes datos
        
        if profile.last_adjustment:
            hours_since_last = (datetime.utcnow().timestamp() - profile.last_adjustment) / 3600
            if hours_since_last < self.adjustment_interval_hours:
                return  # Ajuste muy reciente
        
        # Analizar samples recientes
        recent_samples = profile.samples[-500:]  # Últimas 500 muestras
        
        # Calcular métricas
        avg_active_ratio = statistics.mean([
            s.agents_active / s.agents_registered if s.agents_registered > 0 else 0
            for s in recent_samples
        ])
        
        avg_cpu = statistics.mean([s.cpu_percent for s in recent_samples])
        avg_memory = statistics.mean([s.memory_percent for s in recent_samples])
        
        # Calcular latencia si está disponible
        latencies = [s.latency_ms for s in recent_samples if s.latency_ms > 0]
        avg_latency = statistics.mean(latencies) if latencies else 0
        
        # Decisión de ajuste
        old_factor = profile.overbooking_factor
        new_factor = old_factor
        
        # Escenario 1: Alta utilización constante → aumentar factor
        if avg_active_ratio > 0.80 and avg_cpu < 70 and avg_memory < 70:
            new_factor = min(old_factor + 0.1, 2.0)  # Cap at 2.0x
            reason = "High utilization, resources available"
        
        # Escenario 2: Baja utilización constante → reducir factor
        elif avg_active_ratio < 0.50:
            new_factor = max(old_factor - 0.1, 1.2)  # Min 1.2x
            reason = "Low utilization, reduce overbooking"
        
        # Escenario 3: Recursos saturados → reducir factor
        elif avg_cpu > 85 or avg_memory > 85:
            new_factor = max(old_factor - 0.2, 1.2)
            reason = "Resources saturated, reduce load"
        
        # Escenario 4: Latencia aumentando → reducir factor
        elif avg_latency > 0 and avg_latency > 1000:  # >1s
            new_factor = max(old_factor - 0.1, 1.2)
            reason = "High latency detected"
        
        else:
            return  # No adjustment needed
        
        # Aplicar ajuste
        if new_factor != old_factor:
            profile.overbooking_factor = new_factor
            profile.adjustments_count += 1
            profile.last_adjustment = datetime.utcnow().timestamp()
            
            logger.info(
                f"🔧 Adjusted overbooking for {device_type}: "
                f"{old_factor:.2f}x → {new_factor:.2f}x ({reason})"
            )
            
            # Propagar a devices similares
            self._propagate_to_similar_devices(device_type, new_factor, reason)
            
            self._save_state()
    
    def _propagate_to_similar_devices(
        self,
        source_device_type: str,
        new_factor: float,
        reason: str
    ):
        """
        Propagar aprendizaje a devices similares
        
        Ej: Si raspberry_pi_4 aprende factor 1.7x,
            aplicarlo a otros raspberry_pi_4
        """
        # Devices con mismo prefijo base
        base_type = source_device_type.split('_')[0]  # ej: "raspberry" de "raspberry_pi_4"
        
        for device_type, profile in self.profiles.items():
            if device_type == source_device_type:
                continue  # Skip source
            
            if device_type.startswith(base_type):
                # Device similar, propagar conocimiento
                old_factor = profile.overbooking_factor
                
                # Interpolar: 50% del aprendizaje
                interpolated_factor = (profile.overbooking_factor + new_factor) / 2
                
                profile.overbooking_factor = interpolated_factor
                
                logger.info(
                    f"🔄 Propagated learning to {device_type}: "
                    f"{old_factor:.2f}x → {interpolated_factor:.2f}x "
                    f"(from {source_device_type})"
                )
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas de todos los profiles"""
        stats = {}
        
        for device_type, profile in self.profiles.items():
            recent_samples = profile.samples[-100:] if profile.samples else []
            
            if recent_samples:
                avg_active_ratio = statistics.mean([
                    s.agents_active / s.agents_registered if s.agents_registered > 0 else 0
                    for s in recent_samples
                ])
                avg_cpu = statistics.mean([s.cpu_percent for s in recent_samples])
            else:
                avg_active_ratio = 0
                avg_cpu = 0
            
            stats[device_type] = {
                "overbooking_factor": profile.overbooking_factor,
                "samples_count": len(profile.samples),
                "adjustments_count": profile.adjustments_count,
                "avg_active_ratio": round(avg_active_ratio, 2),
                "avg_cpu_percent": round(avg_cpu, 1),
                "last_adjustment": profile.last_adjustment
            }
        
        return stats
    
    def _save_state(self):
        """Persistir estado"""
        try:
            state_file = self.data_dir / "overbooking_profiles.json"
            
            state = {}
            
            for device_type, profile in self.profiles.items():
                # Solo guardar últimas 1000 muestras para no ocupar mucho espacio
                recent_samples = profile.samples[-1000:]
                
                state[device_type] = {
                    "overbooking_factor": profile.overbooking_factor,
                    "adjustments_count": profile.adjustments_count,
                    "last_adjustment": profile.last_adjustment,
                    "samples": [
                        {
                            "timestamp": s.timestamp,
                            "agents_registered": s.agents_registered,
                            "agents_active": s.agents_active,
                            "cpu_percent": s.cpu_percent,
                            "memory_percent": s.memory_percent,
                            "latency_ms": s.latency_ms
                        }
                        for s in recent_samples
                    ]
                }
            
            state_file.write_text(json.dumps(state, indent=2))
            
        except Exception as e:
            logger.error(f"❌ Failed to save overbooking state: {e}")
    
    def _load_state(self):
        """Cargar estado persistido"""
        try:
            state_file = self.data_dir / "overbooking_profiles.json"
            
            if not state_file.exists():
                return
            
            state = json.loads(state_file.read_text())
            
            for device_type, data in state.items():
                profile = DeviceProfile(
                    device_type=device_type,
                    overbooking_factor=data["overbooking_factor"],
                    adjustments_count=data.get("adjustments_count", 0),
                    last_adjustment=data.get("last_adjustment")
                )
                
                # Cargar samples
                for sample_data in data.get("samples", []):
                    sample = LoadSample(
                        timestamp=sample_data["timestamp"],
                        agents_registered=sample_data["agents_registered"],
                        agents_active=sample_data["agents_active"],
                        cpu_percent=sample_data["cpu_percent"],
                        memory_percent=sample_data["memory_percent"],
                        latency_ms=sample_data.get("latency_ms", 0.0)
                    )
                    profile.samples.append(sample)
                
                self.profiles[device_type] = profile
            
            logger.info(f"📂 Loaded {len(self.profiles)} device profiles")
            
        except Exception as e:
            logger.warning(f"⚠️ Could not load overbooking state: {e}")
