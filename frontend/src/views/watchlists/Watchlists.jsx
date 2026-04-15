import React from 'react'
import classNames from 'classnames'

import {
  CAvatar,
  CButton,
  CButtonGroup,
  CCard,
  CCardTitle,
  CCardBody,
  CCardFooter,
  CCardHeader,
  CCol,
  CProgress,
  CRow,
  CTable,
  CTableBody,
  CTableDataCell,
  CTableHead,
  CTableHeaderCell,
  CTableRow,
  CLink,
} from '@coreui/react'
import Company from 'src/components/Company.jsx'
import SubscribeButton from 'src/components/SubscribeButton.jsx'
import dreamybull from 'src/assets/images/dreamybull_suit.jpg'
import Watchlist from './Watchlist.jsx'

const Watchlists = () => {
  // this is why typescript is helpful i think

  // get watchlists

  // fetch subscribed companies
  const watchlists = [
    {
      id: 1,
      name: 'watchlist1',
    },
    {
      id: 2,
      name: 'watchlist2',
    },
      {
      id: 3,
      name: 'watchlist3',
    },
    {
      id: 4,
      name: 'watchlist4',
    },
  ]

  return (
    <>
      <CRow>
        <CCol className="p-0" xs>
          <CCard className="mb-4">
            <CCardHeader>Your Watchlists</CCardHeader>
            <CTable align="middle" className="mb-0 border" hover responsive>
              <CTableHead className="text-nowrap">
                <CTableRow>
                  <CTableHeaderCell className="bg-body-tertiary text-center">Name</CTableHeaderCell>
                </CTableRow>
              </CTableHead>
              <CTableBody>
                {watchlists.map((watchlist, index) => (
                  <Watchlist watchlist={watchlist} key={index}></Watchlist>
                ))}
              </CTableBody>
            </CTable>
          </CCard>
        </CCol>
      </CRow>
    </>
  )
}

export default Watchlists
