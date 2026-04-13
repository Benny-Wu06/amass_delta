import React from 'react'
import { CCard, CCardBody, CCardLink, CCardSubtitle, CCardText, CCardTitle } from '@coreui/react'

export const Company = ({ className, company }) => (
  <CCard className={className} style={{ width: '18rem' }}>
    <CCardBody>
      <CCardTitle>{company.name}</CCardTitle>
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
)

export default Company
