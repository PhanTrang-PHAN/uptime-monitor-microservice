import pytest
import httpx
import asyncio

BASE_URL = "http://localhost:8000"

@pytest.mark.asyncio
async def test_health_check():
    """Test 1: Health check endpoint"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

@pytest.mark.asyncio
async def test_create_url():
    """Test 2: Create a new URL to monitor"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/api/urls",
            json={
                "name": "Google",
                "url": "https://testunique.com",
                "check_interval_seconds": 60
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Google"
        assert data["url"] == "https://testunique.com"


@pytest.mark.asyncio
async def test_get_urls():
    """Test 3: Get all monitored URLs"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/api/urls")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

@pytest.mark.asyncio
async def test_delete_url():
    """Test 4: Delete a URL"""
    async with httpx.AsyncClient() as client:
        create_resp = await client.post(
            f"{BASE_URL}/api/urls",
            json={"name": "Test Delete", "url": "https://test.com"}
        )
        url_id = create_resp.json()["id"]
        delete_resp = await client.delete(f"{BASE_URL}/api/urls/{url_id}")
        assert delete_resp.status_code == 200

@pytest.mark.asyncio
async def test_metrics_endpoint():
    """Test 5: Prometheus metrics endpoint"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/metrics")
        assert response.status_code == 200
