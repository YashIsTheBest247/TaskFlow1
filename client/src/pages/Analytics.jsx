import { useState, useEffect } from 'react';
import { analyticsAPI } from '../api';

function Analytics() {
  const [summary, setSummary] = useState(null);
  const [overTime, setOverTime] = useState(null);
  const [productivity, setProductivity] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [timeView, setTimeView] = useState('daily');

  useEffect(() => {
    fetchAnalytics();
  }, []);

  const fetchAnalytics = async () => {
    try {
      setLoading(true);
      const [summaryRes, overTimeRes, productivityRes] = await Promise.all([
        analyticsAPI.getSummary(),
        analyticsAPI.getOverTime(),
        analyticsAPI.getProductivity(),
      ]);

      setSummary(summaryRes.data);
      setOverTime(overTimeRes.data);
      setProductivity(productivityRes.data);
      setError(null);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to fetch analytics');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="loading">Loading analytics...</div>;
  }

  if (error) {
    return <div className="error">{error}</div>;
  }

  const getTimeData = () => {
    if (!overTime) return [];
    return overTime[timeView] || [];
  };

  return (
    <div className="analytics-page">
      <h1>Analytics Dashboard</h1>

      {summary && (
        <div className="analytics-summary">
          <div className="stat-card">
            <h3>Total Tasks</h3>
            <p className="stat-value">{summary.total_tasks}</p>
          </div>
          <div className="stat-card">
            <h3>Completed</h3>
            <p className="stat-value">{summary.completed_tasks}</p>
          </div>
          <div className="stat-card">
            <h3>Pending</h3>
            <p className="stat-value">{summary.pending_tasks}</p>
          </div>
          <div className="stat-card">
            <h3>Archived</h3>
            <p className="stat-value">{summary.archived_tasks}</p>
          </div>
          <div className="stat-card">
            <h3>Completion Rate</h3>
            <p className="stat-value">{summary.completion_percentage}%</p>
          </div>
        </div>
      )}

      {productivity && (
        <div className="productivity-section">
          <h2>Productivity Insights</h2>
          <div className="productivity-cards">
            <div className="stat-card">
              <h3>Productivity Score</h3>
              <p className="stat-value large">{productivity.productivity_score}</p>
              <p className="stat-label">out of 100</p>
            </div>
            <div className="stat-card">
              <h3>Most Productive Day</h3>
              <p className="stat-value">{productivity.most_productive_day}</p>
            </div>
            <div className="stat-card">
              <h3>Avg Completion Time</h3>
              <p className="stat-value">{productivity.average_completion_time_days}</p>
              <p className="stat-label">days</p>
            </div>
          </div>

          <div className="priority-distribution">
            <h3>Priority Distribution</h3>
            <div className="priority-bars">
              {Object.entries(productivity.priority_distribution).map(([priority, count]) => (
                <div key={priority} className="priority-bar-item">
                  <span className="priority-label">{priority}</span>
                  <div className="priority-bar-container">
                    <div
                      className={`priority-bar priority-${priority}`}
                      style={{ width: `${(count / summary.total_tasks) * 100}%` }}
                    />
                  </div>
                  <span className="priority-count">{count}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {overTime && (
        <div className="over-time-section">
          <h2>Tasks Completed Over Time</h2>
          <div className="time-view-selector">
            <button
              className={timeView === 'daily' ? 'active' : ''}
              onClick={() => setTimeView('daily')}
            >
              Daily (30 days)
            </button>
            <button
              className={timeView === 'weekly' ? 'active' : ''}
              onClick={() => setTimeView('weekly')}
            >
              Weekly (12 weeks)
            </button>
            <button
              className={timeView === 'monthly' ? 'active' : ''}
              onClick={() => setTimeView('monthly')}
            >
              Monthly (12 months)
            </button>
          </div>

          <div className="time-chart">
            {getTimeData().length > 0 ? (
              <div className="chart-bars">
                {getTimeData().map((item, index) => {
                  const label = item.date || item.week || item.month;
                  const maxCount = Math.max(...getTimeData().map(d => d.count), 1);
                  const height = (item.count / maxCount) * 200;
                  
                  return (
                    <div key={index} className="chart-bar-item">
                      <div className="chart-bar-container">
                        <div
                          className="chart-bar"
                          style={{ height: `${height}px` }}
                          title={`${label}: ${item.count} tasks`}
                        />
                      </div>
                      <span className="chart-label">{label}</span>
                      <span className="chart-count">{item.count}</span>
                    </div>
                  );
                })}
              </div>
            ) : (
              <p className="no-data">No completion data available for this period</p>
            )}
          </div>
        </div>
      )}

      <style jsx>{`
        .analytics-page {
          padding: 20px;
        }

        h1 {
          margin-bottom: 30px;
          color: #333;
        }

        h2 {
          margin: 30px 0 20px;
          color: #555;
        }

        .analytics-summary {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
          gap: 20px;
          margin-bottom: 40px;
        }

        .stat-card {
          background: white;
          padding: 20px;
          border-radius: 8px;
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }

        .stat-card h3 {
          margin: 0 0 10px;
          font-size: 14px;
          color: #666;
          text-transform: uppercase;
        }

        .stat-value {
          margin: 0;
          font-size: 32px;
          font-weight: bold;
          color: #2563eb;
        }

        .stat-value.large {
          font-size: 48px;
        }

        .stat-label {
          margin: 5px 0 0;
          font-size: 12px;
          color: #999;
        }

        .productivity-section {
          margin-bottom: 40px;
        }

        .productivity-cards {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
          gap: 20px;
          margin-bottom: 30px;
        }

        .priority-distribution {
          background: white;
          padding: 20px;
          border-radius: 8px;
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }

        .priority-bars {
          margin-top: 20px;
        }

        .priority-bar-item {
          display: flex;
          align-items: center;
          gap: 10px;
          margin-bottom: 15px;
        }

        .priority-label {
          width: 80px;
          font-weight: 500;
          text-transform: capitalize;
        }

        .priority-bar-container {
          flex: 1;
          height: 30px;
          background: #f0f0f0;
          border-radius: 4px;
          overflow: hidden;
        }

        .priority-bar {
          height: 100%;
          transition: width 0.3s ease;
        }

        .priority-bar.priority-low {
          background: #10b981;
        }

        .priority-bar.priority-normal {
          background: #3b82f6;
        }

        .priority-bar.priority-medium {
          background: #f59e0b;
        }

        .priority-bar.priority-high {
          background: #ef4444;
        }

        .priority-count {
          width: 40px;
          text-align: right;
          font-weight: 500;
        }

        .over-time-section {
          background: white;
          padding: 20px;
          border-radius: 8px;
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }

        .time-view-selector {
          display: flex;
          gap: 10px;
          margin-bottom: 20px;
        }

        .time-view-selector button {
          padding: 8px 16px;
          border: 1px solid #ddd;
          background: white;
          border-radius: 4px;
          cursor: pointer;
          transition: all 0.2s;
        }

        .time-view-selector button:hover {
          background: #f5f5f5;
        }

        .time-view-selector button.active {
          background: #2563eb;
          color: white;
          border-color: #2563eb;
        }

        .time-chart {
          min-height: 300px;
        }

        .chart-bars {
          display: flex;
          gap: 10px;
          align-items: flex-end;
          overflow-x: auto;
          padding: 20px 0;
        }

        .chart-bar-item {
          display: flex;
          flex-direction: column;
          align-items: center;
          min-width: 60px;
        }

        .chart-bar-container {
          height: 200px;
          display: flex;
          align-items: flex-end;
          margin-bottom: 5px;
        }

        .chart-bar {
          width: 40px;
          background: #2563eb;
          border-radius: 4px 4px 0 0;
          transition: all 0.3s ease;
        }

        .chart-bar:hover {
          background: #1d4ed8;
        }

        .chart-label {
          font-size: 10px;
          color: #666;
          text-align: center;
          margin-bottom: 2px;
          max-width: 60px;
          overflow: hidden;
          text-overflow: ellipsis;
        }

        .chart-count {
          font-size: 12px;
          font-weight: 500;
          color: #333;
        }

        .no-data {
          text-align: center;
          color: #999;
          padding: 40px;
        }

        .loading, .error {
          text-align: center;
          padding: 40px;
          font-size: 18px;
        }

        .error {
          color: #ef4444;
        }
      `}</style>
    </div>
  );
}

export default Analytics;
