def fetch_company_name(db, company_id):
    db.execute("SELECT company_name FROM companies WHERE id = %s;", (company_id,))
    row = db.fetchone()
    return row[0] if row else None

def fetch_vulnerability_data(db, company_name, days):
    query = """
        SELECT date_added, COUNT(*) as cve_count
        FROM vulnerabilities
        WHERE company_name = %s 
        AND date_added >= CURRENT_DATE - (%s || ' days')::interval
        GROUP BY date_added
        ORDER BY date_added ASC;
    """
    db.execute(query, (company_name, days))
    return db.fetchall()