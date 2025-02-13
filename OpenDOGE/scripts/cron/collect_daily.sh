#!/bin/bash
cd /app
python scripts/collect_data.py >> /var/log/opendoge/collector.log 2>&1 