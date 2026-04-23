import React, { useState } from 'react'
import { CButton } from '@coreui/react'

const SubscribeButton = () => {
  const [isSubscribed, setIsSubscribed] = useState(false)

  const handleToggle = () => {
    setIsSubscribed(!isSubscribed)
  }

  return (
    <CButton
      // changes color based on state (green for subscribe, gray for unsubscribe)
      color={isSubscribed ? 'secondary' : 'success'}
      onClick={handleToggle}
      className="px-4 fw-semibold"
    >
      {isSubscribed ? 'Unsubscribe' : 'Subscribe'}
    </CButton>
  )
}

export default SubscribeButton
