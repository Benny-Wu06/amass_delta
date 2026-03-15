def fetch_company_name(db, company_id):
    db.execute("SELECT company_name FROM companies WHERE id = %s;", (company_id,))
    row = db.fetchone()
    return row[0] if row else None

def get_heatmap_data(db, company_name):
    query = """
        SELECT 
            CASE
                WHEN cvss_score < 2 THEN '0-2'
                WHEN cvss_score < 4 THEN '2-4'
                WHEN cvss_score < 6 THEN '4-6'
                WHEN cvss_score < 8 THEN '6-8'
                ELSE '8-10'
            END AS cvss_range,
            CASE 
                WHEN epss_score < 0.2 THEN '0-0.2'
                WHEN epss_score < 0.4 THEN '0.2-0.4'
                WHEN epss_score < 0.6 THEN '0.4-0.6'
                WHEN epss_score < 0.8 THEN '0.6-0.8'
                ELSE '0.8-1.0'
            END AS epss_range,
            COUNT(*) as cve_count
        FROM vulnerabilities
        WHERE company_name = %s
        GROUP BY cvss_range, epss_range;
    """
    db.execute(query, (company_name,))
    
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