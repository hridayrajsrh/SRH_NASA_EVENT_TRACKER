# NASA Natural Events Tracker

A Flask + SQLite web application that tracks real-world natural events using live data from NASA's Earth Observatory Natural Event Tracker (EONET) API. Users can browse current wildfires, storms, volcanoes, and other natural events pulled directly from NASA, filter and view details on any event, and build a personal watch list of events they want to keep an eye on.

## Setup Instructions

1. Clone this repository and navigate into the project folder:
   ```bash
   git clone https://github.com/hridayrajsrh/SRH_NASA_EVENT_TRACKER.git
   cd SRH_NASA_EVENT_TRACKER
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate      # macOS/Linux
   venv\Scripts\activate         # Windows
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the application:
   ```bash
   flask run
   ```
   or
   ```bash
   python app.py
   ```

5. Visit `http://127.0.0.1:5000/` in your browser.

The SQLite database (`events.db`) is created automatically on first run — no manual setup required.

## Features

- **Browse live events** (`/browse`) — pulls current natural events directly from the EONET API, with filters for category, status, and date range.
- **Event detail page** (`/event/<eonet_id>`) — shows full details for a single event, including magnitude data where available.
- **Personal watch list** (`/watchlist`) — save events locally to SQLite, with duplicate protection.
- **Remove from watch list** — with a confirmation step before deletion.
- **Flash messages** — confirm successful adds and removals.

## OOP Design

The data layer is built around three classes in `models.py`:

- **`NaturalEvent`** — represents a single event fetched from the EONET API. Holds core attributes (title, category, status, coordinates, date, magnitude, source) and provides `is_active()` and `summary()` methods. The `eonet_id` attribute is stored as a private field (`__eonet_id`) with a read-only `@property` getter, since it functions as the object's unique identifier and shouldn't be reassigned after creation.

- **`WatchedEvent`** (inherits from `NaturalEvent`) — adds the two attributes specific to saved events: `note` and `alert_active`. It extends (rather than replaces) the parent's `summary()` method via `super()`, and adds `toggle_alert()` to flip the alert state.

- **`EventFetcher`** — wraps all communication with the EONET API. `fetch_events()` and `fetch_event()` both return `NaturalEvent` instances rather than raw JSON, and both raise a `ConnectionError` if the API is unreachable, which Flask routes catch and turn into a friendly error message instead of a crash. Flask routes never call `requests` directly — they always go through this class.

Database access is handled separately in `db.py`, which owns the schema, connection handling, and all CRUD queries — keeping `app.py` focused on routing and `models.py` focused on the API/OOP layer.

## Known Limitations

- Category and status filters on the browse page use a fixed shortlist of EONET categories rather than pulling the full list dynamically from the `categories` table.
- If the EONET API fails specifically during an event-detail lookup, the error page may not have full context (`event` is unset). Broader browse-page failures are handled gracefully.
- Search, sort, and statistics features (originally Groups D and E of the assignment brief) were marked optional by the instructor and are not implemented in this submission.

## AI Disclosure

Portions of this project were developed with the assistance of Claude (Anthropic), used interactively to explain concepts, review code, and debug issues as the project was built section by section. All code was written and tested by me.
