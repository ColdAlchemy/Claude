@echo off
chcp 65001 >nul
title Celular Mouse
cd /d "%~dp0"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0servidor.ps1" %*
echo.
echo Servidor encerrado. Aperte uma tecla para fechar.
pause >nul
