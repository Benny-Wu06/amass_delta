import { useState } from 'react'
import axios from 'axios'
import {
  CButton,
  CFormCheck,
  CDropdown,
  CDropdownItem,
  CDropdownMenu,
  CDropdownToggle,
  CSpinner,
} from '@coreui/react'
import { BASE_URL, getUserEmail } from '../../vars'

const AddCompanyDropdown = ({ companyName }) => {
  const [watchlists, setWatchlists] = useState([])
  const [loading, setLoading] = useState(false)
  const [initialLists, setInitialLists] = useState([])
  const [pendingLists, setPendingLists] = useState([])
  const [saving, setSaving] = useState(false)
  const [isOpen, setIsOpen] = useState(false)

  const email = getUserEmail()

  const fetchWatchlists = async () => {
    if (!email) return
    setLoading(true)
    try {
      const res = await axios.get(`${BASE_URL}/v2/watchlist`, { params: { email } })
      const data = typeof res.data.body === 'string' ? JSON.parse(res.data.body) : res.data
      const lists = data.watchlists || []

      const details = await Promise.all(
        lists.map((wl) =>
          axios
            .get(`${BASE_URL}/v2/watchlist/${wl.id}`, { params: { email } })
            .then((r) => (typeof r.data.body === 'string' ? JSON.parse(r.data.body) : r.data))
            .catch(() => null),
        ),
      )

      const alreadyIn = lists
        .filter((_, i) => {
          const detail = details[i]
          return (detail?.companies || []).some((c) => c.company_name === companyName)
        })
        .map((wl) => wl.id)

      setWatchlists(lists)
      setInitialLists(alreadyIn)
      setPendingLists(alreadyIn)
    } catch (err) {
      console.error('Failed to fetch watchlists:', err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <CDropdown
      visible={isOpen}
      onShow={() => handleToggle(true)}
      onHide={() => handleToggle(false)}
      autoClose="outside"
    >
      <CDropdownToggle color="primary">Add</CDropdownToggle>
      <CDropdownMenu>
        <div className="px-3 py-2 text-muted small fw-bold border-bottom mb-1">
          Save to watchlists
        </div>

        {loading ? (
          <div className="text-center py-2">
            <CSpinner size="sm" />
          </div>
        ) : watchlists.length === 0 ? (
          <div className="px-3 py-2 text-muted small">No watchlists found</div>
        ) : (

        )}

        <div className="d-flex justify-content-end align-items-center mt-2 pt-3 pb-2 px-3 border-top">
          <CButton
            variant="ghost"
            color="secondary"
            onClick={handleCancel}
            className="me-2 text-muted border-0 fw-semibold"
            style={{ textDecoration: 'none' }}
          >
            Cancel
          </CButton>
          <CButton
            color="light"
            shape="rounded"
            onClick={handleDone}
            disabled={saving}
            className="fw-bold px-4 text-dark"
          >
            {saving ? <CSpinner size="sm" className="me-1" /> : null}
            Done
          </CButton>
        </div>
      </CDropdownMenu>
    </CDropdown>
  )
}

export default AddCompanyDropdown
