import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { CCard, CCardBody, CCardLink, CCardSubtitle, CCardText, CCardTitle } from '@coreui/react'
import { BASE_URL, STAGING_URL } from '../vars'

const Company = ({ className, company, company_name }) => {
  const [companyData, setCompanyData] = useState(null)
  const [loading, setLoading] = useState(true)
  console.log(company_name)

  useEffect(() => {
    const fetchCompany = async () => {
      try {
        const response = await axios.get(`${STAGING_URL}/v1/companies/${company_name}`)
        setCompanyData(response.data)
        console.log(response.data)
      } catch (error) {
        console.error('Failed to fetch company:', error)
      } finally {
        setLoading(false)
      }
    }
    fetchCompany(company_name)
  }, [company_name])

  if (loading) return <div>Loading...</div>
  if (!companyData) return <div>No data found.</div>
  return (
    <>
      <CCard className={className} style={{ width: '18rem' }}>
        <CCardBody>
          <CCardTitle>this card should now show info about watchlists</CCardTitle>
          <CCardSubtitle className="mb-2 text-body-secondary">{company.risk_rating}</CCardSubtitle>
          cvss: {company.avg_cvss}
          <br />
          epss: {company.avg_epss}
          <br />
          risk_index: {company.risk_index}
          <br />
          last_vuln_date: {company.earliest_vuln_date}
        </CCardBody>
      </CCard>
    </>
  )
}

export default Company
