import React from 'react'
import classNames from 'classnames'

import {
  CAvatar,
  CButton,
  CButtonGroup,
  CCard,
  CCardTitle,
  CCardBody,
  CCardFooter,
  CCardHeader,
  CCol,
  CProgress,
  CRow,
  CTable,
  CTableBody,
  CTableDataCell,
  CTableHead,
  CTableHeaderCell,
  CTableRow,
  CLink,
} from '@coreui/react'
import Company from 'src/components/Company.jsx'
import SubscribeButton from 'src/views/subscriptions/SubscribeButton.jsx'
import dreamybull from 'src/assets/images/dreamybull_suit.jpg'

const Subscriptions = () => {
  // this is why typescript is helpful i think

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
      <img src={dreamybull}></img>
      <CRow>
        <CCol className="p-0" xs>
          <CCard className="mb-4">
            <CCardHeader>Your Companies</CCardHeader>
            <CTable align="middle" className="mb-0 border" hover responsive>
              <CTableHead className="text-nowrap">
                <CTableRow>
                  <CTableHeaderCell className="bg-body-tertiary text-center">Name</CTableHeaderCell>
                  <CTableHeaderCell className="bg-body-tertiary text-center">
                    RISK_INDEX
                  </CTableHeaderCell>
                  <CTableHeaderCell className="bg-body-tertiary text-center">Risk Rating</CTableHeaderCell>
                  <CTableHeaderCell className="bg-body-tertiary text-center">
                    Last Vulnerability
                  </CTableHeaderCell>
                  <CTableHeaderCell className="bg-body-tertiary text-center">Status</CTableHeaderCell>
                </CTableRow>
              </CTableHead>
              <CTableBody>
                {companies.map((company, index) => (
                  <CTableRow key={index}>
                    <CTableDataCell className="text-center">
                      <CLink href={'#/companies/' + encodeURIComponent(company.name)}>
                        {company.name}
                      </CLink>
                    </CTableDataCell>
                    <CTableDataCell className='text-center'>
                      <div>{company.risk_index}</div>
                    </CTableDataCell>
                    <CTableDataCell className='text-center'>
                      <div>{company.risk_rating}</div>
                    </CTableDataCell>
                    <CTableDataCell className="text-center">
                      <div className="fw-semibold">{company.last_vuln}</div>
                    </CTableDataCell>
                    <CTableDataCell className="text-center">
                      <SubscribeButton></SubscribeButton>
                    </CTableDataCell>
                  </CTableRow>
                ))}
              </CTableBody>
            </CTable>
          </CCard>
        </CCol>
      </CRow>
    </>
  )
}

export default Subscriptions
