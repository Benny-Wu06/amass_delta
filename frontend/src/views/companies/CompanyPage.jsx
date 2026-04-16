import React from 'react'
import { useParams } from 'react-router-dom'
import classNames from 'classnames'

import Graph from 'src/components/Graph.jsx'
import Company from 'src/components/Company.jsx'
import dreamybull from 'src/assets/images/dreamybull_suit.jpg'
import { CRow } from '@coreui/react'

const CompanyPage = () => {
  const { company_name } = useParams()
  const companyName = company_name
  // fetch subscribed companies
  const companies = [
    {
      name: 'Microsoft',
      num_vulnerabilities: 362,
      avg_cvss: 7.8,
      avg_epss: 0.526,
      risk_index: 0.68,
      risk_rating: 'HIGH',
      earliest_vuln_date: '2026-04-10',
      // something about cve growth here as well i think
    },
    {
      name: 'Microsoft',
      num_vulnerabilities: 362,
      avg_cvss: 7.8,
      avg_epss: 0.526,
      risk_index: 0.68,
      risk_rating: 'HIGH',
      earliest_vuln_date: '2026-04-10',
      last_vuln: '2026-04-11',
      // something about cve growth here as well i think
    },
  ]

  return (
    <>
      <h2 className="mx-2 mb-4">{companyName}</h2>
      <CRow>
        <Graph header={"Company Heatmap"}></Graph>
        <Graph header={"CVE Growth vs. Time"}></Graph>
      </CRow>

      <CRow>
        <div>metrics</div>
        <Graph header={"Stock Price vs. CVE GROWTH"}></Graph>
      </CRow>
    </>
  )
}

export default CompanyPage
