const http = require('http');
const fs = require('fs');
const path = require('path');
const WebSocket = require('ws');

const staticDir = path.join(__dirname, 'public_3001');

const server = http.createServer((req, res) => {
  let filePath = path.join(staticDir, req.url === '/' ? 'index.html' : req.url);
  
  if (!filePath.startsWith(staticDir)) {
    res.writeHead(403);
    return res.end("Forbidden");
  }

  fs.readFile(filePath, (err, data) => {
    if (err) {
      res.writeHead(404);
      res.end("Not found");
    } else {
      const ext = path.extname(filePath);
      const types = {
        '.html': 'text/html',
        '.js': 'text/javascript',
        '.css': 'text/css',
        '.png': 'image/png',
        '.jpg': 'image/jpeg'
      };
      res.writeHead(200, { 'Content-Type': types[ext] || 'text/plain' });
      res.end(data);
    }
  });
});

const wss = new WebSocket.Server({ server });

// History of draw events
let drawHistory = [];

wss.on('connection', (ws) => {
  console.log('Client connected');
  ws.send('🦞 Verbunden mit dem Clawdia Spiel-Server');
  
  // Send history to new client
  drawHistory.forEach(msg => {
    ws.send(msg);
  });
  
  ws.on('message', (message) => {
    const msgStr = message.toString();
    console.log('Received message size:', msgStr.length);
    
    try {
        const parsed = JSON.parse(msgStr);
        if (parsed.type === 'draw') {
            if (parsed.data && parsed.data.action === 'clear') {
                drawHistory = []; // Clear history on clear event
            } else {
                drawHistory.push(msgStr);
                // Limit history size to prevent memory leaks (e.g., 50000 strokes)
                if (drawHistory.length > 50000) drawHistory.shift();
            }
        }
    } catch (e) {
        // Not JSON or other error, ignore for history
    }

    // Broadcast
    wss.clients.forEach((client) => {
      if (client.readyState === WebSocket.OPEN) {
        client.send(msgStr);
      }
    });
  });
  
  ws.on('close', () => {
    console.log('Client disconnected');
  });
});

server.listen(3001, '0.0.0.0', () => {
  console.log('Server läuft auf Port 3001 (HTTP & WebSocket) - mit History-Puffer');
});