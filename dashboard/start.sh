#!/bin/bash
set -e
python scripts/download_db.py
streamlit run dashboard/app.py \
    --server.port 7860 \
    --server.address 0.0.0.0 \
    --server.headless true
