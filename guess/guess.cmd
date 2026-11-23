@echo off
rem Guess the number, for Windows.  No colour: cmd has no simple way to
rem print the escape character.
set /a SECRET=%RANDOM% %% 100 + 1
set TRIES=0
echo GUESS THE NUMBER
echo.
echo I am thinking of a number from
echo 1 to 100. Q gives up.
echo.
:loop
set GUESS=
set /p GUESS=Your guess: 
if not defined GUESS goto loop
if /i "%GUESS%"=="q" (
    echo It was %SECRET%.
    exit /b 0
)
echo %GUESS%| findstr /r "^[0-9][0-9]*$" >nul || (
    echo Numbers only, please.
    goto loop
)
set /a TRIES+=1
if %GUESS% LSS %SECRET% (
    echo Higher.
    goto loop
)
if %GUESS% GTR %SECRET% (
    echo Lower.
    goto loop
)
echo Yes! %SECRET% in %TRIES% tries.
