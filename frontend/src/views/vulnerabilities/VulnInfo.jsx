import { useFetcher, useParams } from "react-router-dom"

const VulnInfo = ({}) => {
  const {cveId} = useParams()
  const [cveInfo, setCveInfo] = useState(null)

  useEffect(() => {

  }, [cveId]) 
  
  return (
    <>
      <h1>{cveId}</h1>
    </>
  )
}

export default VulnInfo
