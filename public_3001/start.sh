#!/bin/bash
cd /data/.openclaw/workspace/public_3001
export NODE_PATH=/usr/local/lib/node_modules/openclaw/node_modules
nohup node server_combined.js > combined.log 2>&1 &
echo "Started combined server on port 3001"
