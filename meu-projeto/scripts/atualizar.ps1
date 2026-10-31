# Atualiza o repositório com o que o Claude enviou da nuvem.
# Uso (a partir da pasta meu-projeto):  .\scripts\atualizar.ps1

$ErrorActionPreference = "Stop"

# Sobe até a raiz do repositório Git.
$raiz = git rev-parse --show-toplevel
if (-not $raiz) {
    Write-Host "Esta pasta não está dentro de um repositório Git." -ForegroundColor Red
    exit 1
}
Set-Location $raiz

$pendentes = git status --porcelain
if ($pendentes) {
    Write-Host "Você tem alterações locais não salvas:" -ForegroundColor Yellow
    git status --short
    Write-Host "Faça commit antes de atualizar para evitar conflitos." -ForegroundColor Yellow
    exit 1
}

git pull
Write-Host "Pronto. Arquivos atualizados." -ForegroundColor Green
