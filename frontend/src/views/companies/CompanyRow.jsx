import React from 'react'
import { CTableRow, CTableDataCell, CButton } from '@coreui/react'
import { useNavigate } from 'react-router-dom'

const CompanyRow = ({ companyName }) => {
  return (
    <>
      <CTableRow>
        <CTableDataCell className="text-center">{companyName}</CTableDataCell>
        <CTableDataCell className="text-center">
          <CButton color="primary">Add</CButton>
        </CTableDataCell>
      </CTableRow>
    </>
  )
}

export default CompanyRow
