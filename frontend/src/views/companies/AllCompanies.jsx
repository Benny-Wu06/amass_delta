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
  CFormInput,
  CInputGroup,
  CInputGroupText,
  CLink,
} from '@coreui/react'
import Company from 'src/components/Company.jsx'
import SubscribeButton from 'src/components/SubscribeButton.jsx'
import dreamybull from 'src/assets/images/dreamybull_suit.jpg'
import { BASE_URL } from '../../vars'
import CompanyRow from './CompanyRow.jsx'
import CIcon from '@coreui/icons-react'
import { cilSearch } from '@coreui/icons'

const AllCompanies = () => {
  const [companyNames, setCompanyNames] = useState([])
  const [numCompanies, setNumCompanies] = useState(0)
  const [searchTerm, setSearchTerm] = useState('') 

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

  const filteredCompanies = companyNames.filter((name) =>
    name.toLowerCase().includes(searchTerm.toLowerCase())
  )

  return (
    <>
      <CRow>
        <CCol className="p-0" xs>
          <CCard className="mb-4">
            <CCardHeader>
              <div>
                <strong>Companies</strong> <small className="text-muted">({filteredCompanies.length})</small>
              </div>
              <div style={{ width: '300px' }}>
                <CInputGroup size="sm">
                  <CInputGroupText>
                    <CIcon icon={cilSearch} />
                  </CInputGroupText>
                  <CFormInput
                    placeholder="Search companies..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                  />
                </CInputGroup>
              </div>
            </CCardHeader>
            <CTable align="middle" className="mb-0 border" hover responsive>
              <CTableHead className="text-nowrap">
                <CTableRow>
                  <CTableHeaderCell className="bg-body-tertiary text-center">Name</CTableHeaderCell>
                </CTableRow>
              </CTableHead>
              <CTableBody>
                {filteredCompanies.length > 0 ? (
                  filteredCompanies.map((name, index) => (
                    <CompanyRow companyName={name} key={index} />
                  ))
                ) : (
                  <CTableRow>
                    <CTableDataCell className="text-center p-3 text-muted">
                      No companies found matching "{searchTerm}"
                    </CTableDataCell>
                  </CTableRow>
                )}
              </CTableBody>
            </CTable>
          </CCard>
        </CCol>
      </CRow>
    </>
  )
}

export default AllCompanies
