import React from 'react'
import Highcharts from 'highcharts'
import HighchartsReact from 'highcharts-react-official'
import { CCol, CCard, CCardHeader, CCardBody } from '@coreui/react'

const Graph = ({ header, rawResponse }) => {
  console.log("Graph component received:", rawResponse);

  const parsedData = rawResponse;

  // Data Check - Use the direct reference
  if (!parsedData || !parsedData.data_points) {
    return (
      <CCol md={6}>
        <CCard className="mb-4">
          <CCardHeader>{header}</CCardHeader>
          <CCardBody className="d-flex align-items-center justify-content-center" style={{ height: '350px' }}>
            <div className="text-muted text-center">
              No growth data available <br />
              <small>Wait for data to load...</small>
            </div>
          </CCardBody>
        </CCard>
      </CCol>
    );
  }

  // Mapping logic remains the same
  const categories = parsedData.data_points.map(point => point.date);
  const seriesData = parsedData.data_points.map(point => point.new_cves);

  const options = {
    chart: { type: 'area', height: '350px', backgroundColor: 'transparent' },
    title: { text: null },
    accessibility: { enabled: false },
    xAxis: {
      categories: categories,
      labels: {
        style: { color: '#8a93a2' },
        formatter: function () {

          return this.pos % 5 === 0 ? this.value : '';
        }
      },
      lineColor: '#3c4147'
    },
    yAxis: {
      title: { 
        text: parsedData.metadata?.y_label || 'Count', 
        style: { color: '#8a93a2' } 
      },
      labels: { style: { color: '#8a93a2' } },
      gridLineColor: '#3c4147'
    },
    colors: ['#e55353'],
    plotOptions: {
      area: {
        fillColor: {
          linearGradient: { x1: 0, y1: 0, x2: 0, y2: 1 },
          stops: [
            [0, 'rgba(229, 83, 83, 0.4)'],
            [1, 'rgba(229, 83, 83, 0)']
          ]
        },
        marker: { radius: 3 },
        lineWidth: 2,
      }
    },
    series: [{
      name: 'New CVEs',
      data: seriesData
    }],
    tooltip: {
      backgroundColor: '#2a2e32',
      style: { color: '#ffffff' },
      shared: true
    },
    credits: { enabled: false }
  };

  return (
    <CCol md={6}>
      <CCard className="mb-4">
        <CCardHeader>{header}</CCardHeader>
        <CCardBody>
          <HighchartsReact highcharts={Highcharts} options={options} />
        </CCardBody>
      </CCard>
    </CCol>
  );
}

export default Graph;