# Deploy JurisFlow AI -> HostGator (shared hosting)
param(
    [string]$ArchiveName = "jurisflow-hostgator.tar.gz"
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$unioRoot = "C:\projetos\Nova pasta\unio-corp\unio-corp"
$cfgPath = Join-Path $unioRoot "config\deploy-uniojuridico.local.env"

function Load-EnvFile {
    param([string]$Path, [hashtable]$Into)
    if (-not (Test-Path $Path)) { return }
    Get-Content $Path | ForEach-Object {
        $line = $_.Trim()
        if ($line -eq "" -or $line.StartsWith("#")) { return }
        $idx = $line.IndexOf("=")
        if ($idx -lt 1) { return }
        $key = $line.Substring(0, $idx).Trim()
        $val = $line.Substring($idx + 1).Trim()
        $Into[$key] = $val
    }
}

$cfg = @{}
Load-EnvFile (Join-Path $unioRoot "config\deploy-hostgator.defaults.env") $cfg
Load-EnvFile $cfgPath $cfg

$sshHost = $cfg["DEPLOY_SSH_CANONICAL_HOST"]; if (-not $sshHost) { $sshHost = "br1136.hostgator.com.br" }
$sshUser = $cfg["DEPLOY_SSH_DEFAULT_USER"]; if (-not $sshUser) { $sshUser = "joabef36" }
$sshPort = $cfg["DEPLOY_SSH_DEFAULT_PORT"]; if (-not $sshPort) { $sshPort = "2222" }
$keyFile = $cfg["DEPLOY_KEY_FILE"]; if (-not $keyFile) { $keyFile = "$env:USERPROFILE\.ssh\unio_deploy" }
$remoteDir = "/home2/joabef36/jurisflow-ai"

$sshBase = @("-p", $sshPort, "-i", $keyFile, "-o", "StrictHostKeyChecking=accept-new", "-o", "BatchMode=yes", "-o", "ConnectTimeout=30")
$scpBase = @("-P", $sshPort, "-i", $keyFile, "-o", "StrictHostKeyChecking=accept-new", "-o", "BatchMode=yes", "-o", "ConnectTimeout=30")
$sshTarget = "${sshUser}@${sshHost}"

Write-Host "== Deploy JurisFlow AI -> HostGator ==" -ForegroundColor Cyan
Set-Location $root

$archive = Join-Path $env:TEMP $ArchiveName
if (Test-Path $archive) { Remove-Item $archive -Force }

Write-Host "[1/3] Empacotando..." -ForegroundColor Cyan
$tarArgs = @(
    "--exclude=.git", "--exclude=.venv", "--exclude=__pycache__", "--exclude=*.pyc",
    "--exclude=data/faiss", "--exclude=.env", "--exclude=tests",
    "-czf", $archive, "."
)
& tar @tarArgs
if ($LASTEXITCODE -ne 0) { throw "tar falhou" }

Write-Host "[2/3] Enviando para $remoteDir ..." -ForegroundColor Cyan
& scp @scpBase $archive "${sshTarget}:/tmp/$ArchiveName"
if ($LASTEXITCODE -ne 0) { throw "SCP archive falhou — SSH pode estar instavel. Tente em 2-3 minutos." }

$remoteCmd = @"
mkdir -p $remoteDir && cd $remoteDir && tar -xzf /tmp/$ArchiveName && cp -f .env.hostgator .env 2>/dev/null || true && sed -i 's/\r$//' scripts/*.sh watchdog.sh 2>/dev/null || true && bash scripts/setup-hostgator.sh
"@

& ssh @sshBase $sshTarget $remoteCmd
if ($LASTEXITCODE -ne 0) { throw "Setup remoto falhou (exit $LASTEXITCODE)" }

Write-Host "[3/3] Smoke test externo..." -ForegroundColor Cyan
try {
    $body = '{"message":"Ola, bom dia","escritorio_id":"default","use_rag":false,"history":[],"time_context":{"date":"27/07/2026","time":"11:00","period":"manha"}}'
    $resp = Invoke-WebRequest -Uri "https://uniojuridico.uniowork.com.br/api/chat" -Method POST -ContentType "application/json" -Body $body -UseBasicParsing -TimeoutSec 60
    Write-Host $resp.Content
} catch {
    Write-Host "Smoke via site falhou (pode exigir login): $($_.Exception.Message)" -ForegroundColor Yellow
}

Write-Host "Deploy JurisFlow concluido." -ForegroundColor Green
