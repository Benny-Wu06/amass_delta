import React, { useEffect, useRef } from 'react'
import Highcharts from 'highcharts'
import HighchartsReact from 'highcharts-react-official'
import { CCol, CCard, CCardHeader, CCardBody } from '@coreui/react'

// Use this specific import style for modules
import HeatmapModule from 'highcharts/modules/heatmap'

// Initialize immediately if Highcharts is available
if (typeof HeatmapModule === 'function') {
  HeatmapModule(Highcharts)
}

const Heatmap = ({ header, data, type }) => {
  const chartComponentRef = useRef(null)

  // Data Guard to prevent rendering before data arrives
  if (type === 'heatmap' && (!data || data.length === 0)) {
    return (
      <CCard className="mb-4 h-100 w-100">
        <CCardHeader>{header}</CCardHeader>
        <CCardBody className="d-flex align-items-center justify-content-center" style={{ minHeight: '350px' }}>
          <div className="text-muted text-center">Loading Heatmap Data...</div>
        </CCardBody>
      </CCard>
    );
  }

  if (type === 'heatmap') {
    const cvssCategories = ['0-2', '2-4', '4-6', '6-8', '8-10']
    const epssCategories = ['0-0.2', '0.2-0.4', '0.4-0.6', '0.6-0.8', '0.8-1.0']

    const chartData = data.map((item) => [
      cvssCategories.indexOf(item.cvss_range) === -1 ? 0 : cvssCategories.indexOf(item.cvss_range),
      epssCategories.indexOf(item.epss_range) === -1 ? 0 : epssCategories.indexOf(item.epss_range),
      item.cve_count || 0,
    ])

    const maxCount = Math.max(...data.map(i => i.cve_count || 0), 1);

   const options = {
      chart: { type: 'heatmap', height: '350px', backgroundColor: 'transparent' },
      title: { text: null },
      xAxis: {
        categories: cvssCategories,
        title: { text: 'CVSS Score', style: { color: '#8a93a2' } },
        labels: { style: { color: '#8a93a2' } }
      },
      yAxis: {
        categories: epssCategories,
        title: { text: 'EPSS Score', style: { color: '#8a93a2' } },
        labels: { style: { color: '#8a93a2' } },
        reversed: true
      },
      
      colorAxis: {
        min: 0,
        max: maxCount,
        stops: [
          [0, '#2b2e32'],   // Zero: Grey
          [0.33, '#d6d464'], // Mid1: Yellow
          [0.66, '#d8834b'], // Mid2: Orange
          [1, '#d64b4b']    // High: Red
        ],
      },
      legend: {
        align: 'right',
        layout: 'vertical',
        verticalAlign: 'middle',
        symbolHeight: 200,
        title: { text: 'CVEs', style: { color: '#8a93a2' } },
        labels: { style: { color: '#8a93a2' } }
      },
      series: [{
        name: 'Vulnerabilities',
        borderWidth: 1,
        borderColor: '#3c4147', 
        data: chartData,        
        dataLabels: { enabled: false },
        tooltip: {
          headerFormat: 'Risk Grid<br/>',
          pointFormat: 'CVSS: <b>{point.xCategory}</b>, EPSS: <b>{point.yCategory}</b> <br/>Count: <b>{point.value}</b>'
        }
      }],
      credits: { enabled: false }
    }

    return (
        <CCard className="mb-4 h-100 w-100">
            <CCardHeader>{header}</CCardHeader>
            <CCardBody>
                <HighchartsReact 
                highcharts={Highcharts} 
                options={options} 
                ref={chartComponentRef} 
                />
            </CCardBody>
        </CCard>
        );
    }

  return (
    <CCard className="mb-4 h-100 w-100">
        <CCardHeader>{header}</CCardHeader>
        <CCardBody className="d-flex align-items-center justify-content-center" style={{ height: '350px' }}>
        <div className="text-muted">No Data Available</div>
        </CCardBody>
    </CCard>
  );
}

export default Heatmap