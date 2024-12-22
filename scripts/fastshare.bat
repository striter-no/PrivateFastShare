@echo off
setlocal
set "CURRENT_DIR=%cd%"
E: && cd "E:\py_projs\PrivateFastShare"  
call .\venv\Scripts\activate.bat
py .\main.py
call .\venv\Scripts\deactivate.bat
cd "%CURRENT_DIR%"
endlocal