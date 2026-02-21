@echo off
cd /d "%~dp0"
echo Starting dashboard at http://localhost:8501
streamlit run dashboard/app.py --server.port 8501 --server.address 0.0.0.0
