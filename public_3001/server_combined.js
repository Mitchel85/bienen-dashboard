const express = require("express");
const http = require("http");
const WebSocket = require("ws");
const path = require("path");
const crypto = require("crypto");

const PORT = 3001;
const STATIC_DIR = "/data/.openclaw/workspace/public_3001";

const RATE_LIMIT_WINDOW_MS = 60 * 1000;
const RATE_LIMIT_MAX_PER_IP = 100;
const MAX_CONNECTIONS = 50;
const MAX_EVENTS_PER_USER_PER_MIN = 200;
const MAX_HISTORY_SIZE = 100000;
const MAX_REQUEST_BODY = "1kb";
const MIN_COORD = 0;
const MAX_COORD = 2000;
const COLOR_HEX_REGEX = /^#[0-9A-Fa-f]{1,8}$/;
const VALID_ACTIONS = new Set(["start", "move", "clear", "fill"]);

const rateLimitMap = new Map();
const wsEventMap = new Map();

function checkRateLimit(ip) {
    const now = Date.now();
    let entry = rateLimitMap.get(ip);
    if (!entry || now > entry.resetTime) {
        entry = { count: 0, resetTime: now + RATE_LIMIT_WINDOW_MS };
        rateLimitMap.set(ip, entry);
    }
    entry.count++;
    return entry.count <= RATE_LIMIT_MAX_PER_IP;
}

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

function validateDrawEvent(data) {
    if (!data.action || !VALID_ACTIONS.has(data.action)) return { valid: false, reason: "Invalid Action" };
    if (data.action === "clear") return { valid: true };
    if (typeof data.x !== "number" || typeof data.y !== "number") return { valid: false, reason: "x,y must be numbers" };
    if (data.x < MIN_COORD || data.x > MAX_COORD || data.y < MIN_COORD || data.y > MAX_COORD) return { valid: false, reason: "Out of bounds" };
    if (data.color && !COLOR_HEX_REGEX.test(data.color)) return { valid: false, reason: "Invalid color" };
    return { valid: true };
}

function sanitize(obj, blacklist = new Set()) {
    if (obj === null || typeof obj !== "object" || Array.isArray(obj)) return obj;
    const cleaned = {};
    for (const [key, value] of Object.entries(obj)) {
        if (blacklist.has(key) || ["__proto__", "constructor", "prototype"].includes(key)) continue;
        cleaned[key] = value;
    }
    return cleaned;
}

const app = express();
const server = http.createServer(app);
const wss = new WebSocket.Server({ server, maxPayload: 1024 });

app.use((req, res, next) => {
    const ip = req.headers["x-forwarded-for"] || req.connection.remoteAddress;
    if (!checkRateLimit(ip)) return res.status(429).json({ error: "Rate limit exceeded" });
    res.setHeader("X-Content-Type-Options", "nosniff");
    next();
});

app.use(express.json({ limit: MAX_REQUEST_BODY }));
app.use(express.static(STATIC_DIR));

app.get("/", (req, res) => {
    res.sendFile(path.join(STATIC_DIR, "index.html"));
});

const clients = new Set();
const drawingHistory = [];
let clientCounter = 0;

wss.on("connection", (ws, req) => {
    if (clients.size >= MAX_CONNECTIONS) {
        ws.close(1013, "Server full");
        return;
    }
    const clientId = `client_${++clientCounter}_${crypto.randomBytes(2).toString("hex")}`;
    clients.add(ws);
    ws.clientId = clientId;
    console.log(`Connected: ${clientId}`);

    if (drawingHistory.length > 0) {
        ws.send(JSON.stringify({ type: "history", data: drawingHistory.slice(-500) }));
    }

    ws.on("message", (message) => {
        try {
            if (!checkWsRateLimit(ws.clientId)) return;
            const data = JSON.parse(message.toString());
            if (!data.type || !data.data) return;
            const validation = validateDrawEvent(data.data);
            if (!validation.valid) return;
            const sanitizedData = { type: data.type, data: sanitize(data.data) };
            drawingHistory.push(sanitizedData);
            clients.forEach(client => {
                if (client !== ws && client.readyState === WebSocket.OPEN) {
                    client.send(JSON.stringify(sanitizedData));
                }
            });
        } catch (e) { console.error(e); }
    });

    ws.on("close", () => {
        clients.delete(ws);
        wsEventMap.delete(clientId);
    });
});

server.listen(PORT, "0.0.0.0", () => {
    console.log(`Server running on port ${PORT}`);
});
