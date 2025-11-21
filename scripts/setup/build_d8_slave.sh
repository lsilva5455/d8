#!/bin/bash
###############################################################################
# build_d8_slave.sh - Instalación automática de D8 Slave
# 
# USO: 
#   curl -sSL https://raw.githubusercontent.com/lsilva5455/d8/docker-workers/scripts/setup/build_d8_slave.sh | bash
#   O simplemente: bash build_d8_slave.sh
#
# DESCRIPCIÓN:
#   Instala y configura D8 Slave completamente automático
#   Compatible con: Raspberry Pi, Ubuntu, Debian, macOS
#
# AUTOR: D8 Team
# FECHA: 2025-11-20
###############################################################################

set -e  # Salir si cualquier comando falla

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Variables
D8_DIR="$HOME/d8"
D8_REPO="https://github.com/lsilva5455/d8.git"
D8_BRANCH="docker-workers"
SLAVE_PORT=7600
LOG_FILE="$HOME/d8_slave_install.log"

# Función de logging
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1" | tee -a "$LOG_FILE"
}

# Banner
echo ""
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║                                                           ║"
echo "║           🤖 D8 SLAVE - INSTALACIÓN AUTOMÁTICA           ║"
echo "║                                                           ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""
log_info "Iniciando instalación de D8 Slave..."
log_info "Log: $LOG_FILE"
echo ""

# Detectar sistema operativo
detect_os() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS=$ID
        OS_VERSION=$VERSION_ID
    elif [ -f /etc/lsb-release ]; then
        . /etc/lsb-release
        OS=$DISTRIB_ID
        OS_VERSION=$DISTRIB_RELEASE
    else
        OS=$(uname -s)
        OS_VERSION=$(uname -r)
    fi
    
    log "Sistema detectado: $OS $OS_VERSION"
}

# Verificar si comando existe
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Instalar Python 3
install_python() {
    log "🐍 Verificando Python..."
    
    if command_exists python3; then
        PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
        log "✅ Python ya instalado: $PYTHON_VERSION"
        return 0
    fi
    
    log "📦 Instalando Python 3..."
    
    case "$OS" in
        ubuntu|debian|raspbian)
            sudo apt-get update -qq
            sudo apt-get install -y python3 python3-pip python3-venv
            ;;
        fedora|centos|rhel)
            sudo dnf install -y python3 python3-pip
            ;;
        darwin)
            brew install python3
            ;;
        *)
            log_error "Sistema operativo no soportado: $OS"
            exit 1
            ;;
    esac
    
    if command_exists python3; then
        log "✅ Python instalado correctamente"
    else
        log_error "❌ Falló instalación de Python"
        exit 1
    fi
}

# Instalar Git
install_git() {
    log "📚 Verificando Git..."
    
    if command_exists git; then
        GIT_VERSION=$(git --version 2>&1 | awk '{print $3}')
        log "✅ Git ya instalado: $GIT_VERSION"
        return 0
    fi
    
    log "📦 Instalando Git..."
    
    case "$OS" in
        ubuntu|debian|raspbian)
            sudo apt-get install -y git
            ;;
        fedora|centos|rhel)
            sudo dnf install -y git
            ;;
        darwin)
            brew install git
            ;;
        *)
            log_error "Sistema operativo no soportado: $OS"
            exit 1
            ;;
    esac
    
    if command_exists git; then
        log "✅ Git instalado correctamente"
    else
        log_error "❌ Falló instalación de Git"
        exit 1
    fi
}

# Clonar repositorio D8
clone_d8() {
    log "📥 Clonando repositorio D8..."
    
    if [ -d "$D8_DIR" ]; then
        log_warning "⚠️  Directorio $D8_DIR ya existe"
        read -p "¿Eliminar y clonar de nuevo? (s/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Ss]$ ]]; then
            log "🗑️  Eliminando directorio anterior..."
            rm -rf "$D8_DIR"
        else
            log "📂 Usando directorio existente"
            cd "$D8_DIR"
            log "🔄 Actualizando repositorio..."
            git fetch origin
            git checkout "$D8_BRANCH"
            git pull origin "$D8_BRANCH"
            return 0
        fi
    fi
    
    log "⬇️  Clonando desde $D8_REPO..."
    git clone --branch "$D8_BRANCH" "$D8_REPO" "$D8_DIR" 2>&1 | tee -a "$LOG_FILE"
    
    if [ -d "$D8_DIR" ]; then
        log "✅ Repositorio clonado correctamente"
        cd "$D8_DIR"
    else
        log_error "❌ Falló clonación del repositorio"
        exit 1
    fi
}

# Crear entorno virtual
create_venv() {
    log "🐍 Creando entorno virtual..."
    
    cd "$D8_DIR"
    
    if [ -d "venv" ]; then
        log_warning "⚠️  venv ya existe, eliminando..."
        rm -rf venv
    fi
    
    python3 -m venv venv 2>&1 | tee -a "$LOG_FILE"
    
    if [ -d "venv" ]; then
        log "✅ Entorno virtual creado"
    else
        log_error "❌ Falló creación de venv"
        exit 1
    fi
}

# Instalar dependencias
install_dependencies() {
    log "📦 Instalando dependencias Python..."
    
    cd "$D8_DIR"
    
    # Activar venv
    source venv/bin/activate
    
    # Actualizar pip
    log "⬆️  Actualizando pip..."
    python -m pip install --upgrade pip 2>&1 | tee -a "$LOG_FILE"
    
    # Instalar requirements
    log "📥 Instalando requirements.txt..."
    pip install -r requirements.txt 2>&1 | tee -a "$LOG_FILE"
    
    if [ $? -eq 0 ]; then
        log "✅ Dependencias instaladas correctamente"
    else
        log_error "❌ Falló instalación de dependencias"
        exit 1
    fi
    
    deactivate
}

# Configurar .env
configure_env() {
    log "⚙️  Configurando variables de entorno..."
    
    cd "$D8_DIR"
    
    if [ ! -f ".env" ]; then
        log "📝 Creando archivo .env..."
        cat > .env << EOF
# D8 Slave Configuration
SLAVE_TOKEN=default-dev-token-change-in-production
SLAVE_PORT=$SLAVE_PORT
SLAVE_HOST=0.0.0.0

# LLM API Keys (opcional - solo si este slave usará LLMs)
# GROQ_API_KEY=
# GEMINI_API_KEY=
# DEEPSEEK_API_KEY=
EOF
        log "✅ Archivo .env creado"
    else
        log "✅ Archivo .env ya existe"
    fi
}

# Crear servicio systemd (Linux)
create_systemd_service() {
    if [ "$OS" != "darwin" ] && command_exists systemctl; then
        log "🔧 Configurando servicio systemd..."
        
        SERVICE_FILE="/etc/systemd/system/d8-slave.service"
        
        sudo tee "$SERVICE_FILE" > /dev/null << EOF
[Unit]
Description=D8 Slave Server
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$D8_DIR
ExecStart=$D8_DIR/venv/bin/python $D8_DIR/app/distributed/slave_server.py
Restart=always
RestartSec=10
StandardOutput=append:$HOME/d8_slave.log
StandardError=append:$HOME/d8_slave_error.log

[Install]
WantedBy=multi-user.target
EOF
        
        sudo systemctl daemon-reload
        sudo systemctl enable d8-slave.service
        
        log "✅ Servicio systemd configurado"
        log_info "Para iniciar: sudo systemctl start d8-slave"
        log_info "Para ver logs: sudo journalctl -u d8-slave -f"
    fi
}

# Verificar instalación
verify_installation() {
    log "🔍 Verificando instalación..."
    
    cd "$D8_DIR"
    
    # Verificar estructura
    if [ ! -f "app/distributed/slave_server.py" ]; then
        log_error "❌ Falta archivo slave_server.py"
        exit 1
    fi
    
    # Verificar venv
    if [ ! -d "venv" ]; then
        log_error "❌ Falta directorio venv"
        exit 1
    fi
    
    # Verificar dependencias
    source venv/bin/activate
    python -c "import flask, requests" 2>&1 | tee -a "$LOG_FILE"
    if [ $? -eq 0 ]; then
        log "✅ Dependencias verificadas"
    else
        log_error "❌ Faltan dependencias"
        exit 1
    fi
    deactivate
    
    log "✅ Instalación verificada correctamente"
}

# Test rápido del slave
test_slave() {
    log "🧪 Ejecutando test rápido..."
    
    cd "$D8_DIR"
    source venv/bin/activate
    
    # Test de importación
    python -c "
import sys
sys.path.insert(0, '$D8_DIR')
from app.distributed.slave_server import get_version_info, _get_available_methods

print('Version Info:', get_version_info())
print('Available Methods:', _get_available_methods())
" 2>&1 | tee -a "$LOG_FILE"
    
    if [ $? -eq 0 ]; then
        log "✅ Test completado exitosamente"
    else
        log_warning "⚠️  Test falló, pero la instalación está completa"
    fi
    
    deactivate
}

# Obtener IP local
get_local_ip() {
    if command_exists ip; then
        LOCAL_IP=$(ip route get 1 | awk '{print $7; exit}')
    elif command_exists ifconfig; then
        LOCAL_IP=$(ifconfig | grep "inet " | grep -v 127.0.0.1 | awk '{print $2}' | head -n 1)
    else
        LOCAL_IP="unknown"
    fi
    
    echo "$LOCAL_IP"
}

# Mostrar resumen
show_summary() {
    LOCAL_IP=$(get_local_ip)
    
    echo ""
    echo "╔═══════════════════════════════════════════════════════════╗"
    echo "║                                                           ║"
    echo "║              ✅ INSTALACIÓN COMPLETADA                    ║"
    echo "║                                                           ║"
    echo "╚═══════════════════════════════════════════════════════════╝"
    echo ""
    log "📊 RESUMEN DE INSTALACIÓN"
    echo ""
    log_info "📂 Directorio: $D8_DIR"
    log_info "🐍 Python: $(python3 --version)"
    log_info "📚 Git: $(git --version)"
    log_info "🌐 IP Local: $LOCAL_IP"
    log_info "🔌 Puerto: $SLAVE_PORT"
    echo ""
    log "🚀 PRÓXIMOS PASOS:"
    echo ""
    echo "   1. Iniciar slave server:"
    echo "      cd $D8_DIR"
    echo "      source venv/bin/activate"
    echo "      python app/distributed/slave_server.py"
    echo ""
    echo "   2. O usar servicio systemd (si está configurado):"
    echo "      sudo systemctl start d8-slave"
    echo "      sudo systemctl status d8-slave"
    echo ""
    echo "   3. En el MASTER, registrar este slave:"
    echo "      python scripts/add_slave.py nombre-slave $LOCAL_IP $SLAVE_PORT"
    echo ""
    log_info "📝 Log completo: $LOG_FILE"
    echo ""
}

# Main
main() {
    detect_os
    install_python
    install_git
    clone_d8
    create_venv
    install_dependencies
    configure_env
    create_systemd_service
    verify_installation
    test_slave
    show_summary
}

# Ejecutar
main

exit 0
