import React, { useEffect, useState } from 'react'
import classNames from 'classnames'
import axios from 'axios'

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
import SubscribeButton from 'src/components/SubscribeButton.jsx'
import dreamybull from 'src/assets/images/dreamybull_suit.jpg'
import { BASE_URL } from '../../vars'
import CompanyRow from './CompanyRow.jsx'

const AllCompanies = () => {
  const [companyNames, setCompanyNames] = useState([])
  const [numCompanies, setNumCompanies] = useState(0)
  // this is why typescript is helpful i think
  useEffect(() => {
    const fetchCompanies = async () => {
      try {
        const response = await axios.get(`${BASE_URL}/v1/companies`)
        setCompanyNames(response.data.companies)
        setNumCompanies(response.data.count)
        console.log(response.data)
      } catch (error) {
        console.error('Failed to fetch all companies:', error)
      }
    }
    fetchCompanies()
  }, [])

  return (
    <>
      <CRow>
        <CCol className="p-0" xs>
          <CCard className="mb-4">
            <CCardHeader>
              <div>Companies ({numCompanies})</div>
              <div>Sort by: TODO</div>
              <div>TODO SEARCH bAR</div>
            </CCardHeader>
            <CTable align="middle" className="mb-0 border" hover responsive>
              <CTableHead className="text-nowrap">
                <CTableRow>
                  <CTableHeaderCell className="bg-body-tertiary text-center">Name</CTableHeaderCell>
                </CTableRow>
              </CTableHead>
              <CTableBody>
                {companyNames.map((name, index) => (
                  <CompanyRow companyName={name} key={index}></CompanyRow>
                ))}
              </CTableBody>
            </CTable>
          </CCard>
        </CCol>
      </CRow>
    </>
  )
}

export default AllCompanies
