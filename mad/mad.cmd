@echo off
rem M.A.D. for Windows: runs mad.py with Python 3 (the py launcher, else python).
where py >nul 2>nul
if %errorlevel%==0 (
    py -3 "%~dp0mad.py"
    exit /b
)
rem 9009: no python at all, or only the Microsoft Store stub.
python "%~dp0mad.py"
if %errorlevel%==9009 (
    echo M.A.D. needs Python 3, which is not
    echo installed on this gateway.
    exit /b 1
)
