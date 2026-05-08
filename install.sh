#!/bin/bash
echo "Tworzenie wirtualnego środowiska..."
python3 -m venv venv

echo "Instalacja bibliotek..."
source venv/bin/activate
pip install -r requirements.txt

echo "Uruchamianie gry..."
python3 main.py