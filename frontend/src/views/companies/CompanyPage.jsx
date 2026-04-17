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

    const fetchCompanyGraphs = async () => {
      try {
        const response = await axios.get(
          `${STAGING_URL}/v1/heatmap/${company_name}`,
        )
        console.log(response.data)
        setGraphs(response.data.vulnerabilities)
      } catch (error) {
        console.log('failed,', error)
      }
    }

    fetchCompany()
    fetchCompanyVulns()
    fetchCompanyGraphs()
  }, [company_name])

  return (
    <>
      <h2 className="mx-2 mb-4">{companyName}</h2>
      <CRow className="mb-4">
        <Graph header={'Company Heatmap'}></Graph>
        <Graph header={'CVE Growth vs. Time'}></Graph>
      </CRow>

      <CRow className="mb-4">
        {companyData ? (
          <CCol md={6}>
            <CCard className="h-150">
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
                  <p>
                    <strong>CVE Count:</strong> {companyData.cve_count}
                  </p>
                  <p>
                    <strong>Avg CVSS:</strong> {companyData.avg_cvss}
                  </p>
                  <p>
                    <strong>Avg EPSS:</strong> {companyData.avg_epss}
                  </p>
                  <p>
                    <strong>Latest Vulnerability Date:</strong> {'hardcoded diddyblud'}
                  </p>
                </div>
              </CCardBody>
            </CCard>
          </CCol>
        ) : (
          <div>loading</div>
        )}

        <Graph header={'Stock Price vs. CVE GROWTH'}></Graph>
      </CRow>

      <VulnerabilityTable vulns={vulns}></VulnerabilityTable>
    </>
  )
}

export default CompanyPage
