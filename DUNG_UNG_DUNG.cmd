@echo off
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0study_app\stop.ps1"
if errorlevel 1 pause
