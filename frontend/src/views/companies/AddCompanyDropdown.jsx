import React from 'react'
import { CFormCheck, CDropdown, CDropdownItem, CDropdownMenu, CDropdownToggle } from '@coreui/react'

const AddCompanyDropdown = () => {
  const watchlists = [
    { id: 1, name: 'diddy watchlist' },
    { id: 2, name: 'faang' },
    { id: 3, name: 'diddyblud watchlist' },
    { id: 4, name: 'fukumean'},
  ]

  return (
    <CDropdown>
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
            className="d-flex align-items-center justify-content-between"
              style={{cursor: 'pointer'}}
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
        <CDropdownItem>Watchlist1</CDropdownItem>
        <CDropdownItem>Watchlist2</CDropdownItem>
        <CDropdownItem>Watchlist3</CDropdownItem>
      </CDropdownMenu>
    </CDropdown>
  )
}

export default AddCompanyDropdown
