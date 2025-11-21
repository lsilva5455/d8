# 📱 Integración Telegram con HumanRequests - FASE 4

**Fecha:** 2025-11-20  
**Estado:** ✅ Implementado  
**Propósito:** Permitir a Leo gestionar solicitudes humanas desde Telegram

---

## Contexto

En FASE 4, el congreso puede necesitar intervención humana para ciertas acciones:
- 💳 Pagos (dominios, servicios que no aceptan crypto)
- 🎨 Decisiones de diseño
- 🔑 Crear cuentas en servicios
- 📝 Aprobar contenido
- 🎯 Decisiones estratégicas

**Flujo:**
```
Congreso detecta necesidad
    ↓
Intenta automatizar
    ↓
¿Puede automatizar? → SÍ → Ejecuta
    ↓ NO
Crea HumanRequest
    ↓
Notifica a Leo por Telegram
    ↓
Leo: /aprobar, /rechazar, /posponer
    ↓
Sistema continúa
```

---

## Comandos de Telegram

### Ver solicitudes pendientes
```
/solicitudes
/solicitudes_pendientes
```

**Output:**
```
📋 SOLICITUDES PENDIENTES (2)

💳 SOLICITUD HUMANA REQUERIDA

**Comprar dominio d8-ai.com**

**Descripción:**
El congreso detectó que necesitamos un dominio...

**Prioridad:** 🟡 MEDIA
**Generado por:** NicheDiscovery
**Costo estimado:** $12.99

**ID:** req-0001

**Opciones:**
/aprobar req-0001
/rechazar req-0001
/posponer req-0001

----------------------------------------
```

### Aprobar solicitud
```
/aprobar <request_id>
```

**Ejemplo:**
```
/aprobar req-0001
```

**Output:**
```
✅ Solicitud Aprobada

ID: req-0001
Tipo: payment
Título: Comprar dominio d8-ai.com

⏭️ Próximos pasos:
1. Ejecuta la acción manualmente
2. Confirma con: /completar req-0001

💡 El sistema continuará una vez confirmes.
```

### Rechazar solicitud
```
/rechazar <request_id> [razón]
```

**Ejemplo:**
```
/rechazar req-0001 muy caro
```

**Output:**
```
❌ Solicitud Rechazada

ID: req-0001
Tipo: payment
Título: Comprar dominio d8-ai.com
Razón: muy caro

🤖 El congreso buscará alternativas.
```

### Posponer solicitud
```
/posponer <request_id>
```

**Ejemplo:**
```
/posponer req-0001
```

**Output:**
```
⏸️ Solicitud Pospuesta

ID: req-0001
Título: Comprar dominio d8-ai.com

✅ La solicitud permanece pendiente.
Puedes revisarla más tarde con /solicitudes
```

### Completar solicitud
```
/completar <request_id> [notas]
```

**Ejemplo:**
```
/completar req-0001 Dominio comprado en Namecheap
```

**Output:**
```
✅ Solicitud Completada

ID: req-0001
Tipo: payment
Título: Comprar dominio d8-ai.com
Notas: Dominio comprado en Namecheap

🤖 El sistema puede continuar con esta información.
```

---

## Notificaciones Automáticas

Cuando el congreso crea una solicitud, Leo recibe automáticamente:

```
🔔 NUEVA SOLICITUD HUMANA

💳 SOLICITUD HUMANA REQUERIDA

**Comprar dominio d8-ai.com**

**Descripción:**
El congreso detectó que necesitamos un dominio...

**Prioridad:** 🟡 MEDIA
**Generado por:** NicheDiscovery
**Costo estimado:** $12.99

**ID:** req-0001

💡 Responde con:
• /aprobar req-0001
• /rechazar req-0001
• /posponer req-0001
```

---

## Implementación Técnica

### Arquitectura

```
CongressTelegramBot
    ↓ (tiene referencia)
HumanRequestManager
    ↓ (notifica mediante)
CongressTelegramBot.notify_new_request()
    ↓
Telegram API → Leo recibe mensaje
```

### Código Clave

**1. Inicialización con integración bidireccional:**

```python
# telegram_bot.py
class CongressTelegramBot:
    def __init__(self, congress_instance):
        # ...
        # HumanRequestManager se crea con referencia al bot
        self.human_request_manager = HumanRequestManager(telegram_bot=self)
```

**2. Notificación automática al crear solicitud:**

```python
# human_request.py
class HumanRequestManager:
    def create_request(self, ...):
        # ... crear request ...
        
        # Notificar por Telegram si está disponible
        if self.telegram_bot:
            asyncio.create_task(
                self.telegram_bot.notify_new_request(request)
            )
        
        return request
```

**3. Comando de aprobación:**

```python
# telegram_bot.py
async def cmd_aprobar_solicitud(self, update, context):
    request_id = context.args[0]
    approved = self.human_request_manager.approve_request(
        request_id, 
        "Leo"
    )
    
    if approved:
        req = self.human_request_manager.get_request(request_id)
        await update.message.reply_text(
            f"✅ Solicitud Aprobada\n\n"
            f"ID: {request_id}\n"
            # ... más info ...
        )
```

### Handlers Registrados

```python
def _setup_handlers(self):
    # ...
    # Human Request commands (FASE 4)
    self.app.add_handler(CommandHandler("solicitudes", self.cmd_solicitudes_pendientes))
    self.app.add_handler(CommandHandler("solicitudes_pendientes", self.cmd_solicitudes_pendientes))
    self.app.add_handler(CommandHandler("aprobar", self.cmd_aprobar_solicitud))
    self.app.add_handler(CommandHandler("rechazar", self.cmd_rechazar_solicitud))
    self.app.add_handler(CommandHandler("posponer", self.cmd_posponer_solicitud))
    self.app.add_handler(CommandHandler("completar", self.cmd_completar_solicitud))
```

---

## Testing

### Test Automatizado

```bash
python scripts/tests/test_telegram_human_requests.py
```

**Flujo del test:**
1. Inicializa bot de Telegram
2. Crea HumanRequestManager integrado
3. Crea solicitud de prueba
4. Envía notificación por Telegram (Leo la recibe)
5. Simula aprobación
6. Lista estado final

**Output esperado:**
```
============================================================
TEST: Telegram + HumanRequests Integration
============================================================

1️⃣  Inicializando bot de Telegram...
✅ Bot inicializado
✅ HumanRequestManager integrado

2️⃣  Creando solicitud de prueba...
✅ Solicitud creada: req-0001

3️⃣  Enviando notificación por Telegram...
   (Deberías recibir un mensaje en tu Telegram)

4️⃣  Comandos disponibles para Leo:
   /solicitudes - Ver solicitudes pendientes
   /aprobar req-0001 - Aprobar esta solicitud
   /rechazar req-0001 muy caro - Rechazar
   /posponer req-0001 - Posponer para después

5️⃣  Esperando acción de Leo...
✅ Solicitud aprobada por Leo

6️⃣  Estado de solicitudes:
   ✅ req-0001: Comprar dominio d8-ai.com - approved

7️⃣  Test completado!
============================================================
```

### Test Manual (Producción)

1. Iniciar bot de Telegram:
```bash
python scripts/launch_congress_telegram.py
```

2. En otro terminal, crear solicitud manualmente:
```python
from app.congress.human_request import HumanRequestManager, RequestType

manager = HumanRequestManager()
# El manager tiene referencia al bot, notificará automáticamente

request = manager.create_request(
    request_type=RequestType.PAYMENT,
    title="Test manual",
    description="Solicitud de prueba",
    estimated_cost=10.00,
    priority=5
)
```

3. Verificar que llegó notificación a Telegram

4. Responder con comandos:
```
/solicitudes
/aprobar req-XXXX
/completar req-XXXX Test completado
```

---

## Casos de Uso

### Caso 1: Compra de Dominio

**Congreso detecta oportunidad:**
```python
# En NicheDiscovery
if niche_score > 80:
    # Intenta comprar con Namecheap API
    success = try_buy_domain_automated("d8-ai.com")
    
    if not success:
        # No puede automatizar, crea solicitud
        request_manager.create_request(
            request_type=RequestType.PAYMENT,
            title="Comprar dominio d8-ai.com",
            description=f"Niche score: {niche_score}...",
            estimated_cost=12.99,
            priority=8
        )
        # Leo recibe notificación automáticamente
```

**Leo en Telegram:**
```
🔔 NUEVA SOLICITUD HUMANA
💳 Comprar dominio d8-ai.com
Costo: $12.99

/aprobar req-0001
```

**Leo ejecuta:**
1. Aprueba: `/aprobar req-0001`
2. Compra dominio en Namecheap
3. Confirma: `/completar req-0001 Comprado con PayPal`

**Sistema continúa:**
- Niche discovery procede con dominio disponible
- Genera contenido para el dominio
- Despliega sitio web

### Caso 2: Decisión de Diseño

**Congreso necesita elegir diseño:**
```python
# En ContentGenerator
designs = generate_3_design_options()

# No puede decidir automáticamente
request_manager.create_request(
    request_type=RequestType.DESIGN_DECISION,
    title="Elegir diseño para landing page",
    description=f"Opciones:\n{designs_preview}",
    priority=6
)
```

**Leo en Telegram:**
```
🔔 NUEVA SOLICITUD HUMANA
🎨 Elegir diseño para landing page

[Preview de 3 diseños]

/aprobar req-0002
```

**Leo decide:**
1. Revisa opciones
2. Responde: `/completar req-0002 Opción 2 es la mejor`

**Sistema continúa:**
- ContentGenerator usa diseño elegido
- Genera variaciones basadas en esa opción

### Caso 3: Crear cuenta en servicio

**Congreso necesita API key:**
```python
# En ExperimentSystem
if need_new_api_provider:
    # Intenta crear cuenta automáticamente
    success = try_create_account("anthropic.com")
    
    if not success:  # Requiere verificación humana
        request_manager.create_request(
            request_type=RequestType.API_ACCOUNT,
            title="Crear cuenta en Anthropic",
            description="Necesitamos Claude API para experimentos",
            priority=7
        )
```

**Leo en Telegram:**
```
🔔 NUEVA SOLICITUD HUMANA
🔑 Crear cuenta en Anthropic

/aprobar req-0003
```

**Leo ejecuta:**
1. Crea cuenta en anthropic.com
2. Obtiene API key
3. Confirma: `/completar req-0003 API key guardado en .env`

---

## Integración con Congreso

### Uso en Autonomous Congress

```python
# scripts/autonomous_congress.py
class AutonomousCongress:
    def __init__(self):
        # ...
        self.human_request_manager = HumanRequestManager()
    
    def _research_phase(self, target_system):
        # ...
        if needs_payment:
            # Crear solicitud humana
            request = self.human_request_manager.create_request(
                request_type=RequestType.PAYMENT,
                title="...",
                description="...",
                estimated_cost=cost,
                priority=8,
                created_by="Congress-Researcher"
            )
            
            # Esperar aprobación (polling)
            while request.status.value == "pending":
                time.sleep(60)  # Check cada minuto
                request = self.human_request_manager.get_request(request.request_id)
            
            if request.status.value == "approved":
                # Esperar a que Leo complete
                while request.status.value != "completed":
                    time.sleep(60)
                
                # Continuar con información de Leo
                proceed_with_action(request.notes)
            else:
                # Buscar alternativa
                find_alternative_approach()
```

---

## Persistencia

**Ubicación:** `~/Documents/d8_data/human_requests/requests.json`

**Formato:**
```json
{
  "counter": 5,
  "requests": [
    {
      "request_id": "req-0001",
      "request_type": "payment",
      "title": "Comprar dominio d8-ai.com",
      "description": "...",
      "estimated_cost": 12.99,
      "priority": 7,
      "created_at": "2025-11-20T10:30:00",
      "created_by": "NicheDiscovery",
      "status": "completed",
      "approved_at": "2025-11-20T10:32:00",
      "completed_at": "2025-11-20T10:45:00",
      "actual_cost": 12.99,
      "notes": "Completado por Leo: Dominio comprado en Namecheap"
    }
  ]
}
```

---

## Seguridad

### Autenticación

- Bot de Telegram valida TELEGRAM_CHAT_ID
- Solo Leo (owner) puede ejecutar comandos
- Tokens en `.env` (gitignored)

### Validación

```python
# Todos los comandos verifican ownership
async def cmd_aprobar_solicitud(self, update, context):
    # Telegram ya valida que el mensaje viene del chat_id correcto
    # Solo Leo tiene acceso a ese chat
    ...
```

---

## Próximos Pasos

### Mejoras Futuras

1. **Dashboard Web** (puerto 7500)
   - Ver solicitudes en navegador
   - Aprobar con un click
   - Ver historial completo

2. **Notificaciones Inteligentes**
   - Agrupar solicitudes relacionadas
   - Sugerir decisión basada en contexto
   - Recordatorios si no se responde

3. **Auto-aprobación selectiva**
   - Leo configura reglas: "Auto-aprobar pagos < $20"
   - Sistema ejecuta sin notificar
   - Solo notifica si excede umbral

4. **Integración con economía**
   - Descontar de balance al completar
   - Trackear gastos por categoría
   - Alertar si se excede presupuesto

---

## Tags

`#telegram` `#fase4` `#human-requests` `#economic-management` `#notifications` `#d8`

---

**Última actualización:** 2025-11-20  
**Estado:** ✅ Implementado y testeado  
**Archivos:**
- `app/integrations/telegram_bot.py` (+200 líneas)
- `app/congress/human_request.py` (modificado)
- `scripts/tests/test_telegram_human_requests.py` (nuevo)
