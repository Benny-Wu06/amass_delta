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
import CIcon from '@coreui/icons-react'
import {
  cibCcAmex,
  cibCcApplePay,
  cibCcMastercard,
  cibCcPaypal,
  cibCcStripe,
  cibCcVisa,
  cibGoogle,
  cibFacebook,
  cibLinkedin,
  cifBr,
  cifEs,
  cifFr,
  cifIn,
  cifPl,
  cifUs,
  cibTwitter,
  cilCloudDownload,
  cilPeople,
  cilUser,
  cilUserFemale,
} from '@coreui/icons'

import Company from 'src/components/Company.jsx'

import avatar1 from 'src/assets/images/avatars/1.jpg'
import avatar2 from 'src/assets/images/avatars/2.jpg'
import avatar3 from 'src/assets/images/avatars/3.jpg'
import dreamybull from 'src/assets/images/dreamybull_suit.jpg'

import WidgetsBrand from '../widgets/WidgetsBrand'
import WidgetsDropdown from '../widgets/WidgetsDropdown'
import MainChart from './MainChart'

const Dashboard = () => {
  // this is why typescript is helpful i think
  const exampleCompany = {
    name: 'Microsoft',
    num_vulnerabilities: 362,
    avg_cvss: 7.8,
    avg_epss: 0.526,
    risk_index: 0.68,
    risk_rating: 'HIGH',
    earliest_vuln_date: '2026-04-10',
    // something about cve growth here as well i think
  }

  const tableExample = [
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
      <CCard className="fs-3">TODO alert dropdown maybe should be a modal?</CCard>
      <CRow>
        <Company className="mb-4 mx-2" company={exampleCompany}></Company>
        <Company className="mb-4 mx-2" company={exampleCompany}></Company>
        <Company className="mb-4 mx-2" company={exampleCompany}></Company>
        <Company className="mb-4 mx-2" company={exampleCompany}></Company>
        <Company className="mb-4 mx-2" company={exampleCompany}></Company>
        <Company className="mb-4 mx-2" company={exampleCompany}></Company>
        <Company className="mb-4 mx-2" company={exampleCompany}></Company>
        <Company className="mb-4 mx-2" company={exampleCompany}></Company>
      </CRow>
      <CRow>
        <CCol className="p-0" xs>
          <CCard className="mb-4">
            <CCardHeader>Recent CVEs</CCardHeader>
            <CTable align="middle" className="mb-0 border" hover responsive>
              <CTableHead className="text-nowrap">
                <CTableRow>
                  {/* icon example */}
                  {/* <CTableHeaderCell className="bg-body-tertiary">
                    <CIcon icon={dreamybull} />
                  </CTableHeaderCell> */}
                  <CTableHeaderCell className="bg-body-tertiary text-center">
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
                {tableExample.map((item, index) => (
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

export default Dashboard
