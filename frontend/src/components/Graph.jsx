import React from 'react'
import { CCol, CCard, CCardBody, CCardHeader } from '@coreui/react'

const Graph = ({ header, data, type }) => {
  const getCellColor = (count) => {
    if (count === 0) return '#2a2e32' // Darker gray for dark mode
    if (count < 10) return '#4d3800'  // Dark Yellow
    if (count < 30) return '#662222'  // Dark Red
    return '#e55353'                 // CoreUI Danger Red
  }

  return (
    <CCol md={6}>
      <CCard className="h-100 mb-4">
        <CCardHeader>{header}</CCardHeader>
        <CCardBody>
          {type === 'heatmap' && data ? (
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(5, 1fr)',
              gap: '5px',
              width: '100%',
              height: '250px'
            }}>
              {data.map((cell, index) => (
                <div
                  key={index}
                  title={`CVSS: ${cell.cvss_range} | EPSS: ${cell.epss_range}`}
                  style={{
                    backgroundColor: getCellColor(cell.cve_count),
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: '12px',
                    fontWeight: 'bold',
                    border: '1px solid #dee2e6',
                    borderRadius: '2px',
                    color: cell.cve_count > 30 ? 'white' : 'black'
                  }}
                >
                  {cell.cve_count > 0 ? cell.cve_count : ''}
                </div>
              ))}
            </div>
          ) : (
            <div style={{ height: '250px', background: '#f8f9fa', width: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <span className="text-muted">No data available</span>
            </div>
          )}
        </CCardBody>
      </CCard>
    </CCol>
  )
}

export default Graph