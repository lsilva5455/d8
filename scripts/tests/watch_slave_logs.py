"""
Ver logs del slave_server.py en tiempo real (tail -f)
"""
import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()

SLAVE_IP = "192.168.4.38"
SLAVE_PORT = 7600
TOKEN = os.getenv('GITHUB_TOKEN')

def tail_logs():
    """Simula tail -f del slave.log"""
    url = f"http://{SLAVE_IP}:{SLAVE_PORT}/api/execute"
    headers = {"Authorization": f"Bearer {TOKEN}"}
    
    # Obtener home dir
    response = requests.post(url, json={"command": "echo $HOME"}, headers=headers)
    home_dir = response.json()["stdout"].strip()
    d8_dir = f"{home_dir}/d8"
    
    print(f"📡 Monitoreando logs de {SLAVE_IP}:{SLAVE_PORT}")
    print(f"📂 Archivo: {d8_dir}/slave.log")
    print("=" * 80)
    print("Presiona Ctrl+C para salir\n")
    
    last_lines = 0
    
    try:
        while True:
            # Contar líneas
            response = requests.post(
                url, 
                json={"command": "wc -l < slave.log", "working_dir": d8_dir}, 
                headers=headers,
                timeout=5
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    current_lines = int(result["stdout"].strip())
                    
                    if current_lines > last_lines:
                        # Hay líneas nuevas, mostrarlas
                        new_lines = current_lines - last_lines
                        response = requests.post(
                            url,
                            json={"command": f"tail -n {new_lines} slave.log", "working_dir": d8_dir},
                            headers=headers,
                            timeout=5
                        )
                        
                        if response.status_code == 200:
                            result = response.json()
                            if result.get("stdout"):
                                print(result["stdout"], end='')
                        
                        last_lines = current_lines
            
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\n✅ Monitoreo detenido")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    tail_logs()
