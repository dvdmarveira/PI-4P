@echo off
REM Inicia a API em background
cd backend
start "" python venv\Scripts\python.exe api.py > api.log 2> api.err
cd ..

REM Inicia o simulador de sensores em background
cd backend
start "" python venv\Scripts\python.exe simulador_sensores.py > simulador.log 2> simulador.err
cd ..

REM Abre o dashboard no navegador padrão
start "" frontend\dashboard.html
