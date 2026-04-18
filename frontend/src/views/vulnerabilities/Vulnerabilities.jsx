import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'
import { STAGING_URL } from '../../vars'
import {
  CCard,
  CCardHeader,
  CCol,
  CRow,
  CTable,
  CTableBody,
  CTableDataCell,
  CTableHead,
  CTableHeaderCell,
  CTableRow,
  CSpinner,
  CBadge,
  CButton,
  CFormInput,
  CInputGroup,
  CInputGroupText
} from '@coreui/react'
import CIcon from '@coreui/icons-react'
import { cilSearch } from '@coreui/icons'

const Vulnerabilities = () => {
  const [vulns, setVulns] = useState([])
  const [loading, setLoading] = useState(true)
  const [sortBy, setSortBy] = useState('date_added')
  const [searchTerm, setSearchTerm] = useState('')
  
  const navigate = useNavigate()

  useEffect(() => {
    const fetchCVEs = async () => {
      setLoading(true)
      try {
        const response = await axios.get(`${STAGING_URL}/v1/cves`, {
          params: { sort_by: sortBy }
        })
        
        const parsedBody = typeof response.data.body === 'string' 
          ? JSON.parse(response.data.body) 
          : response.data

        setVulns(parsedBody.cves || [])
      } catch (error) {
        console.error('Error fetching CVEs:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchCVEs()
  }, [sortBy])

  const filteredVulns = vulns.filter((item) => {
    const search = searchTerm.toLowerCase()
    return (
      item.cve_id.toLowerCase().includes(search) || 
      item.company_name.toLowerCase().includes(search)
    )
  })

  const getBadgeColor = (rating) => {
    switch (rating) {
      case 'CRITICAL': return 'danger'
      case 'HIGH': return 'warning'
      case 'MEDIUM': return 'info'
      default: return 'secondary'
    }
  }

  return (
    <CRow>
      <CCol className="p-0" xs>
        <CCard className="mb-4">
          <CCardHeader className="d-flex justify-content-between align-items-center">
            <strong>Vulnerability Feed</strong>
            <div className="d-flex align-items-center gap-3">
              <div style={{ width: '250px' }}>
                <CInputGroup size="sm">
                  <CInputGroupText><CIcon icon={cilSearch} /></CInputGroupText>
                  <CFormInput 
                    placeholder="Search CVE or Company..." 
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                  />
                </CInputGroup>
              </div>
                <div>
                <button 
                    className={`btn btn-sm ${sortBy === 'date_added' ? 'btn-primary' : 'btn-outline-secondary'} me-2`}
                    onClick={() => setSortBy('date_added')}
                >
                    Date Added
                </button>
                <button 
                    className={`btn btn-sm ${sortBy === 'due_date' ? 'btn-primary' : 'btn-outline-secondary'}`}
                    onClick={() => setSortBy('due_date')}
                >
                    Due Date
                </button>
                </div>
            </div>
          </CCardHeader>
          
          {loading ? (
            <div className="text-center p-5"><CSpinner color="primary" /></div>
          ) : (
            <CTable align="middle" className="mb-0 border" hover responsive>
              <CTableHead>
                <CTableRow>
                  <CTableHeaderCell className="bg-body-tertiary text-center">CVE-ID</CTableHeaderCell>
                  <CTableHeaderCell className="bg-body-tertiary">Vendor</CTableHeaderCell>
                  <CTableHeaderCell className="bg-body-tertiary text-center">Risk Index</CTableHeaderCell>
                  <CTableHeaderCell className="bg-body-tertiary text-center">Rating</CTableHeaderCell>
                  <CTableHeaderCell className="bg-body-tertiary text-center text-primary fw-bold">
                    {sortBy === 'date_added' ? 'Date Added' : 'Due Date'}
                  </CTableHeaderCell>
                  <CTableHeaderCell className="bg-body-tertiary text-center">Actions</CTableHeaderCell>
                </CTableRow>
              </CTableHead>
              <CTableBody>
                {filteredVulns.length > 0 ? (
                  filteredVulns.map((item) => (
                    <CTableRow key={item.cve_id}>
                      <CTableDataCell className="text-center font-monospace small">
                        {item.cve_id}
                      </CTableDataCell>
                      <CTableDataCell className="fw-semibold">
                        {item.company_name}
                      </CTableDataCell>
                      <CTableDataCell className="text-center">
                        {(item.risk_index * 100).toFixed(1)}%
                      </CTableDataCell>
                      <CTableDataCell className="text-center">
                        <CBadge color={getBadgeColor(item.risk_rating)}>
                          {item.risk_rating}
                        </CBadge>
                      </CTableDataCell>
                      <CTableDataCell className="text-center small">
                        {sortBy === 'date_added' ? item.date_added : item.due_date}
                      </CTableDataCell>
                      <CTableDataCell className="text-center">
                        <CButton 
                          color="primary" 
                          size="sm"
                          onClick={() => navigate(`/vulnerabilities/${item.cve_id}`)}
                        >
                          View
                        </CButton>
                      </CTableDataCell>
                    </CTableRow>
                  ))
                ) : (
                  <CTableRow>
                    <CTableDataCell colSpan={6} className="text-center p-4 text-muted">
                      No results found for "{searchTerm}"
                    </CTableDataCell>
                  </CTableRow>
                )}
              </CTableBody>
            </CTable>
          )}
        </CCard>
      </CCol>
    </CRow>
  )
}

export default Vulnerabilities