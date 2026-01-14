param (
    [Parameter(Mandatory=$true)]
    [string]$Message
)

$ErrorActionPreference = "Stop"

try {
    Write-Host "Starting maintenance and push process..." -ForegroundColor Cyan

    # Ensure PUSH_LOG.md exists
    if (-not (Test-Path ".\PUSH_LOG.md")) {
        "| Date | Message | Author |`n|---|---|---|" | Out-File ".\PUSH_LOG.md" -Encoding utf8
    }

    # Prepare Log Entry
    $Date = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $Author = $env:USERNAME
    if ([string]::IsNullOrEmpty($Author)) { $Author = "User" }
    
    # Append to PUSH_LOG.md
    # We use a temporary file approach or direct append to ensure encoding is correct
    $LogEntry = "| $Date | $Message | $Author |"
    Add-Content -Path ".\PUSH_LOG.md" -Value $LogEntry -Encoding utf8

    # Git Operations
    Write-Host "Adding files to git..." -ForegroundColor Green
    git add .

    Write-Host "Committing changes..." -ForegroundColor Green
    git commit -m "$Message"

    Write-Host "Pushing to remote (origin/master)..." -ForegroundColor Green
    git push origin master

    Write-Host "Done! Maintenance and push completed." -ForegroundColor Cyan
}
catch {
    Write-Host "Error occurred: $_" -ForegroundColor Red
    exit 1
}
