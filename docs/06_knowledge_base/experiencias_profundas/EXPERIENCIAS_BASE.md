# Experiencias Profundas - Base de Conocimiento

**Fecha:** 2025-11-17  
**Fuente:** Proyecto mapeo_pool  
**Propósito:** Guía de metodología y heurísticas para desarrollo

---

## 🎯 Principios Fundamentales

### 1. Map Before Modify
```
❌ NO: Ver problema → Codear solución
✅ SÍ: Ver problema → Mapear flujo → Identificar causa → Codear solución

ROI: 10 min mapeo = 1-2h ahorradas
```

### 2. Sistemas > Disciplina
```
No confiar en "voy a tener cuidado"
Crear sistemas que FUERCEN el comportamiento correcto

Ejemplo:
❌ "Recuerda invalidar cache"
✅ Cache con TTL automático (imposible olvidar)
```

### 3. Seguir el Dato
```
Verificar CADA eslabón: Origen → Transformación → Destino
No asumir: Verificar con evidencia real
```

---

## 🚨 Sesgos Cognitivos a Evitar

### Sesgo de Confirmación
- Buscar evidencia que REFUTA, no solo que confirma
- Si evidencia contradice hipótesis → cambiar hipótesis

### Action Bias
- Preferir "entender" sobre "hacer algo"
- Pensar 30 min > Codear 2h sin dirección

### Tunnel Vision
- Ver sistema completo, no solo un componente
- Dibujar diagrama antes de tocar código

---

## 📋 Checklist Obligatorio de Debugging

```
[ ] 1. ¿Entiendo el flujo COMPLETO de datos?
[ ] 2. ¿He dibujado un diagrama del flujo?
[ ] 3. ¿Sé exactamente dónde está el punto de falla?
[ ] 4. ¿He verificado CADA eslabón?
[ ] 5. ¿Las preguntas del usuario tienen sentido lógico?
[ ] 6. ¿Estoy asumiendo o verificando?
[ ] 7. ¿Abordo causa raíz o síntoma?
```

---

## 🎯 Heurísticas Clave

### Test de Pregunta Obvia
```
SI usuario pregunta algo obvio
ENTONCES tu plan está mal
ACCIÓN: Detenerse, replantear
```

### Regla de las 3 Capas
```
Problema en UI → Verificar:
1. Frontend (¿dato llega?)
2. API (¿dato se transmite?)
3. Backend (¿dato se genera?)
4. Estado (¿dato se persiste?)
5. Inicialización (¿valores por defecto?)
6. Edge cases (¿reinicios, modos?)
```

### Evidencia Contradictoria
```
SI evidencia contradice hipótesis
ENTONCES hipótesis está MAL
NO adaptar hipótesis, DESCARTARLA
```

### Profundidad Primero
```
❌ Fix incremental sin mapa
✅ Mapear completo → Identificar todas las capas → Fix de raíz
```

---

## 🏗️ Arquitectura de Calidad

### Parametrización
- Backend lista estructuras
- Frontend renderiza dinámicamente
- Escalabilidad automática

### Separación de Concerns
- Lógica de negocio en backend
- UI/UX en frontend
- Estado centralizado y claro

### Progressive Disclosure
- Modo normal (simple)
- Modo avanzado (técnico)
- Información cuando se necesita

---

## 💡 Meta-Aprendizaje

### Documentar NO es suficiente
```
❌ "Cometí error X, lo documento"
✅ "Cometí error X, creo sistema que lo previene"
```

### Paradoja del Éxito
```
Resultado exitoso ≠ Proceso correcto
Validar proceso, no solo resultado
```

### Preguntas Críticas Post-Implementación
1. ¿Qué sistema habría impedido este error?
2. ¿Puedo implementar ese sistema?
3. ¿Cómo fuerzo su uso?

---

## 🔧 Herramientas de Investigación

### Buscar Múltiples Fuentes de Verdad
```bash
# Encontrar TODAS las referencias
grep -r "variable_nombre" .
grep -r "funcion_nombre" .

# Buscar archivos de configuración ocultos
ls -la | grep "^\."
```

### Logs son Evidencia
```
No asumir qué hace el código
Ver qué dicen los logs
Seguir el rastro del dato
```

---

## 📊 Métricas de Calidad

### Señales de Buen Proceso
- ✅ Flujo mapeado antes de codear
- ✅ Hipótesis múltiples consideradas
- ✅ Evidencia contradictoria buscada
- ✅ Usuario valida entendimiento
- ✅ Causa raíz identificada

### Señales de Mal Proceso
- ❌ Codear inmediatamente
- ❌ Una sola hipótesis
- ❌ Solo buscar confirmación
- ❌ Usuario confundido
- ❌ Fix de síntomas

---

## 🎓 Aplicación en Cada Tarea

### Antes de Empezar
1. ¿He consultado experiencias previas?
2. ¿Entiendo el flujo completo?
3. ¿He identificado punto exacto de falla?

### Durante Desarrollo
1. ¿Estoy verificando o asumiendo?
2. ¿Tengo evidencia de mi hipótesis?
3. ¿He buscado evidencia contradictoria?

### Antes de Entregar
1. ¿Probé casos edge?
2. ¿Validé con usuario?
3. ¿Documenté conocimiento nuevo?

---

**Nivel de Importancia:** ⭐⭐⭐⭐⭐ CRÍTICO  
**Uso:** Consultar ANTES de cada tarea compleja  
**ROI:** 10 min lectura = 2-4h ahorradas
