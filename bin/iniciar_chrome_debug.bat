@echo off
chcp 65001 > nul
echo ======================================================================
echo    INICIANDO GOOGLE CHROME EM MODO DE DEPURAÇÃO (PORTA 9222)
echo ======================================================================
echo.
echo [ATENÇÃO] Feche COMPLETAMENTE todas as janelas do Google Chrome antes!
echo Se houver alguma instância rodando em segundo plano, a depuração remota
echo NÃO será ativada e o script de automação não funcionará.
echo.
pause
echo.
echo Tentando iniciar o Google Chrome...

set CHROME_PATH=""
if exist "C:\Program Files\Google\Chrome\Application\chrome.exe" (
    set CHROME_PATH="C:\Program Files\Google\Chrome\Application\chrome.exe"
) else if exist "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" (
    set CHROME_PATH="C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
) else (
    echo [AVISO] Chrome não encontrado nos caminhos padrão. Tentando comando geral 'chrome.exe'...
    set CHROME_PATH="chrome.exe"
)

start "" %CHROME_PATH% --remote-debugging-port=9222

echo.
echo [SUCESSO] Chrome iniciado com a porta 9222 habilitada.
echo.
echo IMPORTANTE:
echo 1. Faça login no SEI na janela que acabou de se abrir.
echo 2. Mantenha essa janela do Chrome aberta.
echo 3. Execute o script de automação no terminal:
echo    .venv\Scripts\python.exe exportador_sei.py
echo.
pause
