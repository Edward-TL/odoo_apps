"""
Optional Postgres read accelerator + verification helpers.

The in-process engine writes **only** through the ORM (so accounting integrity — taxes,
journal items, sequences, balances — is preserved). Postgres is used here strictly for
*reads*: pre-flight dedup (skip already-imported keys without an ORM round-trip) and
post-run verification (counts / balance checks). Never INSERT accounting rows directly.

``psycopg2`` is imported lazily so importing this module never forces the dependency.
"""
from __future__ import annotations

from typing import Iterable, Optional


def _connect(dsn: str):
    import psycopg2  # local import: optional dependency

    return psycopg2.connect(dsn)


def existing_values(
    dsn: str,
    table: str,
    column: str,
    *,
    where: Optional[str] = None,
    params: Optional[Iterable] = None,
) -> set:
    """
    Return the set of non-null ``column`` values in ``table`` (optionally filtered).

    Example — UUIDs already imported::

        existing_values(dsn, "account_move", "mx_edi_cfdi_uuid",
                        where="company_id = ANY(%s)", params=[company_ids])
    """
    sql = f'SELECT DISTINCT "{column}" FROM "{table}" WHERE "{column}" IS NOT NULL'
    if where:
        sql += f" AND ({where})"
    conn = _connect(dsn)
    try:
        with conn.cursor() as cur:
            cur.execute(sql, list(params) if params is not None else None)
            return {row[0] for row in cur.fetchall()}
    finally:
        conn.close()


def count(dsn: str, table: str, *, where: Optional[str] = None, params: Optional[Iterable] = None) -> int:
    """Row count for ``table`` (optionally filtered) — handy for verification."""
    sql = f'SELECT count(*) FROM "{table}"'
    if where:
        sql += f" WHERE {where}"
    conn = _connect(dsn)
    try:
        with conn.cursor() as cur:
            cur.execute(sql, list(params) if params is not None else None)
            return int(cur.fetchone()[0])
    finally:
        conn.close()


def unbalanced_moves(dsn: str, *, where: Optional[str] = None) -> list[tuple]:
    """
    Verification query: posted moves whose journal items don't sum to zero (should be empty).
    Returns ``[(move_id, sum_balance), ...]``.
    """
    sql = (
        "SELECT am.id, round(sum(aml.balance), 2) AS bal "
        "FROM account_move am JOIN account_move_line aml ON aml.move_id = am.id "
        "WHERE am.state = 'posted'"
    )
    if where:
        sql += f" AND ({where})"
    sql += " GROUP BY am.id HAVING round(sum(aml.balance), 2) <> 0"
    conn = _connect(dsn)
    try:
        with conn.cursor() as cur:
            cur.execute(sql)
            return [(row[0], row[1]) for row in cur.fetchall()]
    finally:
        conn.close()
