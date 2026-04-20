import React from 'react'
import axios from 'axios'
import { useNavigate } from 'react-router-dom'
import {
  CAvatar,
  CBadge,
  CDropdown,
  CDropdownDivider,
  CDropdownHeader,
  CDropdownItem,
  CDropdownMenu,
  CDropdownToggle,
} from '@coreui/react'
import {
  cilBell,
  cilCreditCard,
  cilCommentSquare,
  cilEnvelopeOpen,
  cilFile,
  cilLockLocked,
  cilSettings,
  cilTask,
  cilUser,
} from '@coreui/icons'
import CIcon from '@coreui/icons-react'
import { BASE_URL, getUserEmail } from '../../vars'

import avatar8 from './../../assets/images/avatars/8.jpg'

const AppHeaderDropdown = () => {
  const navigate = useNavigate()
  const userEmail = getUserEmail()

  const handleLogout = async (e) => {
    e.preventDefault()
    try {
      await axios.post(`${BASE_URL}/auth/logout`)
    } catch (error) {
      console.error('Logout failed:', error)
    } finally {
      localStorage.removeItem('user')
      navigate('/login')
    }
  }
  return (
    <CDropdown variant="nav-item">
      <CDropdownToggle placement="bottom-end" className="py-0 pe-0" caret={false}>
        <CAvatar src={avatar8} size="md" />
      </CDropdownToggle>
      <CDropdownMenu className="pt-0" placement="bottom-end">
        <CDropdownHeader className="bg-body-secondary fw-semibold mb-2">
          {userEmail || 'Account'}
        </CDropdownHeader>
        <CDropdownItem onClick={() => navigate('/watchlists')} style={{ cursor: 'pointer' }}>
          <CIcon icon={cilTask} className="me-2" />
          Watchlists
        </CDropdownItem>

        <CDropdownDivider />
        <CDropdownItem onClick={handleLogout} style={{ cursor: 'pointer' }}>
          <CIcon icon={cilLockLocked} className="me-2" />
          Logout
        </CDropdownItem>
      </CDropdownMenu>
    </CDropdown>
  )
}

export default AppHeaderDropdown
