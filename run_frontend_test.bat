@echo off
cd /d "d:\sif sentimental"
python test_frontend_and_alerts.py > frontend_test_output.txt 2>&1
echo Test completed. Results saved to frontend_test_output.txt
pause
