import React from 'react'
import CIcon from '@coreui/icons-react'
import { cilBug, cilPeople, cilSpeedometer, cilStar, cilLaptop } from '@coreui/icons'
import { CNavItem } from '@coreui/react'

const _nav = [
  {
    component: CNavItem,
    name: 'Dashboard',
    to: '/dashboard',
    icon: <CIcon icon={cilSpeedometer} customClassName="nav-icon" />,
  },
  {
    component: CNavItem,
    name: 'Watchlists',
    to: '/watchlists',
    icon: <CIcon icon={cilStar} customClassName="nav-icon" />,
  },
  {
    component: CNavItem,
    name: 'Companies',
    to: '/companies',
    icon: <CIcon icon={cilPeople} customClassName="nav-icon" />,
  },
  {
    component: CNavItem,
    name: 'Vulnerabilities',
    to: '/vulnerabilities',
    icon: <CIcon icon={cilBug} customClassName="nav-icon" />,
  },
  {
    component: CNavItem,
    name: 'PC Scanner',
    to: '/scanner',
    icon: <CIcon icon={cilLaptop} customClassName="nav-icon" />,
  },
]

export default _nav
