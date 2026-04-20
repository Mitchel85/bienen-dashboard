const WebSocket = require('ws');

// Verbindung zum lokalen WebSocket-Server (Port 3001)
const ws = new WebSocket('ws://localhost:3001');

ws.on('open', () => {
    console.log('✅ Mit Mal-Server verbunden. Sende Zeichenbefehle...');
    
    // Hilfsfunktion zum Senden eines Draw-Events
    function sendDraw(data) {
        ws.send(JSON.stringify({ type: 'draw', data }));
    }
    
    // Canvas erst einmal löschen
    sendDraw({ action: 'clear' });
    
    // Kurze Pause, dann zeichnen
    setTimeout(() => {
        // Farben definieren
        const colors = ['#FF5733', '#33FF57', '#3357FF', '#F033FF', '#FF33A1'];
        let colorIndex = 0;
        
        // Einfache Linie: Trallalero (wellenförmig)
        const startX = 100;
        const startY = 200;
        let x = startX;
        let y = startY;
        
        // Startpunkt
        sendDraw({
            x, y,
            color: colors[colorIndex],
            size: 8,
            action: 'start',
            isEraser: false
        });
        
        // Wellenlinie zeichnen
        for (let i = 0; i < 50; i++) {
            x += 10;
            y = startY + Math.sin(i * 0.5) * 40;
            sendDraw({
                x, y,
                color: colors[colorIndex],
                size: 8,
                action: 'move',
                isEraser: false
            });
            // Farbwechsel alle 10 Schritte
            if (i % 10 === 0) {
                colorIndex = (colorIndex + 1) % colors.length;
            }
        }
        
        // Zweite Linie: Tralala (Kreise)
        setTimeout(() => {
            colorIndex = 2;
            const centerX = 400;
            const centerY = 300;
            const radius = 60;
            const steps = 30;
            
            for (let i = 0; i <= steps; i++) {
                const angle = (i / steps) * 2 * Math.PI;
                const x = centerX + radius * Math.cos(angle);
                const y = centerY + radius * Math.sin(angle);
                sendDraw({
                    x, y,
                    color: colors[colorIndex],
                    size: 6,
                    action: i === 0 ? 'start' : 'move',
                    isEraser: false
                });
            }
            
            // Ein paar Punkte hinzufügen
            setTimeout(() => {
                [[500, 150], [550, 180], [600, 220]].forEach(([px, py], idx) => {
                    sendDraw({
                        x: px, y: py,
                        color: colors[idx],
                        size: 12,
                        action: 'start',
                        isEraser: false
                    });
                });
                
                console.log('🎨 Trallalero Tralala gemalt!');
                ws.close();
            }, 500);
        }, 500);
    }, 500);
});

ws.on('error', (err) => {
    console.error('❌ WebSocket-Fehler:', err.message);
});

ws.on('close', () => {
    console.log('🔌 Verbindung geschlossen.');
});