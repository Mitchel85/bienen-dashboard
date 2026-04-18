#!/bin/sh
cd /data/.openclaw/workspace/public_3001
export NODE_PATH=/usr/local/lib/node_modules/openclaw/node_modules
exec node server_ws.js