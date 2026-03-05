import { Outlet, Link, useLocation } from 'react-router-dom';
import { authAPI } from '../api';

function Layout({ user, onLogout }) {
  const location = useLocation();

  const handleLogout = async () => {
    try {
      await authAPI.logout();
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      onLogout();
    }
  };

  return (
    <div>
      <header className="header">
        <nav className="nav">
          <div className="nav-links">
            <Link
              to="/dashboard"
              className={`nav-link ${location.pathname === '/dashboard' ? 'active' : ''}`}
            >
              Dashboard
            </Link>
            <Link
              to="/tasks"
              className={`nav-link ${location.pathname === '/tasks' ? 'active' : ''}`}
            >
              Tasks
            </Link>
            <Link
              to="/analytics"
              className={`nav-link ${location.pathname === '/analytics' ? 'active' : ''}`}
            >
              Analytics
            </Link>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
            <span style={{ color: '#6b7280' }}>
              {user.name} ({user.role})
            </span>
            <button onClick={handleLogout} className="btn btn-secondary">
              Logout
            </button>
          </div>
        </nav>
      </header>
      <div className="container">
        <Outlet />
      </div>
    </div>
  );
}

export default Layout;
