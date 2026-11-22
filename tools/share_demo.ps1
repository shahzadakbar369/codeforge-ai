param([int]$Port = 8001)
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $projectRoot
$demoDirectory = Join-Path $projectRoot 'tmp/presentation'
New-Item -ItemType Directory -Force -Path $demoDirectory | Out-Null
$client = Join-Path $demoDirectory 'cloudflared.exe'
if (-not (Test-Path -LiteralPath $client)) {
    $release = Invoke-RestMethod -Uri 'https://api.github.com/repos/cloudflare/cloudflared/releases/latest'
    $asset = $release.assets | Where-Object name -eq 'cloudflared-windows-amd64.exe'
    if (-not $asset -or -not $asset.digest) { throw 'Official download/checksum metadata unavailable.' }
    Invoke-WebRequest -Uri $asset.browser_download_url -OutFile $client
    $actual = 'sha256:' + (Get-FileHash -LiteralPath $client -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($actual -ne $asset.digest) { throw 'Cloudflared checksum mismatch. Do not run the downloaded file.' }
}
$health = Invoke-RestMethod -Uri "http://127.0.0.1:$Port/api/health"
if (-not $health.ok) { throw 'Start the backend first.' }
Write-Host 'Share only the HTTPS trycloudflare.com address printed below with your instructor/team.'
Write-Host 'New accounts require the invitation code printed by start_demo.ps1.'
Write-Host 'Keep the laptop, Docker, backend terminal and this terminal running. Ctrl+C closes the link.'
& $client tunnel --url "http://127.0.0.1:$Port" --no-autoupdate
exit $LASTEXITCODE
