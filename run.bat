@echo off
REM Navigate to the directory of the virtual environment
cd /d %~dp0

REM Activate the virtual environment
call .\.venv\Scripts\activate

REM Run the Python script
python crawler_gui.py

REM Optional: Deactivate the virtual environment
deactivate
