# Celular Mouse - inicia o servidor. Use o iniciar.bat (duplo clique).
# Este arquivo e' so ASCII de proposito: o PowerShell 5.1 le .ps1 sem BOM como ANSI.
param(
    [int]$Porta = 8765,
    [switch]$SemNavegador
)

$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

try {
    $codigo = [System.IO.File]::ReadAllText((Join-Path $PSScriptRoot 'servidor.cs'), [System.Text.Encoding]::UTF8)
    Add-Type -TypeDefinition $codigo -Language CSharp
}
catch {
    Write-Host "Nao consegui preparar o servidor:" -ForegroundColor Red
    Write-Host $_ -ForegroundColor Red
    exit 1
}

try {
    [CelularMouse.Programa]::Executar($PSScriptRoot, $Porta, (-not $SemNavegador.IsPresent))
}
catch {
    Write-Host "Erro: $_" -ForegroundColor Red
    exit 1
}
