"""
Verification script for VinylDB Analytics
Run this AFTER verifying 'docker compose up' is running successfully.
"""
import httpx
import asyncio
import sys

BASE_URL = "http://localhost:8000"

async def verify_analytics():
    print("⏳ Checking API health...")
    async with httpx.AsyncClient() as client:
        try:
            # Check Health
            resp = await client.get(f"{BASE_URL}/health")
            resp.raise_for_status()
            print("✅ API is healthy")
            
            # Check Analytics Dashboard
            print("\n⏳ Verifying Analytics Dashboard (this triggers Spark)...")
            resp = await client.get(f"{BASE_URL}/analytics/dashboard", timeout=30.0)
            resp.raise_for_status()
            data = resp.json()
            
            # Basic validation
            if "overview" in data and "top_artists" in data:
                print("✅ Analytics Dashboard returned valid data")
                print(f"   - Engine: {data.get('engine', 'Unknown')}")
                print(f"   - Total Vinyls: {data['overview']['total_vinyls']}")
                print(f"   - Generated At: {data['generated_at']}")
            else:
                print("❌ Analytics Dashboard returned unexpected structure")
                return False
                
        except httpx.ConnectError:
            print("❌ Could not connect to API. Is Docker running?")
            return False
        except httpx.ReadTimeout:
            print("❌ Request timed out. Spark might be initializing or slow.")
            return False
        except Exception as e:
            print(f"❌ Verification failed: {e}")
            return False
            
    return True

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    success = asyncio.run(verify_analytics())
    sys.exit(0 if success else 1)
