#!/usr/bin/env python3
"""
Installation Monitor Server
Servidor para monitorear instalaciones de slaves en tiempo real
"""

from flask import Flask, request, jsonify
from datetime import datetime
from pathlib import Path
import json
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Almacenamiento en memoria de instalaciones activas
active_installations = {}

# Directorio para logs
LOGS_DIR = Path.home() / "Documents" / "d8_data" / "installation_logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)


@app.route('/api/installation/start', methods=['POST'])
def installation_start():
    """Notifica el inicio de una instalación"""
    data = request.json
    hostname = data.get('hostname', 'unknown')
    
    installation_id = f"{hostname}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    active_installations[installation_id] = {
        'hostname': hostname,
        'start_time': datetime.now().isoformat(),
        'status': 'running',
        'steps': [],
        'errors': []
    }
    
    logger.info(f"📦 Nueva instalación iniciada: {installation_id}")
    
    return jsonify({
        'status': 'ok',
        'installation_id': installation_id
    })


@app.route('/api/installation/progress', methods=['POST'])
def installation_progress():
    """Recibe reportes de progreso de la instalación"""
    data = request.json
    
    step = data.get('step', 'unknown')
    status = data.get('status', 'running')
    message = data.get('message', '')
    hostname = data.get('hostname', 'unknown')
    
    # Encontrar instalación activa por hostname
    installation_id = None
    for inst_id, inst_data in active_installations.items():
        if inst_data['hostname'] == hostname and inst_data['status'] == 'running':
            installation_id = inst_id
            break
    
    if not installation_id:
        # Crear nueva entrada si no existe
        installation_id = f"{hostname}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        active_installations[installation_id] = {
            'hostname': hostname,
            'start_time': datetime.now().isoformat(),
            'status': 'running',
            'steps': [],
            'errors': []
        }
    
    # Agregar paso
    step_data = {
        'step': step,
        'status': status,
        'message': message,
        'timestamp': datetime.now().isoformat()
    }
    
    active_installations[installation_id]['steps'].append(step_data)
    
    # Log según status
    if status == 'failed':
        active_installations[installation_id]['errors'].append(message)
        logger.error(f"❌ [{hostname}] {step}: {message}")
    elif status == 'success':
        logger.info(f"✅ [{hostname}] {step}: {message}")
    else:
        logger.info(f"🔄 [{hostname}] {step}: {message}")
    
    return jsonify({'status': 'ok'})


@app.route('/api/installation/complete', methods=['POST'])
def installation_complete():
    """Finaliza la instalación y registra el slave"""
    data = request.json
    
    slave_id = data.get('slave_id')
    host = data.get('host')
    port = data.get('port', 7600)
    hostname = data.get('hostname', 'unknown')
    
    # Registrar slave automáticamente
    try:
        from app.distributed.slave_manager import SlaveManager
        
        manager = SlaveManager()
        manager.register_slave(
            slave_id=slave_id,
            host=host,
            port=port,
            install_method="auto_http"
        )
        
        logger.info(f"✅ Slave auto-registrado: {slave_id} ({host}:{port})")
        
        # Marcar instalación como completada
        for inst_id, inst_data in active_installations.items():
            if inst_data['hostname'] == hostname and inst_data['status'] == 'running':
                inst_data['status'] = 'completed'
                inst_data['end_time'] = datetime.now().isoformat()
                inst_data['slave_id'] = slave_id
                
                # Guardar log
                log_file = LOGS_DIR / f"{inst_id}.json"
                log_file.write_text(json.dumps(inst_data, indent=2))
                
                break
        
        return jsonify({
            'status': 'ok',
            'slave_id': slave_id,
            'registered': True
        })
        
    except Exception as e:
        logger.error(f"❌ Error al registrar slave: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/installation/status', methods=['GET'])
def installation_status():
    """Retorna el estado de todas las instalaciones activas"""
    return jsonify({
        'active': len([i for i in active_installations.values() if i['status'] == 'running']),
        'completed': len([i for i in active_installations.values() if i['status'] == 'completed']),
        'failed': len([i for i in active_installations.values() if i['status'] == 'failed']),
        'installations': active_installations
    })


@app.route('/api/installation/<installation_id>', methods=['GET'])
def get_installation(installation_id):
    """Obtiene detalles de una instalación específica"""
    if installation_id in active_installations:
        return jsonify(active_installations[installation_id])
    else:
        return jsonify({'error': 'Installation not found'}), 404


def start_installation_monitor(port=7600):
    """Inicia el servidor de monitoreo"""
    logger.info(f"🔧 Installation Monitor Server iniciando en puerto {port}...")
    logger.info(f"📝 Logs guardados en: {LOGS_DIR}")
    app.run(host='0.0.0.0', port=port, debug=False)


if __name__ == '__main__':
    start_installation_monitor()
