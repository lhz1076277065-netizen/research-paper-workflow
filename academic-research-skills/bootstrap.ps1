# No policy bypass, administrator elevation, global setup or automatic download.
$ErrorActionPreference = "Stop"
foreach ($candidate in @("python3", "python", "py")) {
    $cmd = Get-Command $candidate -ErrorAction SilentlyContinue
    if ($null -ne $cmd) {
        $prefix = @()
        if ($candidate -eq "py") { $prefix = @("-3") }
        & $cmd.Source @prefix -c "import sys; raise SystemExit(sys.version_info < (3,10))" 2>$null
        if ($LASTEXITCODE -eq 0) {
            & $cmd.Source @prefix (Join-Path $PSScriptRoot "scripts/environment.py") @args
            exit $LASTEXITCODE
        }
    }
}
Write-Error "Python >=3.10 is required for executable setup. Install it through an authorized official or system installer. Text-only protocol use needs no Python."
exit 3
