# Executable Path Contract (.bat)

Este documento define o contrato de formato padrão e tratamento de caminhos que os arquivos `.bat` migrados para a pasta `bin/` devem obedecer para invocar os scripts Python.

## 1. Padrão de Invocação de Interpretador e Scripts

Todo arquivo `.bat` localizado em `bin/` deve estruturar seus caminhos usando o prefixo `%~dp0..\` para acessar a raiz do projeto e delegar a execução ao Python virtual local (`.venv`).

### Estrutura Genérica
```batch
@echo off
rem Define suporte a cores ANSI no console do Windows
if "%OS%"=="Windows_NT" (
  reg query "HKCU\Console" /v VirtualTerminalLevel >nul 2>&1
  if errorlevel 1 (
    reg add "HKCU\Console" /v VirtualTerminalLevel /t REG_DWORD /d 1 /f >nul 2>&1
  )
)

"%~dp0..\.venv\Scripts\python.exe" "%~dp0..\scripts\nome_do_script.py" [argumentos...]
pause
```

## 2. Padrão de Caminho de Dependência de Dados

Caso os scripts necessitem referenciar arquivos localizados na raiz do repositório (como `processos.txt` ou o arquivo SQLite `automacao.db`), a execução do Python a partir de `bin/` usando `%~dp0..\` garantirá que o CWD (Current Working Directory) do Python possa ler e gravar os arquivos no mesmo nível relativo original.
