import sqlglot
from sqlglot import exp

ALLOWED_TABLES = {"products", "sales"}


def check_sql(sql: str) -> str:
    parsed = sqlglot.parse_one(sql, read="sqlite")
    if not isinstance(parsed, (exp.Select, exp.With)):
        raise ValueError("Only SELECT queries are allowed.")
    for forbidden in (exp.Insert, exp.Update, exp.Delete, exp.Drop, exp.Alter):
        if parsed.find(forbidden):
            raise ValueError("Write or delete queries are blocked.")
    tables = {t.name.lower() for t in parsed.find_all(exp.Table) if t.name}
    if not tables.issubset(ALLOWED_TABLES):
        raise ValueError("Table not allowed.")
    if isinstance(parsed, exp.Select) and parsed.args.get("limit") is None:
        parsed = parsed.limit(100)
    return parsed.sql(dialect="sqlite")