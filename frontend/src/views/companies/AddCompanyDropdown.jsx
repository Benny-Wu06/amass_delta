import React, { useEffect, useState } from 'react'
import {
  CButton,
  CFormCheck,
  CDropdown,
  CDropdownItem,
  CDropdownMenu,
  CDropdownToggle,
} from '@coreui/react'

const AddCompanyDropdown = () => {
  const watchlists = [
    { id: 1, name: 'diddy watchlist' },
    { id: 2, name: 'faang' },
    { id: 3, name: 'diddyblud watchlist' },
    { id: 4, name: 'fukumean' },
  ]
  const [isOpen, setIsOpen] = useState(false)
  const [savedLists, setSavedLists] = useState([])
  const [pendingLists, setPendingLists] = useState([])

  return (
    <CDropdown visible={isOpen} autoClose="outside">
      <CDropdownToggle color="primary">Add</CDropdownToggle>
      <CDropdownMenu>
        {/* header */}
        <div className="px-3 py-2 text-muted small fw-bold border-bottom mb-1">
          Save to watchlists
        </div>

        {watchlists.map((watchlist) => {
          return (
            <CDropdownItem
              key={watchlist.id}
              onClick={(e) => handleToggleItem(e, watchlist.id)}
              className="d-flex align-items-center justify-content-between"
              style={{ cursor: 'pointer' }}
              // onClick={(e) => handleToggleItem(e, list.id)}
            >
              <span>{watchlist.name}</span>

              <CFormCheck
                id={`check-${watchlist.id}`}
                // checked={isSelected}
                onChange={() => {}}
                style={{ pointerEvents: 'none', margin: 0 }}
              />
            </CDropdownItem>
          )
        })}
        {/* footer for saving changes */}
        <div className="d-flex justify-content-end align-items-center mt-2 pt-3 pb-2 px-3 border-top">
          <CButton
            variant="ghost"
            color="secondary"
            // onClick={handleCancel}
            className="me-2 text-muted border-0 fw-semibold"
            style={{ textDecoration: 'none' }}
          >
            Cancel
          </CButton>

          <CButton
            color="light"
            shape="rounded"
            // onClick={handleDone}
            className="fw-bold px-4 text-dark"
          >
            Done
          </CButton>
        </div>
      </CDropdownMenu>
    </CDropdown>
  )
}

export default AddCompanyDropdown
