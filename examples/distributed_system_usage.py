"""
Ejemplo de Uso del Sistema Distribuido D8
==========================================
Demuestra cómo usar workers distribuidos desde el sistema principal
"""

import time
from app.distributed_integration import (
    D8DistributedClient,
    DistributedEvolutionAdapter,
    check_distributed_system_health
)


def example_1_agent_action():
    """Ejemplo 1: Ejecutar acción de agente en worker distribuido"""
    print("\n" + "="*60)
    print("EJEMPLO 1: Ejecutar Acción de Agente")
    print("="*60)
    
    # Conectar al orchestrator
    client = D8DistributedClient("http://localhost:5000")
    
    # Ejecutar acción
    messages = [
        {"role": "system", "content": "You are a creative AI assistant"},
        {"role": "user", "content": "Generate 3 unique business ideas for sustainable energy"}
    ]
    
    print("\n📤 Enviando tarea al orchestrator...")
    result = client.execute_agent_action(
        messages=messages,
        model="llama-3.3-70b",
        temperature=0.8,
        priority=5
    )
    
    if result.get("success"):
        print("\n✅ Resultado recibido:")
        print(result["output"][:200] + "...")
    else:
        print(f"\n❌ Error: {result.get('error')}")


def example_2_evolution():
    """Ejemplo 2: Evolución genética distribuida"""
    print("\n" + "="*60)
    print("EJEMPLO 2: Evolución Genética Distribuida")
    print("="*60)
    
    # Crear adapter
    adapter = DistributedEvolutionAdapter("http://localhost:5000")
    
    # Genomas de ejemplo
    genome1 = {
        "temperature": 0.8,
        "max_tokens": 1000,
        "system_prompt": "You are helpful",
        "exploration_rate": 0.3
    }
    
    genome2 = {
        "temperature": 0.6,
        "max_tokens": 1500,
        "system_prompt": "You are creative",
        "exploration_rate": 0.5
    }
    
    print("\n🧬 Ejecutando crossover distribuido...")
    offspring = adapter.crossover(genome1, genome2)
    print(f"✅ Offspring generado: {offspring}")
    
    print("\n🔬 Ejecutando mutación distribuida...")
    mutated = adapter.mutate(genome1, mutation_rate=0.1)
    print(f"✅ Genoma mutado: {mutated}")


def example_3_async_tasks():
    """Ejemplo 3: Enviar múltiples tareas sin esperar"""
    print("\n" + "="*60)
    print("EJEMPLO 3: Tareas Asíncronas")
    print("="*60)
    
    client = D8DistributedClient("http://localhost:5000")
    
    # Enviar múltiples tareas
    task_ids = []
    
    for i in range(5):
        messages = [
            {"role": "user", "content": f"Generate idea #{i+1} for AI applications"}
        ]
        
        result = client.execute_agent_action(
            messages=messages,
            wait_for_result=False  # No esperar
        )
        
        task_ids.append(result["task_id"])
        print(f"📤 Tarea {i+1} enviada: {result['task_id']}")
    
    print(f"\n✅ {len(task_ids)} tareas enviadas. Procesándose en paralelo...")
    
    # Esperar un momento
    time.sleep(3)
    
    # Consultar resultados
    print("\n📊 Consultando resultados...")
    for task_id in task_ids:
        result = client._wait_for_result(task_id)
        status = "✅" if result.get("success") else "❌"
        print(f"{status} Tarea {task_id[:8]}: {result.get('output', 'N/A')[:50]}...")


def example_4_monitoring():
    """Ejemplo 4: Monitoreo del sistema"""
    print("\n" + "="*60)
    print("EJEMPLO 4: Monitoreo del Sistema")
    print("="*60)
    
    orchestrator_url = "http://localhost:5000"
    
    # Check health
    print("\n🩺 Verificando salud del sistema...")
    health = check_distributed_system_health(orchestrator_url)
    
    if health["orchestrator_healthy"]:
        print(f"✅ Orchestrator: ONLINE")
        print(f"   Workers online: {health['workers_online']}")
        print(f"   Tareas pendientes: {health['tasks_pending']}")
        print(f"   Tareas en progreso: {health['tasks_in_progress']}")
    else:
        print(f"❌ Orchestrator: OFFLINE")
        print(f"   Error: {health.get('error')}")
    
    # Get detailed stats
    client = D8DistributedClient(orchestrator_url)
    
    print("\n📊 Estadísticas del sistema:")
    stats = client.get_stats()
    
    print(f"\n🤖 Workers:")
    print(f"   Total: {stats['workers']['total']}")
    print(f"   Online: {stats['workers']['online']}")
    print(f"   Busy: {stats['workers']['busy']}")
    print(f"   Por tipo: {stats['workers']['by_type']}")
    
    print(f"\n📝 Tareas:")
    print(f"   Total: {stats['tasks']['total']}")
    print(f"   Pendientes: {stats['tasks']['pending']}")
    print(f"   Asignadas: {stats['tasks']['assigned']}")
    print(f"   Completadas: {stats['tasks']['completed']}")
    print(f"   Fallidas: {stats['tasks']['failed']}")
    
    print(f"\n📈 Performance:")
    print(f"   Completadas totales: {stats['performance']['total_completed']}")
    print(f"   Fallidas totales: {stats['performance']['total_failed']}")
    print(f"   Success rate: {stats['performance']['success_rate']:.1f}%")


def example_5_integration_with_darwin():
    """Ejemplo 5: Integración con Darwin (sistema evolutivo)"""
    print("\n" + "="*60)
    print("EJEMPLO 5: Integración con Darwin")
    print("="*60)
    
    print("""
Este ejemplo muestra cómo modificar Darwin para usar workers distribuidos:

# En app/evolution/darwin.py:

from app.distributed_integration import DistributedEvolutionAdapter

class Darwin:
    def __init__(self, use_distributed=False, orchestrator_url=None):
        self.use_distributed = use_distributed
        
        if use_distributed:
            self.evolution_adapter = DistributedEvolutionAdapter(orchestrator_url)
    
    def crossover(self, parent1, parent2):
        if self.use_distributed:
            # Usar worker distribuido
            return self.evolution_adapter.crossover(parent1.genome, parent2.genome)
        else:
            # Usar implementación local
            return self._local_crossover(parent1, parent2)
    
    def mutate(self, genome):
        if self.use_distributed:
            # Usar worker distribuido
            return self.evolution_adapter.mutate(genome, self.mutation_rate)
        else:
            # Usar implementación local
            return self._local_mutation(genome)

# Uso:
darwin = Darwin(use_distributed=True, orchestrator_url="http://192.168.1.100:5000")
population = darwin.evolve(generations=100)

# Ventaja: Las operaciones genéticas se ejecutan en Raspberry Pi con DeepSeek
# Costo: $0 (local), vs $5-10/mes con API
""")


def example_6_congress_integration():
    """Ejemplo 6: Integración con Congreso Autónomo"""
    print("\n" + "="*60)
    print("EJEMPLO 6: Integración con Congreso Autónomo")
    print("="*60)
    
    print("""
El Congreso puede usar workers distribuidos para sus experimentos:

# En scripts/autonomous_congress.py:

from app.distributed_integration import D8DistributedClient

class AutonomousCongress:
    def __init__(self, use_distributed=False):
        self.use_distributed = use_distributed
        
        if use_distributed:
            self.distributed_client = D8DistributedClient("http://orchestrator:5000")
    
    def _research_phase(self, target_system):
        if self.use_distributed:
            # Enviar múltiples investigaciones en paralelo
            task_ids = []
            for research_topic in self.research_topics:
                task_id = self.distributed_client.execute_agent_action(
                    messages=[{"role": "user", "content": research_topic}],
                    wait_for_result=False
                )
                task_ids.append(task_id)
            
            # Esperar resultados
            results = [self.distributed_client._wait_for_result(tid) for tid in task_ids]
            return results
        else:
            # Secuencial local
            return [self._local_research(topic) for topic in self.research_topics]

# Ventaja: Paralelización real de experimentos
# 5 workers = 5x más rápido que secuencial
""")


def main():
    """Ejecutar todos los ejemplos"""
    import sys
    
    print("\n" + "="*60)
    print(" EJEMPLOS DE SISTEMA DISTRIBUIDO D8")
    print("="*60)
    print("\n⚠️  Asegúrate de que el orchestrator esté corriendo:")
    print("   python app/orchestrator_app.py")
    print("\n⚠️  Y al menos un worker:")
    print("   ./scripts/setup/setup_worker.sh")
    print("\n")
    
    # Verificar si orchestrator está disponible
    health = check_distributed_system_health("http://localhost:5000")
    
    if not health["orchestrator_healthy"]:
        print("❌ Orchestrator no disponible. Inicia el orchestrator primero.")
        print("   Comando: python app/orchestrator_app.py")
        sys.exit(1)
    
    if health["workers_online"] == 0:
        print("⚠️  No hay workers online. Los ejemplos funcionarán pero no habrá resultados.")
        print("   Inicia un worker: ./scripts/setup/setup_worker.sh")
    
    try:
        # Ejecutar ejemplos
        example_1_agent_action()
        time.sleep(2)
        
        example_2_evolution()
        time.sleep(2)
        
        example_3_async_tasks()
        time.sleep(2)
        
        example_4_monitoring()
        
        # Ejemplos conceptuales (no ejecutables)
        example_5_integration_with_darwin()
        example_6_congress_integration()
        
        print("\n" + "="*60)
        print("✅ Todos los ejemplos completados")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
