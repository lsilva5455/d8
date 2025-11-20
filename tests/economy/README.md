# Tests del Sistema Económico D8

> **Pool de Tests para Sistema Mock y Sistema Real**

---

## 📋 Índice

1. [Estructura de Tests](#estructura)
2. [Tests Mock vs Tests Real](#mock-vs-real)
3. [Ejecutar Tests](#ejecutar)
4. [Fixtures Disponibles](#fixtures)
5. [Agregar Nuevos Tests](#agregar)
6. [CI/CD Integration](#cicd)

---

## Estructura de Tests {#estructura}

```
tests/economy/
├── conftest.py                  # Fixtures compartidas + configuración pytest
├── test_mock_economy.py         # Tests para sistema MOCK (sin dependencias)
├── test_economy_system.py       # Tests para sistema REAL (con blockchain BSC)
└── README.md                    # Esta documentación
```

### Archivos

| Archivo | Propósito | Dependencias | Tests |
|---------|-----------|--------------|-------|
| `test_mock_economy.py` | Tests de sistema mock | Solo Python std | ~45 tests |
| `test_economy_system.py` | Tests de sistema real | web3, cryptography | ~12 tests |
| `conftest.py` | Fixtures + configuración | - | 15 fixtures |

---

## Tests Mock vs Tests Real {#mock-vs-real}

### 🎭 Tests Mock (`test_mock_economy.py`)

**Propósito:** Validar sistema económico SIN blockchain real ni dependencias externas.

**Características:**
- ✅ **Sin dependencias:** Solo Python estándar
- ✅ **Rápidos:** ~3-5 segundos para ejecutar todos
- ✅ **Confiables:** No dependen de red/servicios externos
- ✅ **Portables:** Funcionan en cualquier máquina

**Casos de uso:**
- ✅ Testing durante desarrollo
- ✅ CI/CD pipelines
- ✅ Pre-commit hooks
- ✅ Testing en máquinas sin dependencias instaladas

**Ejecutar:**
```powershell
# Todos los tests mock
pytest tests/economy/test_mock_economy.py -v

# Suite específica
pytest tests/economy/test_mock_economy.py::TestMockBlockchainClient -v

# Con coverage
pytest tests/economy/test_mock_economy.py --cov=app.economy.mock_blockchain --cov=app.economy.mock_security -v
```

**Test Suites Incluidas:**
1. `TestMockBlockchainClient` - Validación de MockBSCClient (4 tests)
2. `TestMockTokenClient` - Validación de MockD8TokenClient (4 tests)
3. `TestMockSecurity` - Validación de mock_security.py (4 tests)
4. `TestMockD8CreditsSystem` - D8Credits con mock (4 tests)
5. `TestMockRevenueAttribution` - Attribution con mock (3 tests)
6. `TestMockAutonomousAccounting` - Accounting con mock (4 tests)
7. `TestMockIntegratedWorkflow` - Flujos end-to-end (3 tests)
8. `TestMockEdgeCases` - Casos límite y errores (6 tests)
9. `TestMockPerformance` - Tests de rendimiento (3 tests)

### 🔗 Tests Real (`test_economy_system.py`)

**Propósito:** Validar integración con blockchain BSC real y smart contracts.

**Características:**
- ⚠️ **Requiere dependencias:** web3, eth-account, cryptography
- ⚠️ **Requiere configuración:** .env con PRIVATE_KEY_BSC
- ⚠️ **Más lentos:** Dependen de red blockchain
- ⚠️ **Costo:** Requieren gas fees (usar testnet)

**Casos de uso:**
- ✅ Testing de integración con BSC
- ✅ Validación antes de deploy a producción
- ✅ Testing de smart contracts reales

**Ejecutar:**
```powershell
# Instalar dependencias primero
pip install web3 eth-account cryptography

# Configurar .env con PRIVATE_KEY_BSC

# Ejecutar tests
pytest tests/economy/test_economy_system.py -v
```

---

## Ejecutar Tests {#ejecutar}

### Comandos Básicos

```powershell
# Todos los tests de economy
pytest tests/economy/ -v

# Solo tests MOCK (rápidos, sin dependencias)
pytest tests/economy/ -m mock -v

# Solo tests REAL (requieren blockchain)
pytest tests/economy/ -m real -v

# Excluir tests lentos
pytest tests/economy/ -m "not slow" -v

# Con output detallado
pytest tests/economy/ -vv

# Detener en primer fallo
pytest tests/economy/ -x

# Ejecutar tests en paralelo (requiere pytest-xdist)
pytest tests/economy/ -n auto
```

### Comandos con Coverage

```powershell
# Coverage de sistema mock
pytest tests/economy/test_mock_economy.py --cov=app.economy.mock_blockchain --cov=app.economy.mock_security --cov-report=html

# Coverage de sistema completo
pytest tests/economy/ --cov=app.economy --cov-report=html

# Ver reporte
start htmlcov/index.html
```

### Comandos con Filtros

```powershell
# Solo tests de MockBlockchainClient
pytest tests/economy/test_mock_economy.py::TestMockBlockchainClient -v

# Solo un test específico
pytest tests/economy/test_mock_economy.py::TestMockBlockchainClient::test_create_account_generates_valid_address -v

# Tests que contengan "transfer" en el nombre
pytest tests/economy/ -k "transfer" -v

# Tests marcados como integration
pytest tests/economy/ -m integration -v
```

---

## Fixtures Disponibles {#fixtures}

Ver [`conftest.py`](./conftest.py) para implementación completa.

### Fixtures Principales

| Fixture | Descripción | Uso |
|---------|-------------|-----|
| `mock_economy` | Sistema económico mock completo | `def test_x(mock_economy):` |
| `fresh_blockchain` | Blockchain limpio sin TX | `def test_x(fresh_blockchain):` |
| `mock_bsc_client` | Cliente BSC mock | `def test_x(mock_bsc_client):` |
| `mock_token_client` | Cliente D8Token mock | `def test_x(mock_token_client):` |

### Fixtures de Agentes

| Fixture | Descripción | Retorna |
|---------|-------------|---------|
| `three_agents` | 3 agentes registrados | `dict` con researcher, optimizer, validator |
| `funded_agent` | Agente con 1000 D8C | `str` (agent_id) |
| `agent_pair` | Par sender/receiver | `tuple` (sender_id, receiver_id) |

### Fixtures de Datos

| Fixture | Descripción | Retorna |
|---------|-------------|---------|
| `sample_contributions` | Contribuciones de ejemplo | `list` de dicts |
| `fitness_event` | Fitness event pre-registrado | `dict` con event_id |
| `sample_expenses` | Gastos registrados | `list` de expense_ids |

### Fixtures de Utilidades

| Fixture | Descripción | Retorna |
|---------|-------------|---------|
| `transaction_validator` | Valida estructura de TX | `callable` |
| `balance_checker` | Verifica balances de agentes | `callable` |

### Ejemplo de Uso

```python
def test_revenue_distribution(mock_economy, three_agents, sample_contributions):
    """Test usando múltiples fixtures"""
    
    # Registrar fitness event
    event = mock_economy.attribution.record_fitness_event(
        event_type="twitter_thread",
        fitness_score=90.0,
        niche="twitter_threads",
        contributions=sample_contributions
    )
    
    # Distribuir revenue
    distribution = mock_economy.attribution.distribute_revenue(
        event_id=event['event_id'],
        revenue_amount=100.0
    )
    
    # Verificar distribución 40/40/20
    assert len(distribution) == 3
    amounts = sorted([d['amount'] for d in distribution], reverse=True)
    assert amounts == [40.0, 40.0, 20.0]
```

---

## Agregar Nuevos Tests {#agregar}

### Template para Test Mock

```python
class TestNewFeature:
    """Tests para nueva funcionalidad"""
    
    def test_basic_functionality(self, mock_economy):
        """Test: Descripción clara de qué se valida"""
        # Arrange
        agent = mock_economy.credits.create_wallet("test_agent")
        
        # Act
        result = mock_economy.nueva_funcionalidad(agent)
        
        # Assert
        assert result is not None
        assert result['status'] == 'success'
    
    def test_edge_case(self, mock_economy):
        """Test: Caso límite o error esperado"""
        # Test de error handling
        with pytest.raises(ValueError):
            mock_economy.nueva_funcionalidad(invalid_input)
    
    def test_integration(self, mock_economy, three_agents):
        """Test: Integración con otros componentes"""
        # Test de flujo completo
        pass
```

### Checklist para Nuevos Tests

- [ ] **Nombre descriptivo:** `test_<what>_<expected_behavior>`
- [ ] **Docstring:** Descripción clara de qué valida el test
- [ ] **Arrange-Act-Assert:** Estructura clara de setup/ejecución/validación
- [ ] **Fixtures:** Usa fixtures existentes cuando sea posible
- [ ] **Assertions:** Assertions específicas y claras
- [ ] **Edge cases:** Incluye casos límite y error handling
- [ ] **Markers:** Marca con `@pytest.mark.mock` o `@pytest.mark.slow` si aplica

### Markers Disponibles

```python
@pytest.mark.mock          # Test usa sistema mock
@pytest.mark.real          # Test requiere blockchain real
@pytest.mark.slow          # Test toma >5 segundos
@pytest.mark.integration   # Test de integración entre componentes
```

---

## CI/CD Integration {#cicd}

### Pre-commit Hook

Ver [`scripts/tests/validate_mock_economy.py`](../../scripts/tests/validate_mock_economy.py) para script de validación.

```powershell
# Validar antes de commit
python scripts/tests/validate_mock_economy.py
```

### GitHub Actions (Ejemplo)

```yaml
name: Economy Tests

on: [push, pull_request]

jobs:
  test-mock:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      - name: Install dependencies
        run: |
          pip install pytest pytest-cov
      - name: Run mock tests
        run: |
          pytest tests/economy/test_mock_economy.py -v --cov=app.economy.mock_blockchain
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

### Script de Validación Local

```powershell
# scripts/tests/validate_mock_economy.ps1
pytest tests/economy/test_mock_economy.py -v --tb=short
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ All mock tests passed!" -ForegroundColor Green
} else {
    Write-Host "❌ Tests failed!" -ForegroundColor Red
    exit 1
}
```

---

## Métricas y Cobertura

### Objetivos de Cobertura

| Módulo | Objetivo | Actual |
|--------|----------|--------|
| `mock_blockchain.py` | >90% | - |
| `mock_security.py` | >90% | - |
| `d8_credits.py` | >80% | - |
| `attribution.py` | >80% | - |
| `accounting.py` | >80% | - |

### Generar Reporte de Coverage

```powershell
# Generar reporte HTML
pytest tests/economy/test_mock_economy.py --cov=app.economy --cov-report=html

# Ver líneas no cubiertas
pytest tests/economy/test_mock_economy.py --cov=app.economy --cov-report=term-missing

# Generar reporte XML (para CI)
pytest tests/economy/test_mock_economy.py --cov=app.economy --cov-report=xml
```

---

## Troubleshooting

### Error: "ModuleNotFoundError: No module named 'web3'"

**Solución:** Estás ejecutando tests REAL sin dependencias. Ejecuta solo tests mock:
```powershell
pytest tests/economy/test_mock_economy.py -v
```

### Error: "ImportError: cannot import name 'PBKDF2' from cryptography"

**Solución:** Sistema automáticamente usa mock_security cuando cryptography no está disponible. Ejecuta tests mock:
```powershell
pytest tests/economy/test_mock_economy.py -v
```

### Tests Lentos

**Solución:** Excluir tests lentos:
```powershell
pytest tests/economy/ -m "not slow" -v
```

### Tests Fallan en CI pero Pasan Localmente

**Checklist:**
- [ ] Verificar que tests mock no dependan de estado externo
- [ ] Usar `fresh_blockchain` fixture para estado limpio
- [ ] Evitar hardcodear paths o timestamps
- [ ] Verificar que fixtures se resetean entre tests

---

## Referencias

### Documentación Relacionada

- [Sistema Económico](../../docs/01_arquitectura/economia.md)
- [Mock Blockchain](../../app/economy/mock_blockchain.py)
- [Mock Security](../../app/economy/mock_security.py)
- [Quick Start Demo](../../scripts/quick_start_economy.py)

### Testing Best Practices

- [Pytest Documentation](https://docs.pytest.org/)
- [Testing Best Practices D8](../../docs/04_desarrollo/testing.md)
- [Knowledge Base](../../docs/06_knowledge_base/README.md)

---

**Última actualización:** 2025-11-20  
**Mantenedor:** D8 System  
**Versión:** 1.0
