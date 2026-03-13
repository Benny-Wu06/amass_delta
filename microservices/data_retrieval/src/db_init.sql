-- DRAFT, may need to change companies as above into below
create table companies (
    id serial primary key,
    company_name text unique not null
    );

-- this table needs to be created before vulnerabilities i believe
create table companies(
	id serial primary key,
	company_name text not null,
	num_vulnerabilities integer, 
	avg_cvss numeric,
	avg_epss numeric,
	risk_index numeric not null,
	risk_rating text not null,
	earliest_vuln_date date);


create table vulnerabilities(
    cve_id varchar(20) primary key,
    company_id integer not null,
    foreign key (company_id) references companies(id),
    vulnerability_name text not null,
    description text not null,
    date_added date not null,
    due_date date not null,
    cvss_score numeric,
    cvss_severity text,
    epss_score numeric,
    epss_percentile numeric
);

-- get company summary query
SELECT 
    c.company_name as company,
    COUNT(v.cve_id) as cve_count,
    AVG(v.epss_score) as avg_epss,
    AVG(v.cvss_score) as avg_cvss,
    c.risk_index,
    c.risk_rating
FROM companies c
LEFT JOIN vulnerabilities v ON c.id = v.company_id
WHERE c.company_name = 'COMPANY_NAME'
GROUP BY c.id;
