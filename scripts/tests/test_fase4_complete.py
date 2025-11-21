#!/usr/bin/env python3
"""
🧪 FASE 4 - Módulo de Prueba Completo
Demuestra integración de Master-Slave con gestión de solicitudes humanas

Escenarios de prueba:
1. Registro de slave local (localhost)
2. Health check y verificación de versiones
3. Ejecución de tarea simple
4. Simulación de solicitud de pago (requiere intervención humana)
5. Flujo completo: Niche Discovery → Detecta oportunidad → Solicita dominio
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import time
import logging
from app.distributed.slave_manager import SlaveManager
from app.distributed.slave_server import app as slave_app
from app.congress.human_request import HumanRequestManager, RequestType
import threading
import os

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def start_local_slave_server():
    """Inicia slave server en thread separado para testing"""
    def run_server():
        slave_app.run(host="127.0.0.1", port=7600, debug=False, use_reloader=False)
    
    thread = threading.Thread(target=run_server, daemon=True)
    thread.start()
    logger.info("🚀 Slave server iniciado en localhost:7600")
    time.sleep(2)  # Esperar que inicie


def test_1_register_slave():
    """Test 1: Registrar slave local"""
    print("\n" + "="*60)
    print("TEST 1: REGISTRO DE SLAVE")
    print("="*60)
    
    manager = SlaveManager()
    
    # Registrar localhost como slave
    success = manager.register_slave(
        slave_id="slave-local-test",
        host="127.0.0.1",
        port=7600,
        install_method="python"
    )
    
    if success:
        print("✅ Slave registrado exitosamente")
    else:
        print("❌ Error registrando slave")
    
    return manager


def test_2_health_check(manager: SlaveManager):
    """Test 2: Health check y verificación de versiones"""
    print("\n" + "="*60)
    print("TEST 2: HEALTH CHECK Y VERSIONES")
    print("="*60)
    
    slave_id = "slave-local-test"
    
    print(f"\n🔍 Verificando health de {slave_id}...")
    is_healthy = manager.check_health(slave_id)
    
    if is_healthy:
        print("✅ Slave está saludable")
        
        slave_data = manager.slaves[slave_id]
        print(f"\n📊 Información del slave:")
        print(f"   Host: {slave_data['host']}:{slave_data['port']}")
        print(f"   Status: {slave_data['status']}")
        print(f"   Commit: {slave_data.get('commit', 'unknown')}")
        print(f"   Última conexión: {slave_data.get('last_seen', 'never')}")
        
        if slave_data.get('version_mismatch', False):
            print(f"   ⚠️  DESINCRONIZACIÓN DE VERSIÓN DETECTADA")
            print(f"   Master: {manager.master_version}")
            print(f"   Slave:  {slave_data.get('commit', 'unknown')}")
        else:
            print(f"   ✅ Versión sincronizada con master")
    else:
        print("❌ Slave no responde o está unhealthy")


def test_3_execute_simple_task(manager: SlaveManager):
    """Test 3: Ejecutar tarea simple"""
    print("\n" + "="*60)
    print("TEST 3: EJECUCIÓN DE TAREA SIMPLE")
    print("="*60)
    
    slave_id = "slave-local-test"
    
    # Tarea simple: calcular fibonacci
    task = {
        "type": "custom",
        "command": """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

import json
result = [fibonacci(i) for i in range(10)]
print(json.dumps({'success': True, 'result': result}))
"""
    }
    
    print(f"\n🔄 Ejecutando tarea en {slave_id}...")
    result = manager.execute_remote_task(slave_id, task)
    
    if result and result.get('success'):
        print(f"✅ Tarea ejecutada exitosamente")
        print(f"   Método: {result.get('method', 'unknown')}")
        print(f"   Output: {result.get('output', '')[:200]}...")
    else:
        print(f"❌ Error ejecutando tarea")
        if result:
            print(f"   Error: {result.get('error', 'unknown')}")


def test_4_human_request_payment():
    """Test 4: Solicitud de pago (requiere intervención humana)"""
    print("\n" + "="*60)
    print("TEST 4: SOLICITUD DE PAGO HUMANO")
    print("="*60)
    
    request_manager = HumanRequestManager()
    
    # Simular: Congreso detecta necesidad de dominio
    print("\n🏛️  Congreso detectó oportunidad de nicho:")
    print("   Nicho: AI Tools Reviews")
    print("   ROI estimado: 35%")
    print("   Necesita: dominio d8-ai-tools.com")
    print("\n🤖 Congreso intenta automatizar compra...")
    print("   ❌ No hay API de Namecheap configurada")
    print("   ❌ Requiere tarjeta de crédito")
    print("   ❌ Requiere verificación humana")
    print("\n📋 Congreso crea solicitud humana...")
    
    request = request_manager.create_request(
        request_type=RequestType.PAYMENT,
        title="Comprar dominio d8-ai-tools.com",
        description="""Congreso detectó nicho rentable: AI Tools Reviews

**ROI estimado:** 35%
**Demanda:** Alta
**Competencia:** Media

**Acción requerida:**
1. Comprar dominio: d8-ai-tools.com
2. Proveedor sugerido: Namecheap
3. Renovación: 1 año

**Siguiente paso después de compra:**
- Configurar DNS
- Instalar WordPress
- Generar contenido inicial
""",
        estimated_cost=15.0,
        priority=7,
        created_by="Congress-NicheDiscovery"
    )
    
    print(f"✅ Solicitud creada: {request.request_id}\n")
    
    # Mostrar mensaje de Telegram
    print("📱 MENSAJE PARA TELEGRAM:")
    print("-" * 60)
    print(request.to_telegram_message())
    print("-" * 60)
    
    return request_manager, request


def test_5_approval_flow(request_manager: HumanRequestManager, request):
    """Test 5: Flujo de aprobación"""
    print("\n" + "="*60)
    print("TEST 5: FLUJO DE APROBACIÓN")
    print("="*60)
    
    print(f"\n👤 Leo recibe notificación en Telegram")
    print(f"📝 Leo revisa solicitud {request.request_id}")
    print(f"💭 Leo decide: APROBAR\n")
    
    # Simular aprobación
    success = request_manager.approve_request(
        request.request_id,
        notes="Aprobado. Nicho tiene buen potencial."
    )
    
    if success:
        print(f"✅ Solicitud {request.request_id} aprobada")
    
    # Simular que Leo compró el dominio
    print(f"\n🛒 Leo compra dominio en Namecheap...")
    time.sleep(1)  # Simular tiempo de compra
    print(f"💳 Pago procesado: $14.88")
    
    # Leo confirma completación
    success = request_manager.complete_request(
        request.request_id,
        actual_cost=14.88,
        notes="Dominio comprado. DNS configurado apuntando a 192.168.1.100"
    )
    
    if success:
        print(f"✅ Solicitud {request.request_id} completada")
        print(f"📊 Costo real: $14.88")
    
    print(f"\n🤖 Sistema continúa automáticamente:")
    print(f"   → Instalar WordPress en slave")
    print(f"   → Generar contenido inicial")
    print(f"   → Configurar SEO")


def test_6_rejected_request():
    """Test 6: Solicitud rechazada"""
    print("\n" + "="*60)
    print("TEST 6: SOLICITUD RECHAZADA")
    print("="*60)
    
    request_manager = HumanRequestManager()
    
    # Solicitud de API que Leo rechaza
    print("\n🏛️  Congreso solicita API de Claude...")
    
    request = request_manager.create_request(
        request_type=RequestType.API_ACCOUNT,
        title="Crear cuenta en Anthropic (Claude API)",
        description="""Congreso quiere probar Claude 3.5 Sonnet para optimización.

**Beneficio esperado:** +15% en calidad de respuestas
**Costo estimado:** $20/mes

¿Aprobar?
""",
        estimated_cost=20.0,
        priority=5,
        created_by="Congress-Optimizer"
    )
    
    print(f"✅ Solicitud creada: {request.request_id}\n")
    
    # Leo rechaza
    print(f"👤 Leo revisa y decide: RECHAZAR")
    print(f"💭 Razón: Ya tenemos Groq y Gemini, no justifica costo adicional\n")
    
    success = request_manager.reject_request(
        request.request_id,
        reason="No justificado. Usar Groq y Gemini existentes."
    )
    
    if success:
        print(f"❌ Solicitud {request.request_id} rechazada")
        print(f"🤖 Sistema continúa sin Claude API")


def test_7_pending_requests_summary(request_manager: HumanRequestManager):
    """Test 7: Resumen de solicitudes pendientes"""
    print("\n" + "="*60)
    print("TEST 7: RESUMEN DE SOLICITUDES")
    print("="*60)
    
    pending = request_manager.get_pending_requests()
    approved = request_manager.get_all_requests(status=None)
    
    print(f"\n📊 ESTADÍSTICAS:")
    print(f"   Total de solicitudes: {len(approved)}")
    print(f"   Pendientes: {len(pending)}")
    print(f"   Completadas: {len([r for r in approved if r.status.value == 'completed'])}")
    print(f"   Rechazadas: {len([r for r in approved if r.status.value == 'rejected'])}")
    
    if pending:
        print(f"\n⏳ SOLICITUDES PENDIENTES:")
        for req in pending:
            print(f"\n   {req.request_id}: {req.title}")
            print(f"   Prioridad: {req.priority}/10")
            print(f"   Creado: {req.created_at.strftime('%Y-%m-%d %H:%M')}")
            if req.estimated_cost:
                print(f"   Costo estimado: ${req.estimated_cost:.2f}")


def main():
    """Ejecuta todos los tests"""
    print("\n" + "="*60)
    print("🧪 FASE 4 - MÓDULO DE PRUEBA COMPLETO")
    print("="*60)
    print("\nEste módulo demuestra:")
    print("✅ Registro y gestión de slaves")
    print("✅ Health checks y verificación de versiones")
    print("✅ Ejecución remota de tareas")
    print("✅ Solicitudes humanas (pagos, decisiones)")
    print("✅ Flujo Congreso → Intenta automatizar → Notifica Leo")
    print("\n" + "="*60)
    
    # Configurar token (en producción usar .env)
    os.environ["SLAVE_TOKEN"] = "test-token-123"
    
    try:
        # Iniciar slave server local
        start_local_slave_server()
        
        # Test 1: Registrar slave
        manager = test_1_register_slave()
        
        # Test 2: Health check
        test_2_health_check(manager)
        
        # Test 3: Ejecutar tarea simple
        test_3_execute_simple_task(manager)
        
        # Test 4: Solicitud de pago
        request_manager, request = test_4_human_request_payment()
        
        # Test 5: Aprobar y completar
        test_5_approval_flow(request_manager, request)
        
        # Test 6: Solicitud rechazada
        test_6_rejected_request()
        
        # Test 7: Resumen
        test_7_pending_requests_summary(request_manager)
        
        print("\n" + "="*60)
        print("✅ TODOS LOS TESTS COMPLETADOS")
        print("="*60)
        
        print("\n📁 Archivos generados:")
        print(f"   ~/Documents/d8_data/slaves/config.json")
        print(f"   ~/Documents/d8_data/human_requests/requests.json")
        
        print("\n🎯 PRÓXIMOS PASOS:")
        print("1. Instalar slave en máquina remota")
        print("2. Configurar Telegram para recibir solicitudes")
        print("3. Integrar con Darwin, Niche Discovery, Congreso")
        print("4. Probar con caso real de monetización")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrumpido por usuario")
    except Exception as e:
        print(f"\n\n❌ Error en tests: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
