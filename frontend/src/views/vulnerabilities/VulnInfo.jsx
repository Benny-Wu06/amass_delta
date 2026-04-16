import { useFetcher, useParams } from "react-router-dom"
import {useEffect, useState} from 'react'
import { 
  CRow, CCol, CCard, CCardHeader, CCardBody, CBadge, CCallout 
} from '@coreui/react'
import axios from 'axios'
import { STAGING_URL } from '../../vars'

const VulnInfo = ({}) => {
  const {cveId} = useParams()
  const [cveInfo, setCveInfo] = useState(null)

  useEffect(() => {
    const fetchCveInfo = async () => {
      try {
        const response = await axios.get(`${STAGING_URL}/v1/vulnerabilities/${cveId}`)
        setCveInfo(response.data)
        console.log(response.data)
      } catch (error) {
        console.error('Failed to fetch CVE:', error)
      }
    }
    fetchCveInfo()
  }, [cveId])
  if (cveInfo === null) return <div>loading</div>
  return (
    <>
      <h1>{cveId}</h1>
      <CCard className="mb-4 shadow-sm">
        <CCardHeader className="d-flex justify-content-between align-items-center bg-dark text-white">
          <h4 className="mb-0">Companyname needs to be fetched</h4>
          <CBadge color="danger" shape="rounded-pill">TO DO</CBadge>
        </CCardHeader>
        <CCardBody>
          <CRow className="mb-3">
            <CCol md={6}>
              <h6>Affected Products</h6>
              <p>blhalahlbhalh</p>
              {/* <p className="fs-5 fw-bold">{cveInfo.affected_products || 'Roundcube Webmail'}</p> */}
            </CCol>
          </CRow>
          <hr />
          <CRow>
            <CCol md={6}>
              <h6 className="text-muted">Name</h6>
              <p className="fw-bold">
                {cveInfo.name}
              </p>
            </CCol>
            <CCol md={6}>
              <h6 className="text-muted">Description</h6>
                <p>
                    {cveInfo.description}
                  </p>
            </CCol>
          </CRow>
        </CCardBody>
      </CCard>
    </>
  )
}

export default VulnInfo
