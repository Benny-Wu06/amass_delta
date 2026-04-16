import { useFetcher, useParams } from 'react-router-dom'
import { useEffect, useState } from 'react'
import { CRow, CCol, CCard, CCardHeader, CCardBody, CBadge, CCallout } from '@coreui/react'
import axios from 'axios'
import { STAGING_URL } from '../../vars'

const VulnInfo = ({}) => {
  const { cveId } = useParams()
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
      <CCard className="mb-4">
        <CCardHeader className="d-flex justify-content-between align-items-center text-white">
          <h4 className="mb-0">Companyname needs to be fetched</h4>
          <CBadge color="danger" shape="rounded-pill">
            TO DO
          </CBadge>
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
              <p className="fw-bold">{cveInfo.name}</p>
            </CCol>
            <CCol md={6}>
              <h6 className="text-muted">Description</h6>
              <p>{cveInfo.description}</p>
            </CCol>
          </CRow>
        </CCardBody>
      </CCard>

      <CRow>
        <CCol md={6}>
          <CCard>
            <CCardHeader className="text-white">
              <h4>Metrics</h4>
            </CCardHeader>
            <CCardBody>
              <CCol md={6}>
                <CRow className="mb-4">
                  {[
                    { label: 'Risk Index', value: cveInfo.risk_index },
                    { label: 'Risk Rating', value: cveInfo.risk_rating },
                    { label: 'CVSS', value: cveInfo.cvss },
                    { label: 'EPSS', value: cveInfo.epss },
                  ].map((metric, i) => (
                    <CCol xs={6} md={6} key={i}>
                      <CCard className="text-center border-top-3 shadow-sm">
                        <CCardBody>
                          <div className="text-muted small text-uppercase fw-semibold">
                            {metric.label}
                          </div>
                          <div className={`fs-4 fw-bold text-${metric.color}`}>{metric.value}</div>
                        </CCardBody>
                      </CCard>
                    </CCol>
                  ))}
                </CRow>
              </CCol>
            </CCardBody>
          </CCard>
        </CCol>

        <CCol md={6}>
          <CCard>
            <CCardHeader className="text-white">
              <h4>Remediation</h4>
            </CCardHeader>
            <CCardBody>
              <p>fix this and do this, fetch from cisa kev</p>
            </CCardBody>
          </CCard>
        </CCol>
      </CRow>
    </>
  )
}

export default VulnInfo
