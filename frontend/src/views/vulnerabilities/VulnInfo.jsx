import { useFetcher, useParams } from 'react-router-dom'
import { useEffect, useState } from 'react'
import { CRow, CCol, CCard, CCardHeader, CCardBody, CBadge, CCallout, CSpinner } from '@coreui/react'
import axios from 'axios'
import { STAGING_URL } from '../../vars'

const VulnInfo = ({}) => {
  const { cveId } = useParams()
  const [cveInfo, setCveInfo] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchCveInfo = async () => {
      try {
        const response = await axios.get(`${STAGING_URL}/v1/vulnerabilities/${cveId}`)
        const data = typeof response.data.body === 'string' 
          ? JSON.parse(response.data.body) 
          : response.data

        setCveInfo(data)
      } catch (error) {
        console.error('Failed to fetch CVE:', error)
      } finally {
        setLoading(false)
      }
    }
    fetchCveInfo()
  }, [cveId])

  if (loading) return <div className="text-center p-5"><CSpinner color="primary" /></div>
  if (!cveInfo) return <div className="text-center p-5">Vulnerability not found.</div>

  const getRatingColor = (rating) => {
    if (rating === 'CRITICAL') return 'danger'
    if (rating === 'HIGH') return 'warning'
    return 'info'
  }

  return (
    <>
      <div className="d-flex align-items-center mb-3">
        <h1 className="me-3">{cveId}</h1>
        <CBadge color={getRatingColor(cveInfo.risk_rating)} shape="rounded-pill">
          {cveInfo.risk_rating}
        </CBadge>
      </div>

      <CCard className="mb-4 shadow-sm">
        <CCardHeader className="bg-dark text-white">
          <h4 className="mb-0">{cveInfo.name || 'Vulnerability Details'}</h4>
        </CCardHeader>
        <CCardBody>
          <CRow>
            <CCol md={12}>
              <h6 className="text-muted text-uppercase small fw-bold">Description</h6>
              <p className="fs-5">{cveInfo.description}</p>
            </CCol>
          </CRow>
          <hr />
          <CRow>
            <CCol md={4}>
              <h6 className="text-muted text-uppercase small fw-bold">Date Added</h6>
              <p>{cveInfo.dateAdded}</p>
            </CCol>
            <CCol md={4}>
              <h6 className="text-muted text-uppercase small fw-bold">Due Date</h6>
              <p className="text-danger fw-bold">{cveInfo.dueDate}</p>
            </CCol>
          </CRow>
        </CCardBody>
      </CCard>

      <CRow>
        <CCol md={6}>
          <CCard className="h-100 shadow-sm">
            <CCardHeader className="bg-secondary text-white">
              <h4 className="mb-0">Risk Metrics</h4>
            </CCardHeader>
            <CCardBody>
              <CRow className="g-3">
                {[
                    { 
                        label: 'Risk Index', 
                        value: `${(cveInfo.risk_index * 100).toFixed(1)}%`, 
                        color: 'primary' 
                    },
                    { 
                        label: 'CVSS Score', 
                        value: cveInfo.cvss, 
                        color: cveInfo.cvss >= 9 ? 'danger' : cveInfo.cvss >= 7 ? 'warning' : 'info' 
                    },
                    { 
                        label: 'EPSS Score', 
                        value: cveInfo.epss?.toFixed(4), 
                        color: cveInfo.epss > 0.1 ? 'danger' : 'secondary' 
                    },
                    { 
                        label: 'Risk Rating', 
                        value: cveInfo.risk_rating, 
                        color: getRatingColor(cveInfo.risk_rating) 
                    },
                    ].map((metric, i) => (
                    <CCol xs={6} key={i}>
                        <div className="p-3 border border-secondary rounded bg-dark text-center shadow-sm h-100">
                        <div className="text-white fw-bold text-uppercase mb-2" style={{ fontSize: '0.7rem', letterSpacing: '0.05rem', opacity: 0.7 }}>
                            {metric.label}
                        </div>
                        <div className={`fs-3 fw-bold text-${metric.color}`}>
                            {metric.value}
                        </div>
                        </div>
                    </CCol>
                    ))}
              </CRow>
            </CCardBody>
          </CCard>
        </CCol>

        <CCol md={6}>
          <CCard className="h-100 shadow-sm border-start-warning border-start-4">
            <CCardHeader className="bg-warning text-dark">
              <h4 className="mb-0">Remediation</h4>
            </CCardHeader>
            <CCardBody>
              <h6>Action Required</h6>
              <p>
                Based on the CISA KEV listing (Added: {cveInfo.dateAdded}), 
                this vulnerability requires remediation by <strong>{cveInfo.dueDate}</strong>.
              </p>
              <CCallout color="warning">
                Update the affected software to the latest version. For 7-Zip, 
                ensure versions are updated to address the Mark-of-the-Web bypass.
              </CCallout>
            </CCardBody>
          </CCard>
        </CCol>
      </CRow>
    </>
  )
}

export default VulnInfo
