const express = require('express');
const http = require('http');
const WebSocket = require('ws');
const path = require('path');
const crypto = require('crypto');

const PORT = 3001;
const STATIC_DIR = __dirname;

// =============================================
// SEC: Sicherheitskonfiguration
// =============================================

// Max Requests pro IP (Zeitfenster 1 Minute)
const RATE_LIMIT_WINDOW_MS = 60 * 1000;
const RATE_LIMIT_MAX_PER_IP = 100;

// Max parallele WebSocket-Verbindungen
const MAX_CONNECTIONS = 50;

// Max Events pro User (WebSocket, pro Minute)
const MAX_EVENTS_PER_USER_PER_MIN = 200;

// Max History-Groesse (Events)
const MAX_HISTORY_SIZE = 100000;

// Max Payload-Groesse (Bytes)
const MAX_REQUEST_BODY = '1kb';

// Erlaubte Canvas-Groessen
const MIN_COORD = 0;
const MAX_COORD = 2000;

// Max Color-Laenge (HEX)
const COLOR_HEX_REGEX = /^#[0-9A-Fa-f]{1,8}$/;

// Rate-Limit Speicher
const rateLimitMap = new Map(); // { "ip:timestamp": count }
const wsEventMap = new Map(); // { clientId: { count, resetTime } }

// Erlaubte Action-Typen
const VALID_ACTIONS = new Set(['start', 'move', 'clear', 'fill']);

// Helfer: Rate-Limit Check
function checkRateLimit(ip) {
    const now = Date.now();
    const windowStart = now - RATE_LIMIT_WINDOW_MS;

    // Alte Eintraege bereinigen
    for (const [key, count] of rateLimitMap.entries()) {
        if (count.resetTime < now) {
            rateLimitMap.delete(key);
        }
    }

    // Eintrag holen oder erstellen
    let entry = rateLimitMap.get(ip);
    if (!entry) {
        entry = { count: 0, resetTime: now + RATE_LIMIT_WINDOW_MS };
        rateLimitMap.set(ip, entry);
    }

    entry.count++;

    if (entry.count > RATE_LIMIT_MAX_PER_IP) {
        return false; // Limit ueberschritten
    }

    return true;
}

// Helfer: WS-Event-Rate-Limit Check
function checkWsRateLimit(clientId) {
    const now = Date.now();
    let entry = wsEventMap.get(clientId);

    if (!entry || now > entry.resetTime) {
        entry = { count: 0, resetTime: now + RATE_LIMIT_WINDOW_MS };
        wsEventMap.set(clientId, entry);
    }

    entry.count++;

    return entry.count <= MAX_EVENTS_PER_USER_PER_MIN;
}

// Helper: Input validieren
function validateDrawEvent(data) {
    // action muss gueltig sein
    if (!data.action || !VALID_ACTIONS.has(data.action)) {
        return { valid: false, reason: 'Ungueltige Action' };
    }

    // clear benötigt keine Koordinaten
    if (data.action === 'clear') {
        return { valid: true };
    }

    // Koordinaten müssen Zahlen sein
    if (typeof data.x !== 'number' || typeof data.y !== 'number') {
        return { valid: false, reason: 'x und y muessen Zahlen sein' };
    }

    // Koordinaten innerhalb gueltiger Bereich
    if (data.x < MIN_COORD || data.x > MAX_COORD || data.y < MIN_COORD || data.y > MAX_COORD) {
        return { valid: false, reason: 'Koordinaten ausserhalb des gueltigen Bereichs' };
    }

    // Color validieren (wenn vorhanden)
    if (data.color !== undefined) {
        if (typeof data.color !== 'string') {
            return { valid: false, reason: 'Color muss String sein' };
        }
        // Pruefe auf gueltigen HEX
        if (!COLOR_HEX_REGEX.test(data.color)) {
            return { valid: false, reason: 'Ungueltige Farbe (nur HEX)' };
        }
        // Laengen-Check (Schutz vor Buffer Overflow)
        if (data.color.length > 50) {
            return { valid: false, reason: 'Color zu lang' };
        }
    }

    // Size validieren
    if (data.size !== undefined) {
        if (typeof data.size !== 'number' || data.size < 0.1 || data.size > 100) {
            return { valid: false, reason: 'Size muss zwischen 0.1 und 100 sein' };
        }
    }

    return { valid: true };
}

// Helper: XSS-Entfernung aus Strings (sanitization)
function sanitize(obj, blacklist = new Set()) {
    // Entferne alle Keys die __proto__ oder constructor enthalten
    if (obj === null || typeof obj !== 'object' || Array.isArray(obj)) {
        return obj;
    }

    const cleaned = {};
    for (const [key, value] of Object.entries(obj)) {
        if (blacklist.has(key)) continue;
        if (key === '__proto__' || key === 'constructor' || key === 'prototype') continue;
        cleaned[key] = value;
    }
    return cleaned;
}

// =============================================
// SERVER
// =============================================

const app = express();
const server = http.createServer(app);
const wss = new WebSocket.Server({ 
    server,
    maxPayload: 1024, // Max 1KB pro WebSocket-Nachricht
    perMessageDeflate: false // Performance + Angriffsoberfläche reduzieren
});

// Rate-Limit Middleware (global)
app.use((req, res, next) => {
    const ip = req.connection.remoteAddress || req.socket.remoteAddress || 'unknown';
    if (!checkRateLimit(ip)) {
        return res.status(429).json({ 
            error: 'Rate-Limit ueberschritten. Warte eine Minute.' 
        });
    }

    // Header setzen: Security
    res.setHeader('X-Content-Type-Options', 'nosniff');
    res.setHeader('X-Frame-Options', 'DENY');
    res.setHeader('Content-Security-Policy', "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; font-src 'self' https://cdnjs.cloudflare.com; img-src 'self' data:;");
    res.setHeader('X-XSS-Protection', '1; mode=block');

    next();
});

// Body-Parsing begrenzen
app.use(express.json({ limit: MAX_REQUEST_BODY }));

// Statische Dateien ausliefern
app.use(express.static(STATIC_DIR, {
    etag: true,
    lastModified: true,
    maxAge: 3600000 // 1h Cache für statische Dateien
}));

// Startseite
app.get('/', (req, res) => {
    res.sendFile(path.join(STATIC_DIR, 'index.html'));
});

// API-Endpoint zum Senden eines Zeichen-Events (für Clawdia)
app.post('/api/draw', (req, res) => {
    // Input validieren
    if (!req.body || typeof req.body !== 'object') {
        return res.status(400).json({ error: 'Invalid request body' });
    }

    // Sanitize: Entferne prototype-pollution keys
    const cleaned = sanitize(req.body);
    const { type = 'draw', data } = cleaned;

    if (!data) {
        return res.status(400).json({ error: 'Missing data' });
    }

    // Zeichnung validieren
    const validation = validateDrawEvent(data);
    if (!validation.valid) {
        return res.status(400).json({ error: validation.reason });
    }

    // Max History size prüfen
    if (drawingHistory.length >= MAX_HISTORY_SIZE) {
        return res.status(429).json({ error: 'History-Voll. Warte bis zum naechsten Clear.' });
    }

    const event = { type, data: sanitize(data) };
    drawingHistory.push(event);

    // Broadcast an alle Clients
    clients.forEach(client => {
        if (client.readyState === WebSocket.OPEN) {
            try {
                client.send(JSON.stringify(event));
            } catch (e) {
                // Fehlerhaftes Client entfernen
                clients.delete(client);
            }
        }
    });

    res.json({ ok: true, clients: clients.size });
});

// API-Endpoint zum Abrufen der Zeichnungs-Historie
app.get('/api/history', (req, res) => {
    res.json({ ok: true, history: drawingHistory.slice(-100) }); // Nur die letzten 100 Events
});

// =============================================
// WEBSOCKET
// =============================================

const clients = new Set();
const drawingHistory = []; // Speichert alle Zeichen-Events für neue Clients

// Client-Zähler für Rate-Limiting
let clientCounter = 0;

wss.on('connection', (ws, req) => {
    // Max connections prüfen
    if (clients.size >= MAX_CONNECTIONS) {
        ws.close(1013, 'Server voll - versuche es spater nochmal');
        return;
    }

    // Client ID zuweisen
    const clientId = `client_${++clientCounter}_${crypto.randomBytes(4).toString('hex')}`;
    
    console.log(`Neuer Client verbunden: ${clientId}`);
    
    clients.add(ws);
    ws.clientId = clientId;

    // Sende aktuelle Zeichnung an neuen Client
    if (drawingHistory.length > 0) {
        const historySlice = drawingHistory.slice(-500); // Max 500 Events senden
        try {
            ws.send(JSON.stringify({
                type: 'history',
                data: historySlice
            }));
        } catch (e) {
            console.error('Fehler beim Senden der History:', e);
        }
    }

    ws.on('message', (message) => {
        try {
            // Rate-Limit prüfen
            if (!checkWsRateLimit(ws.clientId)) {
                ws.send(JSON.stringify({ 
                    type: 'error', 
                    data: { reason: 'Rate-Limit ueberschritten. Warte kurz.' }
                }));
                return;
            }

            const raw = message.toString();

            // Max-Nachrichten-Laenge prüfen
            if (raw.length > 1024) {
                ws.send(JSON.stringify({ 
                    type: 'error', 
                    data: { reason: 'Nachricht zu lang (max 1KB).' }
                }));
                return;
            }

            const data = JSON.parse(raw);

            // Input validieren
            if (!data.type || !data.data) {
                return;
            }

            // Validierung für Zeichenevents
            const validation = validateDrawEvent(data.data);
            if (!validation.valid) {
                ws.send(JSON.stringify({
                    type: 'error',
                    data: { reason: `Ungueltige Daten: ${validation.reason}` }
                }));
                return;
            }

            // Max History prüfen
            if (drawingHistory.length >= MAX_HISTORY_SIZE) {
                return;
            }

            // Validiertes Event speichern
            const sanitizedData = sanitize(data, new Set(['constructor', 'prototype', '__proto__']));
            drawingHistory.push(sanitizedData);

            // Broadcast an alle anderen Clients
            clients.forEach(client => {
                if (client !== ws && client.readyState === WebSocket.OPEN) {
                    client.send(JSON.stringify(sanitizedData));
                }
            });

        } catch (e) {
            console.error(`Fehler von ${ws.clientId}:`, e.message);
        }
    });

    ws.on('close', () => {
        console.log(`Client getrennt: ${ws.clientId}`);
        clients.delete(ws);
        wsEventMap.delete(ws.clientId);
    });

    ws.on('error', (err) => {
        console.error(`WebSocket-Fehler (${ws.clientId}):`, err.message);
    });
});

// Auto-Clear (nur wenn wirklich voll)
setInterval(() => {
    if (drawingHistory.length > MAX_HISTORY_SIZE * 0.8) {
        const removed = drawingHistory.splice(0, Math.floor(drawingHistory.length * 0.5));
        console.log(`History gekürzt: ${removed.length} Events entfernt`);
    }
    
    // Rate-Limit Speicher bereinigen
    const now = Date.now();
    for (const [key, entry] of rateLimitMap.entries()) {
        if (entry.resetTime < now) {
            rateLimitMap.delete(key);
        }
    }
    for (const [key, entry] of wsEventMap.entries()) {
        if (entry.resetTime < now) {
            wsEventMap.delete(key);
        }
    }
}, 30000);

// =============================================
// START
// =============================================

server.listen(PORT, '172.16.1.2', () => {
    console.log(`✅ Gesicherter Mal-Server läuft auf http://172.16.1.2:${PORT}`);
    console.log(`🔒 Security: Rate-Limit (100/min), Max Connections (${MAX_CONNECTIONS}), Input-Validierung`);
    console.log(`📁 Statische Dateien aus: ${STATIC_DIR}`);
    console.log(`🦞 WebSocket-Endpoint: ws://172.16.1.2:${PORT}`);
});

// Graceful shutdown
process.on('SIGINT', () => {
    console.log('Server wird heruntergefahren...');
    wss.close(() => {
        server.close(() => {
            process.exit(0);
        });
    });
});
