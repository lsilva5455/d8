#!/usr/bin/env python3
"""
Generate Slave Installer Script
Genera scripts de instalación (.sh o .bat) con la configuración actual del master
"""
import os
import json
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime

class SlaveInstallerGenerator:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.env_file = self.project_root / ".env"
        self.config = self._load_config()
        
    def _load_config(self):
        """Carga configuración del .env"""
        load_dotenv(self.env_file)
        
        # Detectar master IP
        import socket
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            master_ip = s.getsockname()[0]
            s.close()
        except:
            master_ip = "127.0.0.1"
        
        return {
            "master_host": master_ip,
            "master_port": 7600,
            "slave_port": 7600,
            "github_repo": "https://github.com/lsilva5455/d8.git",
            "github_branch": "docker-workers",
            "github_token": os.getenv("GITHUB_TOKEN", ""),
            "git_token": os.getenv("GIT_TOKEN", ""),
            "groq_api_key": os.getenv("GROQ_API_KEY", ""),
            "gemini_api_key": os.getenv("GEMINI_API_KEY", ""),
            "telegram_token": os.getenv("TELEGRAM_TOKEN", ""),
            "telegram_chat_id": os.getenv("TELEGRAM_CHAT_ID", ""),
        }
    
    def generate_bash_script(self, output_path: Path):
        """Genera script .sh que crea un servidor HTTP en Python puro (sin dependencias)"""
        script_content = f'''#!/bin/bash
###############################################################################
# D8 Slave Server - MÍNIMO ABSOLUTO
# Crea servidor HTTP usando Python puro (built-in, sin pip install)
###############################################################################

PORT={self.config["slave_port"]}
TOKEN="{self.config["github_token"]}"

# Obtener IP
IP=$(hostname -I 2>/dev/null | awk '{{print $1}}' || echo "0.0.0.0")

clear
echo ""
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║    🤖 D8 SLAVE SERVER - Esperando comandos del master    ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""
echo "  📍 IP: $IP"
echo "  🔌 Puerto: $PORT"
echo "  🔑 Token: ****"
echo ""
echo "  ⏳ Iniciando servidor HTTP..."

# Verificar Python
if ! command -v python3 >/dev/null 2>&1; then
    echo ""
    echo "  ❌ ERROR: Python 3 no está instalado"
    echo "  📦 Instala con: sudo apt-get install python3"
    echo ""
    exit 1
fi

echo "  ✅ Python disponible"
echo ""
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "🚀 Servidor iniciado - Esperando conexión del master..."
echo ""

# Crear servidor HTTP en Python (sin dependencias externas)
python3 << 'ENDPYTHON'
import json
import subprocess
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path

PORT = {self.config["slave_port"]}
TOKEN = "{self.config["github_token"]}"

class SlaveHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        """Override para log personalizado"""
        print(f"[{{self.log_date_time_string()}}] {{format % args}}")
    
    def _send_json(self, status_code, data):
        """Envía respuesta JSON"""
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def _validate_token(self):
        """Valida Bearer token"""
        auth_header = self.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return False
        token = auth_header[7:]  # Remove "Bearer "
        return token == TOKEN
    
    def do_GET(self):
        """Handle GET requests"""
        if self.path == "/api/health":
            self._send_json(200, {{"status": "ok", "version": "1.0.0"}})
        else:
            self._send_json(404, {{"error": "Not found"}})
    
    def do_POST(self):
        """Handle POST requests"""
        # Validar token
        if not self._validate_token():
            self._send_json(401, {{"error": "Unauthorized"}})
            return
        
        if self.path == "/api/execute":
            # Leer body
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode("utf-8")
            
            try:
                data = json.loads(body)
                command = data.get("command")
                working_dir = data.get("working_dir", str(Path.home()))
                
                if not command:
                    self._send_json(400, {{"error": "No command provided"}})
                    return
                
                print(f"[CMD] {{command}}")
                
                # Ejecutar comando
                try:
                    result = subprocess.run(
                        command,
                        shell=True,
                        cwd=working_dir,
                        capture_output=True,
                        text=True,
                        timeout=300
                    )
                    
                    self._send_json(200, {{
                        "success": result.returncode == 0,
                        "stdout": result.stdout,
                        "stderr": result.stderr,
                        "exit_code": result.returncode
                    }})
                    
                except subprocess.TimeoutExpired:
                    self._send_json(200, {{
                        "success": False,
                        "stdout": "",
                        "stderr": "Command timeout (300s)",
                        "exit_code": -1
                    }})
                except Exception as e:
                    self._send_json(500, {{
                        "success": False,
                        "stdout": "",
                        "stderr": str(e),
                        "exit_code": -1
                    }})
                    
            except json.JSONDecodeError:
                self._send_json(400, {{"error": "Invalid JSON"}})
        else:
            self._send_json(404, {{"error": "Not found"}})

# Iniciar servidor
server = HTTPServer(("0.0.0.0", PORT), SlaveHandler)
print(f"✅ Servidor HTTP activo en 0.0.0.0:{{PORT}}")
print()
print("💡 El master puede enviar comandos a:")
print(f"   POST http://<IP>:{{PORT}}/api/execute")
print(f"   GET  http://<IP>:{{PORT}}/api/health")
print()

try:
    server.serve_forever()
except KeyboardInterrupt:
    print("\\n\\n⏹️  Servidor detenido")
    server.shutdown()
ENDPYTHON
'''
        
        # Escribir con line endings Unix (LF)
        output_path.write_text(script_content, newline='\n')
        output_path.chmod(0o755)  # Hacer ejecutable
        print(f"✅ Script Bash generado: {output_path}")
    
    def generate_batch_script(self, output_path: Path):
        """Genera script .bat - MÍNIMO ABSOLUTO: Solo PowerShell puro"""
        script_content = f'''@echo off
REM ###########################################################################
REM D8 Slave Server - MINIMO ABSOLUTO
REM Solo ejecuta comandos que el master envie via HTTP
REM PowerShell puro, sin dependencias
REM ###########################################################################

PowerShell -NoProfile -ExecutionPolicy Bypass -Command "& {{
    $PORT = {self.config["slave_port"]}
    $TOKEN = '{self.config["github_token"]}'
    
    # Obtener IP
    $IP = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object {{$_.IPAddress -notlike '127.*'}} | Select-Object -First 1).IPAddress
    if (-not $IP) {{ $IP = 'unknown' }}
    
    Clear-Host
    Write-Host ''
    Write-Host '╔═══════════════════════════════════════════════════════════╗'
    Write-Host '║    🤖 D8 SLAVE SERVER - Esperando comandos del master    ║'
    Write-Host '╚═══════════════════════════════════════════════════════════╝'
    Write-Host ''
    Write-Host \"  📍 IP: $IP\"
    Write-Host \"  🔌 Puerto: $PORT\"
    Write-Host '  🔑 Token: ****'
    Write-Host ''
    Write-Host '  ⏳ Esperando conexión del master...'
    Write-Host '  💡 El master enviará comandos via HTTP POST /api/execute'
    Write-Host ''
    Write-Host '═══════════════════════════════════════════════════════════'
    Write-Host ''
    
    # Crear listener HTTP
    $listener = New-Object System.Net.HttpListener
    $listener.Prefixes.Add(\"http://+:$PORT/\")
    $listener.Start()
    
    Write-Host \"[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] Servidor iniciado en puerto $PORT\"
    Write-Host ''
    
    while ($listener.IsListening) {{
        try {{
            # Esperar request
            $context = $listener.GetContext()
            $request = $context.Request
            $response = $context.Response
            
            $method = $request.HttpMethod
            $path = $request.Url.LocalPath
            
            Write-Host \"[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] $method $path\"
            
            # Leer body
            $reader = New-Object System.IO.StreamReader($request.InputStream)
            $body = $reader.ReadToEnd()
            $reader.Close()
            
            # Verificar Authorization
            $authHeader = $request.Headers['Authorization']
            $validAuth = $false
            if ($authHeader -and $authHeader.StartsWith('Bearer ')) {{
                $receivedToken = $authHeader.Substring(7)
                $validAuth = ($receivedToken -eq $TOKEN)
            }}
            
            # Responder
            $responseObj = @{{}}
            $statusCode = 200
            
            if (-not $validAuth) {{
                $statusCode = 401
                $responseObj = @{{ error = 'Unauthorized' }}
            }}
            elseif ($path -eq '/api/health') {{
                $responseObj = @{{ 
                    status = 'ok'
                    version = '1.0.0'
                }}
            }}
            elseif ($path -eq '/api/execute') {{
                # Parsear JSON body
                try {{
                    $data = $body | ConvertFrom-Json
                    $command = $data.command
                    $workingDir = $data.working_dir
                    
                    if (-not $workingDir) {{ $workingDir = $HOME }}
                    
                    Write-Host \"[CMD] $command\"
                    
                    # Ejecutar comando
                    try {{
                        $output = Invoke-Expression \"cd '$workingDir'; $command\" 2>&1 | Out-String
                        $exitCode = $LASTEXITCODE
                        if ($null -eq $exitCode) {{ $exitCode = 0 }}
                        
                        $responseObj = @{{
                            success = ($exitCode -eq 0)
                            stdout = $output
                            stderr = ''
                            exit_code = $exitCode
                        }}
                    }}
                    catch {{
                        $responseObj = @{{
                            success = $false
                            stdout = ''
                            stderr = $_.Exception.Message
                            exit_code = 1
                        }}
                    }}
                }}
                catch {{
                    $statusCode = 400
                    $responseObj = @{{ error = 'Invalid JSON' }}
                }}
            }}
            else {{
                $statusCode = 404
                $responseObj = @{{ error = 'Not found' }}
            }}
            
            # Enviar respuesta
            $response.StatusCode = $statusCode
            $response.ContentType = 'application/json'
            
            $json = $responseObj | ConvertTo-Json -Compress
            $buffer = [System.Text.Encoding]::UTF8.GetBytes($json)
            $response.ContentLength64 = $buffer.Length
            $response.OutputStream.Write($buffer, 0, $buffer.Length)
            $response.Close()
        }}
        catch {{
            Write-Host \"[ERROR] $_\"
        }}
    }}
    
    $listener.Stop()
}}"
'''
        
        output_path.write_text(script_content, encoding='utf-8')
        print(f"✅ Script Batch generado: {output_path}")
    
    def generate_both(self, output_dir: Path = None):
        """Genera ambos scripts (.sh y .bat)"""
        if output_dir is None:
            output_dir = self.project_root / "scripts" / "setup"
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        bash_path = output_dir / f"install_slave_{timestamp}.sh"
        batch_path = output_dir / f"install_slave_{timestamp}.bat"
        
        self.generate_bash_script(bash_path)
        self.generate_batch_script(batch_path)
        
        return bash_path, batch_path


def main():
    """CLI para generar scripts"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Genera scripts de instalación de D8 Slave con configuración actual"
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="Directorio de salida (default: scripts/setup/)"
    )
    parser.add_argument(
        "--platform",
        choices=["linux", "windows", "both"],
        default="both",
        help="Plataforma objetivo"
    )
    
    args = parser.parse_args()
    
    generator = SlaveInstallerGenerator()
    
    print("\n🔧 Generador de Scripts de Instalación D8 Slave")
    print("=" * 60)
    print(f"Master: {generator.config['master_host']}:{generator.config['master_port']}")
    print(f"Repo: {generator.config['github_repo']}")
    print(f"Branch: {generator.config['github_branch']}")
    print("=" * 60)
    print()
    
    output_dir = args.output_dir or (generator.project_root / "scripts" / "setup")
    
    if args.platform == "linux":
        bash_path = output_dir / f"install_slave_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sh"
        generator.generate_bash_script(bash_path)
    elif args.platform == "windows":
        batch_path = output_dir / f"install_slave_{datetime.now().strftime('%Y%m%d_%H%M%S')}.bat"
        generator.generate_batch_script(batch_path)
    else:
        bash_path, batch_path = generator.generate_both(output_dir)
    
    print()
    print("✅ Scripts generados exitosamente")
    print()
    print("📝 Uso:")
    if args.platform != "windows":
        print(f"   Linux/Raspberry: bash {bash_path.name}")
    if args.platform != "linux":
        print(f"   Windows: {batch_path.name}")
    print()


if __name__ == "__main__":
    main()
