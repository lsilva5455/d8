# 🧪 Scripts de Pruebas Locales D8

Pruebas completas de las opciones de negocio y análisis de nichos.

## 📋 Tests Disponibles

### 1️⃣ Content Empire Test
**Archivo:** `test_content_empire.py`

Prueba generación de contenido para diferentes plataformas:
- ✅ Twitter/X posts (280 chars)
- ✅ LinkedIn articles
- ✅ TikTok/Instagram captions
- ✅ Email marketing
- ✅ Hashtag generation

**Ejecutar:**
```powershell
python test_content_empire.py
```

**Output esperado:**
- 5 tipos de contenido generados
- Métricas de tiempo y calidad
- Resultados guardados en `data/test_results/content_empire_test.json`

---

### 2️⃣ Device Farm Test
**Archivo:** `test_device_farm.py`

Prueba planes de automatización para dispositivos Android:
- ✅ Instagram automation (login + post)
- ✅ WhatsApp bulk messaging
- ✅ TikTok engagement loops
- ✅ Multi-device coordination
- ✅ App E2E testing

**Ejecutar:**
```powershell
python test_device_farm.py
```

**Output esperado:**
- 5 planes de automatización generados
- Comandos Appium detallados
- Resultados guardados en `data/test_results/device_farm_test.json`

---

### 3️⃣ Niche Discovery Congress
**Archivo:** `test_niche_congress.py`

Congreso de 5 agentes especializados analizan nichos:
- 🤖 **Tech Analyst** - Tecnología emergente
- 🧘 **Lifestyle Analyst** - Wellness y productividad
- 💼 **Business Analyst** - B2B y startups
- 🎨 **Creative Analyst** - Herramientas creativas
- 💰 **Finance Analyst** - Fintech y crypto

**Ejecutar:**
```powershell
python test_niche_congress.py
```

**Output esperado:**
- 4 temas analizados × 5 agentes = 20 análisis
- Consenso del congreso por tema
- Mejor nicho identificado
- Resultados guardados en `data/test_results/niche_congress.json`

---

## 🚀 Ejecutar Todos los Tests

### Opción A: Ejecutar uno por uno
```powershell
# Activar entorno
.\venv\Scripts\Activate.ps1

# Content Empire
python test_content_empire.py

# Device Farm
python test_device_farm.py

# Niche Congress
python test_niche_congress.py
```

### Opción B: Script batch completo
```powershell
# Ejecuta los 3 tests secuencialmente
.\run_all_tests.ps1
```

---

## 📊 Resultados

Todos los resultados se guardan en:
```
data/test_results/
├── content_empire_test.json
├── device_farm_test.json
└── niche_congress.json
```

Cada archivo incluye:
- ✅ Timestamp de ejecución
- ✅ Agent IDs utilizados
- ✅ Resultados detallados
- ✅ Métricas de performance
- ✅ Success rate

---

## 🔧 Requisitos

1. **Orchestrator corriendo:**
   ```powershell
   python test_orchestrator.py
   ```

2. **Worker de Groq activo:**
   ```powershell
   python app/distributed/worker_groq.py
   ```

3. **Configuración en Documents:**
   - `C:\Users\PcDos\Documents\d8_data\agentes\config.json`
   - `C:\Users\PcDos\Documents\d8_data\workers\groq\credentials.json`

---

## 💡 Tips

- Los tests son **independientes**, puedes ejecutarlos en cualquier orden
- Cada test toma entre **30-90 segundos**
- Los agentes aprenden: métricas se actualizan en tiempo real
- Revisa los JSON para análisis detallados

---

## 🐛 Troubleshooting

**Error: "GROQ_API_KEY not found"**
```
→ Verifica: C:\Users\PcDos\Documents\d8_data\workers\groq\credentials.json
```

**Error: "Connection refused"**
```
→ Asegúrate que orchestrator y worker estén corriendo
```

**Test tarda mucho**
```
→ Normal: cada agente piensa ~3-5 segundos
→ 5 agentes × 4 temas = ~2 minutos para niche congress
```

---

## 📈 Próximos Pasos

Después de ejecutar los tests:

1. **Revisar resultados** en `data/test_results/`
2. **Elegir mejor opción** basado en métricas
3. **Refinar prompts** de agentes ganadores
4. **Escalar** con más agentes en el congreso
5. **Evolucionar** genomas con mejores fitness scores

---

**Última actualización:** 2025-11-19  
**Versión:** 1.0.0
