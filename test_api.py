"""Test script — downloads sample audio and sends to the API."""

import base64
import json
import time
import httpx

API_URL = "http://localhost:8000/api/call-analytics"
API_KEY = "sk_track3_987654321"
SAMPLE_AUDIO_URL = "https://recordings.exotel.com/exotelrecordings/guvi64/5780094ea05a75c867120809da9a199f.mp3"

def main():
    print("=" * 60)
    print("Call Center Compliance API — Integration Test")
    print("=" * 60)

    # 1. Download sample audio
    print("\n[1/3] Downloading sample audio...")
    audio_resp = httpx.get(SAMPLE_AUDIO_URL, timeout=60, follow_redirects=True)
    audio_resp.raise_for_status()
    audio_bytes = audio_resp.content
    print(f"      Downloaded {len(audio_bytes):,} bytes")

    # 2. Encode to Base64
    print("[2/3] Encoding to Base64...")
    audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")
    print(f"      Base64 length: {len(audio_b64):,} chars")

    # 3. Send to API
    print("[3/3] Sending to API...")
    start = time.time()

    response = httpx.post(
        API_URL,
        json={
            "language": "Tamil",
            "audioFormat": "mp3",
            "audioBase64": audio_b64,
        },
        headers={
            "Content-Type": "application/json",
            "x-api-key": API_KEY,
        },
        timeout=300,
    )

    elapsed = time.time() - start
    print(f"      Status: {response.status_code} ({elapsed:.1f}s)")

    if response.status_code == 200:
        data = response.json()
        print(f"\n{'=' * 60}")
        print("✅ SUCCESS")
        print(f"{'=' * 60}")
        print(f"\nLanguage: {data.get('language')}")
        print(f"\n--- Transcript (first 500 chars) ---")
        print(data.get("transcript", "")[:500])
        print(f"\n--- Summary ---")
        print(data.get("summary", ""))
        print(f"\n--- SOP Validation ---")
        sop = data.get("sop_validation", {})
        for k, v in sop.items():
            print(f"  {k}: {v}")
        print(f"\n--- Analytics ---")
        analytics = data.get("analytics", {})
        for k, v in analytics.items():
            print(f"  {k}: {v}")
        print(f"\n--- Keywords ---")
        print(data.get("keywords", []))

        # Save full response
        with open("test_response.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"\nFull response saved to test_response.json")
    else:
        print(f"\n❌ FAILED: {response.text}")

if __name__ == "__main__":
    main()
