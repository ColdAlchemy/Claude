@echo off
rem Opcional: so use se o celular nao conseguir abrir a pagina.
rem Cria uma regra no Firewall do Windows liberando as portas 8765-8774 (so redes privadas).
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo Pedindo permissao de administrador...
    powershell.exe -NoProfile -Command "Start-Process -FilePath '%~f0' -Verb RunAs"
    exit /b
)
netsh advfirewall firewall delete rule name="Celular Mouse" >nul 2>&1
netsh advfirewall firewall add rule name="Celular Mouse" dir=in action=allow protocol=TCP localport=8765-8774 profile=private
echo.
echo Pronto. Se sua rede Wi-Fi estiver como "Publica", mude para "Particular"
echo em Configuracoes ^> Rede e Internet ^> Wi-Fi ^> (sua rede) ^> Tipo de perfil de rede.
pause
