@echo off
chcp 65001 > nul
echo ======================================================================
echo    EXECUTANDO EXPORTADOR SEI EM MODO DIAGNÓSTICO/DEBUG
echo ======================================================================
echo.
echo Este script executará a automação gerando logs e capturas de tela 
echo detalhadas caso ocorra falha ao localizar elementos no SEI.
echo.
.venv\Scripts\python.exe exportador_sei_isoleted_debug.py
echo.
echo Pressione qualquer tecla para encerrar.
pause
