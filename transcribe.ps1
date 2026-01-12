# Transcribe video files using GPU-accelerated whisper
# Usage: .\transcribe.ps1 "path\to\video.mp4"
# Or drag and drop onto the .bat version for convenience

param(
    [Parameter(Mandatory=$true, Position=0, HelpMessage="Path to video file")]
    [string]$VideoPath
)

# Resolve to absolute path (handles relative paths and special characters safely)
$VideoPath = (Resolve-Path -LiteralPath $VideoPath -ErrorAction Stop).Path

if (-not (Test-Path -LiteralPath $VideoPath)) {
    Write-Error "File not found: $VideoPath"
    exit 1
}

$VideoName = Split-Path -Leaf $VideoPath
Write-Host "Transcribing: $VideoName"
Write-Host ""

# Get script directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# Run transcription (Python handles the path safely)
& python "$ScriptDir\transcribe_video.py" $VideoPath

Write-Host ""
Write-Host "Done!"
