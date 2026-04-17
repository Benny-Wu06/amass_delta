import React, { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import classNames from 'classnames'
import axios from 'axios'

import Graph from 'src/components/Graph.jsx'
import Company from 'src/components/Company.jsx'
import dreamybull from 'src/assets/images/dreamybull_suit.jpg'
import { CRow, CCol, CCard, CCardHeader, CCardBody, CBadge } from '@coreui/react'
import { STAGING_URL } from '../../vars'
import VulnerabilityTable from '../vulnerabilities/VulnerabilityTable.jsx'

const CompanyPage = () => {
  const { company_name } = useParams()
  const [companyData, setCompanyData] = useState(null)
  const [vulns, setVulns] = useState([])
  const [heatmapData, setHeatmapData] = useState([])
  const [loading, setLoading] = useState(true)
  const companyName = company_name

  useEffect(() => {
    const fetchCompany = async () => {
      try {
        const response = await axios.get(`${STAGING_URL}/v1/companies/${company_name}`)
        setCompanyData(response.data)
        console.log(response.data)
      } catch (error) {
        console.log('Failed to fetch company:', error)
      } finally {
        setLoading(false)
      }
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
    
        // If body is already an object, use it. If it's a string, parse it.
        const data = typeof response.data.body === 'string' 
        ? JSON.parse(response.data.body) 
        : response.data;

        setHeatmapData(data.heatmap_grid || []);
      } catch (error) {
        console.log('failed fetching heatmap,', error)
      }
    }

    fetchCompany()
    fetchCompanyVulns()
    fetchCompanyHeatmap()
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
      
      {/* Row 1: Charts */}
      <CRow className="mb-4">
        {/* Only call the heatmap once and pass the data */}
        <Graph header={'Company Risk Heatmap'} data={heatmapData} type="heatmap" />
        <Graph header={'CVE Growth vs. Time'} />
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

        <Graph header={'Stock Price vs. CVE GROWTH'} />
      </CRow>

      <VulnerabilityTable vulns={vulns} />
    </>
  )
}

export default CompanyPage
