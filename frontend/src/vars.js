export const BASE_URL = 'https://2r5sbcl74l.execute-api.ap-southeast-2.amazonaws.com'
export const STAGING_URL = 'https://7mz3fi8zw1.execute-api.ap-southeast-2.amazonaws.com'

export function getUserEmail() {
  try {
    const user = JSON.parse(localStorage.getItem('user') || '{}')
    if (user.email) return user.email
    const token = user.access_token
    if (!token) return ''
    const payload = JSON.parse(atob(token.split('.')[1]))
    return payload.sub || ''
  } catch {
    return ''
  }
}
