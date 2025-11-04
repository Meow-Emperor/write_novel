from __future__ import annotations


def test_create_novel(client):
    """Test creating a novel."""
    response = client.post(
        "/api/novels/",
        json={
            "title": "Test Novel",
            "author": "Test Author",
            "genre": "Fantasy",
            "synopsis": "A test novel",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Novel"
    assert data["author"] == "Test Author"
    assert "id" in data


def test_list_novels(client):
    """Test listing novels."""
    # Create a novel first
    client.post(
        "/api/novels/",
        json={"title": "Test Novel", "author": "Test Author"},
    )
    
    # List novels
    response = client.get("/api/novels/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1


def test_get_novel(client):
    """Test getting a specific novel."""
    # Create a novel
    create_response = client.post(
        "/api/novels/",
        json={"title": "Test Novel", "author": "Test Author"},
    )
    novel_id = create_response.json()["id"]
    
    # Get the novel
    response = client.get(f"/api/novels/{novel_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == novel_id
    assert data["title"] == "Test Novel"


def test_update_novel(client):
    """Test updating a novel."""
    # Create a novel
    create_response = client.post(
        "/api/novels/",
        json={"title": "Test Novel", "author": "Test Author"},
    )
    novel_id = create_response.json()["id"]
    
    # Update the novel
    response = client.put(
        f"/api/novels/{novel_id}",
        json={"title": "Updated Novel"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Novel"
    assert data["author"] == "Test Author"


def test_delete_novel(client):
    """Test deleting a novel."""
    # Create a novel
    create_response = client.post(
        "/api/novels/",
        json={"title": "Test Novel", "author": "Test Author"},
    )
    novel_id = create_response.json()["id"]
    
    # Delete the novel
    response = client.delete(f"/api/novels/{novel_id}")
    assert response.status_code == 204
    
    # Verify it's deleted
    get_response = client.get(f"/api/novels/{novel_id}")
    assert get_response.status_code == 404


def test_get_nonexistent_novel(client):
    """Test getting a novel that doesn't exist."""
    response = client.get("/api/novels/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404
