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
} from '@coreui/react'

const Vulnerabilities = () => {
  const vulns = [
    {
      cve_id: 'CVE-2026-0001',
      company: 'diddyblud_inc',
      description: 'TODO connect to backend',
      risk_index: 9,
      risk_rating: 'DEATH',
      due_date: '2026-04-12',
    },
    {
      cve_id: 'CVE-2026-0001',
      company: 'diddyblud_inc',
      description: 'TODO connect to backend',
      risk_index: 9,
      risk_rating: 'DEATH',
      due_date: '2026-04-12',
    },
    {
      cve_id: 'CVE-2026-0001',
      company: 'diddyblud_inc',
      description: 'TODO connect to backend',
      risk_index: 9,
      risk_rating: 'DEATH',
      due_date: '2026-04-12',
    },
    {
      cve_id: 'CVE-2026-0001',
      company: 'diddyblud_inc',
      description:
        'very long long description supre not good and bad holy shit lets see how this renders ok',
      risk_index: 9,
      risk_rating: 'DEATH',
      due_date: '2026-04-12',
    },
    {
      cve_id: 'CVE-2026-0001',
      company: 'diddyblud_inc',
      description:
        'very long long description supre not good and bad holy shit lets see how this renders ok',
      risk_index: 9,
      risk_rating: 'DEATH',
      due_date: '2026-04-12',
    },
  ]

  return (
    <>
      <CRow>
        <CCol className="p-0" xs>
          <CCard className="mb-4">
            <CCardHeader>Recent CVEs</CCardHeader>
            <CTable align="middle" className="mb-0 border" hover responsive>
              <CTableHead className="text-nowrap">
                <CTableRow>
                  {/* icon example */}
                  <CTableHeaderCell className="bg-body-tertiary text-center">
                    {/* <CIcon icon={cilBug} /> */}
                    CVE-ID
                  </CTableHeaderCell>
                  <CTableHeaderCell className="bg-body-tertiary text-center">
                    Company
                  </CTableHeaderCell>
                  <CTableHeaderCell className="bg-body-tertiary">Description</CTableHeaderCell>
                  <CTableHeaderCell className="bg-body-tertiary text-center">
                    Risk Index
                  </CTableHeaderCell>
                  <CTableHeaderCell className="bg-body-tertiary">Risk Rating</CTableHeaderCell>
                  <CTableHeaderCell className="bg-body-tertiary">Due Date</CTableHeaderCell>
                </CTableRow>
              </CTableHead>
              <CTableBody>
                {vulns.map((item, index) => (
                  <CTableRow v-for="item in tableItems" key={index}>
                    <CTableDataCell className="text-center">
                      <div>{item.cve_id}</div>
                    </CTableDataCell>
                    <CTableDataCell>
                      <div>{item.company}</div>
                    </CTableDataCell>
                    <CTableDataCell>
                      <div>{item.description}</div>
                    </CTableDataCell>
                    <CTableDataCell className="text-center">
                      <div className="fw-semibold">{item.risk_index}</div>
                    </CTableDataCell>
                    <CTableDataCell className="text-center">
                      <div className="fw-semibold">{item.risk_rating}</div>
                    </CTableDataCell>
                    <CTableDataCell className="text-center">
                      <div>{item.due_date}</div>
                      {/* <div className="small text-body-secondary text-nowrap">Last login</div>
                            <div className="fw-semibold text-nowrap">{item.activity}</div> */}
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

export default Vulnerabilities
