def test_get_releases_empty(client):
    print("First release test")
    response = client.get("/api/releases")
    assert response.status_code == 200
    assert response.get_json() == []

def test_create_release(client):
    service_post = client.post("/api/services", json = {"name": "first name"})
    assert service_post.status_code == 201
    service_id = service_post.get_json()["id"]

    release_data = {
        "version": "1.0.0",
        "changelog": "first stable",
        "service_id": service_id
    }
    release_post = client.post("/api/releases", json = release_data)
    data = release_post.get_json()
    assert data["version"] == "1.0.0"
    assert data["changelog"] == "first stable"
    assert data["service_id"] == service_id
    assert data["status"] == "Draft"

def test_create_release_without_service(client):
    release_data = {
        "version": "1.0.0",
        "service_id": "123"
    }
    release_post = client.post("/api/releases", json = release_data)
    assert release_post.status_code == 404
    assert "error" in release_post.get_json()

def test_get_all_releases_by_service(client):
    service_post = client.post("/api/services", json = {"name": "second name"})
    service_id = service_post.get_json()["id"]
    client.post('/api/releases', json={"version": "1.0.0", "service_id": service_id})
    client.post('/api/releases', json={"version": "1.1.0", "service_id": service_id})

    response = client.get(f"/api/services/{service_id}/releases")
    assert response.status_code == 200
    releases = response.get_json()
    assert len(releases) == 2
    assert releases[0]["version"] == "1.0.0"
    assert releases[1]["version"] == "1.1.0"

def test_change_status(client):
    service_post = client.post("/api/services", json = {"name": "third name"})
    service_id = service_post.get_json()["id"]
    release_post = client.post('/api/releases', json={"version": "1.0.0", "service_id": service_id})
    release_id = release_post.get_json()["id"]

    data = release_post.get_json()
    patch_response = client.patch(f"/api/releases/{release_id}/status", json = {"status": "Testing"})
    assert patch_response.status_code == 200
    assert patch_response.get_json()["status"] == "Testing"

# def test_change_status_invalid(client):
#     service_post = client.post("/api/services", json={"name": "test_service"})
#     service_id = service_post.get_json()["id"]
#     release_post = client.post('/api/releases', json={"version": "1.0.0", "service_id": service_id})
#     release_id = release_post.get_json()["id"]

#     response = client.patch(f"/api/releases/{release_id}/status", json={"status": "invalid_status"})
#     assert response.status_code == 400
#     assert "error" in response.get_json()

def test_get_all_releases(client):
    service_post = client.post("/api/services", json = {"name": "fourth name"})
    service_id = service_post.get_json()["id"]
    client.post("/api/releases", json={"version": "2.0.0", "service_id": service_id})
    client.post("/api/releases", json={"version": "2.1.0", "service_id": service_id})
    response = client.get("/api/releases")
    assert response.status_code == 200
    data = response.get_json()
    assert data[0]["version"] == "2.0.0"
    assert data[1]["version"] == "2.1.0"
    print("Last release test")      #debug print