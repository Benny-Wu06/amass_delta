type RiskLevel = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';

export interface Company {
  name: string;
  num_vulnerabilities: string; // Keep as string since your example uses quotes
  avg_cvss: number;
  avg_epss: number;
  risk_index: number;
  risk_rating: RiskLevel;
  earliest_vuln_date: string;
  cve_growth?: number; // Added as an optional field based on your comment
}
