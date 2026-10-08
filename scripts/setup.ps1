$ErrorActionPreference = "Stop"

$Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$VenvDir = Join-Path $Root ".venv"
$VenvPython = Join-Path $VenvDir "Scripts\python.exe"

if (-not (Test-Path $VenvPython)) {
    $launcher = Get-Command python -ErrorAction Stop
    & $launcher.Source -m venv $VenvDir
}

& $VenvPython -m pip install --upgrade pip
& $VenvPython -m pip install -r (Join-Path $Root "requirements.txt")

$CursorDir = Join-Path $Root ".cursor"
New-Item -ItemType Directory -Force -Path $CursorDir | Out-Null

& $VenvPython -c @"
import json, pathlib, sys
root = pathlib.Path(sys.argv[1])
python = pathlib.Path(sys.argv[2])
payload = {
    'mcpServers': {
        name: {
            'command': str(python),
            'args': ['-m', module],
            'cwd': str(root),
            'env': {'MINING_DATA': 'fixture'},
        }
        for name, module in {
            'mining-news-mcp': 'mining_news_mcp',
            'mineral-pdf-mcp': 'mineral_pdf_mcp',
            'lme-price-mcp': 'lme_price_mcp',
        }.items()
    }
}
text = json.dumps(payload, indent=2, ensure_ascii=False) + chr(10)
(root / 'mcp-config.json').write_text(text, encoding='utf-8')
(root / '.cursor' / 'mcp.json').write_text(text, encoding='utf-8')
"@ $Root $VenvPython

Write-Host "venv: $VenvPython"
Write-Host "wrote mcp-config.json and .cursor/mcp.json"
