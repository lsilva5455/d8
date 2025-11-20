# 💬 Telegram Bot - Quick Start

## Setup Rápido

### 1. Obtener credenciales

```bash
# En Telegram:
# 1. Habla con @BotFather → /newbot → Nombra: "D8CongressBot"
# 2. Copia el token
# 3. Habla con @userinfobot → /start → Copia tu Chat ID
```

### 2. Configurar .env

```bash
TELEGRAM_TOKEN="tu_token_aqui"
TELEGRAM_CHAT_ID="tu_chat_id_aqui"
```

### 3. Instalar dependencia

```powershell
pip install python-telegram-bot==20.7
```

### 4. Lanzar

```powershell
python scripts/launch_congress_telegram.py
```

## Uso

En Telegram, envía:

```
/start          → Inicio
/status         → Estado del congreso
/experiments    → Experimentos recientes
/task <desc>    → Asignar tarea
/stop           → Pausar congreso
/resume         → Reanudar
/help           → Ayuda
```

O escribe directamente:
- "¿Qué está haciendo el congreso?"
- "Optimiza los prompts para SEO"
- "Investiga nuevos modelos de IA"

## Documentación Completa

Ver: `docs/03_operaciones/telegram_integration.md`

## Arquitectura

```
Leo (Telegram) ←→ CongressTelegramBot ←→ AutonomousCongress
                     (app/integrations/)    (scripts/)
```

**Principio:** Autonomía por defecto, oversight opcional.

El congreso opera 100% autónomo. Leo recibe notificaciones y puede intervenir cuando sea necesario.
