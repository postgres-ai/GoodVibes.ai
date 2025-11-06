from __future__ import annotations

import re
from collections import defaultdict
from typing import Dict, List, Tuple

from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = "Report index usage and size for shop tables using pg_stat_user_indexes."

    def handle(self, *args, **options):
        rows = self._fetch()
        if not rows:
            self.stdout.write(self.style.WARNING("No indexes found for shop_* tables."))
            return

        # Build simple redundancy hints based on same leading columns per table
        duplicates: Dict[Tuple[str, str], List[int]] = defaultdict(list)
        leading_cols: List[str] = []
        for i, r in enumerate(rows):
            lead = self._leading_columns(r[3])
            leading_cols.append(lead)
            duplicates[(r[0], r[1], lead)].append(i)

        header = f"{'schema':<10} {'table':<18} {'index':<34} {'scan':>8} {'tup_read':>10} {'size_mb':>8}  flags"
        self.stdout.write(header)
        self.stdout.write("-" * len(header))

        for i, (schema, table, index, indexdef, idx_scan, idx_tup_read, bytes_) in enumerate(rows):
            size_mb = bytes_ / (1024 * 1024)
            flags: List[str] = []
            if idx_scan == 0:
                flags.append("unused")
            # Heuristic: any other index on same table with identical leading columns
            key = (schema, table, leading_cols[i])
            if len(duplicates[key]) > 1:
                flags.append("duplicate/covered")
            self.stdout.write(
                f"{schema:<10} {table:<18} {index:<34} {idx_scan:>8} {idx_tup_read:>10} {size_mb:>8.1f}  {' '.join(flags)}"
            )

        self.stdout.write("")
        self.stdout.write("Tip: run `python manage.py reset_index_stats` before a new load to zero scans.")

    def _fetch(self):
        sql = """
        SELECT
          n.nspname AS schema,
          c.relname AS table,
          ic.relname AS index,
          pg_get_indexdef(ic.oid) AS indexdef,
          COALESCE(s.idx_scan, 0) AS idx_scan,
          COALESCE(s.idx_tup_read, 0) AS idx_tup_read,
          pg_relation_size(ic.oid) AS bytes
        FROM pg_class c
        JOIN pg_namespace n ON n.oid = c.relnamespace
        JOIN pg_index i ON i.indrelid = c.oid
        JOIN pg_class ic ON ic.oid = i.indexrelid
        LEFT JOIN pg_stat_user_indexes s ON s.indexrelid = ic.oid
        WHERE n.nspname NOT IN ('pg_catalog', 'information_schema')
          AND c.relkind = 'r'
          AND c.relname LIKE 'shop_%'
        ORDER BY bytes DESC;
        """
        with connection.cursor() as cur:
            cur.execute(sql)
            return cur.fetchall()

    def _leading_columns(self, indexdef: str) -> str:
        # parse between first pair of parentheses, take first column/expression (naive but effective)
        m = re.search(r"\((.+?)\)", indexdef)
        if not m:
            return ""
        cols = m.group(1)
        # Normalize: trim, collapse spaces, lowercase, cut at comma
        first = cols.split(",")[0].strip().lower()
        return first


