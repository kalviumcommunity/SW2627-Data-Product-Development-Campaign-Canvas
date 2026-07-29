from __future__ import annotations

import re
from typing import Final

_DANGEROUS_TOKENS: Final[tuple[str, ...]] = (
    "DELETE",
    "DROP",
    "INSERT",
    "UPDATE",
    "CREATE",
    "ALTER",
    "REPLACE",
    "ATTACH",
    "DETACH",
    "PRAGMA",
    "BEGIN",
    "COMMIT",
    "ROLLBACK",
    "VACUUM",
    "COPY",
    "IMPORT",
    "EXPORT",
    "GRANT",
    "REVOKE",
    "TRUNCATE",
    "MERGE",
    "CALL",
    "EXEC",
)


def validate_sql_query(query: str) -> str:
    """Validate that a SQL statement is a single read-only query.

    The SQL workspace is intentionally restricted to read-only statements so it
    cannot mutate the database or issue arbitrary administrative commands.
    """
    if not isinstance(query, str):
        raise TypeError("SQL query must be a string")

    cleaned = re.sub(r"--.*?$", "", query, flags=re.MULTILINE)
    cleaned = re.sub(r"/\*.*?\*/", "", cleaned, flags=re.DOTALL)
    cleaned = cleaned.strip()

    if not cleaned:
        raise ValueError("SQL query cannot be empty")

    if ";" in cleaned:
        raise ValueError("Only a single read-only statement is allowed")

    upper_query = cleaned.lstrip().upper()
    if not upper_query.startswith("SELECT") and not upper_query.startswith("WITH"):
        raise ValueError("Only SELECT or WITH read-only queries are allowed")

    for token in _DANGEROUS_TOKENS:
        if re.search(rf"\b{token}\b", cleaned, flags=re.IGNORECASE):
            raise ValueError("Only read-only SELECT queries are allowed")

    return cleaned
