@echo off
chcp 65001 > nul
echo ======================================================================
echo    EXECUTANDO EXPORTADOR SEI (NAVEGADOR ISOLADO)
echo ======================================================================
echo.
echo Este script abrirá o Google Chrome de forma isolada e persistente.
echo.
echo Instruções:
echo 1. Na janela do navegador que se abrir, digite a URL do SEI (se solicitado no terminal) e faça o login.
echo 2. O script detectará o login e iniciará a exportação em lote automaticamente.
echo 3. Os PDFs serão salvos na pasta C:\SEI_Exportacoes.
echo.
.venv\Scripts\python.exe exportador_sei_isoleted.py
echo.
pause
