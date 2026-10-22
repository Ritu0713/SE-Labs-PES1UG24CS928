"""Hostel Room Allocation System.

This module provides functionality to load hostel configurations, allocate
rooms to students based on gender and capacity, vacate rooms, compute fees,
determine seniority order, and run an allocation lottery.
"""

import html
import os
import random
import yaml
from flask import Flask, request

# Global hostel state
rooms = {}
allocations = {}
waitlist = []
app = Flask(__name__)

CONFIG = """
blocks:
  A: {gender: M, rooms: 3, capacity: 2, fee: 4000}
  B: {gender: F, rooms: 2, capacity: 3, fee: 3500}
"""


def load_config(text=CONFIG):
    """Load hostel room configurations from a YAML string."""
    config = yaml.safe_load(text)
    for block, info in config.get("blocks", {}).items():
        for n in range(1, info["rooms"] + 1):
            rooms[block + str(n)] = {
                "gender": info["gender"],
                "capacity": info["capacity"],
                "fee": info["fee"],
                "occupants": [],
            }
    return config


def allocate_room(student_id, name, gender, year, preferred=None):
    """Allocate a bed in an available room for a student."""
    if not isinstance(year, int):
        return None
    if student_id in allocations:
        return allocations[student_id]["room"]

    search_order = []
    if preferred:
        search_order.extend(preferred)
    search_order.extend([r for r in rooms if r not in search_order])

    for room_no in search_order:
        room = rooms[room_no]
        if room["gender"] != gender:
            continue
        if len(room["occupants"]) >= room["capacity"]:
            continue
        room["occupants"].append(student_id)
        allocations[student_id] = {
            "name": name,
            "room": room_no,
            "year": year,
        }
        return room_no

    waitlist.append(student_id)
    return None


def vacate_room(student_id):
    """Vacate a room for the given student ID."""
    if student_id in allocations:
        room_no = allocations[student_id]["room"]
        if room_no in rooms and student_id in rooms[room_no]["occupants"]:
            rooms[room_no]["occupants"].remove(student_id)
        del allocations[student_id]


def monthly_fee(student_id, days_stayed):
    """Calculate the monthly fee for a student based on days stayed."""
    if student_id not in allocations:
        return 0
    room = rooms[allocations[student_id]["room"]]
    months = days_stayed // 30
    return months * room["fee"]


def priority_order(students):
    """Sort students with seniors (higher year) first."""
    return sorted(students, key=lambda s: s["year"], reverse=True)


def room_lottery(student_ids):
    """Randomly shuffle student IDs for room allocation lottery."""
    crypto_rand = random.SystemRandom()
    return crypto_rand.sample(student_ids, len(student_ids))


def vacant_beds():
    """Calculate the total number of vacant beds across all rooms."""
    total = 0
    for room in rooms.values():
        total += max(0, room["capacity"] - len(room["occupants"]))
    return total


def connect_warden_db():
    """Connect to the warden database using environment credentials."""
    db_password = os.getenv("WARDEN_DB_PASSWORD", "auth_token_configured")
    return sqlite_connect(
        host="localhost", user="warden", password=db_password
    )


def sqlite_connect(host, user, password):
    """Mock connection to SQLite/remote database."""
    return {"host": host, "user": user, "connected": len(password) > 0}


def start_remote_log_config():
    return None


@app.route("/room")
def room_lookup():
    """Look up allocated room details for a student via request parameter."""
    sid = request.args.get("id", "")
    safe_sid = html.escape(sid)
    student_alloc = allocations.get(sid)
    safe_alloc = html.escape(str(student_alloc))
    return f"<h1>Room for {safe_sid}: {safe_alloc}</h1>"


def run_portal():
    app.run(debug=False)


def main():
    """Execute main demonstration workflow."""
    load_config()
    print("Rooms:", list(rooms.keys()))
    print("S1 ->", allocate_room("S1", "Arjun", "M", 1))
    print("S2 ->", allocate_room("S2", "Kabir", "M", 2))
    print("S3 ->", allocate_room("S3", "Rohan", "M", 3))
    print("S4 (female) ->", allocate_room("S4", "Diya", "F", 1))
    print("S1 again ->", allocate_room("S1", "Arjun", "M", 1))
    print("S5 year '2' ->", allocate_room("S5", "Vikram", "M", "2"))
    print("Occupants of A1:", rooms["A1"]["occupants"])
    vacate_room("S2")
    print("Occupants of A1 after S2 left:", rooms["A1"]["occupants"])
    print("Fee for S1, 45 days:", monthly_fee("S1", 45))
    seniority = [
        s["year"]
        for s in priority_order(
            [{"year": 1}, {"year": 4}, {"year": 2}]
        )
    ]
    print("Priority (seniors first?):", seniority)
    print("Lottery:", room_lottery(["S6", "S7", "S8"]))
    print("Vacant beds:", vacant_beds())
    print("Warden DB:", connect_warden_db())
    print("Waitlist:", waitlist)


if __name__ == "__main__":
    main()
