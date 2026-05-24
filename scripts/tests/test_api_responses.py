#!/usr/bin/env python3
"""
Script para probar todas las APIs del backend y ver las respuestas.
Útil para debugging de inconsistencias entre front y back.
"""
import requests
import json
from pprint import pprint

BASE_URL = "http://127.0.0.1:8000"
TIMEOUT = 5

def test_endpoint(method, path, data=None, name=None):
	"""Test un endpoint y muestra la respuesta"""
	url = f"{BASE_URL}{path}"
	name = name or f"{method} {path}"
    
	try:
		print(f"\n{'='*60}")
		print(f"Test: {name}")
		print(f"URL: {url}")
		if data:
			print(f"DATA: {json.dumps(data, indent=2)}")
        
		if method == "GET":
			resp = requests.get(url, timeout=TIMEOUT)
		elif method == "POST":
			resp = requests.post(url, json=data, timeout=TIMEOUT)
		else:
			print(f"Unknown method: {method}")
			return
        
		print(f"Status: {resp.status_code}")
		print(f"Headers: {dict(resp.headers)}")
        
		try:
			body = resp.json()
			print(f"Response:")
			pprint(body, width=120, compact=False)
		except Exception as e:
			print(f"Response (text): {resp.text[:500]}")
        
	except requests.exceptions.ConnectionError:
		print(f"✗ Connection error - backend not running?")
	except Exception as e:
		print(f"✗ Error: {e}")

# Test endpoints
print("="*60)
print("BACKEND API TEST SUITE")
print("="*60)

# 1. Health check
test_endpoint("GET", "/ping", name="Health check")

# 2. Get solvers
test_endpoint("GET", "/ejecucion/solvers", name="Get available solvers")

# 3. List batteries
test_endpoint("GET", "/bateria/all?skip=0&limit=100", name="List all batteries")

# 4. Create a battery
create_bateria_data = {"nombre": f"TestBat_{int(__import__('time').time())}"}
test_endpoint("POST", "/bateria/", data=create_bateria_data, name="Create battery")

# Try to get battery 2 (if exists)
test_endpoint("GET", "/bateria/2", name="Get battery 2")

# Try to get tests for battery 2
test_endpoint("GET", "/bateria/prueba/2?skip=0&limit=100", name="Get tests for battery 2")

print("\n" + "="*60)
print("TEST SUITE COMPLETE")
print("="*60)
