#!/bin/bash

<<<<<<< HEAD
=======
#Windows
# entra na pasta backend
cd backend

# cria o ambiente virtual
python -m venv venv

# ativa o ambiente virtual
venv\Scripts\activate

# instala as dependências
pip install -r requirements.txt

#Startar
python app.py


#Mac/OS
>>>>>>> 3f426f2 (Ajustes)
# Verifica se o Python 3 está instalado
if ! command -v python3 &> /dev/null
then
    echo "Python 3 não está instalado. Por favor, instale o Python 3 para continuar."
    exit 1
fi

# Verifica se o pip está instalado
if ! command -v pip3 &> /dev/null
then
    echo "pip3 não está instalado. Por favor, instale o pip3 para continuar."
    exit 1
fi

# Cria o ambiente virtual na pasta backend
cd backend
python3 -m venv venv

# Ativa o ambiente virtual
source venv/bin/activate

# Instala as dependências
pip3 install -r requirements.txt

# Informa os próximos passos
echo "
Ambiente configurado com sucesso!"
echo "Para iniciar o ambiente de desenvolvimento, execute:"
echo "./start_dev.sh"
