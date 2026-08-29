def test_get_services_empty(client):
    print("First service test")     #debug print
    response = client.get("/api/services")
    assert response.status_code == 200
    assert response.get_json() == []

def test_add_service(client):
    new_servise = {
        "name": "some name",
        "repository_url": "https://github.com/"
    }
    response = client.post('/api/services', json=new_servise)
    assert response.status_code == 201
    data = response.get_json()
    assert data["id"] == 1
    assert data["name"] == "some name"
    assert data["repository_url"] == "https://github.com/"

def test_add_service_without_name(client):
    new_servise = {
        "repository_url": "https://github.com/"
    }
    response = client.post('/api/services', json=new_servise)
    assert response.status_code == 400

def test_create_service_duplicate_name(client):
    new_servise = {"name": "some new name"}
    
    res1 = client.post('/api/services', json=new_servise)
    assert res1.status_code == 201

    res2 = client.post('/api/services', json=new_servise)
    assert res2.status_code == 400

def test_get_all_services(client):
    client.post("/api/services", json={"name": "ServiceA"})
    client.post("/api/services", json={"name": "ServiceB"})
    response = client.get("/api/services")
    assert response.status_code == 200
    data = response.get_json()
    assert data[2]["name"] == "ServiceA"
    assert data[3]["name"] == "ServiceB"
    print("Last service test")      #debug print