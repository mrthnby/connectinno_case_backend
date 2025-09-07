## ConnectInno Case Backend

FastAPI backend using Firebase Authentication and Cloud Firestore to manage user-scoped notes under `users/{uid}/notes`.

### Prerequisites

- **Python**: 3.9+
- **Firebase project** with a service account key (JSON)

### Setup

1. Place your Firebase service account JSON at the repo root as `service_account_key.json`.
   - The app loads credentials from `firebase_config.py` via `credentials.Certificate("service_account_key.json")`.
   - For convenience, a test `service_account_key.json` is already included in this repo for local testing only.
2. (Optional) Create and activate a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

### Start the server

Development (auto-reload):

```bash
uvicorn main:app --reload
```


Server runs at `http://127.0.0.1:8000`. Interactive docs are at `http://127.0.0.1:8000/docs`.

### Authentication

All endpoints require a valid **Firebase ID token** in the `Authorization` header as `Bearer <ID_TOKEN>`.

Token verification is performed with `firebase_admin.auth.verify_id_token` in `dependencies.get_current_user`.

### Data model

`Note` (Pydantic):

```json
{
  "uid": "note-unique-id",
  "title": "Title",
  "content": "Body text",
  "createdAt": "2025-01-01T12:00:00Z",
  "updatedAt": "2025-01-01T12:00:00Z"
}
```

- `createdAt`/`updatedAt` must be ISO 8601 timestamps. The server uses the values provided by the client.

### Firestore layout

- Notes are stored under `users/{uid}/notes/{note_uid}` where `{uid}` is the authenticated user's UID.

### API

All requests must include:

```
Authorization: Bearer <ID_TOKEN>
Content-Type: application/json
```

- **GET `/notes`** → List all notes for the current user.

```bash
curl -X GET \
  http://127.0.0.1:8000/notes \
  -H "Authorization: Bearer $ID_TOKEN"
```

- **POST `/notes`** → Create a note under the current user.

```bash
curl -X POST \
  http://127.0.0.1:8000/notes \
  -H "Authorization: Bearer $ID_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "uid": "note-123",
    "title": "My Note",
    "content": "Hello",
    "createdAt": "2025-01-01T12:00:00Z",
    "updatedAt": "2025-01-01T12:00:00Z"
  }'
```

- **PUT `/notes/{note_uid}`** → Update a note. Body `uid` must match the path `note_uid`.

```bash
curl -X PUT \
  http://127.0.0.1:8000/notes/note-123 \
  -H "Authorization: Bearer $ID_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "uid": "note-123",
    "title": "Updated Title",
    "content": "Updated body",
    "createdAt": "2025-01-01T12:00:00Z",
    "updatedAt": "2025-01-02T08:30:00Z"
  }'
```

- **DELETE `/notes/{note_uid}`** → Delete a note.

```bash
curl -X DELETE \
  http://127.0.0.1:8000/notes/note-123 \
  -H "Authorization: Bearer $ID_TOKEN"
```

### Project structure

- `main.py`: FastAPI app and CRUD endpoints for notes
- `dependencies.py`: Auth dependency verifying Firebase ID tokens
- `firebase_config.py`: Initializes Firebase Admin and Firestore client
- `models.py`: Pydantic models
- `requirements.txt`: Python dependencies

### Troubleshooting

- Ensure `service_account_key.json` is present at the repo root and matches your Firebase project.
- Verify Firestore is enabled in your Firebase project.
- If auth fails, confirm the ID token is freshly minted from your client app and not an OAuth access token.


