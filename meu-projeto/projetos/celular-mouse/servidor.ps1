# Celular Mouse - inicia o servidor. Use o iniciar.bat (duplo clique).
# Este arquivo e' so ASCII de proposito: o PowerShell 5.1 le .ps1 sem BOM como ANSI.
# Opcao: iniciar.bat -SemHttps  (so modo toque; nao cria nem usa certificado)
param(
    [int]$Porta = 8765,
    [switch]$SemNavegador,
    [switch]$SemHttps
)

$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# O navegador do celular so libera o giroscopio em paginas HTTPS. Criamos (uma vez)
# o arquivo cert.pfx nesta pasta. NAO usa a loja de certificados do Windows.
# O celular vai avisar "conexao nao particular": e' normal, toque em Avancado e Continuar.
$pfx = Join-Path $PSScriptRoot 'cert.pfx'
if (-not $SemHttps) {
    $precisa = (-not (Test-Path $pfx)) -or ((Get-Item $pfx).LastWriteTime -lt (Get-Date).AddYears(-2))
    if ($precisa) {
        try {
            Write-Host 'Criando certificado local (so na primeira vez)...'
            $cert = [System.IO.File]::ReadAllText((Join-Path $PSScriptRoot 'certificado.cs'), [System.Text.Encoding]::UTF8)
            Add-Type -TypeDefinition $cert -Language CSharp
            [CelularMouse.Certificado]::Criar($PSScriptRoot)
        }
        catch {
            Write-Host "Aviso: nao consegui criar o certificado HTTPS: $_" -ForegroundColor Yellow
            Write-Host 'Seguindo so com o modo toque. Veja o README (secao HTTPS).' -ForegroundColor Yellow
        }
    }
}

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
    [CelularMouse.Programa]::Executar($PSScriptRoot, $Porta, (-not $SemNavegador.IsPresent), (-not $SemHttps.IsPresent))
}
catch {
    Write-Host "Erro: $_" -ForegroundColor Red
    exit 1
}
