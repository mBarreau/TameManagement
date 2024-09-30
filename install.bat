python -m venv .venv
CALL .\.venv\Scripts\activate
python.exe -m pip install --upgrade pip
pip install dash dash-bootstrap-components icalendar recurring_ical_events
python db.py
pause