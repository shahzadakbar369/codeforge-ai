$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
foreach ($entry in @(@('tunnel.pid', 'share_demo.ps1'), @('backend.pid', 'start_demo.ps1'))) {
    $pidPath = Join-Path $projectRoot ('tmp/presentation/' + $entry[0])
    if (-not (Test-Path -LiteralPath $pidPath)) { continue }
    $demoProcessId = [int](Get-Content -LiteralPath $pidPath -Raw).Trim()
    $rootProcess = Get-CimInstance Win32_Process -Filter "ProcessId = $demoProcessId"
    if (-not $rootProcess) { continue }
    if ($rootProcess.CommandLine -notlike ('*' + $projectRoot + '\tools\' + $entry[1] + '*')) {
        Write-Warning "Saved process $demoProcessId no longer belongs to this demo; leaving it alone."
        continue
    }
    # Only descendants of the verified demo launcher are eligible for stopping.
    function Stop-DemoChildren([int]$parentId) {
        foreach ($child in @(Get-CimInstance Win32_Process -Filter "ParentProcessId = $parentId")) {
            Stop-DemoChildren $child.ProcessId
            Stop-Process -Id $child.ProcessId -ErrorAction SilentlyContinue
        }
    }
    Stop-DemoChildren $demoProcessId
    Stop-Process -Id $demoProcessId -ErrorAction SilentlyContinue
    Write-Host ('Stopped demo launcher: ' + $entry[1])
}
Write-Host 'For manually opened demo terminals, use Ctrl+C in each terminal.'
