#!/bin/bash

# Inicia a API em background
cd backend
./venv/bin/python api.py > api.log 2> api.err &
cd ..

# Inicia o simulador de sensores em background
cd backend
./venv/bin/python simulador_sensores.py > simulador.log 2> simulador.err &
cd ..

# Abre o dashboard no navegador padrão
open frontend/dashboard.html
