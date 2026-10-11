@echo off
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0study_app\launch.ps1"
if errorlevel 1 pause
