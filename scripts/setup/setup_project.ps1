# Setup script for The Hive - AI Agent Ecosystem
# PowerShell version
# Generated: 2025-11-17

Write-Host "🐝 Setting up The Hive project structure..." -ForegroundColor Green

# Create main directories
$directories = @(
    "app\agents",
    "app\evolution",
    "app\memory",
    "app\integrations",
    "app\utils",
    "tests\unit",
    "tests\integration",
    "tests\e2e",
    "data\genomes",
    "data\metrics",
    "data\logs",
    "docs",
    "scripts"
)

foreach ($dir in $directories) {
    New-Item -ItemType Directory -Force -Path $dir | Out-Null
}

Write-Host "📁 Creating directory structure..." -ForegroundColor Yellow

# Create empty files
$files = @(
    "app\memory\__init__.py",
    "app\memory\vector_store.py",
    "app\memory\episode_buffer.py",
    "app\utils\__init__.py",
    "app\utils\logger.py",
    "app\utils\metrics.py",
    "tests\__init__.py",
    "tests\unit\__init__.py",
    "tests\integration\__init__.py",
    "tests\e2e\__init__.py",
    "data\genomes\.gitkeep",
    "data\metrics\.gitkeep",
    "data\logs\.gitkeep"
)

foreach ($file in $files) {
    New-Item -ItemType File -Force -Path $file | Out-Null
}

Write-Host "✅ Project structure created successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "📂 Structure:" -ForegroundColor Cyan
Write-Host "."
Write-Host "├── app/"
Write-Host "│   ├── agents/          # Agent implementations"
Write-Host "│   ├── evolution/       # Genetic algorithms"
Write-Host "│   ├── memory/          # Vector DB & memory"
Write-Host "│   ├── integrations/    # External APIs"
Write-Host "│   └── utils/           # Utilities"
Write-Host "├── tests/               # Test suite"
Write-Host "├── data/                # Runtime data"
Write-Host "├── docs/                # Documentation"
Write-Host "└── scripts/             # Utility scripts"
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Copy .env.example to .env and configure your API keys"
Write-Host "2. Install dependencies: pip install -r requirements.txt"
Write-Host "3. Run tests: pytest"
Write-Host "4. Start the hive: python app/main.py"
