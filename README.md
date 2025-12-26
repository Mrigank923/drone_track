# Drone FastAPI Backend

A robust FastAPI backend for drone tracking with real-time coordinate broadcasting via WebSocket. Store and manage mines, poles, and live drone positions with multi-client WebSocket support.

## Features
- 📍 Store and retrieve mines and pole coordinates
- 🚁 Real-time drone position tracking via WebSocket
- 🔐 Auth key-based API security
- 📡 Multi-client WebSocket broadcasting
- 🗄️ MongoDB integration for data persistence
- 🚀 CORS enabled for cross-origin requests

## API Endpoints

### REST Endpoints
- `POST /mines` → Store mine coordinates (requires auth_key)
- `GET /mines` → Retrieve all mines
- `DELETE /mines` → Delete all mines (requires auth_key)
- `POST /poles` → Store pole coordinates (requires auth_key)
- `GET /poles` → Retrieve all poles
- `DELETE /poles` → Delete all poles (requires auth_key)
- `POST /drone` → Receive drone position (stores and broadcasts to WebSocket clients)(requires auth_key)
- `GET /drone` → Retrieve all drone positions
- `GET /drone/latest` → Get the latest drone position
- `DELETE /drone` → Delete all drone positions (requires auth_key)
- `POST /safe_paths` → Store safe path coordinates (requires auth_key)
- `GET /safe_paths` → Retrieve all safe paths coordinates
- `DELETE /safe_paths` → Delete all safe paths coordinates (requires auth_key)

### WebSocket Endpoint
- `WebSocket /ws/drone` → Connect for real-time drone position updates

## Installation

### Prerequisites
- Python 3.8+
- MongoDB (local or remote)

### Setup

1. Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the project root (optional):

```env
MONGO_URI=mongodb://localhost:27017
MONGO_DB=drone_db
AUTH_KEY=your_secret_key
```

4. Start the server:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000` and WebSocket at `ws://localhost:8000/ws/drone`.

## WebSocket Usage

### Connecting from JavaScript

```javascript
// Connect to WebSocket
const ws = new WebSocket('ws://localhost:8000/ws/drone');

// Connection opened
ws.onopen = () => {
    console.log('Connected to drone tracking server');
};

// Receive drone position updates
ws.onmessage = (event) => {
    const message = JSON.parse(event.data);
    if (message.type === 'drone_position') {
        const { latitude, longitude, id } = message.data;
        console.log(`Drone position: Lat ${latitude}, Lon ${longitude}`);
    }
};

// Handle disconnection
ws.onclose = () => {
    console.log('Disconnected from server');
};

// Handle errors
ws.onerror = (error) => {
    console.error('WebSocket error:', error);
};
```

### Message Format

The server broadcasts drone positions in the following format:

```json
{
    "type": "drone_position",
    "data": {
        "id": "507f1f77bcf86cd799439011",
        "latitude": 12.9730,
        "longitude": 77.5960
    }
}
```

### Web Dashboard

A sample HTML dashboard is provided in `drone_tracking.html`. Open it in a browser to visualize live drone tracking with:
- Real-time coordinate display
- Position history log with timestamps
- Connection status indicator
- Responsive design

Simply open the file and click "Connect" to start receiving live updates.

Run locally

Postman testing guide
---------------------

## Testing with Postman

### Quick Setup

1. Start the server and confirm it's reachable at `http://localhost:8000`
2. In Postman, create an Environment with these variables:
   - `base_url` = `http://localhost:8000`
   - `auth_key` = `devkey` (or your custom AUTH_KEY from `.env`)

### Authentication Notes

- All `POST` endpoints require an `auth_key` field in the JSON body
- All `DELETE` endpoints require `auth_key` as a query parameter
- The default auth key is `devkey` (set `AUTH_KEY` environment variable to override)

### Example Requests

### Example Requests

#### 1. Create Mine
- **URL**: `{{base_url}}/mines`
- **Method**: `POST`
- **Headers**: `Content-Type: application/json`
- **Body**:

```json
{
    "latitude": 12.9715987,
    "longitude": 77.594566,
    "label": "mine-1",
    "auth_key": "{{auth_key}}"
}
```

#### 2. Create Pole
- **URL**: `{{base_url}}/poles`
- **Method**: `POST`
- **Body**:

```json
{
    "latitude": 12.9721,
    "longitude": 77.595,
    "label": "pole-A",
    "auth_key": "{{auth_key}}"
}
```

#### 3. Submit Drone Position (triggers WebSocket broadcast)
- **URL**: `{{base_url}}/drone`
- **Method**: `POST`
- **Body**:

```json
{
    "latitude": 12.9730,
    "longitude": 77.5960,
    "auth_key": "{{auth_key}}"
}
```

**Response** (broadcasted to all WebSocket clients):
```json
{
    "status": "ok",
    "data": {
        "id": "507f1f77bcf86cd799439011",
        "latitude": 12.9730,
        "longitude": 77.5960
    }
}
```

#### 4. Get All Poles
- **URL**: `{{base_url}}/poles`
- **Method**: `GET`

#### 5. Get All Mines
- **URL**: `{{base_url}}/mines`
- **Method**: `GET`

#### 6. Get All Drone Positions
- **URL**: `{{base_url}}/drone`
- **Method**: `GET`

#### 7. Get Latest Drone Position
- **URL**: `{{base_url}}/drone/latest`
- **Method**: `GET`

#### 8. Delete Operations (requires auth_key as query parameter)

Delete all poles:
```
DELETE {{base_url}}/poles?auth_key={{auth_key}}
```

Delete all mines:
```
DELETE {{base_url}}/mines?auth_key={{auth_key}}
```

Delete all drone positions:
```
DELETE {{base_url}}/drone?auth_key={{auth_key}}
```

## Environment Variables

Configure the following in your `.env` file:

| Variable | Default | Description |
|----------|---------|-------------|
| `MONGO_URI` | `mongodb://localhost:27017` | MongoDB connection string |
| `MONGO_DB` | `drone_db` | MongoDB database name |
| `AUTH_KEY` | `devkey` | Authentication key for API endpoints |

## Project Structure

```
.
├── main.py              # FastAPI app entry point with CORS setup
├── api.py               # API routes (REST + WebSocket endpoints)
├── database.py          # MongoDB async client setup
├── schemas.py           # Pydantic data models
├── ws_manager.py        # WebSocket connection manager
├── drone_tracking.html  # Sample frontend dashboard
├── requirements.txt     # Python dependencies
├── README.md            # This file
└── .env                 # Environment variables (create this)
```

## Technical Details

### WebSocket Connection Manager (`ws_manager.py`)
- Manages active WebSocket connections
- Broadcasts messages to all connected clients
- Handles client disconnections gracefully

### Real-Time Broadcasting Flow
1. Client POSTs drone position to `/drone` endpoint with auth_key
2. Position is saved to MongoDB
3. Position is automatically broadcasted to all WebSocket-connected clients
4. Clients receive JSON message with position data
5. Frontend updates dashboard in real-time

### Data Models
- **CoordBase**: Base model with latitude and longitude
- **MineCreate/PoleCreate/DroneCreate**: Input schemas with auth_key
- **CoordOut**: Output schema with MongoDB ObjectId as string id

## Requirements

All dependencies are listed in `requirements.txt`:
- FastAPI: Web framework
- Uvicorn: ASGI server
- Motor: Async MongoDB driver
- Pydantic: Data validation
- Python-dotenv: Environment variables
- Websockets: WebSocket support

Importing into Postman
- Create a new Collection and add the requests above. Save them to the collection.
- You can run /drone repeatedly every 500ms with the Collection Runner: set Delay = 500 ms and Iterations = N.

Quick curl examples

Create a pole with curl:

```bash
curl -X POST "http://localhost:8000/poles" \
	-H "Content-Type: application/json" \
	-d '{"latitude":12.9721,"longitude":77.595,"label":"pole-A","auth_key":"devkey"}'
```

Delete all poles:

```bash
curl -X DELETE "http://localhost:8000/poles?auth_key=devkey"
```

Useful tips
- If you use a `.env` file, either export its variables before running uvicorn or use `python-dotenv` to load it at the top of `main.py` (so env vars exist before modules import them).
- If Mongo is unreachable, make sure `mongod` or a Mongo container is running and `MONGO_URI` in `.env` points to the correct host/credentials.

Postman collection (optional)
- If you'd like, I can generate a Postman collection JSON for import containing all requests and environment variables — tell me and I'll add it to the repo.

