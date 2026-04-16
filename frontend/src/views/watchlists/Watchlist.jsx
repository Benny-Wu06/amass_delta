import React from 'react'
import { CTableRow, CTableDataCell, CButton } from '@coreui/react'
import { useNavigate } from 'react-router-dom'

const Watchlist = ({ watchlist }) => {
  const navigate = useNavigate()

  return (
    <>
      <CTableRow>
        <CTableDataCell className="text-center">{watchlist.name}</CTableDataCell>
        <CTableDataCell className="text-center">
          <CButton color="primary" onClick={navigate(`/watchlists/${watchlist.id}`)}>
            Edit
          </CButton>
        </CTableDataCell>
      </CTableRow>
    </>
  )
}

export default Watchlist
