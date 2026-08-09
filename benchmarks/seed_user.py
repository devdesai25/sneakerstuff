import requests
import time

def seed_user():
    url = "http://127.0.0.1:8000/api/signup"
    payload = {
        "username": "bench_test_user",
        "email": "bench_test_user@benchmark.com",
        "password": "password123"
    }
    
    # Retry loop waiting for backend to be ready
    for attempt in range(15):
        try:
            resp = requests.post(url, json=payload, timeout=5)
            if resp.status_code in (200, 201):
                print("Seeded bench_test_user successfully!")
                return True
            elif resp.status_code == 409:
                print("bench_test_user already exists, ready for testing!")
                return True
            else:
                print(f"Attempt {attempt+1}: Status {resp.status_code} - {resp.text}")
        except Exception as e:
            print(f"Attempt {attempt+1}: Waiting for backend... ({e})")
        time.sleep(2)
    return False

if __name__ == "__main__":
    seed_user()
