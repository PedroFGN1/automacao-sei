@echo off
setlocal DisableDelayedExpansion

cd /d "%~dp0"

set "PYTHON=%~dp0..\.venv\Scripts\python.exe"
set "SCRIPT=%~dp0..\scripts\indexador_pdf.py"

if not exist "%PYTHON%" (
    echo.
    echo [ERRO] Python do ambiente virtual nao encontrado:
    echo "%PYTHON%"
    echo.
    pause
    exit /b 1
)

if not exist "%SCRIPT%" (
    echo.
    echo [ERRO] Script Python nao encontrado:
    echo "%SCRIPT%"
    echo.
    pause
    exit /b 1
)

:MENU
cls
echo ======================================================================
echo             INDEXADOR E BUSCADOR DE PROCESSOS SEI
echo ======================================================================
echo.
echo [1] Atualizar banco lendo PDFs do caminho padrao
echo [2] Atualizar banco usando um caminho personalizado
echo [3] Pesquisar palavra-chave ou termo no banco
echo [4] Sair
echo.
echo ======================================================================

set "opcao="
set /p "opcao=Escolha uma opcao de 1 a 4: "

if "%opcao%"=="1" goto OPCAO1
if "%opcao%"=="2" goto OPCAO2
if "%opcao%"=="3" goto OPCAO3
if "%opcao%"=="4" goto SAIR

echo.
echo [ERRO] Opcao invalida.
pause
goto MENU


:OPCAO1
cls
echo ======================================================================
echo INDEXACAO NO CAMINHO PADRAO
echo ======================================================================
echo.
echo Executando indexacao...
echo.

"%PYTHON%" "%SCRIPT%"
set "RESULTADO=%ERRORLEVEL%"

echo.
if not "%RESULTADO%"=="0" (
    echo [ERRO] O programa terminou com codigo %RESULTADO%.
) else (
    echo [OK] Indexacao concluida.
)

echo.
pause
goto MENU


:OPCAO2
cls
echo ======================================================================
echo INDEXACAO EM CAMINHO PERSONALIZADO
echo ======================================================================
echo.

set "caminho="
set /p "caminho=Digite o caminho completo da pasta com os PDFs: "

if not defined caminho (
    echo.
    echo [ERRO] Nenhum caminho foi informado.
    pause
    goto MENU
)

pushd "%caminho%" >nul 2>&1

if errorlevel 1 (
    echo.
    echo [ERRO] A pasta nao existe ou nao esta acessivel:
    echo "%caminho%"
    echo.
    pause
    goto MENU
)

popd

echo.
echo Executando indexacao em:
echo "%caminho%"
echo.

"%PYTHON%" "%SCRIPT%" --dir "%caminho%"
set "RESULTADO=%ERRORLEVEL%"

echo.
if not "%RESULTADO%"=="0" (
    echo [ERRO] O programa terminou com codigo %RESULTADO%.
) else (
    echo [OK] Indexacao concluida.
)

echo.
pause
goto MENU


:OPCAO3
cls
echo ======================================================================
echo PESQUISA NO BANCO
echo ======================================================================
echo.

set "termo="
set /p "termo=Digite o termo que procura: "

if not defined termo (
    echo.
    echo [ERRO] O termo de busca nao pode ficar vazio.
    pause
    goto MENU
)

set "termo_ignorar="
set /p "termo_ignorar=Digite o termo que NAO pode ter nos registros (deixe em branco se nenhum): "

echo.
echo Pesquisando por: "%termo%"
if defined termo_ignorar (
    echo Ignorando registros com: "%termo_ignorar%"
)
echo.

set "enviar_n8n="
set /p "enviar_n8n=Deseja enviar os PDFs encontrados para o webhook do n8n? (S/N): "

echo.
if defined termo_ignorar (
    if /i "%enviar_n8n%"=="S" (
        echo [*] Pesquisando e enviando resultados para o n8n...
        echo.
        "%PYTHON%" "%SCRIPT%" --search "%termo%" --ignore "%termo_ignorar%" --n8n
    ) else (
        echo [*] Executando apenas a pesquisa...
        echo.
        "%PYTHON%" "%SCRIPT%" --search "%termo%" --ignore "%termo_ignorar%"
    )
) else (
    if /i "%enviar_n8n%"=="S" (
        echo [*] Pesquisando e enviando resultados para o n8n...
        echo.
        "%PYTHON%" "%SCRIPT%" --search "%termo%" --n8n
    ) else (
        echo [*] Executando apenas a pesquisa...
        echo.
        "%PYTHON%" "%SCRIPT%" --search "%termo%"
    )
)
set "RESULTADO=%ERRORLEVEL%"

echo.
if not "%RESULTADO%"=="0" (
    echo [ERRO] A operacao terminou com codigo %RESULTADO%.
) else (
    echo [OK] Operacao concluida com sucesso.
)

echo.
pause
goto MENU


:SAIR
echo.
echo Encerrando o indexador...
timeout /t 2 /nobreak >nul
endlocal
exit /b 0