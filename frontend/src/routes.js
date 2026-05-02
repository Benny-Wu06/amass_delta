/**
 * Application Routes Configuration
 *
 * Defines all protected routes in the application using React lazy loading
 * for code splitting and performance optimization.
 *
 * Each route object contains:
 * - path: URL path for the route
 * - name: Human-readable name for breadcrumbs
 * - element: Lazy-loaded React component
 * - exact: (optional) Requires exact path match
 *
 * @module routes
 */

import React from 'react'

// used routes
const Dashboard = React.lazy(() => import('./views/dashboard/Dashboard'))
const Watchlists = React.lazy(() => import('./views/watchlists/Watchlists'))
const ViewWatchlist = React.lazy(() => import('./views/watchlists/ViewWatchlist'))
const AllCompanies = React.lazy(() => import('./views/companies/AllCompanies'))
const CompanyPage = React.lazy(() => import('./views/companies/CompanyPage'))
const Vulnerabilities = React.lazy(() => import('./views/vulnerabilities/Vulnerabilities'))
const VulnInfo = React.lazy(() => import('./views/vulnerabilities/VulnInfo'))
const PCScanner = React.lazy(() => import('./views/scanner/PCScanner'))
const Login = React.lazy(() => import('./views/auth/Login'))
const Register = React.lazy(() => import('./views/auth/Register'))

// DEFAULT ROUTES

/**
 * Array of route configuration objects
 *
 * @type {Array<Object>}
 * @property {string} path - URL path pattern
 * @property {string} name - Display name for breadcrumbs and navigation
 * @property {React.LazyExoticComponent} element - Lazy-loaded component
 * @property {boolean} [exact] - Whether to match path exactly
 *
 * @example
 * // Route renders when URL matches '/dashboard'
 * { path: '/dashboard', name: 'Dashboard', element: Dashboard }
 *
 * @example
 * // Route with exact match required
 * { path: '/base', name: 'Base', element: Cards, exact: true }
 */
export const routes = [
  { path: '/', exact: true, name: 'Home' },
  { path: '/dashboard', name: 'Dashboard', element: Dashboard },
  { path: '/watchlists', name: 'Watchlists', element: Watchlists },
  { path: '/companies', name: 'Companies', element: AllCompanies },
  { path: '/watchlists/:watchlist_id', name: 'ViewWatchlist', element: ViewWatchlist },
  { path: '/vulnerabilities', name: 'Vulnerabilities', element: Vulnerabilities },
  { path: '/vulnerabilities/:cveId', name: 'VulnInfo', element: VulnInfo },
  { path: '/companies/:company_name', name: 'Company', element: CompanyPage },
  { path: '/scanner', name: 'PC Scanner', element: PCScanner },
  { path: '/login', name: 'Login', element: Login },
  { path: '/register', name: 'Register', element: Register },
]

export default routes
