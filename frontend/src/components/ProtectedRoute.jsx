import React from 'react'
import { Navigate } from 'react-router-dom'

const ProtectedRoute = ({ children }) => {
  const user = JSON.parse(localStorage.getItem('user'))

  if (!user || !user.access_token) {
    return <Navigate to="/login" replace />
  }

  return children
}

export default ProtectedRoute