#!/usr/bin/env python3
"""
📊 Monitoring Dashboard - FASE 3
Dashboard en tiempo real del estado del sistema D8
"""

from flask import Flask, jsonify, render_template_string
from pathlib import Path
import json
import sys
from datetime import datetime
import logging

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.economy import D8CreditsSystem

app = Flask(__name__)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Dashboard HTML template
DASHBOARD_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>D8 Monitoring Dashboard</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: #0f172a;
            color: #e2e8f0;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        h1 {
            text-align: center;
            color: #38bdf8;
            margin-bottom: 30px;
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .card {
            background: #1e293b;
            border-radius: 10px;
            padding: 20px;
            border: 1px solid #334155;
        }
        .card h2 {
            margin-top: 0;
            color: #38bdf8;
            font-size: 18px;
            border-bottom: 2px solid #334155;
            padding-bottom: 10px;
        }
        .metric {
            display: flex;
            justify-content: space-between;
            margin: 10px 0;
            padding: 8px;
            background: #0f172a;
            border-radius: 5px;
        }
        .metric-label {
            color: #94a3b8;
        }
        .metric-value {
            font-weight: bold;
            color: #38bdf8;
        }
        .status-active {
            color: #10b981;
        }
        .status-inactive {
            color: #ef4444;
        }
        .refresh-btn {
            background: #38bdf8;
            color: #0f172a;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            font-weight: bold;
            display: block;
            margin: 20px auto;
        }
        .refresh-btn:hover {
            background: #0ea5e9;
        }
        .timestamp {
            text-align: center;
            color: #64748b;
            margin-top: 20px;
        }
    </style>
    <script>
        async function refreshData() {
            try {
                const response = await fetch('/api/status');
                const data = await response.json();
                
                // Update metrics
                document.getElementById('active-niches').textContent = data.niche_discovery.active_niches;
                document.getElementById('last-discovery').textContent = data.niche_discovery.last_run || 'N/A';
                
                document.getElementById('congress-cycles').textContent = data.congress.cycles_completed;
                document.getElementById('last-improvement').textContent = (data.congress.last_improvement * 100).toFixed(1) + '%';
                
                document.getElementById('current-gen').textContent = data.evolution.current_generation;
                document.getElementById('avg-fitness').textContent = data.evolution.avg_fitness.toFixed(2);
                document.getElementById('best-agent').textContent = data.evolution.best_agent;
                
                document.getElementById('total-revenue').textContent = '$' + data.economy.total_revenue.toFixed(2);
                document.getElementById('active-agents').textContent = data.economy.active_agents;
                
                document.getElementById('timestamp').textContent = 'Last updated: ' + new Date().toLocaleString();
            } catch (error) {
                console.error('Error refreshing data:', error);
            }
        }
        
        // Auto-refresh every 30 seconds
        setInterval(refreshData, 30000);
        
        // Initial load
        window.onload = refreshData;
    </script>
</head>
<body>
    <div class="container">
        <h1>🤖 D8 System Dashboard</h1>
        
        <div class="grid">
            <!-- Niche Discovery -->
            <div class="card">
                <h2>🔬 Niche Discovery</h2>
                <div class="metric">
                    <span class="metric-label">Active Niches:</span>
                    <span class="metric-value" id="active-niches">-</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Last Run:</span>
                    <span class="metric-value" id="last-discovery">-</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Status:</span>
                    <span class="metric-value status-active">ACTIVE</span>
                </div>
            </div>
            
            <!-- Congress -->
            <div class="card">
                <h2>🏛️ Autonomous Congress</h2>
                <div class="metric">
                    <span class="metric-label">Cycles Completed:</span>
                    <span class="metric-value" id="congress-cycles">-</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Last Improvement:</span>
                    <span class="metric-value" id="last-improvement">-</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Status:</span>
                    <span class="metric-value status-active">ACTIVE</span>
                </div>
            </div>
            
            <!-- Evolution -->
            <div class="card">
                <h2>🧬 Darwin Evolution</h2>
                <div class="metric">
                    <span class="metric-label">Current Generation:</span>
                    <span class="metric-value" id="current-gen">-</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Avg Fitness:</span>
                    <span class="metric-value" id="avg-fitness">-</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Best Agent:</span>
                    <span class="metric-value" id="best-agent">-</span>
                </div>
            </div>
            
            <!-- Economy -->
            <div class="card">
                <h2>💰 Economy System</h2>
                <div class="metric">
                    <span class="metric-label">Total Revenue:</span>
                    <span class="metric-value" id="total-revenue">-</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Active Agents:</span>
                    <span class="metric-value" id="active-agents">-</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Status:</span>
                    <span class="metric-value status-active">ACTIVE</span>
                </div>
            </div>
        </div>
        
        <button class="refresh-btn" onclick="refreshData()">🔄 Refresh Now</button>
        
        <div class="timestamp" id="timestamp">Loading...</div>
    </div>
</body>
</html>
"""


def get_niche_discovery_status():
    """Obtener estado del niche discovery"""
    results_dir = Path("data/niche_discovery")
    
    if not results_dir.exists():
        return {"active_niches": 0, "last_run": None}
    
    # Contar archivos de descubrimiento
    files = list(results_dir.glob("discovery_*.json"))
    
    if not files:
        return {"active_niches": 0, "last_run": None}
    
    # Leer último archivo
    latest_file = max(files, key=lambda f: f.stat().st_mtime)
    
    try:
        with open(latest_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return {
                "active_niches": data.get("niches_found", 0),
                "last_run": data.get("timestamp", "Unknown")
            }
    except:
        return {"active_niches": 0, "last_run": None}


def get_congress_status():
    """Obtener estado del congress"""
    results_dir = Path("data/congress_cycles")
    
    if not results_dir.exists():
        return {"cycles_completed": 0, "last_improvement": 0}
    
    files = list(results_dir.glob("cycle_*.json"))
    
    if not files:
        return {"cycles_completed": 0, "last_improvement": 0}
    
    # Leer último archivo
    latest_file = max(files, key=lambda f: f.stat().st_mtime)
    
    try:
        with open(latest_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            results = data.get("results", {})
            return {
                "cycles_completed": data.get("cycle_number", 0),
                "last_improvement": results.get("improvement", 0)
            }
    except:
        return {"cycles_completed": 0, "last_improvement": 0}


def get_evolution_status():
    """Obtener estado de la evolución"""
    results_dir = Path("data/generations")
    
    if not results_dir.exists():
        return {
            "current_generation": 0,
            "avg_fitness": 0,
            "best_agent": "N/A"
        }
    
    # Contar generaciones
    gen_dirs = [d for d in results_dir.iterdir() if d.is_dir() and d.name.startswith("gen_")]
    
    return {
        "current_generation": len(gen_dirs),
        "avg_fitness": 85.5,  # TODO: Calcular real
        "best_agent": "agent_001"  # TODO: Obtener real
    }


def get_economy_status():
    """Obtener estado de la economía"""
    try:
        credits = D8CreditsSystem()
        
        # TODO: Implementar métodos reales
        return {
            "total_revenue": 1250.0,  # Placeholder
            "active_agents": 15  # Placeholder
        }
    except:
        return {
            "total_revenue": 0,
            "active_agents": 0
        }


@app.route('/')
def dashboard():
    """Página principal del dashboard"""
    return render_template_string(DASHBOARD_HTML)


@app.route('/api/status')
def system_status():
    """API endpoint para obtener estado del sistema"""
    try:
        status = {
            "timestamp": datetime.now().isoformat(),
            "niche_discovery": get_niche_discovery_status(),
            "congress": get_congress_status(),
            "evolution": get_evolution_status(),
            "economy": get_economy_status()
        }
        
        return jsonify(status)
    
    except Exception as e:
        logger.error(f"Error getting system status: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/agents')
def list_agents():
    """API endpoint para listar agentes"""
    # TODO: Implementar listado real de agentes
    agents = [
        {
            "id": "agent_001",
            "role": "content_generator",
            "fitness": 85.5,
            "revenue": 150.0,
            "status": "active"
        },
        {
            "id": "agent_002",
            "role": "niche_analyzer",
            "fitness": 78.2,
            "revenue": 120.0,
            "status": "active"
        }
    ]
    
    return jsonify(agents)


@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})


def main():
    """Iniciar dashboard"""
    logger.info("🚀 Starting D8 Monitoring Dashboard...")
    logger.info("📊 Dashboard will be available at: http://localhost:7500")
    logger.info("📡 API endpoint: http://localhost:7500/api/status")
    
    app.run(
        host='0.0.0.0',
        port=7500,
        debug=False
    )


if __name__ == "__main__":
    main()
