@echo off
rem M.A.D. for Windows: runs mad.py with Python 3 (py launcher, else python).
where py >nul 2>nul
if %errorlevel%==0 (
    py -3 "%~dp0mad.py"
) else (
    python "%~dp0mad.py"
)
