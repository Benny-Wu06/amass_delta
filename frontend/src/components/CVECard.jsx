import { useForkedRef } from '@coreui/react'
import axios from 'axios'
import React from 'react'
import { BASE_URL } from '../vars'
import { useState, useEffect } from 'react'

const CVECard = ({ item, onClick }) => {
  const [cveDescription, setCveDescription] = useState(null)
  console.log(item)

  // useEffect(() => {
  //   const getCveDescription = async () => {
  //     try {
  //       const response = await axios.get(`${BASE_URL}/v1/vulnerabilities/${item.cve_id}`)
  //       console.log(response.data)
  //       setCveDescription(response.data.description)
  //     } catch (error) {
  //       console.log('coudlnt get cve description', error)
  //     }
  //   }
  //   getCveDescription()
  // }, [item])

  const riskColor = (index) => {
    // index is 0–1; map to green → yellow → orange → red
    if (index >= 0.75) return '#ff3b3b'
    if (index >= 0.5) return '#ff8c00'
    if (index >= 0.25) return '#f0c040'
    return '#00e676'
  }

  const ratingLabel = (rating) => {
    const map = {
      CRITICAL: { color: '#ff3b3b', bg: 'rgba(255,59,59,0.12)' },
      HIGH: { color: '#ff8c00', bg: 'rgba(255,140,0,0.12)' },
      MEDIUM: { color: '#f0c040', bg: 'rgba(240,192,64,0.12)' },
      LOW: { color: '#00e676', bg: 'rgba(0,230,118,0.12)' },
    }
    return map[rating] || { color: '#6e7681', bg: 'rgba(110,118,129,0.12)' }
  }

  const color = riskColor(item.risk_index ?? 0)
  const badge = ratingLabel(item.risk_rating)

  return (
    <div className="cve-card" onClick={onClick}>
      <div className="cve-card-inner">
        <div className="cve-card-top">
          <span className="cve-id">{item.cve_id}</span>
          <span className="cve-running">
            <span className="cve-dot" style={{ background: color }} />
            {item.risk_rating || 'UNKNOWN'}
          </span>
        </div>

        <div className="cve-company">{item.company_name}</div>

        <div className="cve-description">{cveDescription || 'No description available.'}</div>

        <div className="cve-card-footer">
          <span className="cve-badge" style={{ color: badge.color, background: badge.bg }}>
            {item.risk_rating}
          </span>
          <span className="cve-meta">
            {item.due_date ? `Due ${item.due_date}` : item.date_added}
          </span>
          <span className="cve-score" style={{ color }}>
            {item.risk_index != null ? (item.risk_index * 100).toFixed(1) : '—'}
          </span>
        </div>
      </div>
      <div className="cve-risk-bar" style={{ background: color }} />
    </div>
  )
}

export default CVECard
