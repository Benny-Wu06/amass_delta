import { useFetcher, useParams } from "react-router-dom"
import {useEffect, useState} from 'react'
import axios from 'axios'
import { STAGING_URL } from '../../vars'

const VulnInfo = ({}) => {
  const {cveId} = useParams()
  const [cveInfo, setCveInfo] = useState(null)

  useEffect(() => {
    const fetchCVE = async () => {
      try {
        const response = await axios.get(`${STAGING_URL}/v1/vulnerabilities/${cveId}`)
        setCveData(response.data)
        console.log(response.data)
      } catch (error) {
        console.error('Failed to fetch CVE:', error)
      }
    }
    fetchCVE()
  }, [cveId])

  return (
    <>
      <h1>{cveId}</h1>
    </>
  )
}

export default VulnInfo
