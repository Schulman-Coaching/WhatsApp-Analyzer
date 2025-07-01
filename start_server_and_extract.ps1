# WhatsApp MCP Server Starter and Data Extractor
# This script starts the WhatsApp MCP server and then runs the data extraction

Write-Host "===== WhatsApp Chat Data Analysis for Monetization Opportunities =====" -ForegroundColor Cyan
Write-Host ""

# Path to the WhatsApp MCP server
$serverPath = "C:\Users\elie\OneDrive\Documents\Cline\MCP\whatsapp-mcp\whatsapp-mcp-server\main.py"

# Check if the server file exists
if (Test-Path $serverPath) {
    # Start the server in a new PowerShell window
    Write-Host "Starting WhatsApp MCP server..." -ForegroundColor Yellow
    $serverProcess = Start-Process powershell -ArgumentList "-Command", "python '$serverPath'" -PassThru
    
    # Give the server some time to start up
    Write-Host "Waiting for server to initialize (10 seconds)..." -ForegroundColor Yellow
    Start-Sleep -Seconds 10
    
    # Check if the server process is still running
    if (-not $serverProcess.HasExited) {
        Write-Host "WhatsApp MCP server is running." -ForegroundColor Green
        
        # Run the extraction script
        Write-Host "Starting data extraction..." -ForegroundColor Yellow
        $extractScript = Join-Path $PSScriptRoot "extract_whatsapp_data.py"
        
        # Get any command line arguments passed to this script and forward them
        $extractArgs = $args
        
        # Run the extraction script
        & python $extractScript $extractArgs
        
        # Ask user if they want to keep the server running
        $keepRunning = Read-Host "Do you want to keep the WhatsApp MCP server running? (y/n)"
        if ($keepRunning -ne "y") {
            # Stop the server process
            Stop-Process -Id $serverProcess.Id -Force
            Write-Host "WhatsApp MCP server stopped." -ForegroundColor Yellow
        } else {
            Write-Host "WhatsApp MCP server is still running. You'll need to close it manually when done." -ForegroundColor Yellow
        }
    } else {
        Write-Host "Failed to start WhatsApp MCP server. Please check the server path and try again." -ForegroundColor Red
    }
} else {
    Write-Host "WhatsApp MCP server not found at: $serverPath" -ForegroundColor Red
    Write-Host "Please check the path in this script and update it to match your installation." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
