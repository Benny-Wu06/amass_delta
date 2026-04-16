import {
  CRow,
  CCol,
  CCard,
  CCardBody,
  CCardHeader,
  CTable,
  CTableHead,
  CTableRow,
  CTableHeaderCell,
  CTableBody,
  CTableDataCell,
  CPagination,
  CPaginationItem,
  CBadge,
  CHeader,
} from '@coreui/react'

const Graph = ({header}) => {
  return (
    <>
      <CCol md={6}>
        <CCard className="h-150">
          <CCardHeader>{header}</CCardHeader>
          <CCardBody className="d-flex align-items-center justify-content-center">
            <div style={{ height: '250px', background: '#2f84d9ff', width: '100%' }}>
              PUT image here?
            </div>
          </CCardBody>
        </CCard>
      </CCol>
    </>
  )
}

export default Graph
