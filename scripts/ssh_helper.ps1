# SSH/SCP Helper para PowerShell
# Usa credenciales de .env automáticamente

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet('ssh','scp-upload','scp-download')]
    [string]$Action,
    
    [Parameter(Mandatory=$true)]
    [string]$Host,
    
    [Parameter(Mandatory=$false)]
    [string]$Command,
    
    [Parameter(Mandatory=$false)]
    [string]$LocalPath,
    
    [Parameter(Mandatory=$false)]
    [string]$RemotePath
)

# Cargar .env
$envFile = Join-Path $PSScriptRoot "..\..\.env"
if (Test-Path $envFile) {
    Get-Content $envFile | ForEach-Object {
        if ($_ -match '^\s*([^#][^=]*)\s*=\s*(.*)$') {
            $name = $matches[1].Trim()
            $value = $matches[2].Trim()
            Set-Variable -Name $name -Value $value -Scope Script
        }
    }
}

if (-not $SLAVE_SSH_USER) { $SLAVE_SSH_USER = "admin" }
if (-not $SLAVE_SSH_PASSWORD) {
    Write-Error "SLAVE_SSH_PASSWORD no está configurado en .env"
    exit 1
}

# Crear credencial seguro
$secPassword = ConvertTo-SecureString $SLAVE_SSH_PASSWORD -AsPlainText -Force
$credential = New-Object System.Management.Automation.PSCredential($SLAVE_SSH_USER, $secPassword)

switch ($Action) {
    'ssh' {
        if (-not $Command) {
            Write-Error "Se requiere -Command para ssh"
            exit 1
        }
        
        # Usar Plink (parte de PuTTY) si está disponible
        $plinkPath = "C:\Program Files\PuTTY\plink.exe"
        if (Test-Path $plinkPath) {
            & $plinkPath -batch -pw $SLAVE_SSH_PASSWORD "$SLAVE_SSH_USER@$Host" $Command
        } else {
            Write-Host "⚠️  Plink no encontrado, usando workaround..." -ForegroundColor Yellow
            Write-Host "📋 Comando a ejecutar: $Command"
            Write-Host "💡 Ejecuta manualmente: ssh $SLAVE_SSH_USER@$Host '$Command'"
        }
    }
    
    'scp-upload' {
        if (-not $LocalPath -or -not $RemotePath) {
            Write-Error "Se requiere -LocalPath y -RemotePath para scp-upload"
            exit 1
        }
        
        # Usar PSCP (parte de PuTTY) si está disponible
        $pscpPath = "C:\Program Files\PuTTY\pscp.exe"
        if (Test-Path $pscpPath) {
            & $pscpPath -batch -pw $SLAVE_SSH_PASSWORD $LocalPath "$SLAVE_SSH_USER@$Host`:$RemotePath"
        } else {
            Write-Host "⚠️  PSCP no encontrado, usando workaround..." -ForegroundColor Yellow
            Write-Host "📋 Usar HTTP para transferir..."
            
            # Crear servidor HTTP temporal y descargar desde el slave
            $port = 8765
            $listener = New-Object System.Net.HttpListener
            $listener.Prefixes.Add("http://+:$port/")
            $listener.Start()
            
            Write-Host "🌐 Servidor HTTP temporal en puerto $port"
            Write-Host "📤 Descarga desde slave con:"
            $localIP = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.InterfaceAlias -notlike "*Loopback*"} | Select-Object -First 1).IPAddress
            Write-Host "   wget http://${localIP}:$port/$(Split-Path $LocalPath -Leaf) -O $RemotePath"
            
            # Esperar conexión
            $context = $listener.GetContext()
            $response = $context.Response
            $content = [System.IO.File]::ReadAllBytes($LocalPath)
            $response.ContentLength64 = $content.Length
            $response.OutputStream.Write($content, 0, $content.Length)
            $response.Close()
            $listener.Stop()
            
            Write-Host "✅ Archivo transferido"
        }
    }
    
    'scp-download' {
        if (-not $LocalPath -or -not $RemotePath) {
            Write-Error "Se requiere -LocalPath y -RemotePath para scp-download"
            exit 1
        }
        
        # Usar PSCP (parte de PuTTY) si está disponible
        $pscpPath = "C:\Program Files\PuTTY\pscp.exe"
        if (Test-Path $pscpPath) {
            & $pscpPath -batch -pw $SLAVE_SSH_PASSWORD "$SLAVE_SSH_USER@$Host`:$RemotePath" $LocalPath
        } else {
            Write-Host "⚠️  PSCP no encontrado"
            Write-Host "💡 Usar HTTP API del slave para transferir archivos"
        }
    }
}
