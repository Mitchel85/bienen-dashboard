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

wss.on('connection', (ws) => {
  console.log('Client connected');
  ws.send('🦞 Verbunden mit dem Clawdia Spiel-Server');
  
  ws.on('message', (message) => {
    console.log('Received: %s', message);
    // Simple echo broadcast for drawing games
    wss.clients.forEach((client) => {
      if (client.readyState === WebSocket.OPEN) {
        client.send(message.toString());
      }
    });
  });
  
  ws.on('close', () => {
    console.log('Client disconnected');
  });
});

server.listen(3001, '0.0.0.0', () => {
  console.log('Server läuft auf Port 3001 (HTTP & WebSocket)');
});
