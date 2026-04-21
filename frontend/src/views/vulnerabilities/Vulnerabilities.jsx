import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'
import { BASE_URL } from '@/vars'
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
  CButton,
  CFormInput,
  CInputGroup,
  CInputGroupText,
  CDropdown,
  CDropdownToggle,
  CDropdownMenu,
  CDropdownItem,
} from '@coreui/react'
import CIcon from '@coreui/icons-react'
import { cilSearch, cilFilter } from '@coreui/icons'

const Vulnerabilities = () => {
  const [vulns, setVulns] = useState([])
  const [loading, setLoading] = useState(true)
  const [sortBy, setSortBy] = useState('date_added')
  const [searchTerm, setSearchTerm] = useState('')
  const [dateRange, setDateRange] = useState('all')
  const [startDate, setStartDate] = useState('')
  const [endDate, setEndDate] = useState('')

  const navigate = useNavigate()

  useEffect(() => {
    const fetchCVEs = async () => {
      setLoading(true)
      try {
        const response = await axios.get(`${BASE_URL}/v1/cves`, {
          params: { sort_by: sortBy },
        })

        const parsedBody =
          typeof response.data.body === 'string' ? JSON.parse(response.data.body) : response.data

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
    const matchesSearch =
      item.cve_id.toLowerCase().includes(search) || item.company_name.toLowerCase().includes(search)

    const itemDate = new Date(sortBy === 'date_added' ? item.date_added : item.due_date)

    const matchesCustomDate =
      (!startDate || itemDate >= new Date(startDate)) && (!endDate || itemDate <= new Date(endDate))

    let matchesPreset = true
    if (dateRange !== 'all') {
      const filterDate = new Date()
      filterDate.setDate(filterDate.getDate() - parseInt(dateRange))
      matchesPreset = itemDate >= filterDate
    }

    return matchesSearch && matchesCustomDate && matchesPreset
  })

  const ratingStyle = (rating) => {
    const map = {
      CRITICAL: { color: '#ff3b3b', background: 'rgba(255,59,59,0.12)' },
      HIGH: { color: '#ff8c00', background: 'rgba(255,140,0,0.12)' },
      MEDIUM: { color: '#f0c040', background: 'rgba(240,192,64,0.12)' },
      LOW: { color: '#07d000d4', background: 'rgba(26,122,74,0.12)' },
    }
    return map[rating] || { color: '#6e7681', background: 'rgba(110,118,129,0.12)' }
  }

  return (
    <CRow>
      <CCol className="p-0" xs>
        <CCard className="mb-4">
          <CCardHeader>
            <div className="d-flex flex-wrap align-items-center justify-content-between gap-2">
              <strong>Vulnerability Feed</strong>
              <div className="d-flex flex-wrap align-items-center gap-2">
                <CDropdown variant="btn-group">
                  <CDropdownToggle color="secondary" size="sm" variant="outline">
                    <CIcon icon={cilFilter} className="me-1" />
                    {dateRange === 'all' ? 'All Dates' : `Last ${dateRange} Days`}
                  </CDropdownToggle>
                  <CDropdownMenu>
                    <CDropdownItem onClick={() => setDateRange('all')}>All Time</CDropdownItem>
                    <CDropdownItem onClick={() => setDateRange('7')}>Last 7 Days</CDropdownItem>
                    <CDropdownItem onClick={() => setDateRange('30')}>Last 30 Days</CDropdownItem>
                    <CDropdownItem onClick={() => setDateRange('90')}>Last 90 Days</CDropdownItem>
                  </CDropdownMenu>
                </CDropdown>
                <div className="d-flex align-items-center gap-1">
                  <CFormInput
                    type="date"
                    size="sm"
                    style={{ minWidth: 0, width: '130px' }}
                    value={startDate}
                    onChange={(e) => {
                      setStartDate(e.target.value)
                      setDateRange('all')
                    }}
                  />
                  <span className="small text-muted">to</span>
                  <CFormInput
                    type="date"
                    size="sm"
                    style={{ minWidth: 0, width: '130px' }}
                    value={endDate}
                    onChange={(e) => {
                      setEndDate(e.target.value)
                      setDateRange('all')
                    }}
                  />
                </div>
                <CInputGroup size="sm" style={{ width: '220px', minWidth: '150px' }}>
                  <CInputGroupText>
                    <CIcon icon={cilSearch} />
                  </CInputGroupText>
                  <CFormInput
                    placeholder="Search CVE or Company..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                  />
                </CInputGroup>
                <div className="btn-group btn-group-sm">
                  <button
                    className={`btn btn-sm ${sortBy === 'date_added' ? 'btn-primary' : 'btn-outline-secondary'}`}
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
            </div>
          </CCardHeader>

          {loading ? (
            <div className="text-center p-5">
              <CSpinner color="primary" />
            </div>
          ) : (
            <CTable align="middle" className="mb-0 border" hover responsive>
              <CTableHead>
                <CTableRow>
                  <CTableHeaderCell className="bg-body-tertiary text-center">
                    CVE-ID
                  </CTableHeaderCell>
                  <CTableHeaderCell className="bg-body-tertiary">Vendor</CTableHeaderCell>
                  <CTableHeaderCell className="bg-body-tertiary text-center">
                    Risk Index
                  </CTableHeaderCell>
                  <CTableHeaderCell className="bg-body-tertiary text-center">
                    Rating
                  </CTableHeaderCell>
                  <CTableHeaderCell className="bg-body-tertiary text-center text-primary fw-bold">
                    {sortBy === 'date_added' ? 'Date Added' : 'Due Date'}
                  </CTableHeaderCell>
                  <CTableHeaderCell className="bg-body-tertiary text-center">
                    Actions
                  </CTableHeaderCell>
                </CTableRow>
              </CTableHead>
              <CTableBody>
                {filteredVulns.length > 0 ? (
                  filteredVulns.map((item) => (
                    <CTableRow
                      key={item.cve_id}
                      style={{ cursor: 'pointer' }}
                      onClick={() => navigate(`/vulnerabilities/${item.cve_id}`)}
                    >
                      <CTableDataCell className="text-center font-monospace small">
                        {item.cve_id}
                      </CTableDataCell>
                      <CTableDataCell className="fw-semibold">{item.company_name}</CTableDataCell>
                      <CTableDataCell className="text-center">
                        {(item.risk_index * 100).toFixed(1)}%
                      </CTableDataCell>
                      <CTableDataCell className="text-center">
                        <span
                          style={{
                            ...ratingStyle(item.risk_rating),
                            padding: '2px 8px',
                            borderRadius: 4,
                            fontWeight: 600,
                            fontSize: '0.75rem',
                          }}
                        >
                          {item.risk_rating || '—'}
                        </span>
                      </CTableDataCell>
                      <CTableDataCell className="text-center small">
                        {sortBy === 'date_added' ? item.date_added : item.due_date}
                      </CTableDataCell>
                      <CTableDataCell className="text-center" onClick={(e) => e.stopPropagation()}>
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
