@echo off
powershell -ExecutionPolicy Bypass -File "%~dp0smoke_test_openclaw.ps1" -RepoRoot "%~dp0.."
