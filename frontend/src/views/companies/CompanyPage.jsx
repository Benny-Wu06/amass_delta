import React from 'react'
import { useParams } from 'react-router-dom'
import classNames from 'classnames'

// import {
//   CCard,
//   CHeader,
//   CHeaderBrand
// } from '@coreui/react'

import { 
  CRow, CCol, CCard, CCardBody, CCardHeader,
  CTable, CTableHead, CTableRow, CTableHeaderCell, CTableBody, CTableDataCell,
  CPagination, CPaginationItem, CBadge,
  CHeader
} from '@coreui/react'
import Company from 'src/components/Company.jsx'
import dreamybull from 'src/assets/images/dreamybull_suit.jpg'

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

      <CRow className="mb-4">
        <CCol md={6}>
          <CCard className="h-150">
            <CCardHeader>Company Heatmap</CCardHeader>
            <CCardBody className="d-flex align-items-center justify-content-center">
              <div style={{ height: '250px', background: '#2f84d9ff', width: '100%' }}>
                CONNECT TO HEATMAP
              </div>
            </CCardBody>
          </CCard>
        </CCol>
      </CRow>
    </>
  )
}

export default CompanyPage
