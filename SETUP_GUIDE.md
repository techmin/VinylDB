# VinylDB Setup Guide

This guide provides step-by-step instructions to set up and run the VinylDB project.

## Prerequisites

- **Python 3.11+** installed.
- **Node.js 18+** installed (for Phase 2).
- **PostgreSQL** database (we are using Neon).

## Phase 1: Server Setup

### 1. Environment Setup

The project requires a `.env` file in the `server/` directory.

**File:** `server/.env`
```env
DATABASE_URL=postgresql+asyncpg://user:password@endpoint.neon.tech/dbname?sslmode=require
```
*Note: The `sslmode=require` parameter is handled specifically in the code for compatibility.*

### 2. Install Dependencies

Navigate to the project root and run:

```powershell
# Create virtual environment (if not already created)
cd server
python -m venv venv

# Activate virtual environment (Windows)
.\venv\Scripts\Activate

# Install requirements
pip install -r requirements.txt
```

### 3. Run the Server

From the project root (ensure the virtual environment is verified):

```powershell
# PowerShell
.\server\venv\Scripts\Activate
uvicorn server.main:app --reload
```

```bash
# Bash (Git Bash)
source server/venv/Scripts/activate
uvicorn server.main:app --reload
```

The server will start at `http://localhost:8000`.

### 4. Verify Installation

You can test the health of the API by running:

```powershell
curl http://localhost:8000/health
```

Expected response:
```json
{"status": "healthy", "database": "connected, read/write ready"}
```

## Phase 2: Client Setup (Coming Soon)

_Instructions for the Next.js frontend will be added here._
