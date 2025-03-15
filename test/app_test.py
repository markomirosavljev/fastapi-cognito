import json
from fastapi.testclient import TestClient

from app import app, settings
from utils import boto

t_client = TestClient(app=app)

eu_token = boto.generate_access_token(
    client_id = settings.userpools["eu"]["app_client_id"],
    username = "eu-user1@test.com",
    password = "Password123!"
)

us_token = boto.generate_access_token(
    client_id = settings.userpools["us"]["app_client_id"],
    username = "us-user1@test.com",
    password = "Password123!"
)

def test_no_header():
    resp = t_client.get("/eu")
    assert resp.status_code == 401

def test_default_pool():
    resp = t_client.get("/eu", headers={"Authorization": f"Bearer {eu_token}"})
    assert resp.status_code == 200
    assert json.loads(resp.content)["message"] == "Hello world"

def test_selected_pool():
    resp = t_client.get("/us", headers={"Authorization": f"Bearer {us_token}"})
    assert resp.status_code == 200
    assert json.loads(resp.content)["message"] == "Hello world"

def test_other_client_issued_token():
    resp = t_client.get("/us", headers={"Authorization": f"Bearer {eu_token}"})
    assert resp.status_code == 401
    assert json.loads(resp.content)["detail"] == "Error decoding JWT token."

def test_optional_no_token():
    resp = t_client.get("/optional")
    assert resp.status_code == 200
    assert json.loads(resp.content)["message"] == "Hello world"

def test_optional_no_token():
    resp = t_client.get("/optional", headers={"Authorization": f"Bearer {eu_token}"})
    assert resp.status_code == 200
    assert json.loads(resp.content)["message"] == "Hello world"
