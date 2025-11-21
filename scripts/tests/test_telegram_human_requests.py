"""
Test de integración Telegram + HumanRequests
Prueba el flujo completo de notificaciones
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.congress.human_request import HumanRequestManager, RequestType
from app.integrations.telegram_bot import CongressTelegramBot
import asyncio
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MockCongress:
    """Mock del congreso para testing"""
    def get_status(self):
        return {
            'generation': 1,
            'total_experiments': 0,
            'improvements_implemented': 0,
            'paused': False,
            'last_experiment': 'Ninguno',
            'avg_improvement': 0
        }
    
    def get_recent_experiments(self, limit=5):
        return []
    
    def assign_manual_task(self, description, requested_by):
        return f"task_{hash(description) % 10000}"
    
    def pause(self):
        pass
    
    def resume(self):
        pass


async def test_telegram_integration():
    """
    Test completo de integración
    
    NOTA: Requiere TELEGRAM_TOKEN y TELEGRAM_CHAT_ID en .env
    """
    
    print("=" * 60)
    print("TEST: Telegram + HumanRequests Integration")
    print("=" * 60)
    
    # 1. Crear bot de Telegram
    print("\n1️⃣  Inicializando bot de Telegram...")
    try:
        mock_congress = MockCongress()
        bot = CongressTelegramBot(mock_congress)
        print("✅ Bot inicializado")
    except ValueError as e:
        print(f"❌ Error: {e}")
        print("💡 Asegúrate de tener TELEGRAM_TOKEN y TELEGRAM_CHAT_ID en .env")
        return
    
    # 2. El bot ya tiene HumanRequestManager integrado
    request_manager = bot.human_request_manager
    print("✅ HumanRequestManager integrado")
    
    # 3. Crear solicitud de prueba
    print("\n2️⃣  Creando solicitud de prueba...")
    request = request_manager.create_request(
        request_type=RequestType.PAYMENT,
        title="Comprar dominio d8-ai.com",
        description=(
            "El congreso detectó que necesitamos un dominio para el proyecto.\n\n"
            "**Razón:** Niche discovery identificó oportunidad en mercado AI\n"
            "**ROI Estimado:** +300% en 6 meses\n"
            "**Urgencia:** Media (necesario antes de lanzar MVP)\n\n"
            "**Recomendación:** Comprar en Namecheap (acepta PayPal)"
        ),
        estimated_cost=12.99,
        priority=7,
        created_by="NicheDiscovery"
    )
    
    print(f"✅ Solicitud creada: {request.request_id}")
    
    # 4. Enviar notificación por Telegram
    print("\n3️⃣  Enviando notificación por Telegram...")
    print("   (Deberías recibir un mensaje en tu Telegram)")
    
    # Esperar a que se envíe la notificación
    await asyncio.sleep(2)
    
    # 5. Simular comandos de Leo
    print("\n4️⃣  Comandos disponibles para Leo:")
    print(f"   /solicitudes - Ver solicitudes pendientes")
    print(f"   /aprobar {request.request_id} - Aprobar esta solicitud")
    print(f"   /rechazar {request.request_id} muy caro - Rechazar")
    print(f"   /posponer {request.request_id} - Posponer para después")
    
    # 6. Simular aprobación (manual por Leo)
    print("\n5️⃣  Esperando acción de Leo...")
    print("   (En producción, Leo usa los comandos de Telegram)")
    print("   Para este test, simularemos aprobación automática en 3 segundos...")
    
    await asyncio.sleep(3)
    
    # Simular aprobación
    approved = request_manager.approve_request(request.request_id, "Leo (test)")
    if approved:
        print(f"✅ Solicitud aprobada por Leo")
    
    # 7. Listar solicitudes pendientes
    print("\n6️⃣  Estado de solicitudes:")
    all_requests = request_manager.get_all_requests()
    for req in all_requests:
        status_icon = {
            "pending": "⏳",
            "approved": "✅",
            "rejected": "❌",
            "completed": "✔️",
            "cancelled": "🚫"
        }.get(req.status.value, "❓")
        
        print(f"   {status_icon} {req.request_id}: {req.title} - {req.status.value}")
    
    print("\n7️⃣  Test completado!")
    print("\n💡 NOTA: En producción, Leo respondería con comandos de Telegram.")
    print("   Este test solo verificó la integración básica.")
    
    # Limpiar (comentar si quieres mantener la solicitud de prueba)
    # request_manager.reject_request(request.request_id, "Leo", "Test completado")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    try:
        asyncio.run(test_telegram_integration())
    except KeyboardInterrupt:
        print("\n\n🛑 Test interrumpido por usuario")
    except Exception as e:
        print(f"\n\n❌ Error en test: {e}")
        import traceback
        traceback.print_exc()
