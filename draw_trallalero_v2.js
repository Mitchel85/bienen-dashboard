const WebSocket = require('ws');

const ws = new WebSocket('ws://localhost:3001');

ws.on('open', () => {
    function sendDraw(data) {
        ws.send(JSON.stringify({ type: 'draw', data }));
    }
    
    sendDraw({ action: 'clear' });
    
    setTimeout(() => {
        const colors = ['#FF0000', '#FF7F00', '#FFFF00', '#00FF00', '#0000FF', '#4B0082', '#8B00FF'];
        
        // Draw a large colorful spiral
        const centerX = 450;
        const centerY = 350;
        let x, y;
        
        for (let i = 0; i < 200; i++) {
            const angle = 0.15 * i;
            const radius = 2 * i;
            x = centerX + radius * Math.cos(angle);
            y = centerY + radius * Math.sin(angle);
            
            sendDraw({
                x, y,
                color: colors[i % colors.length],
                size: 5 + (i / 20),
                action: i === 0 ? 'start' : 'move',
                isEraser: false
            });
        }
        
        // Draw some random "confetti" dots
        setTimeout(() => {
            for (let i = 0; i < 50; i++) {
                const rx = Math.random() * 800 + 50;
                const ry = Math.random() * 600 + 50;
                sendDraw({
                    x: rx, y: ry,
                    color: colors[Math.floor(Math.random() * colors.length)],
                    size: Math.random() * 15 + 5,
                    action: 'start',
                    isEraser: false
                });
            }
            
            setTimeout(() => {
                ws.close();
            }, 500);
        }, 500);
    }, 500);
});
