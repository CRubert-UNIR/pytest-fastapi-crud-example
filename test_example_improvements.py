# Ejemplo de pruebas adicionales para mejorar la cobertura
# Este archivo muestra cómo implementar las pruebas faltantes más críticas

import pytest


def test_get_users_empty_list(test_client):
    """Test getting users when database is empty."""
    response = test_client.get("/api/users/")
    assert response.status_code == 200
    response_json = response.json()
    assert response_json["status"] == "Success"
    assert response_json["results"] == 0
    assert response_json["users"] == []


def test_get_users_with_data(test_client, user_payload):
    """Test getting users when database has data."""
    # Create a user first
    create_response = test_client.post("/api/users/", json=user_payload)
    assert create_response.status_code == 201
    
    # Get users list
    response = test_client.get("/api/users/")
    assert response.status_code == 200
    response_json = response.json()
    assert response_json["status"] == "Success"
    assert response_json["results"] == 1
    assert len(response_json["users"]) == 1
    assert response_json["users"][0]["first_name"] == "John"
    assert response_json["users"][0]["last_name"] == "Doe"


def test_get_users_pagination(test_client):
    """Test pagination functionality."""
    # Create multiple users
    users_data = [
        {"first_name": "John", "last_name": "Doe", "address": "123 Main St"},
        {"first_name": "Jane", "last_name": "Smith", "address": "456 Oak Ave"},
        {"first_name": "Bob", "last_name": "Johnson", "address": "789 Pine Rd"},
    ]
    
    for user_data in users_data:
        response = test_client.post("/api/users/", json=user_data)
        assert response.status_code == 201
    
    # Test pagination with limit=2
    response = test_client.get("/api/users/?limit=2&page=1")
    assert response.status_code == 200
    response_json = response.json()
    assert response_json["status"] == "Success"
    assert response_json["results"] == 2
    assert len(response_json["users"]) == 2
    
    # Test second page
    response = test_client.get("/api/users/?limit=2&page=2")
    assert response.status_code == 200
    response_json = response.json()
    assert response_json["status"] == "Success"
    assert response_json["results"] == 1
    assert len(response_json["users"]) == 1


def test_get_users_search_functionality(test_client):
    """Test search functionality by first name."""
    # Create users with different names
    users_data = [
        {"first_name": "John", "last_name": "Doe", "address": "123 Main St"},
        {"first_name": "Jane", "last_name": "Smith", "address": "456 Oak Ave"},
        {"first_name": "Johnny", "last_name": "Johnson", "address": "789 Pine Rd"},
    ]
    
    for user_data in users_data:
        response = test_client.post("/api/users/", json=user_data)
        assert response.status_code == 201
    
    # Search for "John" - should return John and Johnny
    response = test_client.get("/api/users/?search=John")
    assert response.status_code == 200
    response_json = response.json()
    assert response_json["status"] == "Success"
    assert response_json["results"] == 2
    
    # Verify the returned users contain "John" in first_name
    for user in response_json["users"]:
        assert "John" in user["first_name"]
    
    # Search for exact match
    response = test_client.get("/api/users/?search=Jane")
    assert response.status_code == 200
    response_json = response.json()
    assert response_json["status"] == "Success"
    assert response_json["results"] == 1
    assert response_json["users"][0]["first_name"] == "Jane"


def test_get_users_search_no_results(test_client, user_payload):
    """Test search with no matching results."""
    # Create a user
    response = test_client.post("/api/users/", json=user_payload)
    assert response.status_code == 201
    
    # Search for non-existent name
    response = test_client.get("/api/users/?search=NonExistent")
    assert response.status_code == 200
    response_json = response.json()
    assert response_json["status"] == "Success"
    assert response_json["results"] == 0
    assert response_json["users"] == []


def test_get_users_pagination_edge_cases(test_client, user_payload):
    """Test pagination edge cases."""
    # Create a user
    response = test_client.post("/api/users/", json=user_payload)
    assert response.status_code == 201
    
    # Test with page=0 (should default to page 1)
    response = test_client.get("/api/users/?page=0")
    assert response.status_code == 200
    
    # Test with very high page number
    response = test_client.get("/api/users/?page=999")
    assert response.status_code == 200
    response_json = response.json()
    assert response_json["results"] == 0
    assert response_json["users"] == []
    
    # Test with limit=0 (should still work)
    response = test_client.get("/api/users/?limit=0")
    assert response.status_code == 200
    response_json = response.json()
    assert response_json["results"] == 0
    assert response_json["users"] == []


# Ejemplo de test para manejo de errores (requiere mock)
def test_get_users_combined_search_and_pagination(test_client):
    """Test combining search and pagination."""
    # Create multiple users with similar names
    users_data = [
        {"first_name": "John", "last_name": "Doe", "address": "123 Main St"},
        {"first_name": "Johnny", "last_name": "Smith", "address": "456 Oak Ave"},
        {"first_name": "Jonathan", "last_name": "Johnson", "address": "789 Pine Rd"},
        {"first_name": "Jane", "last_name": "Wilson", "address": "321 Elm St"},
    ]
    
    for user_data in users_data:
        response = test_client.post("/api/users/", json=user_data)
        assert response.status_code == 201
    
    # Search for "John" with pagination
    response = test_client.get("/api/users/?search=John&limit=2&page=1")
    assert response.status_code == 200
    response_json = response.json()
    assert response_json["status"] == "Success"
    assert response_json["results"] == 2  # Should find John, Johnny (first 2)
    
    # Verify all returned users contain "John"
    for user in response_json["users"]:
        assert "John" in user["first_name"]


# NOTA: Para implementar estos tests en el proyecto real:
# 1. Agregar estas funciones al archivo tests/test_crud_api.py
# 2. Ejecutar: pytest tests/test_crud_api.py::test_get_users_empty_list -v
# 3. Verificar que la cobertura mejore ejecutando: pytest --cov=app --cov-report=term-missing