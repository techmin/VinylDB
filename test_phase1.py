"""
Phase 1 Verification Test Suite
Verifies:
1. Database Connection (PostgreSQL)
2. Basic API (CRUD operations)
3. Analytics Engine (Availability check)
4. MCP Server (Import check)
"""

import httpx
import asyncio
import sys
import os
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BASE_URL = "http://localhost:8000"

async def test_database_connection():
    """Verify direct database connection"""
    print("\n--- Testing Database Connection ---")
    
    # Import engine from the actual application
    try:
        from server.database import engine
    except ImportError as e:
        print(f"[FAIL] Could not import engine from server.database: {e}")
        return False
    
    try:
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            print(f"[PASS] Database connected successfully (Result: {result.scalar()})")
        return True
    except Exception as e:
        print(f"[FAIL] Database connection failed: {e}")
        return False


async def test_api_health():
    """Verify API health endpoint"""
    print("\n--- Testing API Health ---")
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(f"{BASE_URL}/health")
            if resp.status_code == 200:
                data = resp.json()
                print(f"[PASS] API is healthy")
                print(f"   - Database: {data.get('database')}")
                print(f"   - Spark Available: {data.get('spark_available')}")
                return True
            else:
                print(f"[FAIL] API returned status {resp.status_code}")
                return False
        except httpx.ConnectError:
            print("[FAIL] Could not connect to API (is server running?)")
            return False

async def test_crud_operations():
    """Verify basic CRUD operations"""
    print("\n--- Testing Basic CRUD Operations ---")
    async with httpx.AsyncClient() as client:
        try:
            # 1. Create a Test Vinyl
            vinyl_data = {
                "title": "Test Phase 1 Album",
                "artist": "The Testers",
                "year": 2024,
                "genre": "Test Rock",
                "cat_no": "TST-001"
            }
            resp = await client.post(f"{BASE_URL}/vinyls/", json=vinyl_data)
            if resp.status_code == 200:
                created_vinyl = resp.json()
                print(f"[PASS] Created vinyl: {created_vinyl['title']} (ID: {created_vinyl['id']})")
            else:
                print(f"[FAIL] Failed to create vinyl: {resp.text}")
                return False
            
            # 2. Read Vinyls
            resp = await client.get(f"{BASE_URL}/vinyls/")
            if resp.status_code == 200:
                vinyls = resp.json()
                found = any(v['id'] == created_vinyl['id'] for v in vinyls)
                if found:
                    print(f"[PASS] Retrieved vinyl list containing new item")
                else:
                    print(f"[FAIL] New item not found in list")
                    return False
            else:
                print(f"[FAIL] Failed to retrieve vinyls: {resp.text}")
                return False
            
            return True
        except Exception as e:
            print(f"[FAIL] CRUD test failed: {e}")
            return False

async def verify_mcp_integration():
    """Verify MCP server code integrity"""
    print("\n--- Testing MCP Integration ---")
    try:
        from server import mcp_server
        print("[PASS] MCP Server module imports successfully")
        return True
    except ImportError as e:
        print(f"[FAIL] Could not import server.mcp_server module: {e}")
        return False
    except Exception as e:
        print(f"[FAIL] MCP Server module error: {e}")
        return False

async def main():
    print("Starting Phase 1 Verification Suite")
    
    # 1. Database
    db_success = await test_database_connection()
    if not db_success:
        print("\n[FAIL] Database checks failed. Aborting.")
        sys.exit(1)
        
    # 2. API Health
    # Note: Server must be running for this.
    try:
        api_success = await test_api_health()
    except:
        print("\n[WARN] API seems down. Please start the server manually.")
        api_success = False

    if api_success:
        # 3. CRUD
        await test_crud_operations()
    
    # 4. MCP
    await verify_mcp_integration()
    
    print("\nVerification Complete")

if __name__ == "__main__":
    # Add current directory to path for imports
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
