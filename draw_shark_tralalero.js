const WebSocket = require('ws');

const ws = new WebSocket('ws://localhost:3001');

ws.on('open', () => {
    function sendDraw(data) {
        ws.send(JSON.stringify({ type: 'draw', data }));
    }
    
    // Canvas löschen
    sendDraw({ action: 'clear' });
    
    setTimeout(() => {
        // Hai-Körper (oval)
        const centerX = 400;
        const centerY = 300;
        const bodyWidth = 200;
        const bodyHeight = 100;
        
        // Körperumriss
        for (let i = 0; i <= 100; i++) {
            const angle = (i / 100) * 2 * Math.PI;
            const x = centerX + (bodyWidth / 2) * Math.cos(angle);
            const y = centerY + (bodyHeight / 2) * Math.sin(angle);
            sendDraw({
                x, y,
                color: '#333333',
                size: 4,
                action: i === 0 ? 'start' : 'move',
                isEraser: false
            });
        }
        
        // Rückenflosse
        setTimeout(() => {
            sendDraw({ x: centerX + 80, y: centerY - 40, color: '#333333', size: 4, action: 'start', isEraser: false });
            sendDraw({ x: centerX + 100, y: centerY - 80, color: '#333333', size: 4, action: 'move', isEraser: false });
            sendDraw({ x: centerX + 120, y: centerY - 40, color: '#333333', size: 4, action: 'move', isEraser: false });
        }, 100);
        
        // Schwanzflosse
        setTimeout(() => {
            sendDraw({ x: centerX - 100, y: centerY, color: '#333333', size: 4, action: 'start', isEraser: false });
            sendDraw({ x: centerX - 140, y: centerY - 40, color: '#333333', size: 4, action: 'move', isEraser: false });
            sendDraw({ x: centerX - 140, y: centerY + 40, color: '#333333', size: 4, action: 'move', isEraser: false });
            sendDraw({ x: centerX - 100, y: centerY, color: '#333333', size: 4, action: 'move', isEraser: false });
        }, 200);
        
        // Auge
        setTimeout(() => {
            sendDraw({ x: centerX + 60, y: centerY - 20, color: '#000000', size: 6, action: 'start', isEraser: false });
        }, 300);
        
        // Mund (grinsend)
        setTimeout(() => {
            for (let i = 0; i <= 20; i++) {
                const t = i / 20;
                const x = centerX + 30 + t * 40;
                const y = centerY + 10 + Math.sin(t * Math.PI) * 15;
                sendDraw({
                    x, y,
                    color: '#FF0000',
                    size: 3,
                    action: i === 0 ? 'start' : 'move',
                    isEraser: false
                });
            }
        }, 350);
        
        // Drei Beine mit blauen Schuhen (Nike)
        const legPositions = [
            { x: centerX - 20, y: centerY + 50 },
            { x: centerX + 20, y: centerY + 50 },
            { x: centerX + 60, y: centerY + 50 }
        ];
        
        setTimeout(() => {
            legPositions.forEach((pos, idx) => {
                // Bein (Linie)
                sendDraw({ x: pos.x, y: centerY + 30, color: '#333333', size: 4, action: 'start', isEraser: false });
                sendDraw({ x: pos.x, y: pos.y, color: '#333333', size: 4, action: 'move', isEraser: false });
                
                // Schuh (blaues Rechteck)
                const shoeWidth = 25;
                const shoeHeight = 15;
                for (let i = 0; i <= 4; i++) {
                    let x, y;
                    if (i === 0) { x = pos.x - shoeWidth/2; y = pos.y; }
                    else if (i === 1) { x = pos.x + shoeWidth/2; y = pos.y; }
                    else if (i === 2) { x = pos.x + shoeWidth/2; y = pos.y + shoeHeight; }
                    else if (i === 3) { x = pos.x - shoeWidth/2; y = pos.y + shoeHeight; }
                    else { x = pos.x - shoeWidth/2; y = pos.y; }
                    
                    sendDraw({
                        x, y,
                        color: '#0066CC',
                        size: 5,
                        action: i === 0 ? 'start' : 'move',
                        isEraser: false
                    });
                }
                
                // Nike Swoosh (einfache Kurve)
                for (let i = 0; i <= 10; i++) {
                    const t = i / 10;
                    const swooshX = pos.x - 5 + t * 15;
                    const swooshY = pos.y + 5 + Math.sin(t * Math.PI) * 5;
                    sendDraw({
                        x: swooshX, y: swooshY,
                        color: '#FFFFFF',
                        size: 2,
                        action: i === 0 ? 'start' : 'move',
                        isEraser: false
                    });
                }
            });
        }, 400);
        
        // Text "TRALALERO TRALALA"
        setTimeout(() => {
            const text = "TRALALERO TRALALA";
            const startX = 200;
            const startY = 500;
            for (let i = 0; i < text.length; i++) {
                // Einfache Punkte für Buchstaben (statt echter Schrift)
                const x = startX + i * 20;
                const y = startY + (i % 3) * 10;
                sendDraw({
                    x, y,
                    color: '#FF00FF',
                    size: 8,
                    action: 'start',
                    isEraser: false
                });
            }
        }, 600);
        
        // Verbindung schließen
        setTimeout(() => {
            ws.close();
        }, 800);
    }, 500);
});

ws.on('error', (err) => {
    console.error('WebSocket error:', err.message);
});