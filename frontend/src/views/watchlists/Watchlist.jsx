import React from 'react'
import { CTableRow, CTableDataCell, CButton } from '@coreui/react'

const Watchlist = ({ watchlist }) => {

  return (
    <>
      <CTableRow>
        <CTableDataCell className="text-center">{watchlist.name}</CTableDataCell>
        <CTableDataCell className="text-center">
          <CButton color="primary">Edit</CButton>
        </CTableDataCell>
      </CTableRow>
    </>
  )
}

export default Watchlist
