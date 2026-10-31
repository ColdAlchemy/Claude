# Sincroniza automaticamente com o que o Claude envia da nuvem.
# Deixe rodando em um terminal do Antigravity. Para parar: Ctrl+C.
# Uso (a partir da pasta meu-projeto):  .\scripts\sincronizar.ps1
# Intervalo em segundos (padrão 15):    .\scripts\sincronizar.ps1 -Intervalo 30

param([int]$Intervalo = 15)

$raiz = git rev-parse --show-toplevel 2>$null
if (-not $raiz) {
    Write-Host "Esta pasta não está dentro de um repositório Git." -ForegroundColor Red
    exit 1
}
Set-Location $raiz

Write-Host "Sincronizando a cada $Intervalo s. Ctrl+C para parar." -ForegroundColor Cyan

while ($true) {
    $antes = git rev-parse HEAD
    # --ff-only: só avança; nunca cria merge nem sobrescreve trabalho seu.
    $saida = git pull --ff-only --quiet 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "$(Get-Date -Format HH:mm:ss) Não foi possível atualizar (mudanças locais conflitantes?):" -ForegroundColor Yellow
        Write-Host $saida
    } else {
        $depois = git rev-parse HEAD
        if ($antes -ne $depois) {
            Write-Host "$(Get-Date -Format HH:mm:ss) Atualizado:" -ForegroundColor Green
            git log --oneline "$antes..$depois"
        }
    }
    Start-Sleep -Seconds $Intervalo
}
