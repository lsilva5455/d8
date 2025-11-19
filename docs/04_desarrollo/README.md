# 🛠️ Desarrollo

**Testing, contribución y mejores prácticas para desarrolladores**

---

## 📋 Documentos Disponibles

### [Testing Guide](testing.md)
Guía completa de testing: ejecutar tests unitarios, de integración y E2E, escribir nuevos tests, coverage y CI/CD.

### [Test Guide Legacy](test_guide_legacy.md)
Versión antigua de la guía de tests (mantener por compatibilidad).

### [Contributing Guide](CONTRIBUTING.md) ⭐
**OBLIGATORIO** - Cómo contribuir al proyecto: estructura de carpetas, naming conventions, cómo agregar documentación, proceso de PR.

### [Standards](standards.md)
Estándares de código: Python conventions, docstrings, type hints, logging y manejo de errores.

---

## 🎯 Cuándo Consultar Esta Sección

- ✅ Contribuir código al proyecto
- ✅ Ejecutar o escribir tests
- ✅ Entender convenciones del proyecto
- ✅ Agregar nueva documentación
- ✅ Hacer code review

---

## 🔧 Setup para Desarrolladores

```bash
# Instalar dependencias de desarrollo
pip install -r requirements.txt

# Ejecutar tests
pytest tests/

# Ejecutar tests con coverage
pytest --cov=app tests/

# Linting
flake8 app/ scripts/
```

---

## 📖 Orden de Lectura para Nuevos Contribuidores

1. **[CONTRIBUTING.md](CONTRIBUTING.md)** - EMPIEZA AQUÍ
2. **[Standards](standards.md)** - Entender convenciones
3. **[Testing Guide](testing.md)** - Aprender a testear

---

**Volver al [Índice Principal](../README.md)**
