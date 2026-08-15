from flask import Flask, render_template, flash, redirect, url_for, request
from db import init_db, add_watched_event, remove_watched_event, get_watched_event, get_all_watched_events

from models import EventFetcher

app = Flask(__name__)
app.secret_key = "dev-secret-key-change-later"
init_db()
fetcher = EventFetcher()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/browse")
def browse():
    category = request.args.get("category", "")
    status = request.args.get("status", "open")
    days = request.args.get("days", 30, type=int)

    try:
        events = fetcher.fetch_events(
            status=status if status != "all" else None,
            category=category if category else None,
            days=days
        )
        return render_template(
            "browse.html",
            events=events,
            category=category,
            status=status,
            days=days
        )
    except ConnectionError as e:
        return render_template("browse.html", error=str(e))

@app.route("/event/<eonet_id>")
def event_detail(eonet_id):
    try:
        event = fetcher.fetch_event(eonet_id)
        return render_template("event_detail.html", event=event)
    except ConnectionError as e:
        return render_template("event_detail.html", error=str(e))


@app.route("/watch/add/<eonet_id>", methods=["POST"])
def watch_add(eonet_id):
    try:
        event = fetcher.fetch_event(eonet_id)
    except ConnectionError as e:
        flash(f"Could not add event: {e}", "error")
        return redirect(url_for("browse"))

    added = add_watched_event(event)
    if added:
        flash(f'"{event.title}" added to your watch list.', "success")
    else:
        flash(f'"{event.title}" is already on your watch list.', "success")

    return redirect(url_for("browse"))


@app.route("/watch/remove/<int:id>")
def watch_remove_confirm(id):
    event = get_watched_event(id)
    if event is None:
        flash("That event isn't on your watch list.", "error")
        return redirect(url_for("index"))
    return render_template("confirm_remove.html", event=event)

@app.route("/watch/remove/<int:id>", methods=["POST"])
def watch_remove(id):
    event = get_watched_event(id)
    remove_watched_event(id)
    if event:
        flash(f'"{event["title"]}" removed from your watch list.', "success")
    return redirect(url_for("index"))

@app.route("/watchlist")
def watchlist():
    events = get_all_watched_events()
    return render_template("watchlist.html", events=events)




if __name__ == "__main__":
    app.run(debug=True)