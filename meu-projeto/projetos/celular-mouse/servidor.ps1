# Celular Mouse - inicia o servidor. Use o iniciar.bat (duplo clique).
# Este arquivo e' so ASCII de proposito: o PowerShell 5.1 le .ps1 sem BOM como ANSI.
param(
    [int]$Porta = 8765,
    [switch]$SemNavegador
)

$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# O navegador do celular so libera o giroscopio em paginas HTTPS. Criamos (uma vez)
# um certificado so deste PC. O celular vai avisar "conexao nao particular":
# e' normal, toque em Avancado e Continuar.
try {
    $existe = Get-ChildItem 'Cert:\CurrentUser\My' | Where-Object {
        $_.Subject -eq 'CN=Celular Mouse' -and $_.HasPrivateKey -and $_.NotAfter -gt (Get-Date).AddDays(30)
    }
    if (-not $existe) {
        Write-Host 'Criando certificado local (so na primeira vez)...'
        New-SelfSignedCertificate -Subject 'CN=Celular Mouse' -DnsName 'celular-mouse', 'localhost' `
            -CertStoreLocation 'Cert:\CurrentUser\My' -KeyAlgorithm RSA -KeyLength 2048 `
            -KeySpec KeyExchange -HashAlgorithm SHA256 -KeyExportPolicy NonExportable `
            -NotAfter (Get-Date).AddYears(3) | Out-Null
    }
}
catch {
    Write-Host "Aviso: nao consegui criar o certificado HTTPS ($_)." -ForegroundColor Yellow
    Write-Host 'O modo sensor nao vai funcionar; o modo toque continua.' -ForegroundColor Yellow
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
    [CelularMouse.Programa]::Executar($PSScriptRoot, $Porta, (-not $SemNavegador.IsPresent))
}
catch {
    Write-Host "Erro: $_" -ForegroundColor Red
    exit 1
}
