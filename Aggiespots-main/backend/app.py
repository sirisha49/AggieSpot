from flask import Flask, jsonify, request
from datetime import datetime, time
import json
import math

app = Flask(__name__)

def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def get_slot_status(current_time, start_time_str, end_time_str):
    # start/end as "HH:MM:SS"
    start_time = datetime.strptime(start_time_str, "%H:%M:%S").time()
    end_time = datetime.strptime(end_time_str, "%H:%M:%S").time()

    # If a slot spans midnight (you probably won't need this, but just in case)
    if end_time <= start_time:
        end_dt = datetime.combine(datetime.today(), end_time).replace(day=datetime.today().day + 1)
    else:
        end_dt = datetime.combine(datetime.today(), end_time)

    start_dt = datetime.combine(datetime.today(), start_time)
    now_dt = datetime.combine(datetime.today(), current_time)

    time_until = (start_dt - now_dt).total_seconds() / 60.0

    if time_until > 0 and time_until < 20:
        return "upcoming"
    elif start_time <= current_time <= end_time:
        return "available"
    elif now_dt > end_dt:
        return "passed"
    else:
        return "unavailable"

# --- Minimal TAMU dataset (edit/expand freely) ---
# buildingCode is just a friendly short code; adjust as you like.
TAMU_SPOTS = [
    {
        "building": "Evans Library",
        "building_code": "EVANS",
        "coords": [-96.3399, 30.6194],  # [lng, lat]
        "rooms": {
            "2nd Floor Commons": [
                {"StartTime": "08:00:00", "EndTime": "22:00:00"},
            ],
            "Quiet Stacks Level": [
                {"StartTime": "08:00:00", "EndTime": "22:00:00"},
            ],
        },
    },
    {
        "building": "West Campus Library",
        "building_code": "WCL",
        "coords": [-96.3506, 30.6109],
        "rooms": {
            "Open Study Area": [
                {"StartTime": "08:00:00", "EndTime": "22:00:00"},
            ],
            "Group Rooms": [
                {"StartTime": "09:00:00", "EndTime": "21:00:00"},
            ],
        },
    },
    {
        "building": "Zachry Engineering Education Complex",
        "building_code": "ZACH",
        "coords": [-96.3408, 30.6199],
        "rooms": {
            "Learning Stairs": [
                {"StartTime": "08:00:00", "EndTime": "20:00:00"},
            ],
            "Commons": [
                {"StartTime": "08:00:00", "EndTime": "22:00:00"},
            ],
        },
    },
    {
        "building": "Memorial Student Center",
        "building_code": "MSC",
        "coords": [-96.3410, 30.6102],
        "rooms": {
            "Flag Room": [
                {"StartTime": "08:00:00", "EndTime": "22:00:00"},
            ],
            "Lounges": [
                {"StartTime": "08:00:00", "EndTime": "22:00:00"},
            ],
        },
    },
    {
        "building": "ILCB (Innovative Learning Classroom Building)",
        "building_code": "ILCB",
        "coords": [-96.3404, 30.6153],
        "rooms": {
            "Atrium Tables": [
                {"StartTime": "08:00:00", "EndTime": "20:00:00"},
            ]
        },
    },
]

@app.route('/api/test', methods=['GET'])
def test():
    return jsonify({"message": "Test route is working!"})

@app.route('/api/open-classrooms', methods=['GET', 'POST'])
def get_open_classrooms():
    # Optional user location for distance sorting
    user_lat = 0.0
    user_lng = 0.0

    if request.method == 'POST':
        body = request.get_json(silent=True) or {}
        user_lat = body.get('lat') or 0.0
        user_lng = body.get('lng') or 0.0

    current_time = datetime.now().time()
    building_info_list = []

    for b in TAMU_SPOTS:
        building_status = "unavailable"
        rooms_out = {}

        # For each "room", compute slot statuses, keep non-passed slots
        for room_name, slots in b["rooms"].items():
            slots_with_status = []
            for slot in slots:
                status = get_slot_status(current_time, slot["StartTime"], slot["EndTime"])
                if building_status != "available" and status == "available":
                    building_status = "available"
                elif building_status == "unavailable" and status == "upcoming":
                    building_status = "upcoming"

                if status != "passed":
                    slots_with_status.append({
                        "StartTime": slot["StartTime"],
                        "EndTime": slot["EndTime"],
                        "Status": status
                    })

            if slots_with_status:
                rooms_out[room_name] = {"slots": slots_with_status}

        if rooms_out:
            building_info = {
                "building": b["building"],
                "building_code": b["building_code"],
                "building_status": building_status,
                "rooms": rooms_out,
                "coords": b["coords"],
                "distance": haversine(
                    user_lat, user_lng,
                    b["coords"][1], b["coords"][0]
                ) if user_lat and user_lng else 0
            }
            building_info_list.append(building_info)

    if user_lat and user_lng:
        building_info_list.sort(key=lambda x: x["distance"])

    return jsonify(building_info_list)

if __name__ == '__main__':
    # On Render/Railway you can keep this; on Vercel you’d export via serverless
    app.run(host='0.0.0.0', port=8080, debug=True)
