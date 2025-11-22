#!/usr/bin/env python3
"""
Test script for Vercel API deployment
Usage: python test_vercel_api.py [vercel-url]
"""

import sys
import requests
import json
from typing import Optional

VERCEL_URL = sys.argv[1] if len(sys.argv) > 1 else "https://your-app.vercel.app"


def test_health():
    """Test health endpoint"""
    print("1️⃣ Testing /api/health...")
    try:
        response = requests.get(f"{VERCEL_URL}/api/health", timeout=10)
        response.raise_for_status()
        data = response.json()
        print(f"   ✅ Status: {data.get('status')}")
        print(f"   ✅ Vectors indexed: {data.get('vectors_indexed')}")
        return True
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def test_root():
    """Test root endpoint"""
    print("\n2️⃣ Testing / (root)...")
    try:
        response = requests.get(f"{VERCEL_URL}/", timeout=10)
        response.raise_for_status()
        data = response.json()
        print(f"   ✅ Service: {data.get('service')}")
        print(f"   ✅ Version: {data.get('version')}")
        return True
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def test_chat(use_expansion: bool = False):
    """Test chat endpoint"""
    expansion_text = "with query expansion" if use_expansion else "without query expansion"
    print(f"\n3️⃣ Testing /api/chat ({expansion_text})...")
    try:
        response = requests.post(
            f"{VERCEL_URL}/api/chat",
            json={
                "question": "How do I create a site?",
                "use_query_expansion": use_expansion
            },
            timeout=60
        )
        response.raise_for_status()
        data = response.json()
        print(f"   ✅ Answer length: {len(data.get('answer', ''))} chars")
        print(f"   ✅ Sources: {len(data.get('sources', []))}")
        print(f"   ✅ Confidence: {data.get('metadata', {}).get('confidence')}")
        print(f"   ✅ Answer preview: {data.get('answer', '')[:100]}...")
        return True
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def test_search():
    """Test search endpoint"""
    print("\n4️⃣ Testing /api/search...")
    try:
        response = requests.post(
            f"{VERCEL_URL}/api/search",
            json={
                "query": "create site",
                "k": 3
            },
            timeout=30
        )
        response.raise_for_status()
        data = response.json()
        print(f"   ✅ Results: {len(data.get('results', []))}")
        if data.get('results'):
            print(f"   ✅ Top result: {data['results'][0].get('title', 'N/A')}")
        return True
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def main():
    print(f"\n{'='*60}")
    print(f"🧪 Testing Vercel API: {VERCEL_URL}")
    print(f"{'='*60}\n")
    
    results = []
    results.append(("Health Check", test_health()))
    results.append(("Root Endpoint", test_root()))
    results.append(("Chat (fast)", test_chat(use_expansion=False)))
    results.append(("Search", test_search()))
    
    print(f"\n{'='*60}")
    print("📊 Test Summary")
    print(f"{'='*60}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status}: {name}")
    
    print(f"\n   Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print("\n⚠️  Some tests failed. Check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

