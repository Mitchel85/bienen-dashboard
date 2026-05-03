const http = require('http');
const fs = require('fs');
const path = require('path');
const WebSocket = require('ws');

// ---------------------------
// 1. CORS Configuration
// ---------------------------
const ALLOWED_ORIGINS = [
  'https://oc.clawdia26.com',
  'http://localhost:3001',
  'http://localhost:3000'
];

// ---------------------------
// 2. Rate‑Limiting Configuration
// ---------------------------
const RATE_LIMIT_WINDOW_MS = 1000; // 1 second
const RATE_LIMIT_MAX_MESSAGES = 50; // max messages per window per client
const clientRateMap = new Map(); // ip -> { count, resetTime }

function rateLimit(ip) {
  const now = Date.now();
  let record = clientRateMap.get(ip);
  if (!record || now > record.resetTime) {
    record = { count: 0, resetTime: now + RATE_LIMIT_WINDOW_MS };
    clientRateMap.set(ip, record);
  }
  record.count++;
  if (record.count > RATE_LIMIT_MAX_MESSAGES) {
    return false; // over limit
  }
  return true;
}

// ---------------------------
// 3. HTML escaping (basic, no external lib)
// ---------------------------
function escapeHtml(text) {
  if (typeof text !== 'string') return text;
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

// ---------------------------
// 4. Input Validation Schema
// ---------------------------
function isValidDrawMessage(data) {
  // Must be an object
  if (!data || typeof data !== 'object') return false;

  // Allowed actions for freehand drawing
  if (data.action) {
    if (!['start', 'move', 'clear'].includes(data.action)) return false;
    if (data.action === 'clear') return true; // no further checks needed
    if (typeof data.x !== 'number' || typeof data.y !== 'number') return false;
    if (data.x < 0 || data.x > 2000 || data.y < 0 || data.y > 2000) return false;
    if (data.color && typeof data.color !== 'string') return false;
    if (data.size && (typeof data.size !== 'number' || data.size < 1 || data.size > 100)) return false;
    return true;
  }

  // Structured shapes (rect, circle, line, arc, text)
  if (data.type) {
    if (!['rect', 'circle', 'line', 'arc', 'text'].includes(data.type)) return false;
    // Common required fields
    if (typeof data.x !== 'number' || typeof data.y !== 'number') return false;
    if (data.x < 0 || data.x > 2000 || data.y < 0 || data.y > 2000) return false;
    if (data.color && typeof data.color !== 'string') return false;
    // Type‑specific checks
    if (data.type === 'rect') {
      if (typeof data.w !== 'number' || typeof data.h !== 'number') return false;
    }
    if (data.type === 'circle') {
      if (typeof data.r !== 'number' || data.r < 0) return false;
    }
    if (data.type === 'line') {
      if (typeof data.w !== 'number' || typeof data.h !== 'number') return false;
    }
    if (data.type === 'arc') {
      if (typeof data.r !== 'number' || data.r < 0) return false;
      if (typeof data.start !== 'number' || typeof data.end !== 'number') return false;
    }
    if (data.type === 'text') {
      if (typeof data.text !== 'string') return false;
      // Escape text before broadcasting
      data.text = escapeHtml(data.text);
    }
    return true;
  }

  return false;
}

// ---------------------------
// 5. Main Server
// ---------------------------
const staticDir = path.join(__dirname, 'public_3001');

const server = http.createServer((req, res) => {
  // CORS headers
  const origin = req.headers.origin;
  if (ALLOWED_ORIGINS.includes(origin)) {
    res.setHeader('Access-Control-Allow-Origin', origin);
  }
  res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    res.writeHead(200);
    res.end();
    return;
  }

  // Static file serving
  let filePath = path.join(staticDir, req.url === '/' ? 'index.html' : req.url);
  if (!filePath.startsWith(staticDir)) {
    res.writeHead(403);
    return res.end('Forbidden');
  }

  fs.readFile(filePath, (err, data) => {
    if (err) {
      res.writeHead(404);
      res.end('Not found');
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

// History of draw events (same as before)
let drawHistory = [];

wss.on('connection', (ws, req) => {
  const clientIp = req.socket.remoteAddress;
  console.log(`Client connected from ${clientIp}`);

  // Rate‑limit connection attempt? Not now.

  ws.send('🦞 Verbunden mit dem sicheren Clawdia Spiel‑Server');

  // Send history to new client
  drawHistory.forEach(msg => {
    ws.send(msg);
  });

  ws.on('message', (message) => {
    const msgStr = message.toString();

    // 1. Rate‑Limiting check
    if (!rateLimit(clientIp)) {
      console.log(`Rate limit exceeded for ${clientIp}, disconnecting`);
      ws.close(1008, 'Rate limit exceeded');
      return;
    }

    // 2. Parse & Validate
    let parsed;
    try {
      parsed = JSON.parse(msgStr);
    } catch (e) {
      console.log(`Invalid JSON from ${clientIp}: ${msgStr.substring(0, 50)}`);
      ws.send(JSON.stringify({ error: 'Invalid JSON' }));
      return;
    }

    // Expect { type: 'draw', data: {...} }
    if (!parsed.type || parsed.type !== 'draw' || !parsed.data) {
      console.log(`Invalid message structure from ${clientIp}`);
      ws.send(JSON.stringify({ error: 'Invalid message structure' }));
      return;
    }

    if (!isValidDrawMessage(parsed.data)) {
      console.log(`Invalid draw data from ${clientIp}: ${JSON.stringify(parsed.data)}`);
      ws.send(JSON.stringify({ error: 'Invalid draw data' }));
      return;
    }

    // 3. History management (same as before)
    if (parsed.data.action === 'clear') {
      drawHistory = [];
    } else {
      drawHistory.push(msgStr);
      if (drawHistory.length > 50000) drawHistory.shift();
    }

    // 4. Broadcast validated message to all clients
    wss.clients.forEach((client) => {
      if (client.readyState === WebSocket.OPEN) {
        client.send(msgStr);
      }
    });
  });

  ws.on('close', () => {
    console.log(`Client ${clientIp} disconnected`);
    // Clean up rate‑limit record after a while (optional)
    setTimeout(() => clientRateMap.delete(clientIp), RATE_LIMIT_WINDOW_MS * 2);
  });
});

server.listen(3002, '0.0.0.0', () => {
  console.log('✅ Secure server läuft auf Port 3002 (HTTP & WebSocket)');
  console.log('🔒 Rate‑Limiting: 50 Nachrichten/Sekunde pro Client');
  console.log('🌐 CORS erlaubt: ' + ALLOWED_ORIGINS.join(', '));
});