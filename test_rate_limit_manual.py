#!/usr/bin/env python3
"""
Manual test script to verify rate limiting is working.
Run this from outside the container: python test_rate_limit_manual.py
"""
import httpx
import time

def test_rate_limiting():
    """Test that rate limiting is enforced."""
    base_url = "http://localhost:8000"

    print("Testing rate limiting on /api/v1/plans endpoint...")
    print("Configured limit: 100/minute for read operations\n")

    # Make 105 requests rapidly
    responses = []
    for i in range(105):
        try:
            response = httpx.get(f"{base_url}/api/v1/plans", timeout=5.0)
            responses.append(response.status_code)

            # Print headers from first request
            if i == 0:
                print("First request headers:")
                for key, value in response.headers.items():
                    if 'rate' in key.lower() or 'limit' in key.lower():
                        print(f"  {key}: {value}")
                print()

            # Print every 20th request
            if (i + 1) % 20 == 0:
                print(f"Request {i+1}: Status {response.status_code}")

        except Exception as e:
            print(f"Request {i+1} failed: {e}")
            responses.append(0)

    print(f"\nTotal requests: {len(responses)}")
    print(f"200 OK: {responses.count(200)}")
    print(f"429 Too Many Requests: {responses.count(429)}")
    print(f"Errors: {responses.count(0)}")

    if responses.count(429) > 0:
        print("\n✅ Rate limiting is WORKING! Some requests were blocked.")
    else:
        print("\n❌ Rate limiting might NOT be working - no 429 responses received.")
        print("   This could be normal if requests are under the limit.")

if __name__ == "__main__":
    test_rate_limiting()
