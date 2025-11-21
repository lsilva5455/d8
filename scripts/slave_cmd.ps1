# SSH/SCP Wrapper usando HTTP API del slave
# NO requiere sshpass, Plink, ni nada externo
# Usa el servidor HTTP que ya está corriendo en el slave

param(
    [Parameter(Mandatory=$true)]
    [string]$SlaveHost,
    
    [Parameter(ParameterSetName='SSH', Mandatory=$true)]
    [string]$Command,
    
    [Parameter(ParameterSetName='Upload', Mandatory=$true)]
    [switch]$Upload,
    
    [Parameter(ParameterSetName='Upload', Mandatory=$true)]
    [string]$LocalFile,
    
    [Parameter(ParameterSetName='Upload', Mandatory=$true)]
    [string]$RemoteFile
)

# Cargar token desde .env
$envPath = Join-Path $PSScriptRoot "..\..\.env"
$token = (Get-Content $envPath | Select-String 'GITHUB_TOKEN' | ForEach-Object {$_ -replace 'GITHUB_TOKEN=',''}).ToString().Trim()

$headers = @{Authorization="Bearer $token"}
$apiUrl = "http://${SlaveHost}:7600/api/execute"

if ($PSCmdlet.ParameterSetName -eq 'SSH') {
    # Ejecutar comando SSH via HTTP API
    $body = @{command=$Command} | ConvertTo-Json
    
    try {
        $result = Invoke-RestMethod -Uri $apiUrl -Method POST -Headers $headers -Body $body -ContentType "application/json" -TimeoutSec 300
        
        if ($result.stdout) {
            Write-Host $result.stdout -NoNewline
        }
        
        if ($result.stderr) {
            Write-Host $result.stderr -ForegroundColor Red -NoNewline
        }
        
        exit $result.exit_code
        
    } catch {
        Write-Host "❌ Error de comunicación: $_" -ForegroundColor Red
        exit 1
    }
    
} elseif ($PSCmdlet.ParameterSetName -eq 'Upload') {
    # Transferir archivo via HTTP API
    # 1. Codificar archivo en base64
    $fileBytes = [System.IO.File]::ReadAllBytes($LocalFile)
    $base64 = [Convert]::ToBase64String($fileBytes)
    
    Write-Host "📤 Subiendo $(Split-Path $LocalFile -Leaf) ($([math]::Round($fileBytes.Length/1KB, 2)) KB)..."
    
    # 2. Enviar comando para crear archivo en el slave
    $createCommand = @"
echo '$base64' | base64 -d > $RemoteFile
"@
    
    $body = @{command=$createCommand} | ConvertTo-Json
    
    try {
        $result = Invoke-RestMethod -Uri $apiUrl -Method POST -Headers $headers -Body $body -ContentType "application/json" -TimeoutSec 300
        
        if ($result.success) {
            Write-Host "✅ Archivo transferido a ${SlaveHost}:$RemoteFile" -ForegroundColor Green
        } else {
            Write-Host "❌ Error: $($result.stderr)" -ForegroundColor Red
            exit 1
        }
        
    } catch {
        Write-Host "❌ Error de comunicación: $_" -ForegroundColor Red
        exit 1
    }
}
