#!/bin/bash
# ============================================
# D8 Worker Setup - Bash Wrapper
# ============================================
# Facilita el setup de workers en máquinas Linux
# Detecta automáticamente Raspberry Pi y sugiere configuración óptima

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}      D8 Worker Setup Assistant         ${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Detect if running as root
if [ "$EUID" -eq 0 ]; then
    echo -e "${YELLOW}⚠️  Advertencia: No se recomienda ejecutar como root${NC}"
    echo -e "${YELLOW}   Ejecuta sin sudo (excepto para instalación de servicios)${NC}"
    echo ""
fi

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 no está instalado${NC}"
    echo -e "${YELLOW}Instálalo con: sudo apt install python3${NC}"
    exit 1
fi

# Detect device type
DEVICE_TYPE="generic"
if [ -f /proc/cpuinfo ]; then
    if grep -q "Raspberry Pi" /proc/cpuinfo; then
        DEVICE_TYPE="raspberry_pi"
        echo -e "${GREEN}✅ Raspberry Pi detectada${NC}"
        
        # Get model
        MODEL=$(grep "Model" /proc/cpuinfo | cut -d: -f2 | xargs)
        echo -e "${GREEN}   Modelo: ${MODEL}${NC}"
        echo ""
        
        # Get RAM
        TOTAL_RAM=$(free -g | awk '/^Mem:/{print $2}')
        echo -e "${GREEN}   RAM: ${TOTAL_RAM}GB${NC}"
        echo ""
        
        # Suggest configuration
        if [ "$TOTAL_RAM" -ge 8 ]; then
            echo -e "${GREEN}💡 Configuración recomendada:${NC}"
            echo -e "${GREEN}   - Worker tipo: deepseek${NC}"
            echo -e "${GREEN}   - Modelo: deepseek-coder:6.7b${NC}"
        elif [ "$TOTAL_RAM" -ge 4 ]; then
            echo -e "${YELLOW}💡 Configuración recomendada:${NC}"
            echo -e "${YELLOW}   - Worker tipo: deepseek${NC}"
            echo -e "${YELLOW}   - Modelo: deepseek-coder:1.3b (versión ligera)${NC}"
        else
            echo -e "${RED}⚠️  RAM insuficiente para DeepSeek local${NC}"
            echo -e "${YELLOW}   Usa worker Groq o Gemini (requieren API key)${NC}"
        fi
        echo ""
    fi
fi

# Interactive mode if no arguments
if [ $# -eq 0 ]; then
    echo -e "${BLUE}Modo interactivo${NC}"
    echo ""
    
    # Ask for worker type
    echo "¿Qué tipo de worker deseas configurar?"
    echo "1) DeepSeek (local, sin costo, requiere recursos)"
    echo "2) Groq (cloud, rápido, requiere API key)"
    echo "3) Gemini (cloud, gratis con límites, requiere API key)"
    read -p "Selección [1-3]: " WORKER_CHOICE
    
    case $WORKER_CHOICE in
        1)
            WORKER_TYPE="deepseek"
            API_KEY=""
            ;;
        2)
            WORKER_TYPE="groq"
            read -p "Ingresa tu Groq API key: " API_KEY
            ;;
        3)
            WORKER_TYPE="gemini"
            read -p "Ingresa tu Gemini API key: " API_KEY
            ;;
        *)
            echo -e "${RED}Selección inválida${NC}"
            exit 1
            ;;
    esac
    
    echo ""
    read -p "URL del Orchestrator (ej: http://192.168.1.100:5000): " ORCHESTRATOR_URL
    
    # Build command
    CMD="python3 scripts/setup/setup_worker.py --type $WORKER_TYPE --orchestrator $ORCHESTRATOR_URL"
    if [ -n "$API_KEY" ]; then
        CMD="$CMD --api-key $API_KEY"
    fi
    
    echo ""
    echo -e "${BLUE}Ejecutando: $CMD${NC}"
    echo ""
    
    exec $CMD
else
    # Pass all arguments to Python script
    exec python3 scripts/setup/setup_worker.py "$@"
fi
