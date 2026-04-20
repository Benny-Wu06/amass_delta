import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { useNavigate } from 'react-router-dom'
import { BASE_URL, getUserEmail } from '../../vars'
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
  CBadge,
} from '@coreui/react'
import CIcon from '@coreui/icons-react'
import { cilPlus, cilTrash, cilPen, cilBuilding } from '@coreui/icons'

const Watchlists = () => {
  const [watchlists, setWatchlists] = useState([])
  const [loading, setLoading] = useState(true)
  const [creating, setCreating] = useState(false)
  const [newName, setNewName] = useState('')
  const [showModal, setShowModal] = useState(false)
  const [deleteTarget, setDeleteTarget] = useState(null)
  const navigate = useNavigate()

  const email = getUserEmail()

  const fetchWatchlists = async () => {
    if (!email) return
    setLoading(true)
    try {
      const res = await axios.get(`${BASE_URL}/v2/watchlist`, { params: { email } })
      const data = typeof res.data.body === 'string' ? JSON.parse(res.data.body) : res.data
      setWatchlists(data.watchlists || [])
    } catch (err) {
      console.error('Failed to fetch watchlists:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchWatchlists()
  }, [email])

  const handleCreate = async () => {
    if (!newName.trim()) return
    setCreating(true)
    try {
      await axios.post(`${BASE_URL}/v2/watchlist`, { email, name: newName.trim() })
      setNewName('')
      setShowModal(false)
      await fetchWatchlists()
    } catch (err) {
      console.error('Failed to create watchlist:', err)
    } finally {
      setCreating(false)
    }
  }

  const handleDelete = async (id) => {
    try {
      await axios.delete(`${BASE_URL}/v2/watchlist/${id}`, { data: { email } })
      setDeleteTarget(null)
      await fetchWatchlists()
    } catch (err) {
      console.error('Failed to delete watchlist:', err)
    }
  }

  return (
    <>
      <div className="d-flex align-items-center justify-content-between mb-4">
        <div>
          <h4 className="mb-0 fw-bold">Your Watchlists</h4>
          <small className="text-muted">{watchlists.length} watchlists</small>
        </div>
        <CButton color="primary" onClick={() => setShowModal(true)}>
          <CIcon icon={cilPlus} className="me-1" />
          New Watchlist
        </CButton>
      </div>

      {loading ? (
        <div className="text-center py-5">
          <CSpinner color="primary" />
        </div>
      ) : watchlists.length === 0 ? (
        <CCard className="border-dashed text-center py-5">
          <CCardBody>
            <p className="text-muted mb-3">
              No watchlists yet. Create one to start tracking companies.
            </p>
            <CButton color="primary" onClick={() => setShowModal(true)}>
              <CIcon icon={cilPlus} className="me-1" />
              Create your first watchlist
            </CButton>
          </CCardBody>
        </CCard>
      ) : (
        <CRow xs={{ cols: 1 }} sm={{ cols: 2 }} md={{ cols: 3 }} lg={{ cols: 4 }} className="g-3">
          {watchlists.map((wl) => (
            <CCol key={wl.id}>
              <CCard
                className="h-100 watchlist-card"
                style={{ cursor: 'pointer' }}
                onClick={() => navigate(`/watchlists/${wl.id}`)}
              >
                <CCardBody className="d-flex flex-column">
                  <div
                    className="watchlist-card-icon mb-3 rounded d-flex align-items-center justify-content-center"
                    style={{
                      width: 48,
                      height: 48,
                      background: `hsl(${(wl.id * 47) % 360}, 60%, 50%)`,
                    }}
                  >
                    <CIcon icon={cilBuilding} style={{ color: '#fff' }} size="lg" />
                  </div>
                  <div className="fw-semibold mb-1 text-truncate">{wl.name}</div>
                  <div className="text-muted small mb-3">
                    <CBadge color="secondary" shape="rounded-pill">
                      {wl.company_count ?? 0} {wl.company_count === 1 ? 'company' : 'companies'}
                    </CBadge>
                  </div>
                  <div className="mt-auto d-flex gap-2" onClick={(e) => e.stopPropagation()}>
                    <CButton
                      color="primary"
                      size="sm"
                      variant="outline"
                      className="flex-grow-1"
                      onClick={() => navigate(`/watchlists/${wl.id}`)}
                    >
                      <CIcon icon={cilPen} className="me-1" />
                      Edit
                    </CButton>
                    <CButton
                      color="danger"
                      size="sm"
                      variant="ghost"
                      onClick={() => setDeleteTarget(wl)}
                    >
                      <CIcon icon={cilTrash} />
                    </CButton>
                  </div>
                </CCardBody>
              </CCard>
            </CCol>
          ))}
        </CRow>
      )}

      <CModal visible={showModal} onClose={() => setShowModal(false)} alignment="center">
        <CModalHeader>
          <CModalTitle>New Watchlist</CModalTitle>
        </CModalHeader>
        <CModalBody>
          <CInputGroup>
            <CInputGroupText>Name</CInputGroupText>
            <CFormInput
              placeholder="e.g. FAANG, Cloud Providers..."
              value={newName}
              onChange={(e) => setNewName(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleCreate()}
              autoFocus
            />
          </CInputGroup>
        </CModalBody>
        <CModalFooter>
          <CButton color="secondary" variant="ghost" onClick={() => setShowModal(false)}>
            Cancel
          </CButton>
          <CButton color="primary" onClick={handleCreate} disabled={creating || !newName.trim()}>
            {creating ? <CSpinner size="sm" className="me-1" /> : null}
            Create
          </CButton>
        </CModalFooter>
      </CModal>

      <CModal visible={!!deleteTarget} onClose={() => setDeleteTarget(null)} alignment="center">
        <CModalHeader>
          <CModalTitle>Delete Watchlist</CModalTitle>
        </CModalHeader>
        <CModalBody>
          Delete <strong>{deleteTarget?.name}</strong>? This can't be undone.
        </CModalBody>
        <CModalFooter>
          <CButton color="secondary" variant="ghost" onClick={() => setDeleteTarget(null)}>
            Cancel
          </CButton>
          <CButton color="danger" onClick={() => handleDelete(deleteTarget?.id)}>
            Delete
          </CButton>
        </CModalFooter>
      </CModal>
    </>
  )
}

export default Watchlists
