import re
from urllib.parse import urlparse

VALID_ENTITY_ID_PATTERN = re.compile(r"^[A-Z]\d{1,15}$")
VALID_OPENALEX_URL_PATTERN = re.compile(r"^https://openalex\.org/[A-Z]\d{1,15}$")
VALID_KEYWORD_URL_PATTERN = re.compile(r"^https://openalex\.org/keywords/[A-Za-z0-9-]+$")


def validate_entity_id(entity_id: str, entity_type: str) -> str:
    """Validate and sanitize entity IDs."""
    # Strip whitespace
    entity_id = entity_id.strip()

    # Check if it's a URL
    if entity_id.startswith("http"):
        parsed = urlparse(entity_id)
        if entity_type.lower() == "keyword":
            if not VALID_KEYWORD_URL_PATTERN.match(entity_id):
                message = f"Invalid OpenAlex URL: {entity_id}"
                raise ValueError(message)
            entity_id = parsed.path.split("/")[-1]
        else:
            if not VALID_OPENALEX_URL_PATTERN.match(entity_id):
                message = f"Invalid OpenAlex URL: {entity_id}"
                raise ValueError(message)
            entity_id = parsed.path.split("/")[-1]

    if entity_type.lower() == "keyword":
        if entity_id.startswith("keywords/"):
            entity_id = entity_id.split("/", 1)[1]
        if not entity_id or "/" in entity_id:
            message = f"Invalid keyword slug: {entity_id}"
            raise ValueError(message)
        return entity_id

    # Validate ID format
    if not VALID_ENTITY_ID_PATTERN.match(entity_id):
        message = f"Invalid entity ID format: {entity_id}"
        raise ValueError(message)

    expected_prefix = entity_type[0].upper()
    if not entity_id.startswith(expected_prefix):
        message = f"Entity ID {entity_id} does not match type {entity_type}"
        raise ValueError(message)

    return entity_id
