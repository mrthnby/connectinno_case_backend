from fastapi import FastAPI, Depends, HTTPException
from firebase_config import db
from dependencies import get_current_user
from models import Note
from datetime import datetime, timezone

app = FastAPI()

# GET /notes → list user's notes under users/{uid}/notes
@app.get("/notes", response_model=list[Note])
async def list_notes(user=Depends(get_current_user)):
    uid = user["uid"]
    notes_ref = db.collection("users").document(uid).collection("notes").stream()
    notes = []
    for doc in notes_ref:
        data = doc.to_dict()
        notes.append(
            Note(
                uid=data.get("uid"),
                title=data.get("title"),
                content=data.get("content"),
                createdAt=data.get("createdAt"),
                updatedAt=data.get("updatedAt"),
            )
        )
    return notes

# POST /notes → create under users/{uid}/notes with timestamps
@app.post("/notes", response_model=Note)
async def create_note(note: Note, user=Depends(get_current_user)):
    uid = user["uid"]
    collection_ref = db.collection("users").document(uid).collection("notes")
    new_doc_ref = collection_ref.document(note.uid)
    payload = {
        "uid": note.uid,
        "title": note.title,
        "content": note.content,
        "createdAt": note.createdAt,
        "updatedAt": note.updatedAt,
    }
    new_doc_ref.set(payload)
    created = new_doc_ref.get()
    data = created.to_dict()
    return Note(
        uid=data.get("uid"),
        title=data.get("title"),
        content=data.get("content"),
        createdAt=data.get("createdAt"),
        updatedAt=data.get("updatedAt"),
    )

# PUT /notes/{note_uid} → update within users/{uid}/notes and touch updatedAt
@app.put("/notes/{note_uid}", response_model=Note)
async def update_note(note_uid: str, note: Note, user=Depends(get_current_user)):
    uid = user["uid"]
    if note.uid != note_uid:
        raise HTTPException(status_code=400, detail="Body uid must match path uid")
    doc_ref = db.collection("users").document(uid).collection("notes").document(note_uid)
    doc = doc_ref.get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Note not found")

    doc_ref.update({
        "title": note.title,
        "content": note.content,
        "updatedAt": note.updatedAt,
    })
    updated = doc_ref.get()
    data = updated.to_dict()
    return Note(
        uid=data.get("uid"),
        title=data.get("title"),
        content=data.get("content"),
        createdAt=data.get("createdAt"),
        updatedAt=data.get("updatedAt"),
    )

# DELETE /notes/{note_uid} → delete within users/{uid}/notes
@app.delete("/notes/{note_uid}")
async def delete_note(note_uid: str, user=Depends(get_current_user)):
    uid = user["uid"]
    doc_ref = db.collection("users").document(uid).collection("notes").document(note_uid)
    doc = doc_ref.get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Note not found")

    doc_ref.delete()
    return {"message": "Note deleted successfully"}
