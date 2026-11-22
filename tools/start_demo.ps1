param([int]$Port = 8001)
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $projectRoot
$demoDirectory = Join-Path $projectRoot 'tmp/presentation'
New-Item -ItemType Directory -Force -Path $demoDirectory | Out-Null
$invitePath = Join-Path $demoDirectory 'demo-invite.txt'
if (-not $env:CODEFORGE_INVITE_CODE) {
    if (Test-Path -LiteralPath $invitePath) {
        $env:CODEFORGE_INVITE_CODE = (Get-Content -LiteralPath $invitePath -Raw).Trim()
    } else {
        $env:CODEFORGE_INVITE_CODE = 'CF-' + [Guid]::NewGuid().ToString('N')
        Set-Content -LiteralPath $invitePath -Value $env:CODEFORGE_INVITE_CODE
    }
}
Write-Host "Local website: http://127.0.0.1:$Port"
Write-Host "New-account invitation code: $env:CODEFORGE_INVITE_CODE"
Write-Host 'Keep this terminal open. Ctrl+C stops the backend. Run one server process only.'
& (Join-Path $projectRoot '.venv/Scripts/python.exe') -m uvicorn backend.app:app --host 127.0.0.1 --port $Port --proxy-headers --forwarded-allow-ips 127.0.0.1
exit $LASTEXITCODE
