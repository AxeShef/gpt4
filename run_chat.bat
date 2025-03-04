@echo off
chcp 65001 > nul
echo Запуск GPT чата...
py -3 -c "import sys; print('Python path:', sys.executable); print('Python version:', sys.version)"
py -3 -c "import customtkinter; print('CustomTkinter version:', customtkinter.__version__)"
py -3 gpt_chat.py
pause 