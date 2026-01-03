import asyncio
import httpx
from duckduckgo_search import DDGS
from mcp.server.fastmcp import FastMCP
from sqlalchemy import select

from .database import SessionLocal
from .models import Vinyl

# Initialize FastMCP
mcp = FastMCP("VinylDB")

@mcp.tool()
async def add_vinyl(title: str, artist: str, year: int = None, cat_no: str = None, genre: str = None) -> str:
    """Add a new vinyl record to the database.

    Args:
        title: The title of the album/record.
        artist: The artist name.
        year: Release year (optional).
        cat_no: Catalog number (optional).
        genre: Genre (optional).
    """
    try:
        async with SessionLocal() as session:
            new_vinyl = Vinyl(
                title=title,
                artist=artist,
                year=year,
                cat_no=cat_no,
                genre=genre
            )
            session.add(new_vinyl)
            await session.commit()
            return f"Successfully added '{title}' by {artist} to the collection."
    except Exception as e:
        return f"Error adding vinyl: {str(e)}"

@mcp.tool()
async def list_vinyls() -> str:
    """List all vinyl records in the collection."""
    try:
        async with SessionLocal() as session:
            result = await session.execute(select(Vinyl))
            vinyls = result.scalars().all()
            
            if not vinyls:
                return "The collection is empty."
            
            output = ["Current Vinyl Collection:"]
            for v in vinyls:
                output.append(f"- ID {v.id}: {v.title} by {v.artist} ({v.year or 'Year unknown'})")
            
            return "\n".join(output)
    except Exception as e:
        return f"Error listing vinyls: {str(e)}"

@mcp.tool()
async def search_online_metadata(query: str) -> str:
    """Search for vinyl metadata from MusicBrainz.
    
    Args:
        query: Search query (e.g., 'Album Name Artist').
    """
    url = "https://musicbrainz.org/ws/2/release/"
    params = {
        "query": query,
        "fmt": "json"
    }
    headers = {
        "User-Agent": "VinylDBReference/1.0 ( contact@example.com )"
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, params=params, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            releases = data.get("releases", [])
            if not releases:
                return "No results found on MusicBrainz."
            
            output = [f"Found {len(releases)} results on MusicBrainz (showing top 5):"]
            for r in releases[:5]:
                title = r.get("title", "Unknown")
                artist = "Unknown"
                if "artist-credit" in r and r["artist-credit"]:
                    artist = r["artist-credit"][0].get("name", "Unknown")
                date = r.get("date", "Unknown Date")
                output.append(f"- {title} by {artist} ({date})")
                
            return "\n".join(output)
            
        except httpx.HTTPError as e:
            return f"Error searching MusicBrainz: {e}"
        except Exception as e:
            return f"Unexpected error: {str(e)}"

if __name__ == "__main__":
    mcp.run()
@mcp.tool()
async def search_web(query: str) -> str:
    """Search for vinyl information using DuckDuckGo.
    
    Args:
        query: The search query (e.g. 'Abbey Road Beatles vinyl pressing details').
    """
    try:
        results = list(DDGS().text(query, max_results=5))
        if not results:
            return "No web results found."
        
        output = [f"Found web results for '{query}':"]
        for res in results:
            title = res.get('title', 'No Title')
            link = res.get('href', '#')
            body = res.get('body', '')
            output.append(f"- {title} ({link}): {body}")
            
        return "\n".join(output)
    except Exception as e:
        return f"Error searching web: {e}"


