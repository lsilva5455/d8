# 💬 Telegram Integration - Leo's Congress Interface

**Fecha:** 2025-11-20  
**Propósito:** Interfaz de comunicación entre Leo y el Congreso Autónomo  
**Principio:** Autonomía por defecto, oversight opcional

---

## 🎯 Visión General

El sistema Telegram permite a Leo comunicarse con el Congreso Autónomo mientras se respeta el principio fundamental de D8: **cero intervención humana**.

### ¿Cómo funciona?

1. **Por defecto:** Congreso opera 100% autónomamente
2. **Notificaciones:** Leo recibe updates de cambios importantes
3. **Consultas:** Leo puede preguntar estado cuando quiera
4. **Tareas manuales:** Leo puede asignar investigaciones específicas
5. **Control:** Leo puede pausar/reanudar si es crítico

**Analogía:** Como tener una cámara de seguridad con alarmas. Normalmente no intervienes, pero puedes ver qué pasa y actuar si es necesario.

---

## 🚀 Setup

### 1. Obtener Token de Telegram

```bash
# 1. Habla con @BotFather en Telegram
# 2. Crea nuevo bot: /newbot
# 3. Nombra tu bot: "D8CongressBot"
# 4. Copia el token que te da
```

### 2. Obtener Chat ID

```bash
# 1. Busca @userinfobot en Telegram
# 2. Envíale /start
# 3. Te dará tu Chat ID (número)
```

### 3. Configurar .env

Edita `c:\Users\PcDos\d8\.env`:

```bash
# Telegram Bot (Leo's Congress Interface)
TELEGRAM_TOKEN="tu_token_aqui"
TELEGRAM_CHAT_ID="tu_chat_id_aqui"
```

### 4. Instalar Dependencias

```powershell
pip install python-telegram-bot==20.7
```

### 5. Lanzar Sistema

```powershell
python scripts/launch_congress_telegram.py
```

---

## 📱 Comandos Disponibles

### Consultas

| Comando | Descripción | Ejemplo |
|---------|-------------|---------|
| `/start` | Mensaje de bienvenida | `/start` |
| `/status` | Estado actual del congreso | `/status` |
| `/experiments` | Experimentos recientes | `/experiments` |
| `/help` | Ayuda y lista de comandos | `/help` |

### Control

| Comando | Descripción | Ejemplo |
|---------|-------------|---------|
| `/task <descripción>` | Asignar tarea específica | `/task Optimizar prompts para SEO` |
| `/approve` | Toggle aprobación manual | `/approve` |
| `/stop` | Pausar congreso | `/stop` |
| `/resume` | Reanudar congreso | `/resume` |

### Lenguaje Natural

También puedes escribir directamente:

```
"¿Qué está haciendo el congreso?"
"Optimiza los prompts para mejor conversión"
"¿Cuántas mejoras se han implementado?"
"Investiga nuevos modelos de IA"
```

El bot interpreta intención y responde apropiadamente.

---

## 💡 Ejemplos de Uso

### Ejemplo 1: Consulta rápida de estado

**Leo:**
```
/status
```

**Bot:**
```
📊 ESTADO DEL CONGRESO

🔄 Generación: 5
🧪 Experimentos totales: 42
✅ Mejoras implementadas: 15
⏸️ Estado: ACTIVO

Último experimento:
Optimización de prompts para niche discovery

Mejora promedio: 12.5%
```

### Ejemplo 2: Asignar tarea específica

**Leo:**
```
/task Investigar uso de RAG para mejorar contexto de agentes
```

**Bot:**
```
✅ Tarea asignada al congreso

ID: task_8472
Descripción: Investigar uso de RAG para mejorar contexto de agentes

El congreso comenzará a trabajar en esto.
Te notificaré cuando complete la investigación.
```

### Ejemplo 3: Notificación automática

**Bot (sin solicitud de Leo):**
```
✅ Mejora implementada automáticamente

Experimento: Optimización de prompts con few-shot examples
Mejora: 18.3%
Descripción: Se agregaron 3 ejemplos a prompts de researcher

Cambios aplicados al sistema.
```

### Ejemplo 4: Modo manual (si Leo quiere aprobar)

**Leo:**
```
/approve
```

**Bot:**
```
🔄 Modo de aprobación cambiado a: MANUAL

El congreso esperará tu aprobación antes de implementar cambios.
Te enviaré propuestas para que las revises.
```

Luego cuando el congreso tenga una propuesta:

**Bot:**
```
🔔 APROBACIÓN REQUERIDA

Experimento: Cambio a modelo Mixtral 8x22B
Mejora esperada: 25.0%
Descripción: Upgrade a modelo más potente

Cambios propuestos:
- app/config.py: groq_model = "mixtral-8x22b"
- Costo estimado: +$0.002 por request

¿Aprobar implementación?

[✅ Aprobar] [❌ Rechazar]
```

**Leo:** Presiona "✅ Aprobar"

**Bot:**
```
✅ Experimento exp_12345 aprobado.
El congreso implementará los cambios.
```

### Ejemplo 5: Pausar congreso en emergencia

**Leo:**
```
/stop
```

**Bot:**
```
⏸️ Congreso pausado

El congreso detendrá ejecución automática.
Experimentos en curso se completarán pero no se iniciarán nuevos.

Usa /resume para reanudar.
```

**Logs del congreso:**
```
⏸️  Congreso pausado por Leo. Esperando reanudación...
```

**Leo:** (resuelve el problema)
```
/resume
```

**Bot:**
```
▶️ Congreso reanudado

El congreso continuará con ejecución automática.
```

**Logs del congreso:**
```
▶️  Congreso reanudado. Continuando...
🔄 CICLO 6/∞
```

---

## 🏗️ Arquitectura

### Componentes

```
┌─────────────────────────────────────────────┐
│  AutonomousCongress                         │
│  (scripts/autonomous_congress.py)           │
│                                             │
│  - Ejecuta ciclos autónomamente             │
│  - Investiga, experimenta, valida           │
│  - Implementa mejoras aprobadas             │
│  - Puede ser pausado/reanudado              │
└──────────────┬──────────────────────────────┘
               │
               │ set_telegram_bot()
               │ get_status()
               │ assign_manual_task()
               │
               ▼
┌─────────────────────────────────────────────┐
│  CongressTelegramBot                        │
│  (app/integrations/telegram_bot.py)         │
│                                             │
│  - Maneja comandos de Telegram              │
│  - Envía notificaciones a Leo               │
│  - Interpreta lenguaje natural              │
│  - Request approval si modo manual          │
└──────────────┬──────────────────────────────┘
               │
               │ Telegram Bot API
               │
               ▼
┌─────────────────────────────────────────────┐
│  Leo (Telegram Chat)                        │
│                                             │
│  - Recibe notificaciones                    │
│  - Envía comandos                           │
│  - Conversa en lenguaje natural             │
└─────────────────────────────────────────────┘
```

### Flujo de Ejecución

```
┌────────────────────────────────────────────┐
│  INICIO DEL SISTEMA                        │
│  launch_congress_telegram.py               │
└──────────────┬─────────────────────────────┘
               │
               ├──> Thread 1: Telegram Bot (async)
               │    └─> Escucha comandos de Leo
               │
               └──> Thread 2: Congress Loop (sync)
                    └─> Ejecuta ciclos autónomos
                         │
                         ├─> Research
                         ├─> Design
                         ├─> Execute
                         ├─> Validate
                         ├─> Implement ──┐
                         │               │
                         │               ▼
                         │    ┌──────────────────┐
                         │    │ Notificar a Leo? │
                         │    └──────────────────┘
                         │               │
                         │               ▼
                         │    ┌──────────────────────┐
                         │    │ Modo automático?     │
                         │    └──────────────────────┘
                         │         │            │
                         │        SÍ           NO
                         │         │            │
                         │         ▼            ▼
                         │    Implementar   Esperar
                         │                  aprobación
                         │
                         └──> Sleep 1 hora → Repetir
```

---

## 🔧 Configuración Avanzada

### Modo Automático vs Manual

**Automático (default):**
```python
self.auto_approve = True
```
- Congreso implementa cambios automáticamente
- Leo recibe notificaciones informativas
- No espera aprobación

**Manual:**
```python
self.auto_approve = False
```
- Congreso espera aprobación de Leo
- Leo recibe botones Aprobar/Rechazar
- Cambios solo se aplican si Leo aprueba

**Toggle:** `/approve` en Telegram

### Personalizar Notificaciones

Edita `app/integrations/telegram_bot.py`:

```python
async def request_approval(self, experiment: Dict[str, Any]) -> bool:
    # Personaliza umbral de notificación
    if experiment.get('improvement', 0) < 5:
        # Mejoras < 5% no notificar
        return self.auto_approve
    
    # Notificar solo si mejora > 5%
    await self.notify_leo(...)
```

### Integrar con Otros Sistemas

```python
# En app/main.py o donde corresponda
from app.integrations.telegram_bot import CongressTelegramBot

bot = CongressTelegramBot(congress_instance)

# Enviar notificaciones custom
await bot.notify_leo(
    "🚨 Sistema detectó anomalía en worker-3"
)
```

---

## 🧪 Testing

### Test Manual

1. Lanzar sistema:
```powershell
python scripts/launch_congress_telegram.py
```

2. En Telegram, enviar:
```
/start
/status
/task Test de integración
```

3. Verificar respuestas del bot

### Test Automatizado

```python
# tests/integration/test_telegram_bot.py
import pytest
from app.integrations.telegram_bot import CongressTelegramBot
from scripts.autonomous_congress import AutonomousCongress

def test_status_command():
    congress = AutonomousCongress()
    bot = CongressTelegramBot(congress)
    
    status = congress.get_status()
    assert 'generation' in status
    assert 'total_experiments' in status

def test_assign_task():
    congress = AutonomousCongress()
    task_id = congress.assign_manual_task(
        "Test task",
        "pytest"
    )
    assert task_id.startswith("manual_")
```

---

## 🐛 Troubleshooting

### Bot no responde

**Problema:** Enviaste mensaje pero no hay respuesta.

**Solución:**
1. Verifica que el script esté corriendo
2. Chequea TELEGRAM_CHAT_ID correcto:
   ```powershell
   # Ver valor en .env
   cat .env | Select-String "TELEGRAM_CHAT_ID"
   ```
3. Revisa logs:
   ```powershell
   cat data/logs/congress_telegram.log
   ```

### Notificaciones no llegan

**Problema:** Congreso funciona pero no recibes notificaciones.

**Solución:**
1. Verifica que `set_telegram_bot()` se llamó:
   ```python
   congress.set_telegram_bot(bot)
   ```
2. Chequea que bot esté inicializado:
   ```python
   if self.telegram_bot:
       await self.telegram_bot.notify_leo(...)
   ```

### Error: "Forbidden: bot can't send messages to this user"

**Problema:** Bot no puede enviar mensajes.

**Solución:**
1. Abre chat con tu bot en Telegram
2. Envía `/start` para iniciar conversación
3. Bot necesita que inicies la conversación primero

### Congreso no detecta pause

**Problema:** Enviaste `/stop` pero congreso sigue ejecutando.

**Solución:**
1. El ciclo actual se completa antes de pausar
2. Espera a que termine el ciclo en curso
3. Revisa que `self.paused` se esté checkeando:
   ```python
   if self.paused:
       print("⏸️  Congreso pausado...")
   ```

---

## 📚 Referencias

### Código Fuente

- **Telegram Bot:** `app/integrations/telegram_bot.py`
- **Congress Integration:** `scripts/autonomous_congress.py` (líneas 45-100)
- **Launcher:** `scripts/launch_congress_telegram.py`

### Documentación Externa

- [python-telegram-bot Docs](https://docs.python-telegram-bot.org/)
- [Telegram Bot API](https://core.telegram.org/bots/api)

### Experiencias Relacionadas

- `docs/06_knowledge_base/experiencias_profundas/congreso_autonomo.md`
- `docs/01_arquitectura/VISION_COMPLETA_D8.md` (Sección: Congreso)
- `docs/01_arquitectura/ROADMAP_7_FASES.md` (FASE 3)

---

## 🔮 Próximos Pasos

### FASE 3: Integración Total (Planeado)

1. **Notificaciones Inteligentes**
   - Solo notificar mejoras > umbral configurable
   - Resumen diario de actividad
   - Alertas de degradaciones

2. **Comandos Avanzados**
   - `/history` - Historial completo de experimentos
   - `/rollback <exp_id>` - Revertir cambio específico
   - `/config` - Ver/editar configuración

3. **Análisis de Conversaciones**
   - Leo puede conversar en lenguaje natural
   - Bot interpreta intención con LLM
   - Respuestas contextuales inteligentes

4. **Multi-Usuario** (Si se expande equipo)
   - Roles: Admin, Observer, Contributor
   - Permisos diferenciados
   - Log de quién hizo qué

---

## 📝 Changelog

### 2025-11-20
- ✅ Implementación inicial
- ✅ Comandos básicos (/status, /experiments, /task, /stop, /resume)
- ✅ Modo automático/manual toggle
- ✅ Notificaciones asíncronas
- ✅ Lenguaje natural básico
- ✅ Integration con AutonomousCongress

---

**Última actualización:** 2025-11-20  
**Estado:** ✅ Operacional  
**Principio preservado:** Autonomía total con oversight opcional
