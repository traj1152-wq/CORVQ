param([ValidateSet('backend','frontend')][string]$Service='backend')
$ErrorActionPreference='Stop'
Set-Location $PSScriptRoot
if ($Service -eq 'backend') {
    & "$PSScriptRoot\.venv\Scripts\python.exe" -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
} else {
    $runtimeRoot=Join-Path $env:USERPROFILE '.cache\codex-runtimes\codex-primary-runtime\dependencies'
    if (-not (Get-Command node -ErrorAction SilentlyContinue)) { $env:PATH=(Join-Path $runtimeRoot 'node\bin')+';'+$env:PATH }
    Set-Location frontend
    & node node_modules/vite/bin/vite.js --host 127.0.0.1
}
