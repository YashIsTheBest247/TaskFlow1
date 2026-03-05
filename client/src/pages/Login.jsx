import { useState } from 'react';
import { authAPI } from '../api';
import { Link } from 'react-router-dom';

function Login({ onLogin }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await authAPI.login({ email, password });
      onLogin(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Login failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ 
      minHeight: '100vh', 
      display: 'flex', 
      alignItems: 'center', 
      justifyContent: 'center',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
    }}>
      <div className="card" style={{ maxWidth: '400px', width: '90%' }}>
        <h1 style={{ textAlign: 'center', marginBottom: '30px', color: '#111827' }}>
          TaskFlow
        </h1>
        <h2 style={{ textAlign: 'center', marginBottom: '20px', color: '#6b7280', fontSize: '18px' }}>
          Sign in to your account
        </h2>
        
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="label">Email Address</label>
            <input
              type="email"
              className="input"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@example.com"
              required
            />
          </div>

          <div className="form-group">
            <label className="label">Password</label>
            <input
              type="password"
              className="input"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              required
            />
          </div>

          {error && <div className="error">{error}</div>}

          <button
            type="submit"
            className="btn btn-primary"
            style={{ width: '100%', marginTop: '20px' }}
            disabled={loading}
          >
            {loading ? 'Signing in...' : 'Sign in'}
          </button>
        </form>

        <div style={{ marginTop: '20px', padding: '15px', background: '#f3f4f6', borderRadius: '4px' }}>
          <p style={{ fontSize: '12px', color: '#6b7280', marginBottom: '10px' }}>
            <strong>Demo Credentials:</strong>
          </p>
          <p style={{ fontSize: '12px', color: '#374151' }}>
            Email: admin@taskflow.com<br />
            Password: admin123
          </p>
        </div>

        <div style={{ marginTop: '15px', textAlign: 'center' }}>
          <p style={{ fontSize: '14px', color: '#6b7280' }}>
            Don't have an account?{' '}
            <Link to="/signup" style={{ color: '#2563eb', textDecoration: 'none', fontWeight: '500' }}>
              Sign up
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}

export default Login;
