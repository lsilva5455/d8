# 🚨 Troubleshooting

**Solución de problemas comunes y debugging de D8**

---

## 📋 Documentos Disponibles

### [Error 429 - Rate Limits](error_429.md)
Solución completa al error 429 de APIs: causas, migración a Groq, configuración de rate limiting y estrategias de fallback.

### [Resumen Error 429](resumen_error_429.md)
Resumen ejecutivo de la solución al error 429.

### [Errores Comunes](common_errors.md)
FAQ de errores frecuentes: import errors, API key issues, path problems, worker failures.

### [Debug Guide](debug_guide.md)
Guía completa de debugging: logs, breakpoints, tracing de requests, debugging distribuido.

---

## 🎯 Cuándo Consultar Esta Sección

- ✅ El sistema arroja un error que no entiendes
- ✅ Los workers no responden o fallan
- ✅ API keys no funcionan
- ✅ Rate limits excedidos
- ✅ Necesitas debuggear un componente

---

## 🔍 Flujo de Troubleshooting

```
1. Identifica el error exacto
   ↓
2. Busca en Errores Comunes
   ↓
3. Si no está, consulta Debug Guide
   ↓
4. Revisa logs en data/logs/
   ↓
5. Si persiste, abre un issue en GitHub
```

---

## 🚨 Errores Más Frecuentes

### 429 Too Many Requests
**Solución:** [Error 429 Guide](error_429.md) - Migrar a Groq

### Worker No Responde
**Solución:** [Debug Guide](debug_guide.md) - Verificar heartbeat

### API Key Invalid
**Solución:** [Errores Comunes](common_errors.md) - Revisar `.env`

### Import Errors
**Solución:** [Errores Comunes](common_errors.md) - Activar venv

---

**Volver al [Índice Principal](../README.md)**
