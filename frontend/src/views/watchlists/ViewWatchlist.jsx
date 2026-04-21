import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import axios from 'axios'
import { BASE_URL, getUserEmail } from '@/vars'
import {
  CButton,
  CCard,
  CCardBody,
  CCardHeader,
  CCol,
  CFormInput,
  CInputGroup,
  CInputGroupText,
  CModal,
  CModalBody,
  CModalFooter,
  CModalHeader,
  CModalTitle,
  CRow,
  CSpinner,
  CTable,
  CTableBody,
  CTableDataCell,
  CTableHead,
  CTableHeaderCell,
  CTableRow,
} from '@coreui/react'
import CIcon from '@coreui/icons-react'
import {
  cilArrowLeft,
  cilPlus,
  cilTrash,
  cilSearch,
  cilBuilding,
  cilShieldAlt,
} from '@coreui/icons'

const RATING_STYLES = {
  CRITICAL: { color: '#ff3b3b', background: 'rgba(255,59,59,0.12)' },
  HIGH: { color: '#ff8c00', background: 'rgba(255,140,0,0.12)' },
  MEDIUM: { color: '#f0c040', background: 'rgba(240,192,64,0.12)' },
  LOW: { color: '#07d000d4', background: 'rgba(26,122,74,0.12)' },
}

const ViewWatchlist = () => {
  const { watchlist_id } = useParams()
  const navigate = useNavigate()
  const [watchlist, setWatchlist] = useState(null)
  const [loading, setLoading] = useState(true)
  const [showAddModal, setShowAddModal] = useState(false)
  const [allCompanies, setAllCompanies] = useState([])
  const [companySearch, setCompanySearch] = useState('')
  const [adding, setAdding] = useState(false)
  const [removeTarget, setRemoveTarget] = useState(null)

  const email = getUserEmail()

  const fetchWatchlist = async () => {
    if (!email) return
    setLoading(true)
    try {
      const res = await axios.get(`${BASE_URL}/v2/watchlist/${watchlist_id}`, {
        params: { email },
      })
      const data = typeof res.data.body === 'string' ? JSON.parse(res.data.body) : res.data
      setWatchlist(data)
    } catch (err) {
      console.error('Failed to fetch watchlist:', err)
    } finally {
      setLoading(false)
    }
  }

  const fetchAllCompanies = async () => {
    try {
      const res = await axios.get(`${BASE_URL}/v1/companies`)
      setAllCompanies(res.data.companies || [])
    } catch (err) {
      console.error('Failed to fetch companies:', err)
    }
  }

  useEffect(() => {
    fetchWatchlist()
  }, [watchlist_id, email])

  const handleOpenAdd = () => {
    fetchAllCompanies()
    setCompanySearch('')
    setShowAddModal(true)
  }

  const handleAddCompany = async (companyName) => {
    setAdding(true)
    try {
      await axios.post(`${BASE_URL}/v2/watchlist/${watchlist_id}/companies`, {
        email,
        company_name: companyName,
      })
      setShowAddModal(false)
      await fetchWatchlist()
    } catch (err) {
      console.error('Failed to add company:', err)
    } finally {
      setAdding(false)
    }
  }

  const handleRemoveCompany = async (companyName) => {
    try {
      await axios.delete(
        `${BASE_URL}/v2/watchlist/${watchlist_id}/companies/${encodeURIComponent(companyName)}`,
        { params: { email } },
      )
      setRemoveTarget(null)
      await fetchWatchlist()
    } catch (err) {
      console.error('Failed to remove company:', err)
    }
  }

  const existingNames = new Set((watchlist?.companies || []).map((c) => c.company_name))
  const filteredCompanies = allCompanies.filter(
    (name) => !existingNames.has(name) && name.toLowerCase().includes(companySearch.toLowerCase()),
  )

  if (loading) {
    return (
      <div className="text-center py-5">
        <CSpinner color="primary" />
      </div>
    )
  }

  if (!watchlist) {
    return <p className="text-muted">Watchlist not found.</p>
  }

  return (
    <>
      <div className="d-flex align-items-center gap-3 mb-4">
        <CButton
          color="secondary"
          variant="ghost"
          size="sm"
          onClick={() => navigate('/watchlists')}
        >
          <CIcon icon={cilArrowLeft} />
        </CButton>
        <div className="flex-grow-1">
          <h4 className="mb-0 fw-bold">{watchlist.name}</h4>
          <small className="text-muted">
            {watchlist.companies?.length ?? 0}{' '}
            {watchlist.companies?.length === 1 ? 'company' : 'companies'}
          </small>
        </div>
        <CButton color="primary" onClick={handleOpenAdd}>
          <CIcon icon={cilPlus} className="me-1" />
          Add Company
        </CButton>
      </div>

      <CCard>
        <CCardHeader className="d-flex justify-content-start">
          <CIcon icon={cilBuilding} className="me-2 text-primary" />
          Companies
        </CCardHeader>
        {watchlist.companies?.length === 0 ? (
          <CCardBody className="text-center py-5 text-muted">
            <p className="mb-3">No companies yet. Add one to start monitoring.</p>
            <CButton color="primary" variant="outline" onClick={handleOpenAdd}>
              <CIcon icon={cilPlus} className="me-1" />
              Add Company
            </CButton>
          </CCardBody>
        ) : (
          <CTable align="middle" hover responsive className="mb-0">
            <CTableHead>
              <CTableRow>
                <CTableHeaderCell className="bg-body-tertiary">Company</CTableHeaderCell>
                <CTableHeaderCell className="bg-body-tertiary text-center">CVEs</CTableHeaderCell>
                <CTableHeaderCell className="bg-body-tertiary text-center">
                  Risk Index
                </CTableHeaderCell>
                <CTableHeaderCell className="bg-body-tertiary text-center">Rating</CTableHeaderCell>
                <CTableHeaderCell className="bg-body-tertiary text-center">
                  Avg CVSS
                </CTableHeaderCell>
                <CTableHeaderCell className="bg-body-tertiary text-center">
                  Avg EPSS
                </CTableHeaderCell>
                <CTableHeaderCell className="bg-body-tertiary" />
              </CTableRow>
            </CTableHead>
            <CTableBody>
              {watchlist.companies.map((company) => (
                <CTableRow
                  key={company.company_name}
                  style={{ cursor: 'pointer' }}
                  onClick={() => navigate(`/companies/${company.company_name}`)}
                >
                  <CTableDataCell>
                    <span className="fw-semibold">{company.company_name}</span>
                  </CTableDataCell>
                  <CTableDataCell className="text-center">
                    {company.num_vulnerabilities ?? '—'}
                  </CTableDataCell>
                  <CTableDataCell className="text-center">
                    {company.risk_index != null ? `${(company.risk_index * 100).toFixed(1)}%` : '—'}
                  </CTableDataCell>
                  <CTableDataCell className="text-center">
                    {company.risk_rating ? (
                      <span
                        style={{
                          ...(RATING_STYLES[company.risk_rating] || {
                            color: '#6e7681',
                            background: 'rgba(110,118,129,0.12)',
                          }),
                          padding: '2px 8px',
                          borderRadius: 4,
                          fontWeight: 600,
                          fontSize: '0.75rem',
                        }}
                      >
                        {company.risk_rating}
                      </span>
                    ) : (
                      '—'
                    )}
                  </CTableDataCell>
                  <CTableDataCell className="text-center">
                    {company.avg_cvss?.toFixed(1) ?? '—'}
                  </CTableDataCell>
                  <CTableDataCell className="text-center">
                    {company.avg_epss?.toFixed(3) ?? '—'}
                  </CTableDataCell>
                  <CTableDataCell
                    className="text-center"
                    onClick={(e) => {
                      e.stopPropagation()
                      setRemoveTarget(company.company_name)
                    }}
                  >
                    <CButton color="danger" size="sm" variant="ghost">
                      <CIcon icon={cilTrash} />
                    </CButton>
                  </CTableDataCell>
                </CTableRow>
              ))}
            </CTableBody>
          </CTable>
        )}
      </CCard>

      <CModal
        visible={showAddModal}
        onClose={() => setShowAddModal(false)}
        alignment="center"
        size="lg"
      >
        <CModalHeader>
          <CModalTitle>Add Company to Watchlist</CModalTitle>
        </CModalHeader>
        <CModalBody>
          <CInputGroup className="mb-3">
            <CInputGroupText>
              <CIcon icon={cilSearch} />
            </CInputGroupText>
            <CFormInput
              placeholder="Search companies..."
              value={companySearch}
              onChange={(e) => setCompanySearch(e.target.value)}
              autoFocus
            />
          </CInputGroup>
          <div style={{ maxHeight: 320, overflowY: 'auto' }}>
            {filteredCompanies.length === 0 ? (
              <p className="text-muted text-center py-3">
                {companySearch ? 'No matching companies' : 'All companies already added'}
              </p>
            ) : (
              filteredCompanies.map((name) => (
                <div
                  key={name}
                  className="d-flex align-items-center justify-content-between px-2 py-2 rounded hover-bg"
                  style={{ cursor: 'pointer' }}
                  onClick={() => !adding && handleAddCompany(name)}
                >
                  <div className="d-flex align-items-center gap-2">
                    <CIcon icon={cilBuilding} className="text-muted" />
                    <span>{name}</span>
                  </div>
                  <CButton color="primary" size="sm" variant="outline" disabled={adding}>
                    <CIcon icon={cilPlus} />
                  </CButton>
                </div>
              ))
            )}
          </div>
        </CModalBody>
        <CModalFooter>
          <CButton color="primary" onClick={() => setShowAddModal(false)}>
            Done
          </CButton>
        </CModalFooter>
      </CModal>

      <CModal visible={!!removeTarget} onClose={() => setRemoveTarget(null)} alignment="center">
        <CModalHeader>
          <CModalTitle>Remove Company</CModalTitle>
        </CModalHeader>
        <CModalBody>
          Remove <strong>{removeTarget}</strong> from this watchlist?
        </CModalBody>
        <CModalFooter>
          <CButton color="secondary" variant="ghost" onClick={() => setRemoveTarget(null)}>
            Cancel
          </CButton>
          <CButton color="danger" onClick={() => handleRemoveCompany(removeTarget)}>
            Remove
          </CButton>
        </CModalFooter>
      </CModal>
    </>
  )
}

export default ViewWatchlist
