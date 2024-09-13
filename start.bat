@echo off
CALL ".\.venv\Scripts\activate"
start "" python "dashapp.py"
:Test
Curl http://127.0.0.1:8050
If "%errorlevel%" neq "0" goto :Test
start "" "chrome.exe" "http://127.0.0.1:8050"
exit