import time


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_index_page_french(client):
    r = client.get("/")
    assert r.status_code == 200
    assert "LinguaFlow" in r.text
    assert "lang=\"fr\"" in r.text


def test_settings_endpoints(client):
    r = client.get("/api/settings")
    assert r.status_code == 200
    assert "remote_enabled" in r.json()
    # Never leak a raw key.
    assert client.get("/api/settings").json().get("remote_api_key") in (None, "")


def test_remote_enable_requires_endpoint(client):
    r = client.put("/api/settings", json={"remote_enabled": True})
    assert r.status_code == 400


def test_engines_endpoint(client):
    r = client.get("/api/engines")
    assert r.status_code == 200
    ids = [e["id"] for e in r.json()["engines"]]
    assert "argos" in ids


def test_upload_rejects_bad_extension(client):
    r = client.post("/api/upload", files={"file": ("evil.exe", b"MZ", "application/octet-stream")})
    assert r.status_code == 415


def test_upload_and_progress(client, mock_engine):
    files = {"file": ("note.txt", b"Hello world\nSecond line\n", "text/plain")}
    data = {"target_lang": "fr", "source_lang": "en", "engine": "argos"}
    r = client.post("/api/upload", files=files, data=data)
    assert r.status_code == 200, r.text
    task_id = r.json()["task_id"]

    for _ in range(50):
        p = client.get(f"/api/tasks/{task_id}/progress").json()
        if p["status"] in ("completed", "failed"):
            break
        time.sleep(0.1)
    assert p["status"] == "completed", p

    d = client.get(f"/api/tasks/{task_id}/download")
    assert d.status_code == 200
    assert b"bonjour" in d.content.lower()


def test_glossary_crud(client):
    r = client.post("/api/glossary", json={"source_term": "cloud", "target_term": "nuage"})
    assert r.status_code == 200
    entry_id = r.json()["id"]
    rows = client.get("/api/glossary").json()
    assert any(x["id"] == entry_id for x in rows)
    client.delete(f"/api/glossary/{entry_id}")
    assert not any(x["id"] == entry_id for x in client.get("/api/glossary").json())


def test_protected_terms_crud(client):
    r = client.post("/api/protected-terms", json={"term": "OpenAI", "category": "brand"})
    assert r.status_code == 200
    tid = r.json()["id"]
    assert any(t["term"] == "OpenAI" for t in client.get("/api/protected-terms").json())
    client.delete(f"/api/protected-terms/{tid}")


def test_history_clear(client):
    assert client.delete("/api/history").status_code == 200
