import React from 'react'
import { CTableRow, CTableDataCell, CButton } from '@coreui/react'
import AddCompanyDropdown from './AddCompanyDropdown.jsx'

const CompanyRow = ({ companyName }) => {
  return (
    <>
      <CTableRow>
        <CTableDataCell className="text-center">{companyName}</CTableDataCell>
        <CTableDataCell className="text-center">
        <AddCompanyDropdown></AddCompanyDropdown>
        </CTableDataCell>
      </CTableRow>
    </>
  )
}

export default CompanyRow
