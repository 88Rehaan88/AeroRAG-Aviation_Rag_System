# This code basically detects the intent behind the query, whether the user is asking for a normal query or a table-based one:

import re

def is_numeric_query(query: str) -> bool:
    """
    Detects whether a user query is a numeric/table-based aircraft
    performance question. These usually require using tables 
    instead of normal text retrieval.
    """
    q = query.lower().strip()

    # Count numeric tokens in the query: 
    # (Since table-based questions almost always contain multiple numbers in them) 
    numbers = re.findall(r"\d[\d,]*", q)
    num_count = len(numbers)


    # Performance/table keywords:
    # (These terms appear frequently in Boeing performance tables and
    # help us distinguish numeric queries from general “text” queries.)
    TABLE_KEYWORDS = [
        "takeoff", "calculate", "compute", "landing", "approach",
        "oat", "pressure altitude",
        "climb", "limit", "field length",
        "corrected", "runway",
        "kg", "kgs", "lb", "lbs",
        "ft", "feet",
        "°c", "degrees", "temperature",
        "slope",
        "v1", "v2", "vr",
        "field limit", "climb limit", "limit weight",
        "performance",
    ]

    has_table_word = any(k in q for k in TABLE_KEYWORDS)

    # Classification rule:
    """ A query is treated as numeric only when both conditions hold:
        1) It includes at least two numbers
        2) It references performance/table terminology """    
    numeric = (num_count >= 2) and has_table_word
    
    return numeric
