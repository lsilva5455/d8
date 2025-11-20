# 🤖 D8 Daemons - Sistema Autónomo FASE 3

Daemons que ejecutan los tres subsistemas principales de D8 de forma autónoma 24/7.

---

## 📋 Daemons Disponibles

### 1. 🔬 Niche Discovery Daemon

**Archivo:** `niche_discovery_daemon.py`  
**Frecuencia:** Cada 24 horas  
**Puerto:** N/A (sin HTTP)

**Función:**
- Analiza 3 mercados: USA, Spain, Chile
- Descubre nichos rentables con ROI > 20%
- Prioriza por ROI estimado
- Guarda resultados en `data/niche_discovery/`

**Uso:**
```bash
python scripts/daemons/niche_discovery_daemon.py
```

**Logs:** `data/logs/niche_discovery_daemon.log`

---

### 2. 🏛️ Congress Daemon

**Archivo:** `congress_daemon.py`  
**Frecuencia:** Cada 1 hora  
**Puerto:** N/A (sin HTTP)

**Función:**
- Ejecuta ciclos de mejora continua
- Valida mejoras con threshold > 10%
- Implementa mejoras aprobadas automáticamente
- Guarda resultados en `data/congress_cycles/`

**Uso:**
```bash
python scripts/daemons/congress_daemon.py
```

**Logs:** `data/logs/congress_daemon.log`

---

### 3. 🧬 Evolution Daemon

**Archivo:** `evolution_daemon.py`  
**Frecuencia:** Cada 7 días  
**Puerto:** N/A (sin HTTP)

**Función:**
- Evalúa fitness de población actual
- Selección natural (top 30% sobrevive)
- Reproducción con mutación/crossover
- Guarda genomas en `data/generations/`
- Distribuye revenue 40/40/20

**Uso:**
```bash
python scripts/daemons/evolution_daemon.py
```

**Logs:** `data/logs/evolution_daemon.log`

---

## 🚀 Lanzamiento

### Sistema Completo

Inicia todos los daemons + monitoring + self-healing:

```bash
python scripts/launch/start_autonomous_system.py
```

Esto inicia:
1. Niche Discovery Daemon
2. Congress Daemon
3. Evolution Daemon
4. Monitoring Dashboard (puerto 7500)
5. Self-Healing Monitor

### Componentes Individuales

```bash
# Solo un daemon específico
python scripts/daemons/niche_discovery_daemon.py
python scripts/daemons/congress_daemon.py
python scripts/daemons/evolution_daemon.py
```

---

## 📊 Monitoreo

### Dashboard Web

URL: http://localhost:7500

**Características:**
- Vista en tiempo real del estado del sistema
- Métricas de cada subsistema
- Auto-refresh cada 30 segundos
- API REST disponible

### API Endpoints

```bash
# Status completo del sistema
curl http://localhost:7500/api/status

# Lista de agentes
curl http://localhost:7500/api/agents

# Health check
curl http://localhost:7500/health
```

---

## 📝 Logs y Datos

### Estructura de Directorios

```
data/
├── logs/                          # Logs de daemons
│   ├── niche_discovery_daemon.log
│   ├── congress_daemon.log
│   ├── evolution_daemon.log
│   └── self_healing.log
│
├── niche_discovery/               # Resultados de descubrimiento
│   └── discovery_YYYYMMDD_HHMMSS.json
│
├── congress_cycles/               # Resultados de ciclos
│   └── cycle_YYYYMMDD_HHMMSS.json
│
├── generations/                   # Genomas de generaciones
│   └── gen_N_YYYYMMDD_HHMMSS/
│       └── agent_XXX.json
│
└── incidents/                     # Incidentes de self-healing
    └── INC_YYYYMMDD_HHMMSS_XXX.json
```

---

## 🛡️ Self-Healing

El sistema incluye auto-recuperación automática:

### Checks Realizados

| Check | Frecuencia | Acción |
|-------|-----------|---------|
| Workers Health | 5 min | Restart automático |
| Agents Errors | 5 min | Rollback a versión estable |
| Budget Usage | 15 min | Throttling automático |
| Health Report | 1 hora | Reporte completo |

### Incidentes

Todos los incidentes se registran en `data/incidents/` con:
- Timestamp
- Tipo de incidente
- Acción tomada
- Datos relevantes

---

## 🧪 Testing

### Validación Completa

```bash
# Test de validación de FASE 3
python scripts/tests/test_fase3_validation.py
```

Verifica:
- ✅ Todos los archivos existen
- ✅ Sintaxis Python correcta
- ✅ Directorios creados
- ✅ Documentación completa

### Test Manual de Daemons

```bash
# 1. Test Niche Discovery (esperar 30 segundos)
python scripts/daemons/niche_discovery_daemon.py
# Ctrl+C después de ver resultados

# 2. Verificar resultados
ls data/niche_discovery/
cat data/niche_discovery/discovery_*.json

# 3. Test Congress (esperar 1 minuto)
python scripts/daemons/congress_daemon.py
# Ctrl+C

# 4. Test Dashboard
python app/monitoring/dashboard.py &
curl http://localhost:7500/api/status
```

---

## ⚙️ Configuración

### Variables de Entorno

```bash
# .env
GROQ_API_KEY=gsk_...           # Para Niche Discovery y Congress
```

### Ajustar Schedules

Para testing, modificar frecuencias en el código:

```python
# En niche_discovery_daemon.py
schedule.every(24).hours.do(run_discovery)
# Cambiar a:
schedule.every(1).hours.do(run_discovery)  # Testing
```

---

## 🐛 Troubleshooting

### Daemon no inicia

```bash
# Verificar sintaxis
python -m py_compile scripts/daemons/niche_discovery_daemon.py

# Verificar dependencias
pip install schedule
```

### No genera resultados

```bash
# Verificar logs
tail -f data/logs/niche_discovery_daemon.log

# Verificar permisos de directorios
ls -la data/
```

### Dashboard no responde

```bash
# Verificar puerto
netstat -an | grep 7500

# Verificar proceso
ps aux | grep dashboard.py
```

---

## 📚 Documentación Relacionada

- **FASE 3 Report:** `docs/07_reportes/FASE_3_IMPLEMENTADA.md`
- **Roadmap:** `docs/01_arquitectura/ROADMAP_7_FASES.md`
- **Monitoring:** Dashboard web en puerto 7500
- **Self-Healing:** `app/self_healing/monitor.py`

---

## 🎯 Next Steps

1. **Validar en producción**
   - Desplegar en servidor 24/7
   - Monitorear 7 días continuos
   - Validar auto-recuperación

2. **Conectar sistemas reales**
   - Integrar con D8Credits
   - Usar Darwin real
   - Implementar asignación de agentes

3. **Optimización**
   - Ajustar thresholds según métricas reales
   - Optimizar schedules
   - Mejorar logging

---

**Última actualización:** 2025-11-20  
**Estado:** ✅ FASE 3 IMPLEMENTADA
