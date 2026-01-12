@echo off
REM Drag and drop a video file onto this script to transcribe it
REM Or run: transcribe.bat "path\to\video.mp4"
REM
REM Note: For filenames with special characters, use the PowerShell version:
REM   .\transcribe.ps1 "path\to\video.mp4"

if "%~1"=="" (
    echo Usage: Drag a video file onto this script
    echo    or: transcribe.bat "path\to\video.mp4"
    echo.
    echo For filenames with special characters, use: .\transcribe.ps1
    pause
    exit /b 1
)

REM Validate file exists before processing
if not exist "%~1" (
    echo Error: File not found: %~1
    pause
    exit /b 1
)

echo Transcribing: %~nx1
echo.
python "%~dp0transcribe_video.py" "%~f1"
echo.
echo Done! Press any key to close.
pause >nul
