import React from 'react'
import Highcharts from 'highcharts'
import HighchartsReact from 'highcharts-react-official'
import heatmap from 'highcharts/modules/heatmap'
import { CCard, CCardHeader, CCardBody } from '@coreui/react'

// Initialize the heatmap module
if (typeof Highcharts === 'object') {
  heatmap(Highcharts)
}

const Graph = ({ header, data, type }) => {
  if (type === 'heatmap' && data) {
    // Transform your data: [{cvss_range: "0-2", epss_range: "0-0.2", cve_count: 5}, ...]
    const cvssCategories = ['0-2', '2-4', '4-6', '6-8', '8-10']
    const epssCategories = ['0-0.2', '0.2-0.4', '0.4-0.6', '0.6-0.8', '0.8-1.0']

    const chartData = data.map((item) => [
      cvssCategories.indexOf(item.cvss_range),
      epssCategories.indexOf(item.epss_range),
      item.cve_count,
    ])

    const options = {
      chart: { type: 'heatmap', height: '300px' },
      title: { text: null },
      xAxis: { categories: cvssCategories, title: { text: 'CVSS Score' } },
      yAxis: { categories: epssCategories, title: { text: 'EPSS Score' }, reversed: true },
      colorAxis: {
        min: 0,
        minColor: '#FFFFFF',
        maxColor: '#e55353', 
      },
      legend: {
        align: 'right',
        layout: 'vertical',
        verticalAlign: 'middle',
      },
      series: [{
        name: 'CVE Count',
        borderWidth: 1,
        data: chartData,
        dataLabels: {
          enabled: true,
          color: '#000000',
        },
      }],
      credits: { enabled: false }
    }

    return (
      <CCard className="mb-4">
        <CCardHeader>{header}</CCardHeader>
        <CCardBody>
          <HighchartsReact highcharts={Highcharts} options={options} />
        </CCardBody>
      </CCard>
    )
  }

  return (
    <CCard className="mb-4">
      <CCardHeader>{header}</CCardHeader>
      <CCardBody className="text-center py-5">
        Standard Chart Placeholder
      </CCardBody>
    </CCard>
  )
}

export default Graph