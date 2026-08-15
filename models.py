import requests




class NaturalEvent:
    def __init__(self, eonet_id, title, category, status, latitude = None,
                longitude = None, event_date = None, magnitude = None, mag_unit = None, source_url = None):
        self.__eonet_id = eonet_id
        self.title = title
        self.category = category
        self.status = status
        self.latitude = latitude
        self.longitude = longitude
        self.event_date = event_date
        self.magnitude = magnitude
        self.mag_unit = mag_unit
        self.source_url = source_url


    @property
    def eonet_id(self):
        return self.__eonet_id

    def is_active(self):
        return self.status == "open"

    def summary(self):
        return f"[{self.category}] {self.title} — {self.status}"


class WatchedEvent(NaturalEvent):
    def __init__(self, eonet_id, title, category, status, latitude = None, longitude = None, event_date = None, magnitude = None, mag_unit = None, source_url = None, note = "", alert_active = False):
        super().__init__(eonet_id, title, category, status, latitude, longitude, event_date, magnitude, mag_unit, source_url)

        self.note = note
        self.alert_active = alert_active

    def toggle_alert(self):
        self.alert_active = not self.alert_active
        return self.alert_active

    def summary(self):
        base = super().summary()
        if self.note:
            base += f" | note: {self.note}"
        if self.alert_active:
            base += " | ALERT ON"
        return base



BASE_URL = "https://eonet.gsfc.nasa.gov/api/v3"

class EventFetcher:
    def fetch_events(self, status = "open", category = None, days = 30, limit = 50):
        params = {"days": days, "limit": limit}
        if status:
            params["status"] = status
        if category:
            params["category"] = category

        try:
            response = requests.get(f"{BASE_URL}/events", params=params, timeout=10)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Could not reach EONET API: {e}")

        raw_events = response.json()["events"]
        return [self._to_event(e) for e in raw_events]

    def fetch_event(self, eonet_id):
        try:
            response = requests.get(f"{BASE_URL}/events/{eonet_id}", timeout=10)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Could not reach EONET API: {e}")

        return self._to_event(response.json())

    def _to_event(self, raw):
        geometry = raw["geometry"][0] if raw.get("geometry") else {}
        coords = geometry.get("coordinates", [None, None])
        category = raw["categories"][0]["title"] if raw.get("categories") else None
        source_url = raw["sources"][0]["url"] if raw.get("sources") else None

        return NaturalEvent(
            eonet_id=raw["id"],
            title=raw["title"],
            category=category,
            status="closed" if raw.get("closed") else "open",
            longitude=coords[0],
            latitude=coords[1],
            event_date=geometry.get("date", "")[:10],
            magnitude=raw.get("magnitudeValue"),
            mag_unit=raw.get("magnitudeUnit"),
            source_url=source_url,
        )