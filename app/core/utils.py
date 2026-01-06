from urllib.parse import quote
from app.core.config import NGINX_BASE_URL

def convert_db_path_to_url_path(physical_path: str) -> str:
    """
    Convert database physical path to nginx URL path.
    Input: C:\\Users\\ASUS\\source\\repos\\ggapsang\\dataset-server\\data\\YEP6\\file.png
    Output: /raw/YEP6/file.png
    """
    # Normalize path separators
    normalized = physical_path.replace('\\', '/')

    # Find 'data' directory (case-insensitive search)
    parts = normalized.split('/')
    data_index = -1
    for i, part in enumerate(parts):
        if part.lower() == 'data':
            data_index = i
            break
            
    if data_index >= 0:
        relative_path = '/'.join(parts[data_index + 1:])

        # URL encode each path segment to handle special characters and spaces
        encoded_parts = [quote(part, safe='') for part in relative_path.split('/')]
        encoded_path = '/'.join(encoded_parts)

        return f"/raw/{encoded_path}"
    else:
        # Fallback debug info if strictly needed, or just standard error
        raise ValueError(f"Path does not contain 'data' directory: {physical_path}")

def build_file_url(physical_path: str, base_url: str = None) -> str:
    """Build complete file URL from physical path."""
    url_path = convert_db_path_to_url_path(physical_path)
    if base_url:
        return f"{base_url.rstrip('/')}{url_path}"
    return f"{NGINX_BASE_URL}{url_path}"
