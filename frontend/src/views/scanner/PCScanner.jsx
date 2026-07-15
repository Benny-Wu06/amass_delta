import React, { useRef, useState } from 'react'
import axios from 'axios'
import { STAGING_URL } from '@/vars'
import {
  CAlert,
  CButton,
  CCard,
  CCardBody,
  CCardHeader,
  CCol,
  CRow,
  CSpinner,
  CTable,
  CTableBody,
  CTableDataCell,
  CTableHead,
  CTableHeaderCell,
  CTableRow,
} from '@coreui/react'
import CIcon from '@coreui/icons-react'
import { cilCloudUpload, cilShieldAlt, cilWarning } from '@coreui/icons'

const ratingStyle = (rating) => {
  const map = {
    CRITICAL: { color: '#ff3b3b', background: 'rgba(255,59,59,0.12)' },
    HIGH:     { color: '#ff8c00', background: 'rgba(255,140,0,0.12)'  },
    MEDIUM:   { color: '#f0c040', background: 'rgba(240,192,64,0.12)' },
    LOW:      { color: '#07d000d4', background: 'rgba(26,122,74,0.12)' },
  }
  return map[rating] || { color: '#6e7681', background: 'rgba(110,118,129,0.12)' }
}

const Badge = ({ rating }) => {
  const style = ratingStyle(rating)
  return (
    <span style={{ ...style, padding: '2px 8px', borderRadius: 4, fontWeight: 600, fontSize: '0.75rem' }}>
      {rating || '—'}
    </span>
  )
}

const SummaryCard = ({ label, value, color }) => (
  <CCard className="text-center h-100">
    <CCardBody>
      <div style={{ fontSize: '2rem', fontWeight: 700, color }}>{value}</div>
      <div className="text-muted small">{label}</div>
    </CCardBody>
  </CCard>
)

const PCScanner = () => {
  const fileInputRef = useRef(null)
  const [loading, setLoading]   = useState(false)
  const [results, setResults]   = useState(null)
  const [error, setError]       = useState(null)

  const handleFile = async (file) => {
    setError(null)
    setResults(null)

    let inventory
    try {
      inventory = JSON.parse(await file.text())
    } catch {
      setError('Could not parse the file. Make sure it is a valid JSON file produced by pc_scanner.ps1.')
      return
    }

    setLoading(true)
    try {
      const resp = await axios.post(`${STAGING_URL}/v1/scan/match`, inventory)
      const body = typeof resp.data.body === 'string' ? JSON.parse(resp.data.body) : resp.data
      setResults(body)
    } catch (err) {
      setError(`Scan request failed: ${err.response?.data?.error || err.message}`)
    } finally {
      setLoading(false)
    }
  }

  const onFileChange = (e) => {
    const file = e.target.files?.[0]
    if (file) handleFile(file)
    e.target.value = ''
  }

  const onDrop = (e) => {
    e.preventDefault()
    const file = e.dataTransfer.files?.[0]
    if (file) handleFile(file)
  }

  const highestRating = (cves) => {
    const order = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'UNKNOWN']
    for (const r of order) {
      if (cves.some((c) => c.risk_rating === r)) return r
    }
    return 'UNKNOWN'
  }

  return (
    <CRow>
      <CCol xs>
        {/* Instructions */}
        <CCard className="mb-4">
          <CCardHeader>
            <strong>PC Vulnerability Scanner</strong>
          </CCardHeader>
          <CCardBody>
            <p className="mb-2">
              Run the PowerShell script below on your Windows machine to collect your installed
              software. Then upload the resulting <code>scan_results.json</code> to check it
              against known CVEs.
            </p>
            <ol className="mb-3 ps-4">
              <li>
                Download{' '}
                <a href="/scanner/pc_scanner.exe" download>
                  pc_scanner.exe
                </a>
              </li>
              <li>Double-click <code>pc_scanner.exe</code> — it will save <code>scan_results.json</code> in the same folder.</li>
              <li>Upload the generated <code>scan_results.json</code> below.</li>
            </ol>

            {/* Drop zone */}
            <div
              onDrop={onDrop}
              onDragOver={(e) => e.preventDefault()}
              onClick={() => fileInputRef.current?.click()}
              style={{
                border: '2px dashed var(--cui-border-color)',
                borderRadius: 8,
                padding: '2rem',
                textAlign: 'center',
                cursor: 'pointer',
                transition: 'border-color 0.2s',
              }}
              onMouseEnter={(e) => (e.currentTarget.style.borderColor = 'var(--cui-primary)')}
              onMouseLeave={(e) => (e.currentTarget.style.borderColor = 'var(--cui-border-color)')}
            >
              <CIcon icon={cilCloudUpload} size="xl" className="mb-2 text-muted" />
              <div className="text-muted">
                Drag &amp; drop <code>scan_results.json</code> here, or click to browse
              </div>
              <input
                ref={fileInputRef}
                type="file"
                accept=".json,application/json"
                onChange={onFileChange}
                style={{ display: 'none' }}
              />
            </div>
          </CCardBody>
        </CCard>

        {/* Loading */}
        {loading && (
          <div className="text-center p-5">
            <CSpinner color="primary" />
            <div className="mt-2 text-muted">Querying NVD for matching CVEs…</div>
          </div>
        )}

        {/* Error */}
        {error && (
          <CAlert color="danger" className="d-flex align-items-center gap-2">
            <CIcon icon={cilWarning} />
            {error}
          </CAlert>
        )}

        {/* Results */}
        {results && !loading && (
          <>
            {/* Summary row */}
            <CRow className="mb-4 g-3">
              <CCol sm={4}>
                <SummaryCard
                  label="Software Scanned"
                  value={results.software_scanned}
                  color="var(--cui-body-color)"
                />
              </CCol>
              <CCol sm={4}>
                <SummaryCard
                  label="Vulnerabilities Found"
                  value={results.vulnerabilities_found}
                  color={results.vulnerabilities_found > 0 ? '#ff8c00' : '#07d000d4'}
                />
              </CCol>
              <CCol sm={4}>
                <SummaryCard
                  label="Highest Severity"
                  value={
                    results.matched_cves.length > 0 ? (
                      <Badge rating={highestRating(results.matched_cves)} />
                    ) : (
                      <Badge rating="LOW" />
                    )
                  }
                  color="var(--cui-body-color)"
                />
              </CCol>
            </CRow>

            {results.matched_cves.length === 0 ? (
              <CAlert color="success" className="d-flex align-items-center gap-2">
                <CIcon icon={cilShieldAlt} />
                No known CVEs matched your installed software. Keep your software up to date!
              </CAlert>
            ) : (
              <CCard>
                <CCardHeader>
                  <strong>Matched CVEs</strong>
                  <span className="ms-2 text-muted small">
                    — sorted by risk (highest first)
                  </span>
                </CCardHeader>
                <CTable align="middle" className="mb-0 border" hover responsive>
                  <CTableHead>
                    <CTableRow>
                      <CTableHeaderCell className="bg-body-tertiary text-center">CVE ID</CTableHeaderCell>
                      <CTableHeaderCell className="bg-body-tertiary">Affected Software</CTableHeaderCell>
                      <CTableHeaderCell className="bg-body-tertiary">Description</CTableHeaderCell>
                      <CTableHeaderCell className="bg-body-tertiary text-center">CVSS</CTableHeaderCell>
                      <CTableHeaderCell className="bg-body-tertiary text-center">Risk</CTableHeaderCell>
                      <CTableHeaderCell className="bg-body-tertiary text-center">Rating</CTableHeaderCell>
                    </CTableRow>
                  </CTableHead>
                  <CTableBody>
                    {results.matched_cves.map((item) => (
                      <CTableRow key={item.cve_id}>
                        <CTableDataCell className="text-center font-monospace small">
                          <a
                            href={`https://nvd.nist.gov/vuln/detail/${item.cve_id}`}
                            target="_blank"
                            rel="noreferrer"
                          >
                            {item.cve_id}
                          </a>
                        </CTableDataCell>
                        <CTableDataCell className="small fw-semibold">
                          {item.affected_software}
                        </CTableDataCell>
                        <CTableDataCell
                          className="small text-muted"
                          style={{ maxWidth: 320, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}
                          title={item.description}
                        >
                          {item.description}
                        </CTableDataCell>
                        <CTableDataCell className="text-center small">
                          {item.cvss_score != null ? item.cvss_score.toFixed(1) : '—'}
                        </CTableDataCell>
                        <CTableDataCell className="text-center small">
                          {item.risk_index > 0 ? `${(item.risk_index * 100).toFixed(1)}%` : '—'}
                        </CTableDataCell>
                        <CTableDataCell className="text-center">
                          <Badge rating={item.risk_rating} />
                        </CTableDataCell>
                      </CTableRow>
                    ))}
                  </CTableBody>
                </CTable>
              </CCard>
            )}
          </>
        )}
      </CCol>
    </CRow>
  )
}

export default PCScanner
