import React from 'react'
import classNames from 'classnames'

import {
  CAvatar,
  CButton,
  CButtonGroup,
  CCard,
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
} from '@coreui/react'
import CIcon from '@coreui/icons-react'
import {
  cibCcAmex,
  cibCcApplePay,
  cibCcMastercard,
  cibCcPaypal,
  cibCcStripe,
  cibCcVisa,
  cibGoogle,
  cibFacebook,
  cibLinkedin,
  cifBr,
  cifEs,
  cifFr,
  cifIn,
  cifPl,
  cifUs,
  cibTwitter,
  cilCloudDownload,
  cilPeople,
  cilUser,
  cilUserFemale,
} from '@coreui/icons'

import avatar1 from 'src/assets/images/avatars/1.jpg'
import avatar2 from 'src/assets/images/avatars/2.jpg'
import avatar3 from 'src/assets/images/avatars/3.jpg'
import dreamybull from 'src/assets/images/dreamybull_suit.jpg'

import WidgetsBrand from '../widgets/WidgetsBrand'
import WidgetsDropdown from '../widgets/WidgetsDropdown'
import MainChart from './MainChart'

const Dashboard = () => {
  const progressExample = [
    { title: 'Visits', value: '29.703 Users', percent: 40, color: 'success' },
    { title: 'Unique', value: '24.093 Users', percent: 20, color: 'info' },
    { title: 'Pageviews', value: '78.706 Views', percent: 60, color: 'warning' },
    { title: 'New Users', value: '22.123 Users', percent: 80, color: 'danger' },
    { title: 'Bounce Rate', value: 'Average Rate', percent: 40.15, color: 'primary' },
  ]

  const progressGroupExample1 = [
    { title: 'Monday', value1: 34, value2: 78 },
    { title: 'Tuesday', value1: 56, value2: 94 },
    { title: 'Wednesday', value1: 12, value2: 67 },
    { title: 'Thursday', value1: 43, value2: 91 },
    { title: 'Friday', value1: 22, value2: 73 },
    { title: 'Saturday', value1: 53, value2: 82 },
    { title: 'Sunday', value1: 9, value2: 69 },
  ]

  const progressGroupExample2 = [
    { title: 'Male', icon: cilUser, value: 53 },
    { title: 'Female', icon: cilUserFemale, value: 43 },
  ]

  const progressGroupExample3 = [
    { title: 'Organic Search', icon: cibGoogle, percent: 56, value: '191,235' },
    { title: 'Facebook', icon: cibFacebook, percent: 15, value: '51,223' },
    { title: 'Twitter', icon: cibTwitter, percent: 11, value: '37,564' },
    { title: 'LinkedIn', icon: cibLinkedin, percent: 8, value: '27,319' },
  ]

  const tableExample = [
    {
      cve_id: 'CVE-2026-0001',
      company: 'diddyblud_inc',
      description:
        'very long long description supre not good and bad holy shit lets see how this renders ok',
      risk_index: 9,
      date_added: '2026-03-11',
      due_date: '2026-04-12',
    },
  ]

  return (
    <>
      <WidgetsDropdown className="mb-4" />
      <CCard className="mb-4">
        <CCardFooter>
          <CRow
            xs={{ cols: 1, gutter: 4 }}
            sm={{ cols: 2 }}
            lg={{ cols: 4 }}
            xl={{ cols: 5 }}
            className="mb-2 text-center"
          >
            {progressExample.map((item, index, items) => (
              <CCol
                className={classNames({
                  'd-none d-xl-block': index + 1 === items.length,
                })}
                key={index}
              >
                <div className="text-body-secondary">{item.title}</div>
                <div className="fw-semibold text-truncate">
                  {item.value} ({item.percent}%)
                </div>
                <CProgress thin className="mt-2" color={item.color} value={item.percent} />
              </CCol>
            ))}
          </CRow>
        </CCardFooter>
      </CCard>
      <WidgetsBrand className="mb-4" withCharts />
      <CRow>
        <CCol xs>
          <CCard className="mb-4">
            <CTable align="middle" className="mb-0 border" hover responsive>
              <CTableHead className="text-nowrap">
                <CTableRow>
                  {/* icon example */}
                  {/* <CTableHeaderCell className="bg-body-tertiary">
                    <CIcon icon={dreamybull} />
                  </CTableHeaderCell> */}
                  <CTableHeaderCell className="bg-body-tertiary text-center">
                    CVE-ID
                  </CTableHeaderCell>
                  <CTableHeaderCell className="bg-body-tertiary text-center">
                    Company
                  </CTableHeaderCell>
                  <CTableHeaderCell className="bg-body-tertiary">Description</CTableHeaderCell>
                  <CTableHeaderCell className="bg-body-tertiary text-center">
                    Risk Index
                  </CTableHeaderCell>
                  <CTableHeaderCell className="bg-body-tertiary">Date Added</CTableHeaderCell>
                  <CTableHeaderCell className="bg-body-tertiary">Due Date</CTableHeaderCell>
                </CTableRow>
              </CTableHead>
              <CTableBody>
                {tableExample.map((item, index) => (
                  <CTableRow v-for="item in tableItems" key={index}>
                    <CTableDataCell className="text-center">
                      <div>{item.cve_id}</div>
                    </CTableDataCell>
                    <CTableDataCell>
                      <div>{item.company}</div>
                    </CTableDataCell>
                    <CTableDataCell>
                      <div>{item.description}</div>
                      {/* <CIcon size="xl" icon={item.country.flag} title={item.country.name} /> */}
                    </CTableDataCell>
                    <CTableDataCell className="text-center">
                      <div className="fw-semibold">{item.risk_index}</div>
                    </CTableDataCell>
                    <CTableDataCell className="text-center">
                      <div>{item.date_added}</div>
                    </CTableDataCell>
                    <CTableDataCell className="text-center">
                      <div>{item.due_date}</div>
                      {/* <div className="small text-body-secondary text-nowrap">Last login</div>
                      <div className="fw-semibold text-nowrap">{item.activity}</div> */}
                    </CTableDataCell>
                  </CTableRow>
                ))}
              </CTableBody>
            </CTable>
          </CCard>
        </CCol>
      </CRow>
    </>
  )
}

export default Dashboard
