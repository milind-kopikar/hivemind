import requests

BASE = "http://localhost:8000"

email = "student1@example.com"
password = "TestPass123!"

print("Registering user...")
r = requests.post(f"{BASE}/auth/register", json={"email": email, "password": password})
print(r.status_code, r.text)

print("Logging in...")
r = requests.post(f"{BASE}/auth/login", json={"email": email, "password": password})
print(r.status_code, r.text)

if r.ok:
    token = r.json().get('access_token')
    print("Got token:", token[:40] + '...')
    # test protected endpoint
    headers = {"Authorization": f"Bearer {token}"}
    r2 = requests.get(f"{BASE}/me", headers=headers)
    print("/me ->", r2.status_code, r2.text)
else:
    print("Login failed, cannot test /me endpoint")
