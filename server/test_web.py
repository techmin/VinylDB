import asyncio
from .mcp_server import search_web

async def main():
    print("--- Testing search_web ---")
    try:
        res = await search_web("Abbey Road Beatles")
        print(res)
    except Exception as e:
        print(f"Error calling search_web: {e}")

if __name__ == "__main__":
    asyncio.run(main())
