import React from 'react'
import { CDropdown, CDropdownItem, CDropdownMenu, CDropdownToggle } from '@coreui/react'

const AddCompanyDropdown = () => {
  return (
    <CDropdown>
      <CDropdownToggle color="primary">Add</CDropdownToggle>
      <CDropdownMenu>
        <CDropdownItem>Watchlist1</CDropdownItem>
        <CDropdownItem>Watchlist2</CDropdownItem>
        <CDropdownItem>Watchlist3</CDropdownItem>
      </CDropdownMenu> 
    </CDropdown>
  )
}

export default AddCompanyDropdown
