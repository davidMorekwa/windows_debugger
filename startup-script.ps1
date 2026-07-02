$processName = "CalculatorApp"

# Check if the Calculator is already running
$process = Get-Process -Name $processName -ErrorAction SilentlyContinue

if (-not $process) {
    # Launch via the modern UWP protocol
    Start-Process -FilePath "calc.exe" | Out-Null
    
    # Wait for the UWP app package to initialize 
    Start-Sleep -Milliseconds 600
    
    # Fetch the process again
    $process = Get-Process -Name $processName -ErrorAction SilentlyContinue
}

if ($process) {
    # If multiple instances exist, return all IDs
    $process.Id
} else {
    Write-Error "Failed to start or locate Calculator process."
}
