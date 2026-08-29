$output = & python "d:\sif sentimental\test_frontend_and_alerts.py" 2>&1
$output | Out-File -FilePath "d:\sif sentimental\frontend_test_output.txt" -Encoding UTF8
Write-Host "Test completed. Output saved to d:\sif sentimental\frontend_test_output.txt"
exit 0
