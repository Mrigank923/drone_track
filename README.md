# drone FastAPI Backend

Simple FastAPI backend with endpoints to store mines, poles, drone positions and to broadcast drone positions via WebSocket and webhooks.

APIs
- POST /mines -> store mine coordinates
- POST /poles -> store pole coordinates
- POST /drone -> receive drone position (stores and broadcasts)
- GET /poles -> returns all poles
- GET /mines -> returns all mines
- WebSocket /ws -> receive live drone updates

Run locally

1. Create a virtualenv and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Start the server:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

3. Use the endpoints or connect to websocket at ws://localhost:8000/ws

Postman testing guide
---------------------

Quick setup

- Start the server as above and confirm it is reachable at http://localhost:8000.
- In Postman create an Environment with these variables:
	- base_url = http://localhost:8000
	- auth_key = devkey   # change to the value set in your `.env`

Notes about auth
- All POST endpoints require an `auth_key` field in the JSON body.
- DELETE endpoints require `auth_key` as a query parameter (or header if you modify the API).

Requests (examples)

1) POST /mines
- URL: {{base_url}}/mines
- Method: POST
- Headers: Content-Type: application/json
- Body (raw JSON):

```json
{
	"latitude": 12.9715987,
	"longitude": 77.594566,
	"label": "mine-1",
	"auth_key": "{{auth_key}}"
}
```

2) POST /poles
- URL: {{base_url}}/poles
- Body:

```json
{
	"latitude": 12.9721,
	"longitude": 77.595,
	"label": "pole-A",
	"auth_key": "{{auth_key}}"
}
```

3) POST /drone
- URL: {{base_url}}/drone
- Body:

```json
{
	"latitude": 12.9730,
	"longitude": 77.5960,
	"auth_key": "{{auth_key}}"
}
```

4) GET /poles
- URL: {{base_url}}/poles
- Method: GET

5) GET /mines
- URL: {{base_url}}/mines
- Method: GET

6) DELETE examples (requires auth_key as query param)
- Delete all poles:

```
DELETE {{base_url}}/poles?auth_key={{auth_key}}
```

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

