import React from 'react'
import { useParams } from 'react-router-dom'
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
import dreamybull from 'src/assets/images/dreamybull_suit.jpg'

const CompanyPage = () => {
  const { company_name } = useParams()

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
      <img src={dreamybull}></img>
      <img src={dreamybull}></img>
      <img src={dreamybull}></img>
      <img src={dreamybull}></img>
      <img src={dreamybull}></img>
      <img src={dreamybull}></img>
      <img src={dreamybull}></img>
      <img src={dreamybull}></img>
      <img src={dreamybull}></img>
      <img src={dreamybull}></img>
      <img src={dreamybull}></img>
      <img src={dreamybull}></img>
      <img src={dreamybull}></img>
      <img src={dreamybull}></img>
      <img src={dreamybull}></img>
      <img src={dreamybull}></img>
      <img src={dreamybull}></img>
      <img src={dreamybull}></img>
      <img src={dreamybull}></img>
      <img src={dreamybull}></img>
      <img src={dreamybull}></img>
      {/* <Company></Company> */}
    </>
  )
}

export default CompanyPage
