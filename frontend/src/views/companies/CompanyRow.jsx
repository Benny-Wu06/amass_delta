import React from 'react'
import { CTableRow, CTableDataCell } from '@coreui/react'
import AddCompanyDropdown from './AddCompanyDropdown.jsx'
import { useNavigate } from 'react-router-dom'

const CompanyRow = ({ companyName }) => {
  const navigate = useNavigate()

  return (
    <CTableRow style={{ cursor: 'pointer' }} onClick={() => navigate(`/companies/${companyName}`)}>
      <CTableDataCell className="mx-4">{companyName}</CTableDataCell>
      <CTableDataCell className="text-center" onClick={(e) => e.stopPropagation()}>
        <AddCompanyDropdown companyName={companyName} />
      </CTableDataCell>
    </CTableRow>
  )
}

export default CompanyRow
