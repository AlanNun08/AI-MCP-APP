#!/usr/bin/env python3
import requests

# Test simple login
print("Testing simple login...")

login_data = {
    "email": "demo@test.com", 
    "password": "password123"
}

response = requests.post("https://recipe-cart-app-1.emergent.host/api/auth/login", json=login_data)
print(f"Status: {response.status_code}")
print(f"Response: {response.text}")