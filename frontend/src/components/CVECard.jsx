import React from 'react'

const CVECard = ({ item, onClick }) => {
  const riskStyle = (rating) => {
    const map = {
      CRITICAL: { color: '#ff3b3b', bg: 'rgba(255,59,59,0.12)' },
      HIGH: { color: '#ff8c00', bg: 'rgba(255,140,0,0.12)' },
      MEDIUM: { color: '#f0c040', bg: 'rgba(240,192,64,0.12)' },
      LOW: { color: '#07d000d4', bg: 'rgba(26,122,74,0.12)' },
    }
    return map[rating] || { color: '#6e7681', bg: 'rgba(110,118,129,0.12)' }
  }

  const { color, bg } = riskStyle(item.risk_rating)

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

        <div className="cve-description">{item.description || 'No description available.'}</div>

        <div className="cve-card-footer">
          <span className="cve-badge" style={{ color, background: bg }}>
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
