@echo off
echo Tworzenie wirtualnego srodowiska...
python -m venv venv

echo Instalacja bibliotek...
CALL venv\Scripts\activate
pip install -r requirements.txt

echo Uruchamianie gry...
python main.py
pause