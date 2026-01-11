@echo off
REM Drag and drop a video file onto this script to transcribe it
REM Or run: transcribe.bat "path\to\video.mp4"

if "%~1"=="" (
    echo Usage: Drag a video file onto this script
    echo    or: transcribe.bat "path\to\video.mp4"
    pause
    exit /b 1
)

echo Transcribing: %~1
echo.
python "%~dp0transcribe_video.py" "%~1"
echo.
echo Done! Press any key to close.
pause >nul
