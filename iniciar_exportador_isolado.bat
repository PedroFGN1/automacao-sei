@echo off
chcp 65001 > nul
echo ======================================================================
echo    EXECUTANDO EXPORTADOR SEI (NAVEGADOR ISOLADO)
echo ======================================================================
echo.
echo Este script abrira o Google Chrome de forma isolada e persistente.
echo.
echo Instrucoes:
echo 1. Na janela do navegador que se abrir, digite a URL do SEI (se solicitado no terminal) e faca o login.
echo 2. O script detectara o login e iniciara a exportacao em lote automaticamente.
echo 3. Os PDFs serao salvos na pasta C:\SEI_Exportacoes.
echo.
.venv\Scripts\python.exe exportador_sei_isoleted.py
echo.
pause
