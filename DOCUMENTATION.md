# VinylDB Documentation

## Project Overview

VinylDB is a full-stack application for managing a vinyl record collection. It aims to provide features for cataloging, searching, and visualizing a user's vinyl library.

## Architecture

The project is divided into two main phases:
1.  **Server (Backend)**: Built with Python/FastAPI using SQLAlchemy for ORM and asyncpg for asynchronous database interactions.
2.  **Client (Frontend)**: (Planned) Built with Next.js/React.

## Technology Stack

- **Language**: Python 3.11
- **Framework**: FastAPI
- **Database**: PostgreSQL (Neon Serverless)
- **ORM**: SQLAlchemy (Async)
- **Driver**: asyncpg

## API Reference

### Health Check

-   **GET** `/health`
    -   Checks the status of the API and the database connection.
    -   **Response**: `{"status": "healthy", "database": "connected, read/write ready"}`

### Vinyls

-   **GET** `/vinyls/`
    -   Retrieves a list of vinyl records.
    -   **Parameters**: `skip` (int), `limit` (int)

-   **POST** `/vinyls/`
    -   Creates a new vinyl record.
    -   **Body**:
        ```json
        {
          "title": "Album Title",
          "artist": "Artist Name",
          "year": 2023,
          "genre": "Genre"
        }
        ```

## Database Schema

### `vinyls` Table

| Column       | Type      | Description                  |
| :----------- | :-------- | :--------------------------- |
| `id`         | Integer   | Primary Key                  |
| `title`      | String    | Album title (Indexed)        |
| `artist`     | String    | Artist name (Indexed)        |
| `year`       | Integer   | Release year                 |
| `cat_no`     | String    | Catalog number               |
| `genre`      | String    | Musical genre                |
| `created_at` | DateTime  | Timestamp of creation        |

## Configuration

The application uses `pydantic-settings` or `python-dotenv` to manage configuration via environment variables.

### Key Variables

-   `DATABASE_URL`: Connection string for the PostgreSQL database.
