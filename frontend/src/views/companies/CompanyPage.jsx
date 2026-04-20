import React, { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import classNames from 'classnames'
import axios from 'axios'

import Heatmap from 'src/components/Heatmap.jsx'
import Graph from 'src/components/Graph.jsx'
import Company from 'src/components/Company.jsx'
import dreamybull from 'src/assets/images/dreamybull_suit.jpg'
import { CRow, CCol, CCard, CCardHeader, CCardBody, CBadge } from '@coreui/react'
import { STAGING_URL } from '../../vars'
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
  const [loading, setLoading] = useState(true)
  const companyName = company_name

  useEffect(() => {
    setCompanyData(null);
    setGraphData(null);
    setStockVsCVEData(null);
    setHeatmapData([]);
    setLoading(true);

    const parseLambdaData = (res) => {
      return typeof res.data.body === 'string' 
        ? JSON.parse(res.data.body) 
        : res.data;
    };

    const fetchCompany = async () => {
      try {
        const response = await axios.get(`${STAGING_URL}/v1/companies/${company_name}`)
        setCompanyData(response.data)

        const ticker = SYMBOL_MAP[company_name];

        if (ticker) {
          fetchStockVsCVE(ticker);
        } else {
          console.error(`No symbol mapping found for: ${company_name}`);
        }

     } catch (e) { console.error(e); }
    }

    const fetchCompanyVulns = async () => {
      try {
        const response = await axios.get(
          `${STAGING_URL}/v1/companies/${company_name}/vulnerabilities`,
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
          `${STAGING_URL}/v1/heatmap/${company_name}`,
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
          `${STAGING_URL}/v1/growth/${company_name}`,
        )
        
        console.log("Axios Response Data:", response.data);
        setGraphData(response.data)

      } catch (error) {
        console.log('failed fetching growth ,', error)
      }
    }

    const fetchStockVsCVE = async (symbol) => {
      try {
        const response = await axios.get(`${STAGING_URL}/v1/integration/${symbol}`)
        const data = parseLambdaData(response)
        setStockVsCVEData(data)
      } catch (error) {
        console.error('Failed fetching stock integration:', error)
      }
    }

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
    </>
  )
}

export default CompanyPage
