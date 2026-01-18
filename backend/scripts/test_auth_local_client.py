from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

email = "student_local@example.com"
password = "LocalPass123!"

print("Registering via TestClient...")
r = client.post("/auth/register", json={"email": email, "password": password})
print(r.status_code, r.json())

print("Logging in via TestClient...")
r = client.post("/auth/login", json={"email": email, "password": password})
print(r.status_code, r.json())

if r.ok:
    token = r.json().get('access_token')
    print("Got token:", token[:40] + '...')
    headers = {"Authorization": f"Bearer {token}"}
    r2 = client.get("/me", headers=headers)
    print("/me ->", r2.status_code, r2.json())
else:
    print("Login failed, cannot test /me endpoint")
