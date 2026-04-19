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
    ? new Date(
        Math.max(...vulns.map(v => {
            const d = new Date(v.date_added || v.published_date);
            return isNaN(d.getTime()) ? 0 : d.getTime();
        }))
        ).toLocaleDateString()
    : 'No records found';

  return (
    <>
      <h2 className="mx-2 mb-4">{companyName}</h2>
      
      <CRow className="mb-4">
        <Heatmap header={'Company Risk Heatmap'} data={heatmapData} type="heatmap" />
        <Graph header={'CVE Growth vs. Time'} rawResponse={graphData} />
      </CRow>

      <CRow className="mb-4">
        {companyData ? (
          <CCol md={6}>
            <CCard className="h-100"> 
              <CCardHeader>Metrics</CCardHeader>
              <CCardBody>
                <CRow>
                  <CCol xs={6}>
                    <p className="text-muted mb-0">Risk Index</p>
                    <h3 className="text-warning">{companyData.risk_index}</h3>
                  </CCol>
                  <CCol xs={6}>
                    <p className="text-muted mb-0">Risk Rating</p>
                    <h3>{companyData.risk_rating}</h3>
                  </CCol>
                </CRow>
                <hr />
                <div className="mt-3">
                  <p><strong>CVE Count:</strong> {companyData.cve_count}</p>
                  <p><strong>Avg CVSS:</strong> {companyData.avg_cvss}</p>
                  <p><strong>Avg EPSS:</strong> {companyData.avg_epss}</p>
                  <p><strong>Latest Update:</strong> {latestDate}</p>
                </div>
              </CCardBody>
            </CCard>
          </CCol>
        ) : (
          <CCol md={6}>
            <CCard className="h-100 d-flex align-items-center justify-content-center">
              <div>Loading metrics...</div>
            </CCard>
          </CCol>
        )}

        
          <Graph 
            header={'Stock Price vs. CVE GROWTH'} 
            rawResponse={stockVsCVEData}
            type="stock_correlation"
           />
          
      </CRow>

      <VulnerabilityTable vulns={vulns} />
    </>
  )
}

export default CompanyPage
