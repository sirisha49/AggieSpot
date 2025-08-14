// /app/api/open-classrooms/route.ts
import { NextResponse } from "next/server";

type RawSlot = { StartTime: string; EndTime: string; Status: string };
type RawRoom = { slots: RawSlot[] };
type RawBuilding = {
  building: string;
  building_code: string;
  building_status: "available" | "upcoming" | "unavailable";
  rooms: Record<string, RawRoom>; // key = room name
  coords: [number, number];       // [lng, lat]
  distance: number;
};

type Slot = { StartTime: string; EndTime: string; status: string };
type Room = { roomNumber: string; slots: Slot[] };
type Building = {
  building: string;
  building_code: string;
  building_status: "available" | "upcoming" | "unavailable";
  rooms: Room[];
  coords: [number, number];
  distance: number;
};

const API_BASE =
  process.env.NEXT_PUBLIC_BACKEND_URL ?? "http://localhost:8080";

// Normalize backend shape → UI shape
function normalize(data: RawBuilding[]): Building[] {
  return data.map((b) => ({
    building: b.building,
    building_code: b.building_code,
    building_status: b.building_status,
    coords: b.coords,
    distance: b.distance,
    rooms: Object.entries(b.rooms ?? {}).map(([roomNumber, room]) => ({
      roomNumber,
      slots: (room.slots ?? []).map((s) => ({
        StartTime: s.StartTime,
        EndTime: s.EndTime,
        status: s.Status.toLowerCase(), // "Status" → "status"
      })),
    })),
  }));
}

export async function POST(req: Request) {
  try {
    const { lat, lng } = await req.json();

    const r = await fetch(`${API_BASE}/api/open-classrooms`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      // Lat/Lng can be 0 (fallback). Keep them numeric.
      body: JSON.stringify({ lat: Number(lat) || 0, lng: Number(lng) || 0 }),
      // Avoid caches on server-to-server calls
      cache: "no-store",
    });

    if (!r.ok) {
      return NextResponse.json({ error: "Failed to fetch data" }, { status: 500 });
    }

    const raw: RawBuilding[] = await r.json();
    return NextResponse.json(normalize(raw));
  } catch (err) {
    console.error("Error in POST /api/open-classrooms:", err);
    return NextResponse.json({ error: "Failed to process request" }, { status: 500 });
  }
}

export async function GET() {
  try {
    const r = await fetch(`${API_BASE}/api/open-classrooms`, {
      method: "GET",
      cache: "no-store",
    });

    if (!r.ok) {
      return NextResponse.json({ error: "Failed to fetch data" }, { status: 500 });
    }

    const raw: RawBuilding[] = await r.json();
    return NextResponse.json(normalize(raw));
  } catch (err) {
    console.error("Error in GET /api/open-classrooms:", err);
    return NextResponse.json({ error: "Failed to process request" }, { status: 500 });
  }
}
