import React from 'react'
import { CTableRow, CTableDataCell, CButton } from '@coreui/react'
import AddCompanyDropdown from './AddCompanyDropdown.jsx'
import { useNavigate } from 'react-router-dom'

const CompanyRow = ({ companyName }) => {
  const navigate = useNavigate()

  // const companyId = getCompany().id or something

  return (
    <>
      <CTableRow>
        <CTableDataCell className='mx-4'>{companyName}</CTableDataCell>
        <CTableDataCell className="text-center">
          <CButton className='mx-2'
            color="primary"
            onClick={() => {
              navigate(`/companies/${companyName}`)
            }}
          >
            View
          </CButton>
          <AddCompanyDropdown companyName={companyName} />
        </CTableDataCell>
      </CTableRow>
    </>
  )
}

export default CompanyRow
