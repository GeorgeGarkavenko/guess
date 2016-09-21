@echo off

REM This script converts pricer adjustment export files to MMS import format
setlocal
cd /d %~dp0\..
call scripts\set_iss_env.cmd

set PYTHONPATH=%PYTHONPATH%;%SE_HOME%\scripts\app

python "%SE_HOME%\scripts\app\poller.py" %SE_HOME%\properties\Guess.properties

endlocal
if %1a EQU a pause
