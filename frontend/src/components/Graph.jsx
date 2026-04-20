import React from 'react'
import Highcharts from 'highcharts'
import HighchartsReact from 'highcharts-react-official'
import { CCol, CCard, CCardHeader, CCardBody } from '@coreui/react'

const Graph = ({ header, rawResponse, type }) => {

  let data = rawResponse;
  // Handle stringified bodies from Lambda
  if (rawResponse?.body && typeof rawResponse.body === 'string') {
    try { data = JSON.parse(rawResponse.body); } catch (e) { console.error("Parse error", e); }
  }

  const isStockView = type === 'stock_correlation';
  
  // Growth API uses 'data_points', Integration API uses 'merged_results'
  const dataPoints = isStockView 
    ? (data?.merged_results || []) 
    : (data?.data_points || []);

  const hasData = dataPoints && dataPoints.length > 0;

  if (!hasData) {
    return (
      <CCol md={6}>
        <CCard className="mb-4">
          <CCardHeader>{header}</CCardHeader>
          <CCardBody className="d-flex align-items-center justify-content-center" style={{ height: '350px' }}>
            <div className="text-muted text-center">
              No data points found for this period.
            </div>
          </CCardBody>
        </CCard>
      </CCol>
    );
  }

  //  Chart Configuration
  const options = {
    chart: { height: '350px', backgroundColor: 'transparent' },
    title: { text: null },
    height: 350,
    reflow: true,
    // STOPS THE CONSOLE WARNING
    accessibility: { enabled: false }, 
    credits: { enabled: false },
    xAxis: {
      categories: dataPoints.map(p => p.date || 'N/A'),
      labels: {
        style: { color: '#8a93a2' },
        formatter: function () {
          return this.pos % 5 === 0 ? this.value : ''; 
        }
      }
    },
    yAxis: [
      {
        title: { text: isStockView ? 'Price Diff' : 'CVE Count' },
        gridLineColor: '#3c4147'
      },
      {
        title: { text: 'CVE Volume' },
        opposite: true,
        visible: isStockView,
        gridLineWidth: 0
      }
    ],
    series: isStockView ? [
      {
        name: 'Price Change',
        data: dataPoints.map(p => p.price_diff || 0),
        color: '#3399ff',
        type: 'line',
        zIndex: 2
      },
      {
        name: 'Vulnerabilities',
        data: dataPoints.map(p => p.cve_growth || 0),
        color: '#e55353',
        type: 'column',
        yAxis: 1,
        zIndex: 1
      }
    ] : [
      {
        name: 'New CVEs',
        data: dataPoints.map(p => p.new_cves || 0),
        type: 'area',
        color: '#e55353'
      }
    ],
    tooltip: { shared: true }
  };

  return (
    <CCard className="h-100 w-100">
        <CCardHeader>{header}</CCardHeader>
        <CCardBody>
        <HighchartsReact 
            highcharts={Highcharts} 
            options={options} 
            containerProps={{ style: { height: '100%', width: '100%' } }}
        />
        </CCardBody>
    </CCard>
  )
}

export default Graph;