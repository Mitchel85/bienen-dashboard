const WebSocket = require('ws');

const ws = new WebSocket('ws://localhost:3001');

ws.on('open', () => {
    function sendDraw(data) {
        ws.send(JSON.stringify({ type: 'draw', data }));
    }
    
    // Canvas löschen
    sendDraw({ action: 'clear' });
    
    setTimeout(() => {
        // Kopf (Kreis)
        const headX = 400;
        const headY = 200;
        const headRadius = 50;
        for (let i = 0; i <= 100; i++) {
            const angle = (i / 100) * 2 * Math.PI;
            const x = headX + headRadius * Math.cos(angle);
            const y = headY + headRadius * Math.sin(angle);
            sendDraw({
                x, y,
                color: '#8B4513', // braun
                size: 4,
                action: i === 0 ? 'start' : 'move',
                isEraser: false
            });
        }
        
        // Körper (ovaler Rumpf)
        setTimeout(() => {
            const bodyWidth = 120;
            const bodyHeight = 80;
            for (let i = 0; i <= 100; i++) {
                const angle = (i / 100) * 2 * Math.PI;
                const x = headX + (bodyWidth / 2) * Math.cos(angle);
                const y = headY + 70 + (bodyHeight / 2) * Math.sin(angle);
                sendDraw({
                    x, y,
                    color: '#8B4513',
                    size: 4,
                    action: i === 0 ? 'start' : 'move',
                    isEraser: false
                });
            }
        }, 100);
        
        // Ohren (zwei Dreiecke)
        setTimeout(() => {
            // Linkes Ohr
            sendDraw({ x: headX - 30, y: headY - 30, color: '#8B4513', size: 4, action: 'start', isEraser: false });
            sendDraw({ x: headX - 60, y: headY - 70, color: '#8B4513', size: 4, action: 'move', isEraser: false });
            sendDraw({ x: headX - 10, y: headY - 60, color: '#8B4513', size: 4, action: 'move', isEraser: false });
            sendDraw({ x: headX - 30, y: headY - 30, color: '#8B4513', size: 4, action: 'move', isEraser: false });
            
            // Rechtes Ohr
            sendDraw({ x: headX + 30, y: headY - 30, color: '#8B4513', size: 4, action: 'start', isEraser: false });
            sendDraw({ x: headX + 60, y: headY - 70, color: '#8B4513', size: 4, action: 'move', isEraser: false });
            sendDraw({ x: headX + 10, y: headY - 60, color: '#8B4513', size: 4, action: 'move', isEraser: false });
            sendDraw({ x: headX + 30, y: headY - 30, color: '#8B4513', size: 4, action: 'move', isEraser: false });
        }, 200);
        
        // Augen (zwei Punkte)
        setTimeout(() => {
            sendDraw({ x: headX - 15, y: headY - 10, color: '#000000', size: 6, action: 'start', isEraser: false });
            sendDraw({ x: headX + 15, y: headY - 10, color: '#000000', size: 6, action: 'start', isEraser: false });
        }, 300);
        
        // Nase (dreieckig)
        setTimeout(() => {
            sendDraw({ x: headX, y: headY + 10, color: '#000000', size: 5, action: 'start', isEraser: false });
            sendDraw({ x: headX - 10, y: headY + 25, color: '#000000', size: 5, action: 'move', isEraser: false });
            sendDraw({ x: headX + 10, y: headY + 25, color: '#000000', size: 5, action: 'move', isEraser: false });
            sendDraw({ x: headX, y: headY + 10, color: '#000000', size: 5, action: 'move', isEraser: false });
        }, 350);
        
        // Mund (lächelnd)
        setTimeout(() => {
            for (let i = 0; i <= 20; i++) {
                const t = i / 20;
                const x = headX - 20 + t * 40;
                const y = headY + 40 + Math.sin(t * Math.PI) * 10;
                sendDraw({
                    x, y,
                    color: '#FF0000',
                    size: 2,
                    action: i === 0 ? 'start' : 'move',
                    isEraser: false
                });
            }
        }, 400);
        
        // Beine (vier Linien)
        const legPositions = [
            { x: headX - 40, y: headY + 130 },
            { x: headX - 10, y: headY + 130 },
            { x: headX + 10, y: headY + 130 },
            { x: headX + 40, y: headY + 130 }
        ];
        setTimeout(() => {
            legPositions.forEach((pos) => {
                sendDraw({ x: pos.x, y: headY + 80, color: '#8B4513', size: 5, action: 'start', isEraser: false });
                sendDraw({ x: pos.x, y: pos.y, color: '#8B4513', size: 5, action: 'move', isEraser: false });
            });
        }, 450);
        
        // Schwanz (gebogene Linie)
        setTimeout(() => {
            for (let i = 0; i <= 20; i++) {
                const t = i / 20;
                const x = headX + 70 + t * 30;
                const y = headY + 100 + Math.sin(t * Math.PI) * 40;
                sendDraw({
                    x, y,
                    color: '#8B4513',
                    size: 4,
                    action: i === 0 ? 'start' : 'move',
                    isEraser: false
                });
            }
        }, 500);
        
        // Pfoten (kleine Kreise)
        setTimeout(() => {
            legPositions.forEach((pos) => {
                sendDraw({ x: pos.x, y: pos.y + 5, color: '#000000', size: 8, action: 'start', isEraser: false });
            });
        }, 550);
        
        // Text "WUFF!"
        setTimeout(() => {
            const text = "WUFF!";
            const startX = 350;
            const startY = 500;
            for (let i = 0; i < text.length; i++) {
                const x = startX + i * 30;
                const y = startY + (i % 2) * 15;
                sendDraw({
                    x, y,
                    color: '#FF6600',
                    size: 10,
                    action: 'start',
                    isEraser: false
                });
            }
        }, 600);
        
        // Verbindung schließen
        setTimeout(() => {
            ws.close();
        }, 700);
    }, 500);
});

ws.on('error', (err) => {
    console.error('WebSocket error:', err.message);
});