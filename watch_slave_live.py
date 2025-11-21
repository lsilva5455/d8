"""
Monitor en VIVO de la ejecución en el Raspberry Pi Slave
Muestra stdout/stderr en tiempo real
"""
import os
import sys
import time
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

SLAVE_IP = "192.168.4.38"
SLAVE_PORT = 7600
TOKEN = os.getenv('GITHUB_TOKEN')

def execute_live(command: str, working_dir: str = None):
    """Ejecuta comando y muestra output en tiempo real"""
    url = f"http://{SLAVE_IP}:{SLAVE_PORT}/api/execute"
    headers = {"Authorization": f"Bearer {TOKEN}"}
    
    payload = {"command": command}
    if working_dir:
        payload["working_dir"] = working_dir
    
    print(f"\n🚀 Ejecutando: {command}")
    print(f"📂 En: {working_dir or 'directorio actual'}")
    print("=" * 80)
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=600)
        result = response.json()
        
        if result.get("stdout"):
            print(result["stdout"], end='')
        
        if result.get("stderr"):
            print(result["stderr"], file=sys.stderr, end='')
        
        if result.get("success"):
            print("\n✅ Comando completado exitosamente")
        else:
            print(f"\n❌ Error (exit code: {result.get('exit_code')})")
        
        return result
        
    except requests.exceptions.Timeout:
        print("\n⏱️  Timeout - el comando está tomando más de 10 minutos")
        return None
    except Exception as e:
        print(f"\n❌ Error de comunicación: {e}")
        return None

def main():
    print("=" * 80)
    print("🔴 MONITOR EN VIVO - RASPBERRY PI SLAVE")
    print(f"📍 {SLAVE_IP}:{SLAVE_PORT}")
    print("=" * 80)
    
    # 1. Verificar conectividad
    print("\n1️⃣  Verificando conectividad...")
    try:
        response = requests.get(f"http://{SLAVE_IP}:{SLAVE_PORT}/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ Slave online")
        else:
            print("❌ Slave no responde correctamente")
            return
    except:
        print("❌ No se puede conectar al slave")
        return
    
    # 2. Crear venv
    home_result = execute_live("echo $HOME")
    home_dir = home_result["stdout"].strip()
    d8_dir = f"{home_dir}/d8"
    
    print(f"\n2️⃣  Creando entorno virtual en {d8_dir}...")
    execute_live("rm -rf venv && python3 -m venv venv", working_dir=d8_dir)
    
    # 3. Instalar dependencias (sin --upgrade, solo install)
    print("\n3️⃣  Instalando dependencias (esto puede tomar 2-3 minutos)...")
    execute_live("./venv/bin/pip install -r requirements.txt", working_dir=d8_dir)
    
    # 4. Configurar .env
    print("\n4️⃣  Configurando .env...")
    execute_live("""cat > .env << 'EOF'
SLAVE_HOST=0.0.0.0
SLAVE_PORT=7600
LOG_LEVEL=INFO
EOF""", working_dir=d8_dir)
    
    # 5. Verificar que slave_server.py existe
    print("\n5️⃣  Verificando archivos...")
    execute_live("ls -la app/distributed/slave_server.py", working_dir=d8_dir)
    
    # 6. Iniciar slave_server
    print("\n6️⃣  Iniciando slave_server en background...")
    execute_live("pkill -f slave_server.py", working_dir=d8_dir)  # Matar si existe
    time.sleep(1)
    execute_live("nohup ./venv/bin/python app/distributed/slave_server.py > slave.log 2>&1 &", working_dir=d8_dir)
    time.sleep(2)
    
    # 7. Verificar que está corriendo
    print("\n7️⃣  Verificando proceso...")
    execute_live("pgrep -f slave_server.py && echo 'Proceso encontrado' || echo 'Proceso NO encontrado'", working_dir=d8_dir)
    
    # 8. Ver últimas líneas del log
    print("\n8️⃣  Últimas líneas del log:")
    execute_live("tail -n 20 slave.log", working_dir=d8_dir)
    
    print("\n" + "=" * 80)
    print("✅ INSTALACIÓN COMPLETADA")
    print("=" * 80)
    print(f"\n📋 Para ver logs en vivo en el futuro:")
    print(f"   python watch_slave_logs.py")

if __name__ == "__main__":
    main()
