# 🔬 FRITZ!Box Tiefenanalyse – 01.–02.05.2026

## 📡 Netzwerk-Topologie
| AP | Band | Clients typisch |
|---|---|---|
| FRITZ!Box 5690 XGS | 2.4 + 5 GHz | Zentrale, max. 2401 Mbit/s |
| RepeaterHWR | 2.4 + 5 GHz | Viele IoT, Waschmaschine |
| repeaterkueche | 2.4 + 5 GHz | Linux-PCs, TV Cube |
| repeateroben | 2.4 + 5 GHz | POCO, iPad, moto-g14 |
| fritz.repeater | 2.4 + 5 GHz | S24, diverse |

---

## 🥇 HAUPTSTÖRENFRIED: POCO-X7-Pro (Patricias Handy)

**MACs:** 06:B5:1F:60:66:A1 (5 GHz) / 4E:91:8F:A6:9D:8C (2.4 GHz)

### Belege:
- **4 gescheiterte Anmeldungen** innerhalb 24h:
  - 17:13:20 an RepeaterHWR (01.05)
  - 14:17:01 an repeateroben (02.05)
  - 14:23:31 an repeateroben (02.05)
- **Rastloses Roaming:** Springt im Minutentakt zwischen FritzBox ↔ repeateroben ↔ RepeaterHWR ↔ repeaterkueche
- **Band-Hopping:** Wechselt ständig zwischen 5 GHz (2401 Mbit/s) und 2.4 GHz (192 Mbit/s)
- **Parallele Verbindungen:** Hält oft gleichzeitig 2.4+5 GHz zu verschiedenen APs – verwirrt das Mesh

### Ursachen-Hypothese:
1. **"Intelligentes WLAN" / WLAN+ auf dem POCO aktiv** → aggressive AP-Wechsel
2. **MAC-Randomisierung pro SSID/Band** → FritzBox sieht 2 verschiedene "Geräte"
3. **Schlechtes 5 GHz Signal in repeateroben** → fällt auf 2.4 GHz zurück, versucht dann wieder 5 GHz

### Empfehlung:
- Am POCO: WLAN+ / Intelligentes WLAN **ausschalten**
- In der FritzBox: Diesem Gerät einen **festen AP zuweisen** (z.B. nur RepeaterHWR)
- Alternative: 5 GHz für dieses Gerät priorisieren, 2.4 GHz sperren

---

## 🥈 PROBLEM Nr. 2: S24-von-Michael (DEIN Handy)

**MACs:** 6E:82:CE:90:A4:32 (5 GHz) / 8E:6D:BB:62:58:9A (2.4 GHz)

### Roaming-Orgie 09:46–11:12 (02.05):
- **~40 Wechsel** zwischen FritzBox ↔ repeaterkueche ↔ fritz.repeater in 86 Minuten
- Davon **3 gescheiterte Verbindungen** (repeaterkueche + RepeaterHWR)
- Phasenweises Springen alle 10–30 Sekunden (z.B. 10:16–10:19)
- Stabilisiert sich erst ab 11:12 mit Anmeldung an repeateroben

### Muster:
- S24 bevorzugt 2401 Mbit/s (WiFi 6E?), akzeptiert aber auch 866 Mbit/s
- Fritz.repeater liefert 2402 Mbit/s → S24 will dahin, verliert dann aber Verbindung
- Kampf zwischen "höchster Datenrate" und "stabilster Verbindung"

### Empfehlung:
- S24: "Intelligentes WLAN" prüfen (Samsung: "Mit intelligentem WLAN verbinden")
- FritzBox Mesh Steering für S24 prüfen – ggf. AP-Steering deaktivieren

---

## 🥉 PATHOLOGISCH: Samsung-Washer + SDongleA-HV2310

**01.05.2026, 14:50–14:54 – 5 Minuten Wahnsinn:**

```
Samsung-Washer (1C:E8:9E:C8:C1:82): 19 An-/Abmeldungen in 4 Min
SDongleA-HV2310 (48:4C:29:DB:A4:84): 12 An-/Abmeldungen in 90 Sek
```

- Beide hängen an RepeaterHWR, 2.4 GHz, nur 72 Mbit/s
- SDongleA = vermutlich **Wechselrichter/Dongle für Balkonkraftwerk** (Hoymiles?)
- Flapping im Sekundentakt → deutet auf **Signalverlust / schwache Verbindung**
- SDongleA ist in der Zeit von 14:51:10–14:51:36 **in 26 Sekunden 5× an- und abgemeldet**

### Empfehlung:
- Standort des SDongleA prüfen (näher an RepeaterHWR?)
- Waschmaschine: Ist die im Keller? → Signal durch Betondecke schwach
- Ggf. RepeaterHWR 2.4 GHz Kanal prüfen (Interferenz?)

---

## 🔴 DAUER-ABMELDER: MAC 18:DE:50:41:52:01

**AUSSCHLIESSLICH Abmeldungen** (nie Anmeldung im Log-Zeitraum):

| Zeit | AP |
|---|---|
| 14:50:50 | RepeaterHWR |
| 15:09:10 | RepeaterHWR |
| 02:43:56 | repeateroben (4× ab 02:04) |
| 05:09:xx | repeateroben |
| 06:46:21 | repeateroben (2×) |
| 08:25:19 | repeateroben |
| 09:38:06 | repeaterkueche (10× ab 05:05!) |
| 10:15:19 | repeateroben |
| 13:03:57 | repeateroben (2×) |
| 14:10:18 | repeateroben |

- **~25 Abmeldungen, 0 Anmeldungen** im Log
- Immer 2.4 GHz, keine IP
- **MAC gehört zu: Espressif Inc. (ESP32)** = IoT-Gerät
- Das Gerät war VOR dem Log-Zeitraum verbunden und wird immer wieder abgemeldet

### Hypothese:
- ESP32-basiertes Gerät (Shelly? Sonoff? Eigenbau?)
- Entweder am Rande der Reichweite, oder defekt
- Könnte ein **Shelly 1/2.5/Plus** sein, der hinter einem Schrank/Heizung verbaut ist

### Empfehlung:
- MAC in der FritzBox suchen → Gerätename identifizieren
- Signalstärke prüfen → ggf. Standort optimieren

---

## 🟡 PRINT-SPAMMER: PC-30-68-93-DB-FD-72

**13:45:48–13:46:12 (02.05) – 24 Sekunden, 12 An-/Abmeldungen:**
- Nur an fritz.repeater, 2.4 GHz, **72 Mbit/s**
- Abgemeldet → angemeldet → abgemeldet → angemeldet ... im 2-Sekunden-Takt
- Typisches Drucker-Verhalten (Epson? Brother?)
- **MAC-OUI 30:68:93 = AzureWave** (WiFi-Chip in vielen Druckern)

### Empfehlung:
- Prüfen ob das ein Drucker ist (Epson XP-xxx? Canon?)
- Drucker-Standort zum fritz.repeater optimieren
- Evtl. Drucker-WLAN-Energiesparmodus deaktivieren

---

## ⚡ SYSTEMEREIGNISSE

### 1. DFS-Radar-Ereignis – 11:57:41
- **Radar erkannt auf Kanal 128 (5.630–5.650 GHz)** durch repeateroben
- Massenhafte Abmeldung ALLER Clients
- Autokanal-Wechsel + vollständige Mesh-Rekonfiguration
- ~1000+ Log-Einträge in 60 Sekunden
- **"Mitch"-Gerät (00:45:E2:3D:53:1F)** hatte 6× "ungültiger WLAN-Schlüssel" während Recovery
- Das ist ein **bekanntes FritzOS-Problem** bei Mesh-Recovery → temporär, kein Handlungsbedarf

### 2. Internet-Neuverbindung – 12:44:21
- IPv4 + IPv6 getrennt, ~1 Sekunde später reconnected
- **CGNAT:** 100.115.38.130 → DSLite (du hast keine echte öffentliche IPv4!)
- DNS: 1.1.1.1 + 8.8.8.8
- Provider: ZTE-BRAS-M6000-8S-BER1 (vermutlich 1&1/Vodafone/Telekom?)

### 3. Zweiter Internet-Disconnect – 02.05. 14:44:21
- Gleiches Muster, gleiche IP-Adresse nach Reconnect
- Zeitserver danach nicht erreichbar → Fallback ntp

---

## 📊 ZUSAMMENFASSUNG NACH SCHWEREGRAD

| Gerät | Problem | Schwere | Maßnahme |
|---|---|---|---|
| **POCO-X7-Pro** | Aggressives Roaming + Auth-Fails | 🔴 KRITISCH | WLAN+ deaktivieren, festen AP zuweisen |
| **S24-von-Michael** | 5 GHz Roaming-Exzess (09-11h) | 🟠 HOCH | Intelligentes WLAN prüfen |
| **Samsung-Washer** | 2.4 GHz Signalflapping | 🟠 HOCH | Standort/Repeater prüfen |
| **SDongleA-HV2310** | Extremes WLAN-Flapping | 🟠 HOCH | Balkonkraftwerk-Dongle näher an AP |
| **MAC 18:DE:50:41:52:01** | ESP32 Phantom-Gerät | 🟡 MITTEL | Identifizieren + Signal prüfen |
| **PC-30-68-93** | Drucker-Flapping | 🟡 MITTEL | Energiesparmodus deaktivieren |
| **00:45:E2:3D:53:1F** | WLAN-Key-Fails nach DFS | 🟢 ERWARTET | Mesh-Recovery-Normalität |

---

**Clawdia 🦞 – 02.05.2026 16:30**
