#!/bin/bash
cd /data/.openclaw/workspace
node websocket-server.js > websocket.log 2>&1 &