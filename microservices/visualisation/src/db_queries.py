def fetch_company_name(db, company_id):
    cursor = db.execute("SELECT name FROM companies WHERE id = %s;", (company_id,))
    row = cursor.fetchone()
    return row[0] if row else None

def fetch_vulnerability_data(db, company_id, days):
    query = """
        SELECT date_added, COUNT(*) as cve_count
        FROM vulnerabilities
        WHERE company_id = %s 
        AND date_added >= CURRENT_DATE - (%s || ' days')::interval
        GROUP BY date_added
        ORDER BY date_added ASC;
    """
    cursor = db.execute(query, (company_id, days))
    return cursor.fetchall()