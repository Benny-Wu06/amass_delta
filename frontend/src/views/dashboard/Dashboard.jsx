import React, { useState, useEffect } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import axios from 'axios'
import { BASE_URL, getUserEmail } from '../../vars'
import {
  CSpinner,
  CFormInput,
  CInputGroup,
  CInputGroupText,
  CDropdown,
  CDropdownToggle,
  CDropdownMenu,
  CDropdownItem,
  CCard,
  CCardBody,
  CCol,
  CRow,
  CBadge,
  CButton,
} from '@coreui/react'
import CIcon from '@coreui/icons-react'
import {
  cilSearch,
  cilFilter,
  cilUser,
  cilShieldAlt,
  cilBuilding,
  cilArrowRight,
} from '@coreui/icons'
import CVECard from 'src/components/CVECard'

const Dashboard = () => {
  const [vulns, setVulns] = useState([])
  const [loading, setLoading] = useState(true)
  const [sortBy, setSortBy] = useState('date_added')
  const [searchTerm, setSearchTerm] = useState('')
  const [dateRange, setDateRange] = useState('all')
  const [watchlists, setWatchlists] = useState([])
  const navigate = useNavigate()

  const userEmail = getUserEmail()

  useEffect(() => {
    if (!userEmail) return
    axios
      .get(`${BASE_URL}/v2/watchlist`, { params: { email: userEmail } })
      .then((res) => {
        const data = typeof res.data.body === 'string' ? JSON.parse(res.data.body) : res.data
        setWatchlists(data.watchlists || [])
      })
      .catch(() => {})
  }, [userEmail])

  useEffect(() => {
    const fetchCVEs = async () => {
      setLoading(true)
      try {
        const response = await axios.get(`${BASE_URL}/v1/cves`, {
          params: { sort_by: sortBy },
        })
        const parsed =
          typeof response.data.body === 'string' ? JSON.parse(response.data.body) : response.data
        setVulns(parsed.cves || [])
      } catch (err) {
        console.error('Error fetching CVEs:', err)
      } finally {
        setLoading(false)
      }
    }
    fetchCVEs()
  }, [sortBy])

  const filtered = vulns.filter((item) => {
    const s = searchTerm.toLowerCase()
    const matchSearch =
      item.cve_id.toLowerCase().includes(s) || (item.company_name || '').toLowerCase().includes(s)

    if (dateRange === 'all') return matchSearch
    const d = new Date(sortBy === 'date_added' ? item.date_added : item.due_date)
    const cutoff = new Date()
    cutoff.setDate(cutoff.getDate() - parseInt(dateRange))
    return matchSearch && d >= cutoff
  })

  return (
    <div className="cve-dashboard">
      {/* Account Summary */}
      <CCard className="mb-4 border-0 bg-body-tertiary w-100">
        <CCardBody className="py-3">
          <div className="cve-account-bar">
            <div className="d-flex align-items-center gap-2">
              <CIcon icon={cilUser} size="lg" className="text-primary" />
              <span className="fw-semibold">{userEmail}</span>
            </div>
            <div className="d-flex align-items-center gap-2 text-muted small">
              <CIcon icon={cilShieldAlt} className="text-danger" />
              <span>{vulns.length} tracked vulnerabilities</span>
            </div>
          </div>

          {watchlists.length > 0 && (
            <div className="mt-3">
              <div className="d-flex align-items-center justify-content-between mb-2">
                <span className="text-muted small">Your Watchlists</span>
                <Link
                  to="/watchlists"
                  className="text-muted small text-decoration-none d-flex align-items-center gap-1"
                >
                  View all <CIcon icon={cilArrowRight} size="sm" />
                </Link>
              </div>
              <CRow xs={{ cols: 1 }} sm={{ cols: 3 }} className="g-2">
                {watchlists.slice(0, 3).map((wl) => (
                  <CCol key={wl.id}>
                    <CCard
                      className="h-100 watchlist-card"
                      style={{ cursor: 'pointer' }}
                      onClick={() => navigate(`/watchlists/${wl.id}`)}
                    >
                      <CCardBody className="d-flex flex-column py-2 px-3">
                        <div
                          className="rounded d-flex align-items-center justify-content-center mb-2"
                          style={{
                            width: 36,
                            height: 36,
                            background: `hsl(${(wl.id * 47) % 360}, 60%, 50%)`,
                            flexShrink: 0,
                          }}
                        >
                          <CIcon icon={cilBuilding} style={{ color: '#fff' }} />
                        </div>
                        <div className="fw-semibold text-truncate small">{wl.name}</div>
                        <div className="mt-1">
                          <CBadge color="secondary" shape="rounded-pill">
                            {wl.company_count ?? 0}{' '}
                            {wl.company_count === 1 ? 'company' : 'companies'}
                          </CBadge>
                        </div>
                      </CCardBody>
                    </CCard>
                  </CCol>
                ))}
              </CRow>
            </div>
          )}
        </CCardBody>
      </CCard>

      {/* Toolbar */}
      <div className="cve-toolbar">
        <div className="cve-toolbar-left">
          <span className="cve-toolbar-title">CVE Feed</span>
          <span className="cve-count">{filtered.length} vulnerabilities</span>
        </div>
        <div className="cve-toolbar-right">
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

          <div className="cve-sort-group">
            <button
              className={`cve-sort-btn ${sortBy === 'date_added' ? 'active' : ''}`}
              onClick={() => setSortBy('date_added')}
            >
              Date Added
            </button>
            <button
              className={`cve-sort-btn ${sortBy === 'due_date' ? 'active' : ''}`}
              onClick={() => setSortBy('due_date')}
            >
              Due Date
            </button>
          </div>

          <CInputGroup size="sm" style={{ width: 240 }}>
            <CInputGroupText>
              <CIcon icon={cilSearch} />
            </CInputGroupText>
            <CFormInput
              placeholder="Search CVE or Company..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </CInputGroup>
        </div>
      </div>

      {/* Grid */}
      {loading ? (
        <div className="cve-loading">
          <CSpinner color="primary" />
        </div>
      ) : filtered.length === 0 ? (
        <div className="cve-empty">No results found</div>
      ) : (
        <div className="cve-grid">
          {filtered.map((item) => (
            <CVECard
              key={item.cve_id}
              item={item}
              onClick={() => navigate(`/vulnerabilities/${item.cve_id}`)}
            />
          ))}
        </div>
      )}
    </div>
  )
}

export default Dashboard
