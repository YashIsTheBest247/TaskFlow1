import { useState, useEffect } from 'react';
import { taskAPI } from '../api';
import { Link } from 'react-router-dom';

function Dashboard() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchDashboard();
  }, []);

  const fetchDashboard = async () => {
    try {
      const response = await taskAPI.getDashboard();
      setStats(response.data);
    } catch (err) {
      setError('Failed to load dashboard data');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="loading">Loading dashboard...</div>;
  if (error) return <div className="error">{error}</div>;
  if (!stats) return null;

  return (
    <div>
      <h1 style={{ marginBottom: '30px', color: '#111827' }}>Dashboard</h1>

      {/* Stats Grid */}
      <div className="grid">
        <div className="stat-card">
          <h3>TOTAL TASKS</h3>
          <div className="number">{stats.totalTasks}</div>
        </div>
        <div className="stat-card">
          <h3>TODO</h3>
          <div className="number" style={{ color: '#2563eb' }}>
            {stats.tasks.todo || 0}
          </div>
        </div>
        <div className="stat-card">
          <h3>IN PROGRESS</h3>
          <div className="number" style={{ color: '#f59e0b' }}>
            {stats.tasks['in progress'] || 0}
          </div>
        </div>
        <div className="stat-card">
          <h3>COMPLETED</h3>
          <div className="number" style={{ color: '#10b981' }}>
            {stats.tasks.completed || 0}
          </div>
        </div>
      </div>

      {/* Priority Distribution */}
      <div className="card">
        <h2 style={{ marginBottom: '20px' }}>Tasks by Priority</h2>
        <div className="grid">
          <div>
            <div style={{ fontSize: '14px', color: '#6b7280', marginBottom: '5px' }}>High</div>
            <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#dc2626' }}>
              {stats.graphData.high || 0}
            </div>
          </div>
          <div>
            <div style={{ fontSize: '14px', color: '#6b7280', marginBottom: '5px' }}>Medium</div>
            <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#f59e0b' }}>
              {stats.graphData.medium || 0}
            </div>
          </div>
          <div>
            <div style={{ fontSize: '14px', color: '#6b7280', marginBottom: '5px' }}>Normal</div>
            <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#3b82f6' }}>
              {stats.graphData.normal || 0}
            </div>
          </div>
          <div>
            <div style={{ fontSize: '14px', color: '#6b7280', marginBottom: '5px' }}>Low</div>
            <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#10b981' }}>
              {stats.graphData.low || 0}
            </div>
          </div>
        </div>
      </div>

      {/* Recent Tasks */}
      <div className="card">
        <h2 style={{ marginBottom: '20px' }}>Recent Tasks</h2>
        {stats.last10Task && stats.last10Task.length > 0 ? (
          <ul className="task-list">
            {stats.last10Task.map((task) => (
              <li key={task._id} className={`task-item ${task.priority}`}>
                <Link to={`/tasks/${task._id}`} style={{ textDecoration: 'none', color: 'inherit' }}>
                  <div className="task-header">
                    <div className="task-title">{task.title}</div>
                    <div>
                      <span className={`badge badge-${task.priority}`}>
                        {task.priority}
                      </span>
                      {' '}
                      <span className={`badge badge-${task.stage.replace(' ', '')}`}>
                        {task.stage}
                      </span>
                    </div>
                  </div>
                  <div style={{ fontSize: '14px', color: '#6b7280' }}>
                    Team: {task.team.map(m => m.name).join(', ') || 'No team assigned'}
                  </div>
                </Link>
              </li>
            ))}
          </ul>
        ) : (
          <p style={{ color: '#6b7280' }}>No tasks yet</p>
        )}
      </div>
    </div>
  );
}

export default Dashboard;
