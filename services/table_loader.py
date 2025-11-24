# Loads pre-extracted tables into memory so numeric queries can access them instantly.
# (This does not extract tables from the PDF— it only reads tables.json at runtime.)

import json

TABLE_JSON_PATH = "data/tables.json"

# Load once on import:
with open(TABLE_JSON_PATH, "r", encoding="utf-8") as f:
    TABLE_DATA = json.load(f)

def get_tables_for_page(page_num: int):
    """
    Returns a list of tables for the given page number.
    """
    return [t["table"] for t in TABLE_DATA if t["page"] == page_num]
