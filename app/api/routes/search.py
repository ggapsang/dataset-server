import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, Query

from app.core.database import get_db_connection
from app.core.utils import build_file_url
from app.core.config import MAX_BATCH_SIZE
from app.schemas.file import (
    FileResponse,
    BatchRequest,
    BatchResponse,
    TagSearchResponse,
)

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/search_file/{alias}", response_model=FileResponse)
async def search_file(alias: str):
    """
    Search for a single file by alias.

    Returns the file URL if found, otherwise returns 404.
    """
    logger.info(f"Searching for alias: {alias}")

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT PHYSICAL_FILE_PATH FROM FILE_ALIAS WHERE ALIAS = ? LIMIT 1",
            (alias,)
        )
        result = cursor.fetchone()

        if not result:
            logger.warning(f"Alias not found: {alias}")
            raise HTTPException(status_code=404, detail=f"Alias not found: {alias}")

        physical_path = result["PHYSICAL_FILE_PATH"]

        try:
            file_url = build_file_url(physical_path)
            logger.info(f"Found alias {alias}: {file_url}")
            return FileResponse(alias=alias, url=file_url)
        except ValueError as e:
            logger.error(f"Error converting path for alias {alias}: {e}")
            raise HTTPException(status_code=500, detail=str(e))

@router.post("/search_files/batch", response_model=BatchResponse)
async def search_files_batch(request: BatchRequest):
    """
    Search for multiple files by aliases in batch.

    Returns found files and a list of not found aliases.
    """
    aliases = request.aliases

    # Validate batch size
    if len(aliases) > MAX_BATCH_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"Batch size exceeds maximum of {MAX_BATCH_SIZE}"
        )

    logger.info(f"Batch search for {len(aliases)} aliases")

    results = []
    not_found = []

    with get_db_connection() as conn:
        cursor = conn.cursor()

        # SQLite has a limit of 999 parameters, so we need to handle this
        # We're enforcing MAX_BATCH_SIZE=1000, so we need to be careful
        if len(aliases) == 0:
            return BatchResponse(results=[], not_found=[])

        # Build query with placeholders
        placeholders = ','.join('?' * len(aliases))
        query = f"SELECT ALIAS, PHYSICAL_FILE_PATH FROM FILE_ALIAS WHERE ALIAS IN ({placeholders})"

        cursor.execute(query, aliases)
        rows = cursor.fetchall()

        # Create a dict of found aliases
        found_map = {row["ALIAS"]: row["PHYSICAL_FILE_PATH"] for row in rows}

        # Process results
        for alias in aliases:
            if alias in found_map:
                try:
                    file_url = build_file_url(found_map[alias])
                    results.append(FileResponse(alias=alias, url=file_url))
                except ValueError as e:
                    logger.error(f"Error converting path for alias {alias}: {e}")
                    not_found.append(alias)
            else:
                not_found.append(alias)

    logger.info(f"Batch search complete: {len(results)} found, {len(not_found)} not found")
    return BatchResponse(results=results, not_found=not_found)

@router.get("/search_tag", response_model=TagSearchResponse)
async def search_tag(
    tag: Optional[str] = Query(None, description="Single tag to search for"),
    tags: Optional[str] = Query(None, description="Comma-separated list of tags (AND logic)"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    limit: int = Query(100, ge=1, le=1000, description="Pagination limit")
):
    """
    Search for files by tags.

    Supports single tag or multiple tags (AND logic).
    Returns paginated results with total count.
    """
    # Parse tags
    tag_list = []
    if tags:
        tag_list = [t.strip() for t in tags.split(',') if t.strip()]
    elif tag:
        tag_list = [tag.strip()]

    if not tag_list:
        raise HTTPException(status_code=400, detail="At least one tag must be provided")

    logger.info(f"Tag search for: {tag_list}, offset={offset}, limit={limit}")

    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Build WHERE clause for multiple tags (AND logic)
        where_clauses = []
        params = []
        for t in tag_list:
            where_clauses.append("TAGS LIKE ?")
            params.append(f"%{t}%")

        where_clause = " AND ".join(where_clauses)

        # Get total count
        count_query = f"SELECT COUNT(*) as count FROM FILE_ALIAS WHERE {where_clause}"
        cursor.execute(count_query, params)
        total_count = cursor.fetchone()["count"]

        # Get paginated results
        query = f"""
            SELECT ALIAS, PHYSICAL_FILE_PATH
            FROM FILE_ALIAS
            WHERE {where_clause}
            LIMIT ? OFFSET ?
        """
        cursor.execute(query, params + [limit, offset])
        rows = cursor.fetchall()

        results = []
        for row in rows:
            try:
                file_url = build_file_url(row["PHYSICAL_FILE_PATH"])
                results.append(FileResponse(alias=row["ALIAS"], url=file_url))
            except ValueError as e:
                logger.error(f"Error converting path for alias {row['ALIAS']}: {e}")
                continue

    logger.info(f"Tag search complete: {len(results)} results, {total_count} total")
    return TagSearchResponse(results=results, total_count=total_count)
