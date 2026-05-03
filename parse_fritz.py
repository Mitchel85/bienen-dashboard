import re
from collections import defaultdict
from pdfminer.high_level import extract_text

text = extract_text('/data/.openclaw/media/inbound/FRITZ_Box_5690_XGS_11---8a9bea44-adcc-4e4d-8fb5-3b3f9653bb11.pdf')

# Parse events
events = []
lines = text.split('\n')
current_entry = None

# Pattern: "02.05.26" date followed by time and event text
date_pat = re.compile(r'(\d{2}\.\d{2}\.\d{2})\s*\n?\s*(\d{2}:\d{2}:\d{2})\s*\n?\s*(.*)')

# Combine continued lines from PDF page breaks
i = 0
while i < len(lines):
    line = lines[i].strip()
    if not line:
        i += 1
        continue
    # Match date
    m = re.match(r'(\d{2}\.\d{2}\.\d{2})', line)
    if m:
        date = m.group(1)
        # Next line should have time
        j = i + 1
        while j < len(lines) and not lines[j].strip():
            j += 1
        if j < len(lines):
            time_match = re.match(r'(\d{2}:\d{2}:\d{2})', lines[j].strip())
            if time_match:
                timestamp = time_match.group(1)
                # Collect event text from subsequent non-empty lines until next date marker
                event_lines = []
                k = j + 1
                while k < len(lines):
                    l = lines[k].strip()
                    if re.match(r'\d{2}\.\d{2}\.\d{2}', l) or re.match(r'\d{2}:\d{2}:\d{2}', l) or l.startswith('') or l.startswith('Zusätzliche'):
                        break
                    if l:
                        event_lines.append(l)
                    k += 1
                event_text = ' '.join(event_lines)
                events.append((timestamp, event_text))
                i = k
                continue
    i += 1

print(f"Total events parsed: {len(events)}")

# Count per MAC
from collections import Counter

mac_events = []
device_counts = Counter()
connect_counts = defaultdict(int)
disconnect_counts = defaultdict(int)
fail_counts = defaultdict(int)
device_info = {}  # mac -> {name, ip, band, speed}

for ts, txt in events:
    # Extract MAC
    mac_match = re.search(r'MAC\s+([0-9A-F]{2}:[0-9A-F]{2}:[0-9A-F]{2}:[0-9A-F]{2}:[0-9A-F]{2}:[0-9A-F]{2})', txt)
    mac = mac_match.group(1) if mac_match else None
    
    # Determine action
    is_connect = bool(re.search(r'(angemeldet|angemeldet,)\s', txt)) and 'abgemeldet' not in txt[:80] and 'gescheitert' not in txt
    is_disconnect = bool(re.search(r'(abgemeldet|hat sich abgemeldet)', txt))
    is_fail = bool(re.search(r'(gescheitert|fehlgeschlagen)', txt))
    
    # Extract name
    name_match = re.search(r'Mbit/s,\s+([^,]+(?:-[^,]+)?)', txt)
    if not name_match:
        name_match = re.search(r'(?:wurde abgemeldet|hat sich abgemeldet)\s*\([^)]*\),\s*([^,]+)', txt)
    name = name_match.group(1).strip() if name_match else '???'
    
    # Extract IP
    ip_match = re.search(r'IP\s+([\d.]+|-- -)', txt)
    ip = ip_match.group(1) if ip_match else '???'
    
    # Extract band
    band_match = re.search(r'\(([25]),4\s*GHz\)', txt)
    band = band_match.group(1) + 'G' if band_match else '???'
    
    # Extract speed
    speed_match = re.search(r'(\d+)\s*Mbit/s', txt)
    speed = speed_match.group(1) if speed_match else '???'
    
    if mac:
        if is_connect:
            connect_counts[mac] += 1
        elif is_disconnect:
            disconnect_counts[mac] += 1
        elif is_fail:
            fail_counts[mac] += 1
        
        device_counts[mac] += 1
        if mac not in device_info or name != '???':
            device_info[mac] = {'name': name, 'ip': ip, 'band': band, 'speed': speed}

# Print results sorted by total events
print("\n=== QUANTITATIVE ANALYSIS: Connect/Disconnect per MAC ===")
print(f"{'MAC':<20} {'Name':<30} {'Conn':>5} {'Disc':>5} {'Fail':>5} {'Total':>5}")
print("-" * 80)

for mac, total in device_counts.most_common(50):
    info = device_info.get(mac, {})
    name = info.get('name', '???')[:29]
    c = connect_counts[mac]
    d = disconnect_counts[mac]
    f = fail_counts[mac]
    print(f"{mac:<20} {name:<30} {c:>5} {d:>5} {f:>5} {total:>5}")

# Also print top 10 by different metrics
print("\n=== TOP 10 by CONNECTS ===")
for mac, count in connect_counts.most_common(10):
    info = device_info.get(mac, {})
    print(f"{mac}  {info.get('name','???')}: {count}")

print("\n=== TOP 10 by DISCONNECTS ===")
for mac, count in disconnect_counts.most_common(10):
    info = device_info.get(mac, {})
    print(f"{mac}  {info.get('name','???')}: {count}")

print("\n=== TOP 10 by FAILS ===")
for mac, count in fail_counts.most_common(10):
    info = device_info.get(mac, {})
    print(f"{mac}  {info.get('name','???')}: {count}")

print("\n=== TOTAL ===")
print(f"Connect events: {sum(connect_counts.values())}")
print(f"Disconnect events: {sum(disconnect_counts.values())}")
print(f"Fail events: {sum(fail_counts.values())}")
print(f"Total device events: {sum(device_counts.values())}")
print(f"Unique MACs: {len(device_counts)}")
