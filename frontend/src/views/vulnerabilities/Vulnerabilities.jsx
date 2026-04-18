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
  CButton
} from '@coreui/react'

const Vulnerabilities = () => {
  const [vulns, setVulns] = useState([])
  const [loading, setLoading] = useState(true)
  const [sortBy, setSortBy] = useState('date_added')
  
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
                  <CTableHeaderCell className="bg-body-tertiary text-center">{sortBy === 'date_added' ? 'Date Added' : 'Due Date'}</CTableHeaderCell>
                </CTableRow>
              </CTableHead>
              <CTableBody>
                {vulns.map((item) => (
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
                            type="button"
                            size="sm"
                            onClick={() => navigate(`/vulnerabilities/${item.cve_id}`)}
                        >
                            View
                        </CButton>
                    </CTableDataCell>
                  </CTableRow>
                ))}
              </CTableBody>
            </CTable>
          )}
        </CCard>
      </CCol>
    </CRow>
  )
}

export default Vulnerabilities