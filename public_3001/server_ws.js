const express = require('express');
const http = require('http');
const WebSocket = require('ws');
const path = require('path');

const PORT = 3001;
const STATIC_DIR = __dirname;

const app = express();
const server = http.createServer(app);
const wss = new WebSocket.Server({ server });

// Statische Dateien ausliefern
app.use(express.static(STATIC_DIR));
app.use(express.json());

// Startseite
app.get('/', (req, res) => {
    res.sendFile(path.join(STATIC_DIR, 'index.html'));
});

// API‑Endpoint zum Senden eines Zeichen‑Events (für Clawdia)
app.post('/api/draw', (req, res) => {
    const { type = 'draw', data } = req.body;
    if (!data) {
        return res.status(400).json({ error: 'Missing data' });
    }
    const event = { type, data };
    drawingHistory.push(event);
    // Broadcast an alle verbundenen Clients
    clients.forEach(client => {
        if (client.readyState === WebSocket.OPEN) {
            client.send(JSON.stringify(event));
        }
    });
    res.json({ ok: true, clients: clients.size });
});

// API‑Endpoint zum Abrufen der aktuellen Zeichnungshistorie
app.get('/api/history', (req, res) => {
    res.json({
        ok: true,
        history: drawingHistory,
        totalEvents: drawingHistory.length,
        activeClients: clients.size
    });
});

// WebSocket‑Logik für gemeinsames Malen
const clients = new Set();
const drawingHistory = []; // Speichert alle Zeichen‑Events für neue Clients

wss.on('connection', (ws) => {
    console.log('Neuer Client verbunden');
    clients.add(ws);

    // Sende die bisherige Zeichnung an den neuen Client
    if (drawingHistory.length > 0) {
        ws.send(JSON.stringify({
            type: 'history',
            data: drawingHistory
        }));
    }

    ws.on('message', (message) => {
        try {
            const data = JSON.parse(message);
            // Validiere und speichere Event
            if (data.type && data.data) {
                drawingHistory.push(data);
                // Broadcast an alle anderen Clients
                clients.forEach(client => {
                    if (client !== ws && client.readyState === WebSocket.OPEN) {
                        client.send(JSON.stringify(data));
                    }
                });
            }
        } catch (e) {
            console.error('Fehler beim Verarbeiten der Nachricht:', e);
        }
    });

    ws.on('close', () => {
        console.log('Client getrennt');
        clients.delete(ws);
    });

    ws.on('error', (err) => {
        console.error('WebSocket‑Fehler:', err);
    });
});

// Alle 30 Sekunden leeren wir die History, um Speicher zu sparen (optional)
setInterval(() => {
    if (drawingHistory.length > 100000) {
        drawingHistory.length = 0;
        console.log('Drawing history cleared');
    }
}, 30000);

server.listen(PORT, '172.16.1.2', () => {
    console.log(`✅ Gemeinsamer Mal‑Server läuft auf http://172.16.1.2:${PORT}`);
    console.log(`📁 Statische Dateien aus: ${STATIC_DIR}`);
    console.log(`🦞 WebSocket‑Endpoint: ws://172.16.1.2:${PORT}`);
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