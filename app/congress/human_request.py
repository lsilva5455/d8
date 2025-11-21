"""
Human Request System - Gestión de solicitudes que requieren intervención humana
Congreso → Intenta automatizar → Si no puede → Solicita a Leo por Telegram
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime
from enum import Enum
from pathlib import Path
import json
import logging

logger = logging.getLogger(__name__)


class RequestType(Enum):
    """Tipos de solicitudes"""
    PAYMENT = "payment"  # Pagos (dominios, servicios, etc.)
    DESIGN_DECISION = "design_decision"  # Decisiones de diseño
    API_ACCOUNT = "api_account"  # Crear cuenta en servicio
    CONTENT_APPROVAL = "content_approval"  # Aprobar contenido
    STRATEGIC_DECISION = "strategic_decision"  # Decisiones estratégicas
    OTHER = "other"


class RequestStatus(Enum):
    """Estados de solicitud"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


@dataclass
class HumanRequest:
    """Solicitud que requiere intervención humana"""
    request_id: str
    request_type: RequestType
    title: str
    description: str
    estimated_cost: Optional[float] = None
    priority: int = 5  # 1-10
    created_at: datetime = field(default_factory=datetime.now)
    created_by: str = "Congress"  # Qué sistema la generó
    status: RequestStatus = RequestStatus.PENDING
    approved_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    actual_cost: Optional[float] = None
    notes: str = ""
    
    def to_dict(self) -> dict:
        return {
            'request_id': self.request_id,
            'request_type': self.request_type.value,
            'title': self.title,
            'description': self.description,
            'estimated_cost': self.estimated_cost,
            'priority': self.priority,
            'created_at': self.created_at.isoformat(),
            'created_by': self.created_by,
            'status': self.status.value,
            'approved_at': self.approved_at.isoformat() if self.approved_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'actual_cost': self.actual_cost,
            'notes': self.notes
        }
    
    def to_telegram_message(self) -> str:
        """Formatea solicitud para Telegram"""
        icon = {
            RequestType.PAYMENT: "💳",
            RequestType.DESIGN_DECISION: "🎨",
            RequestType.API_ACCOUNT: "🔑",
            RequestType.CONTENT_APPROVAL: "📝",
            RequestType.STRATEGIC_DECISION: "🎯",
            RequestType.OTHER: "❓"
        }.get(self.request_type, "📋")
        
        priority_text = "🔴 ALTA" if self.priority >= 8 else "🟡 MEDIA" if self.priority >= 5 else "🟢 BAJA"
        
        message = f"""{icon} SOLICITUD HUMANA REQUERIDA

**{self.title}**

**Descripción:**
{self.description}

**Prioridad:** {priority_text}
**Generado por:** {self.created_by}
"""
        
        if self.estimated_cost:
            message += f"**Costo estimado:** ${self.estimated_cost:.2f}\n"
        
        message += f"""
**ID:** `{self.request_id}`

**Opciones:**
/aprobar {self.request_id}
/rechazar {self.request_id}
/posponer {self.request_id}
"""
        
        return message


class HumanRequestManager:
    """
    Gestiona solicitudes que requieren intervención humana
    
    Flujo:
    1. Congreso detecta necesidad
    2. Intenta resolver automáticamente
    3. Si no puede → Crea HumanRequest
    4. Notifica a Leo por Telegram
    5. Leo aprueba/rechaza
    6. Sistema procede según decisión
    """
    
    def __init__(self, data_dir: Optional[Path] = None, telegram_bot=None):
        self.data_dir = data_dir or Path.home() / "Documents" / "d8_data" / "human_requests"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.requests: Dict[str, HumanRequest] = {}
        self.request_counter = 0
        self.telegram_bot = telegram_bot  # Referencia al bot de Telegram
        
        self._load_requests()
    
    def set_telegram_bot(self, telegram_bot):
        """Configura el bot de Telegram para notificaciones"""
        self.telegram_bot = telegram_bot
        logger.info("✅ Bot de Telegram configurado en HumanRequestManager")
    
    def _load_requests(self):
        """Carga solicitudes desde disco"""
        requests_file = self.data_dir / "requests.json"
        
        if requests_file.exists():
            try:
                data = json.loads(requests_file.read_text())
                
                for req_data in data.get("requests", []):
                    req = HumanRequest(
                        request_id=req_data["request_id"],
                        request_type=RequestType(req_data["request_type"]),
                        title=req_data["title"],
                        description=req_data["description"],
                        estimated_cost=req_data.get("estimated_cost"),
                        priority=req_data.get("priority", 5),
                        created_at=datetime.fromisoformat(req_data["created_at"]),
                        created_by=req_data.get("created_by", "Congress"),
                        status=RequestStatus(req_data["status"]),
                        notes=req_data.get("notes", "")
                    )
                    
                    if req_data.get("approved_at"):
                        req.approved_at = datetime.fromisoformat(req_data["approved_at"])
                    if req_data.get("completed_at"):
                        req.completed_at = datetime.fromisoformat(req_data["completed_at"])
                    if req_data.get("actual_cost"):
                        req.actual_cost = req_data["actual_cost"]
                    
                    self.requests[req.request_id] = req
                
                self.request_counter = data.get("counter", 0)
                logger.info(f"✅ Cargadas {len(self.requests)} solicitudes humanas")
                
            except Exception as e:
                logger.error(f"❌ Error cargando solicitudes: {e}")
    
    def _save_requests(self):
        """Guarda solicitudes a disco"""
        requests_file = self.data_dir / "requests.json"
        
        data = {
            "counter": self.request_counter,
            "requests": [req.to_dict() for req in self.requests.values()]
        }
        
        requests_file.write_text(json.dumps(data, indent=2))
    
    def create_request(
        self,
        request_type: RequestType,
        title: str,
        description: str,
        estimated_cost: Optional[float] = None,
        priority: int = 5,
        created_by: str = "Congress"
    ) -> HumanRequest:
        """
        Crea nueva solicitud humana
        
        Args:
            request_type: Tipo de solicitud
            title: Título corto
            description: Descripción detallada
            estimated_cost: Costo estimado (opcional)
            priority: 1-10 (default 5)
            created_by: Sistema que la creó
        
        Returns:
            HumanRequest creado
        """
        self.request_counter += 1
        request_id = f"req-{self.request_counter:04d}"
        
        request = HumanRequest(
            request_id=request_id,
            request_type=request_type,
            title=title,
            description=description,
            estimated_cost=estimated_cost,
            priority=priority,
            created_by=created_by
        )
        
        self.requests[request_id] = request
        self._save_requests()
        
        logger.info(f"📋 Solicitud humana creada: {request_id} - {title}")
        
        # Notificar por Telegram si está disponible
        if self.telegram_bot:
            try:
                import asyncio
                asyncio.create_task(self.telegram_bot.notify_new_request(request))
            except Exception as e:
                logger.error(f"Error notificando por Telegram: {e}")
        
        return request
    
    def approve_request(self, request_id: str, approved_by: str = "Leo", notes: str = "") -> bool:
        """Aprueba solicitud"""
        if request_id not in self.requests:
            return False
        
        request = self.requests[request_id]
        request.status = RequestStatus.APPROVED
        request.approved_at = datetime.now()
        if notes:
            request.notes = notes
        else:
            request.notes = f"Aprobado por {approved_by}"
        
        self._save_requests()
        logger.info(f"✅ Solicitud aprobada: {request_id} por {approved_by}")
        
        return True
    
    def reject_request(self, request_id: str, rejected_by: str = "Leo", reason: str = "") -> bool:
        """Rechaza solicitud"""
        if request_id not in self.requests:
            return False
        
        request = self.requests[request_id]
        request.status = RequestStatus.REJECTED
        if reason:
            request.notes = f"Rechazado por {rejected_by}: {reason}"
        else:
            request.notes = f"Rechazado por {rejected_by}"
        
        self._save_requests()
        logger.info(f"❌ Solicitud rechazada: {request_id} por {rejected_by}")
        
        return True
    
    def complete_request(self, request_id: str, completed_by: str = "Leo", actual_cost: Optional[float] = None, notes: str = "") -> bool:
        """Marca solicitud como completada"""
        if request_id not in self.requests:
            return False
        
        request = self.requests[request_id]
        request.status = RequestStatus.COMPLETED
        request.completed_at = datetime.now()
        
        if actual_cost is not None:
            request.actual_cost = actual_cost
        
        if notes:
            request.notes += f"\nCompletado por {completed_by}: {notes}"
        else:
            request.notes += f"\nCompletado por {completed_by}"
        
        self._save_requests()
        logger.info(f"✅ Solicitud completada: {request_id} por {completed_by} (${actual_cost or 0})")
        
        return True
    
    def get_pending_requests(self) -> List[HumanRequest]:
        """Obtiene solicitudes pendientes"""
        return [
            req for req in self.requests.values()
            if req.status == RequestStatus.PENDING
        ]
    
    def get_request(self, request_id: str) -> Optional[HumanRequest]:
        """Obtiene solicitud por ID"""
        return self.requests.get(request_id)
    
    def get_all_requests(self, status: Optional[RequestStatus] = None) -> List[HumanRequest]:
        """Obtiene todas las solicitudes, opcionalmente filtradas por estado"""
        if status:
            return [req for req in self.requests.values() if req.status == status]
        return list(self.requests.values())
