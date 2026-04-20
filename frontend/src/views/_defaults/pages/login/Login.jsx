import React, { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import axios from 'axios'
import { STAGING_URL } from '../../../../vars'
import {
  CButton,
  CCard,
  CCardBody,
  CCardGroup,
  CCol,
  CContainer,
  CForm,
  CFormInput,
  CInputGroup,
  CInputGroupText,
  CRow,
} from '@coreui/react'
import CIcon from '@coreui/icons-react'
import { cilLockLocked, cilUser } from '@coreui/icons'

const Login = () => {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const navigate = useNavigate()

  const handleLogin = async (e) => {
    e.preventDefault()
    try {
      const response = await axios.post(`${STAGING_URL}/auth/login`, { email, password })
      if (response.data.access_token) {
        localStorage.setItem('user', JSON.stringify(response.data))
        navigate('/dashboard')
      }
    } catch (error) {
      alert('Login failed: ' + (error.response?.data?.detail || 'Unknown error'))
    }
  }


  const darkThemeColor = { backgroundColor: '#4a68a1', border: 'none' }

  return (
    <div className="bg-body-tertiary min-vh-100 d-flex align-items-center">
      <CContainer>
        <CRow className="justify-content-center">
          <CCol md={8}>
            <CCardGroup>
              <CCard className="p-4 shadow-sm">
                <CCardBody>
                  <CForm onSubmit={handleLogin}>
                    <h1 style={{ color: '#4a68a1' }}>Login</h1>
                    <p className="text-body-secondary">Sign In to your account</p>
                    <CInputGroup className="mb-3">
                      <CInputGroupText>
                        <CIcon icon={cilUser} />
                      </CInputGroupText>
                      <CFormInput 
                        placeholder="Email" 
                        onChange={(e) => setEmail(e.target.value)} 
                      />
                    </CInputGroup>
                    <CInputGroup className="mb-4">
                      <CInputGroupText>
                        <CIcon icon={cilLockLocked} />
                      </CInputGroupText>
                      <CFormInput 
                        type="password" 
                        placeholder="Password" 
                        onChange={(e) => setPassword(e.target.value)} 
                      />
                    </CInputGroup>
                    <CRow>
                      <CCol xs={6}>
                        <CButton 
                          style={darkThemeColor} 
                          className="px-4 text-white" 
                          type="submit"
                        >
                          Login
                        </CButton>
                      </CCol>
                    </CRow>
                  </CForm>
                </CCardBody>
              </CCard>
              <CCard 
                className="text-white py-5" 
                style={{ ...darkThemeColor, width: '44%' }}
              >
                <CCardBody className="text-center">
                  <div>
                    <h2>Sign up</h2>
                    <p className="opacity-75">Register to start monitoring vulnerabilities.</p>
                    <Link to="/register">
                      <CButton 
                        color="light" 
                        variant="outline" 
                        className="mt-3 px-4 fw-bold" 
                        active 
                        tabIndex={-1}
                      >
                        Register Now!
                      </CButton>
                    </Link>
                  </div>
                </CCardBody>
              </CCard>
            </CCardGroup>
          </CCol>
        </CRow>
      </CContainer>
    </div>
  )
}

export default Login