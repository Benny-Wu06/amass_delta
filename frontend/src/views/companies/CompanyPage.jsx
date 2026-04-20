import React, { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import classNames from 'classnames'
import axios from 'axios'

import Heatmap from 'src/components/Heatmap.jsx'
import Graph from 'src/components/Graph.jsx'
import Company from 'src/components/Company.jsx'
import dreamybull from 'src/assets/images/dreamybull_suit.jpg'
import { CRow, CCol, CCard, CCardHeader, CCardBody, CBadge, CSpinner } from '@coreui/react'
import { BASE_URL } from '../../vars'
import VulnerabilityTable from '../vulnerabilities/VulnerabilityTable.jsx'

const SYMBOL_MAP = {
  'Google': 'GOOGL',
  'Apple': 'AAPL',
  'Microsoft': 'MSFT',
  'Broadcom': 'AVGO',
  'Meta': 'META',
  'Cisco': 'CSCO',
  'Intel': 'INTC'
};

const CompanyPage = () => {
  const { company_name } = useParams()
  const [companyData, setCompanyData] = useState(null)
  const [vulns, setVulns] = useState([])
  const [heatmapData, setHeatmapData] = useState([])
  const [graphData, setGraphData] = useState(null)
  const [growthData, setGrowthData] = useState([])
  const [stockVsCVEData, setStockVsCVEData] = useState(null)
  const [news, setNews] = useState([])
  const [loading, setLoading] = useState(true)
  const companyName = company_name

  useEffect(() => {
    setCompanyData(null);
    setGraphData(null);
    setStockVsCVEData(null);
    setHeatmapData([]);
    setNews([]);
    setLoading(true);

    const parseLambdaData = (res) => {
      return typeof res.data.body === 'string' 
        ? JSON.parse(res.data.body) 
        : res.data;
    };

    const fetchCompany = async () => {
      try {
        const response = await axios.get(`${BASE_URL}/v1/companies/${company_name}`)
        setCompanyData(response.data)

        const ticker = SYMBOL_MAP[company_name]
        if (ticker) fetchStockVsCVE(ticker)
     } catch (e) { console.error(e); }
    }

    const fetchCompanyVulns = async () => {
      try {
        const response = await axios.get(
          `${BASE_URL}/v1/companies/${company_name}/vulnerabilities`,
        )
        console.log(response.data)
        setVulns(response.data.vulnerabilities)
      } catch (error) {
        console.log('failed,', error)
      }
    }

    const fetchCompanyHeatmap = async () => {
      try {
        const response = await axios.get(
          `${BASE_URL}/v1/heatmap/${company_name}`,
        )
        let grid = [];
    
        const data = typeof response.data.body === 'string' 
        ? JSON.parse(response.data.body) 
        : response.data;

        setHeatmapData(data.heatmap_grid || []);
      } catch (error) {
        console.log('failed fetching heatmap,', error)
      }
    }

    const fetchCompanyGraph = async () => {
      try {
        const response = await axios.get(
          `${BASE_URL}/v1/growth/${company_name}`,
        )
        
        console.log("Axios Response Data:", response.data);
        setGraphData(response.data)

      } catch (error) {
        console.log('failed fetching growth ,', error)
      }
    }

    const fetchStockVsCVE = async (symbol) => {
      try {
        const response = await axios.get(`${BASE_URL}/v1/integration/${symbol}`)
        const data = parseLambdaData(response)
        setStockVsCVEData(data)
      } catch (error) {
        console.error('Failed fetching stock integration:', error)
      }
    }

    const fetchNews = async (symbol) => {
      try {
        const response = await axios.get(`${BASE_URL}/v1/news/${symbol}`)
        const data = parseLambdaData(response)
        setNews(data.news_data || [])
      } catch (error) {
        console.error('Failed fetching news:', error)
      }
    }

    const ticker = SYMBOL_MAP[company_name]
    if (ticker) fetchNews(ticker)

    fetchCompany()
    fetchCompanyVulns()
    fetchCompanyHeatmap()
    fetchCompanyGraph()
  }, [company_name])

  const latestDate = vulns && vulns.length > 0 
  ? (() => {
      const timestamps = vulns.map(v => {
        const d = new Date(v.dateAdded); 
        return isNaN(d.getTime()) ? 0 : d.getTime();
      });

      const maxTimestamp = Math.max(...timestamps);

      return maxTimestamp === 0 
        ? 'No valid dates' 
        : new Date(maxTimestamp).toLocaleDateString('en-AU'); 
    })()
  : 'No records found';

  return (
    <>
      <h2 className="mx-2 mb-4">{companyName}</h2>
      
      {/* Row 1: Heatmap and Growth Graph */}
      <CRow className="mb-4 d-flex align-items-stretch">
        <CCol md={6} className="d-flex">
            <Heatmap header={'Company Risk Heatmap'} data={heatmapData} type="heatmap" />
        </CCol>
        <CCol md={6} className="d-flex">
            <Graph header={'CVE Growth vs. Time'} rawResponse={graphData} />
        </CCol>
      </CRow>

      {/* Row 2: Metrics and Stock Integration */}
      <CRow className="mb-4 d-flex align-items-stretch">
        <CCol md={6} className="d-flex">
          {companyData ? (
            <CCard className="h-100 w-100"> 
              <CCardHeader>Metrics</CCardHeader>
              <CCardBody className="d-flex flex-column justify-content-center">
                <CRow>
                  <CCol xs={6}>
                    <p className="text-muted mb-0">Risk Index</p>
                    <h1 className="display-4 fw-bold text-warning">{companyData.risk_index}</h1>
                  </CCol>
                  <CCol xs={6}>
                    <p className="text-muted mb-0">Risk Rating</p>
                    <h1 className="display-4 fw-bold text-primary">{companyData.risk_rating}</h1>
                  </CCol>
                </CRow>
                <hr />
                <div className="mt-3">
                  <p className="mb-1"><strong>CVE Count:</strong> {companyData.cve_count}</p>
                  <p className="mb-1"><strong>Avg CVSS:</strong> {companyData.avg_cvss}</p>
                  <p className="mb-1"><strong>Avg EPSS:</strong> {companyData.avg_epss}</p>
                  <p className="mb-0"><strong>Most Recent Vulnerability:</strong> {latestDate}</p>
                </div>
              </CCardBody>
            </CCard>
          ) : (
            <CCard className="h-100 w-100 d-flex align-items-center justify-content-center">
              <div className="text-muted">Loading metrics...</div>
            </CCard>
          )}
        </CCol>

        <CCol md={6} className="d-flex">
          <Graph 
            header={'Stock Price vs. CVE GROWTH'} 
            rawResponse={stockVsCVEData}
            type="stock_correlation"
          />
        </CCol>
      </CRow>

      <VulnerabilityTable vulns={vulns} />

      {SYMBOL_MAP[company_name] && (
        <CCard className="mt-4">
          <CCardHeader className="fw-semibold">News & Sentiment</CCardHeader>
          <CCardBody>
            {news.length === 0 ? (
              <div className="text-center py-4"><CSpinner color="primary" /></div>
            ) : (
              <div className="d-flex flex-column gap-3">
                {news.slice(0, 10).map((article, i) => (
                  <div key={i} className="d-flex gap-3 pb-3" style={{ borderBottom: '1px solid var(--cui-border-color)' }}>
                    {article.banner_image && (
                      <img
                        src={article.banner_image}
                        alt=""
                        style={{ width: 80, height: 60, objectFit: 'cover', borderRadius: 6, flexShrink: 0 }}
                        onError={(e) => { e.target.style.display = 'none' }}
                      />
                    )}
                    <div className="flex-grow-1 min-w-0">
                      <a
                        href={article.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="fw-semibold text-decoration-none d-block mb-1"
                        style={{ lineHeight: 1.3 }}
                      >
                        {article.title}
                      </a>
                      <p className="text-muted small mb-1" style={{ display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>
                        {article.summary}
                      </p>
                      <div className="d-flex align-items-center gap-2 flex-wrap">
                        <span className="text-muted" style={{ fontSize: '0.75rem' }}>{article.source}</span>
                        <CBadge
                          color={
                            article.ticker_sentiment_label?.includes('Bullish') ? 'success' :
                            article.ticker_sentiment_label?.includes('Bearish') ? 'danger' : 'secondary'
                          }
                          shape="rounded-pill"
                          style={{ fontSize: '0.7rem' }}
                        >
                          {article.ticker_sentiment_label || 'Neutral'}
                        </CBadge>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CCardBody>
        </CCard>
      )}
    </>
  )
}

export default CompanyPage
