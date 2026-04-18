#!/usr/bin/env python3
"""
Wetter‑Client für den Imker‑Begleiter‑Skill.
Ruft aktuelle Bedingungen und Vorhersagen von Open‑Meteo ab.
"""
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import urllib.request
import urllib.error

# Pfade
SKILL_DIR = Path(__file__).parent.parent
CONFIG_FILE = SKILL_DIR / "data" / "config.json"

# Default‑Standort (Ludwigsfelde, Französische Allee 30)
DEFAULT_LOCATION = {
    "latitude": 52.300_556,   # Ludwigsfelde
    "longitude": 13.267_5,
    "city": "Ludwigsfelde"
}

# Open‑Meteo API Endpoints
OPENMETEO_BASE = "https://api.open-meteo.com/v1/forecast"
OPENMETEO_CURRENT = OPENMETEO_BASE + "?current=temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,rain,showers,snowfall,cloud_cover,wind_speed_10m,wind_direction_10m,is_day&timezone=Europe%2FBerlin"
OPENMETEO_HOURLY = OPENMETEO_BASE + "?hourly=temperature_2m,relative_humidity_2m,precipitation_probability,precipitation,rain,showers,snowfall,cloud_cover,wind_speed_10m,wind_direction_10m&timezone=Europe%2FBerlin"
OPENMETEO_DAILY = OPENMETEO_BASE + "?daily=temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_hours,wind_speed_10m_max&timezone=Europe%2FBerlin"

def load_config() -> Dict[str, Any]:
    """Lädt die Skill‑Konfiguration."""
    if not CONFIG_FILE.exists():
        return {"location": DEFAULT_LOCATION}
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            config = json.load(f)
            if "location" not in config:
                config["location"] = DEFAULT_LOCATION
            return config
    except (json.JSONDecodeError, FileNotFoundError):
        return {"location": DEFAULT_LOCATION}

def get_location() -> Dict[str, float]:
    """Gibt die aktuellen Standortkoordinaten zurück."""
    config = load_config()
    loc = config.get("location", DEFAULT_LOCATION)
    return {"latitude": loc["latitude"], "longitude": loc["longitude"]}

def fetch_weather(url_suffix: str = "current") -> Dict[str, Any]:
    """
    Ruft Wetterdaten von Open‑Meteo ab.
    
    Args:
        url_suffix: "current", "hourly" oder "daily"
    
    Returns:
        JSON‑Antwort der API.
    
    Raises:
        urllib.error.URLError: Bei Netzwerk‑ oder API‑Fehlern.
    """
    loc = get_location()
    
    if url_suffix == "current":
        url = f"{OPENMETEO_CURRENT}&latitude={loc['latitude']}&longitude={loc['longitude']}"
    elif url_suffix == "hourly":
        url = f"{OPENMETEO_HOURLY}&latitude={loc['latitude']}&longitude={loc['longitude']}"
    elif url_suffix == "daily":
        url = f"{OPENMETEO_DAILY}&latitude={loc['latitude']}&longitude={loc['longitude']}"
    else:
        raise ValueError(f"Ungültiger url_suffix: {url_suffix}")
    
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.load(response)
            if "error" in data:
                raise urllib.error.URLError(f"Open‑Meteo API Fehler: {data['error']}")
            return data
    except urllib.error.URLError as e:
        raise urllib.error.URLError(f"Open‑Meteo Anfrage fehlgeschlagen: {e}") from e

def get_current_weather() -> Dict[str, Any]:
    """
    Gibt die aktuellen Wetterbedingungen zurück.
    
    Returns:
        Dictionary mit keys: temperature, cloud_cover, wind_speed, precipitation, is_day
    """
    data = fetch_weather("current")
    current = data.get("current", {})
    
    return {
        "temperature": current.get("temperature_2m"),
        "cloud_cover": current.get("cloud_cover"),
        "wind_speed": current.get("wind_speed_10m"),
        "precipitation": current.get("precipitation"),
        "rain": current.get("rain"),
        "showers": current.get("showers"),
        "snowfall": current.get("snowfall"),
        "is_day": current.get("is_day"),
        "time": current.get("time"),
        "fetched_at": datetime.now(timezone.utc).isoformat()
    }

def get_hourly_forecast(hours: int = 24) -> List[Dict[str, Any]]:
    """
    Gibt die stündliche Vorhersage für die nächsten N Stunden zurück.
    
    Args:
        hours: Anzahl der vorherzusagenden Stunden (max. 168)
    
    Returns:
        Liste von Hourly‑Dictionaries.
    """
    data = fetch_weather("hourly")
    hourly = data.get("hourly", {})
    
    times = hourly.get("time", [])
    temps = hourly.get("temperature_2m", [])
    clouds = hourly.get("cloud_cover", [])
    winds = hourly.get("wind_speed_10m", [])
    preci = hourly.get("precipitation", [])
    
    forecast = []
    for i in range(min(hours, len(times))):
        forecast.append({
            "time": times[i],
            "temperature": temps[i] if i < len(temps) else None,
            "cloud_cover": clouds[i] if i < len(clouds) else None,
            "wind_speed": winds[i] if i < len(winds) else None,
            "precipitation": preci[i] if i < len(preci) else None
        })
    
    return forecast

def get_daily_forecast(days: int = 7) -> List[Dict[str, Any]]:
    """
    Gibt die tägliche Vorhersage für die nächsten N Tage zurück.
    
    Args:
        days: Anzahl der vorherzusagenden Tage (max. 16)
    
    Returns:
        Liste von Daily‑Dictionaries.
    """
    data = fetch_weather("daily")
    daily = data.get("daily", {})
    
    times = daily.get("time", [])
    temp_max = daily.get("temperature_2m_max", [])
    temp_min = daily.get("temperature_2m_min", [])
    precip = daily.get("precipitation_sum", [])
    wind_max = daily.get("wind_speed_10m_max", [])
    
    forecast = []
    for i in range(min(days, len(times))):
        forecast.append({
            "date": times[i],
            "temp_max": temp_max[i] if i < len(temp_max) else None,
            "temp_min": temp_min[i] if i < len(temp_min) else None,
            "precipitation": precip[i] if i < len(precip) else None,
            "wind_max": wind_max[i] if i < len(wind_max) else None
        })
    
    return forecast

def is_swarm_weather(current: Dict[str, Any] = None, hour_of_day: int = None) -> Tuple[bool, str]:
    """
    Prüft, ob die aktuellen Bedingungen "Schwarmwetter" sind.
    
    Kriterien (basierend auf Recherche):
    - Temperatur ≥ 18°C (optimal 20–25°C)
    - Bewölkung < 30% (sonnig)
    - Windgeschwindigkeit < 15 km/h (windstill/leicht)
    - Kein Niederschlag (precipitation = 0)
    - Tageszeit: 10–14 Uhr (später Vormittag bis früher Nachmittag)
    
    Args:
        current: Optional, aktuelles Wetter‑Dictionary (sonst wird es abgerufen)
        hour_of_day: Optional, Stunde des Tages (0–23, sonst aktuelle Stunde)
    
    Returns:
        Tuple (is_swarm: bool, message: str)
    """
    if current is None:
        current = get_current_weather()
    
    if hour_of_day is None:
        now = datetime.now()
        hour_of_day = now.hour
    
    temp = current.get("temperature")
    cloud = current.get("cloud_cover")
    wind = current.get("wind_speed")
    precip = current.get("precipitation", 0)
    rain = current.get("rain", 0)
    showers = current.get("showers", 0)
    snowfall = current.get("snowfall", 0)
    
    # Prüfe jede Bedingung
    conditions = {
        "temperatur": temp is not None and temp >= 18,
        "sonne": cloud is not None and cloud < 30,
        "wind": wind is not None and wind < 15,
        "niederschlag": precip == 0 and rain == 0 and showers == 0 and snowfall == 0,
        "tageszeit": 10 <= hour_of_day <= 14
    }
    
    score = sum(conditions.values())
    message_parts = []
    
    if temp is not None:
        message_parts.append(f"{temp}°C")
    if cloud is not None:
        message_parts.append(f"{cloud}% Bewölkung")
    if wind is not None:
        message_parts.append(f"{wind} km/h Wind")
    if precip > 0:
        message_parts.append(f"{precip} mm Niederschlag")
    
    conditions_text = ", ".join([k for k, v in conditions.items() if v])
    
    if score >= 5:
        return True, f"⚠️ PERFEKTES SCHWARMWETTER! ({score}/5 Bedingungen: {conditions_text}) – {', '.join(message_parts)}"
    elif score >= 4:
        return True, f"🔶 Erhöhte Schwarmgefahr ({score}/5 Bedingungen: {conditions_text}) – {', '.join(message_parts)}"
    else:
        return False, f"✅ Kein Schwarmwetter ({score}/5 Bedingungen) – {', '.join(message_parts)}"

# CLI für manuelle Tests
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Wetter‑Client für Imker‑Begleiter")
    subparsers = parser.add_subparsers(dest="command", help="Befehl")
    
    # current
    subparsers.add_parser("current", help="Zeigt aktuelles Wetter")
    
    # hourly
    hourly_parser = subparsers.add_parser("hourly", help="Zeigt stündliche Vorhersage")
    hourly_parser.add_argument("--hours", type=int, default=24, help="Anzahl Stunden")
    
    # daily
    daily_parser = subparsers.add_parser("daily", help="Zeigt tägliche Vorhersage")
    daily_parser.add_argument("--days", type=int, default=7, help="Anzahl Tage")
    
    # swarm-check
    swarm_parser = subparsers.add_parser("swarm-check", help="Prüft auf Schwarmwetter")
    swarm_parser.add_argument("--hour", type=int, help="Stunde des Tages (0‑23)")
    
    args = parser.parse_args()
    
    try:
        if args.command == "current":
            weather = get_current_weather()
            print("🌤️ Aktuelles Wetter:")
            print(json.dumps(weather, ensure_ascii=False, indent=2))
        
        elif args.command == "hourly":
            forecast = get_hourly_forecast(args.hours)
            print(f"📅 Stündliche Vorhersage ({args.hours} h):")
            for entry in forecast:
                time = entry["time"].split("T")[1][:5] if "T" in entry["time"] else entry["time"]
                temp = entry["temperature"]
                cloud = entry["cloud_cover"]
                wind = entry["wind_speed"]
                print(f"  {time}: {temp}°C, {cloud}% Wolken, {wind} km/h Wind")
        
        elif args.command == "daily":
            forecast = get_daily_forecast(args.days)
            print(f"📅 Tägliche Vorhersage ({args.days} Tage):")
            for entry in forecast:
                date = entry["date"]
                tmax = entry["temp_max"]
                tmin = entry["temp_min"]
                precip = entry["precipitation"]
                wind = entry["wind_max"]
                print(f"  {date}: max {tmax}°C, min {tmin}°C, {precip} mm, Wind max {wind} km/h")
        
        elif args.command == "swarm-check":
            is_swarm, msg = is_swarm_weather(hour_of_day=args.hour)
            print(msg)
            if is_swarm:
                print("🎯 Empfehlung: Schwarmkontrolle durchführen!")
        
        else:
            parser.print_help()
    
    except urllib.error.URLError as e:
        print(f"❌ Netzwerk‑/API‑Fehler: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unerwarteter Fehler: {e}", file=sys.stderr)
        sys.exit(1)