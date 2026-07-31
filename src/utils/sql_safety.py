from __future__ import annotations

import os
import sqlite3
from typing import Any, Final
import pandas as pd

try:
    import sqlglot
    from sqlglot import exp
except ImportError:
    sqlglot = None  # Fallback gracefully if library is missing


_ALLOWED_ROOT_TYPES: Final[tuple[type[exp.Expression], ...]] = (
    exp.Select,
    exp.Expression,  # Fallback for general expressions if fully safe
)

# Explicit list of non-read-only expressions to reject during AST traversal
_FORBIDDEN_AST_NODES: Final[tuple[type[exp.Expression], ...]] = (
    exp.Insert,
    exp.Update,
    exp.Delete,
    exp.Create,
    exp.Drop,
    exp.AlterTable,
    exp.Pragma,
    exp.Command,
    exp.Transaction,
    exp.Commit,
    exp.Rollback,
)


def validate_sql_query(query: str) -> str:
    """Validate that a SQL statement is strictly a single read-only query.

    Uses AST parsing (via sqlglot) to guarantee that no mutation statements,
    multiple statements, or state-changing commands can be executed.

    Raises:
        TypeError: If query is not a string.
        ValueError: If query is empty, contains multiple statements, or is not read-only.
    """
    if not isinstance(query, str):
        raise TypeError("SQL query must be a string")

    cleaned = query.strip()
    if not cleaned:
        raise ValueError("SQL query cannot be empty")

    # If sqlglot is installed, perform AST-level parsing and validation
    if sqlglot is not None:
        try:
            parsed_statements = sqlglot.parse(cleaned, read="sqlite")
        except Exception as err:
            raise ValueError(f"Invalid SQL syntax: {err}") from err

        # Filter out empty statements resulting from trailing semicolons
        valid_statements = [s for s in parsed_statements if s is not None]

        if not valid_statements:
            raise ValueError("SQL query cannot be empty")

        if len(valid_statements) > 1:
            raise ValueError("Only a single read-only statement is allowed")

        ast = valid_statements[0]

        # Verify root statement type is a SELECT or WITH (CTE) query
        if not isinstance(ast, (exp.Select, exp.Union)):
            # Handle CTEs (WITH ... SELECT ...)
            if isinstance(ast, exp.Expression) and ast.key == "select":
                pass
            else:
                raise ValueError("Only SELECT or CTE (WITH ... SELECT) queries are allowed")

        # Walk full AST tree to catch nested mutation operations (e.g. inside CTEs or subqueries)
        for node in ast.walk():
            if isinstance(node, _FORBIDDEN_AST_NODES):
                raise ValueError(
                    f"Forbidden SQL operation detected: {node.key.upper()}. Only read-only queries are allowed."
                )

    else:
        # Fallback basic checks if sqlglot isn't present
        # Reject trailing or embedded multiple statements
        statements = [s for s in cleaned.split(";") if s.strip()]
        if len(statements) > 1:
            raise ValueError("Only a single read-only statement is allowed")

        upper_query = cleaned.lstrip().upper()
        if not (upper_query.startswith("SELECT") or upper_query.startswith("WITH")):
            raise ValueError("Only SELECT or WITH read-only queries are allowed")

    return cleaned.rstrip(";")


def execute_read_only_query(db_path: str, query: str) -> pd.DataFrame:
    """Safely executes a validated SQL query against a SQLite database in strict READ-ONLY mode.

    Args:
        db_path: Absolute or relative file path to the SQLite database.
        query: The raw SQL query string from user input.

    Returns:
        pandas.DataFrame: Query result set.

    Raises:
        FileNotFoundError: If the target SQLite file does not exist.
        ValueError: If query validation fails.
        sqlite3.OperationalError: If the database execution fails or attempts a write action.
    """
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Database file not found at: {db_path}")

    # Step 1: Validate query at AST level
    sanitized_query = validate_sql_query(query)

    # Step 2: Enforce database-level read-only URI connection
    # URI format: file:path/to/db.sqlite?mode=ro
    abs_db_path = os.path.abspath(db_path)
    db_uri = f"file:{abs_db_path}?mode=ro"

    conn = sqlite3.connect(db_uri, uri=True)
    try:
        # Step 3: Enforce secondary connection-level safety PRAGMA
        conn.execute("PRAGMA query_only = ON;")
        df = pd.read_sql_query(sanitized_query, conn)
        return df
    finally:
        conn.close()