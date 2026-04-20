const fs = require('fs');
const path = '/data/.openclaw/workspace/skills/imker-begleiter/data/voelker.json';

let data = JSON.parse(fs.readFileSync(path, 'utf8'));
const now = new Date().toISOString();

// Log entries for each colony based on the image
const entries = {
  '1': {
    volk_id: '1',
    name: 'Roter Stock',
    log: {
      timestamp: now,
      aktion: 'foto_analyse',
      menge: '',
      details: 'Foto vom 20.04.2026: Beute (rechter Stapel) rot‑rot‑grün, drei Zargen, auf Paletten auf Dach. Volk aktiv? Flugloch frei, kein Anflug im Bild. Dach nass (Regen). Zustand äußerlich intakt.'
    }
  },
  '2': {
    volk_id: '2',
    name: 'Grüner Stock',
    log: {
      timestamp: now,
      aktion: 'foto_analyse',
      menge: '',
      details: 'Foto vom 20.04.2026: Beute (mittlerer Stapel) grün‑rot‑grün, drei Zargen, auf Paletten auf Dach. Volk aktiv? Flugloch frei, kein Anflug im Bild. Dach nass (Regen). Zustand äußerlich intakt.'
    }
  },
  '3': {
    volk_id: '3',
    name: 'Gelber Stock',
    log: {
      timestamp: now,
      aktion: 'foto_analyse',
      menge: '',
      details: 'Foto vom 20.04.2026: Beute (linker Stapel) gelb‑gelb, zwei Zargen, auf Paletten auf Dach. Leere Beute? Flugloch frei, kein Anflug im Bild. Dach nass (Regen). Zustand äußerlich intakt.'
    }
  }
};

Object.keys(entries).forEach(id => {
  if (data[id]) {
    if (!data[id].logs) data[id].logs = [];
    data[id].logs.push(entries[id].log);
    console.log(`✅ Log added for ${entries[id].name}`);
  }
});

// Update meta last update
data.meta.letzte_aktualisierung = new Date().toISOString().split('T')[0];

fs.writeFileSync(path, JSON.stringify(data, null, 2));
console.log('📝 voelker.json updated successfully.');