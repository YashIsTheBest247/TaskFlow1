import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { taskAPI } from '../api';

function TaskDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [task, setTask] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [activity, setActivity] = useState('');
  const [posting, setPosting] = useState(false);

  useEffect(() => {
    fetchTask();
  }, [id]);

  const fetchTask = async () => {
    try {
      const response = await taskAPI.getById(id);
      setTask(response.data.task);
    } catch (err) {
      setError('Failed to load task');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleStageChange = async (newStage) => {
    try {
      await taskAPI.changeStage(id, newStage);
      fetchTask();
    } catch (err) {
      alert('Failed to update stage');
    }
  };

  const handlePostActivity = async (e) => {
    e.preventDefault();
    if (!activity.trim()) return;

    setPosting(true);
    try {
      await taskAPI.postActivity(id, {
        type: 'comment',
        activity: activity.trim()
      });
      setActivity('');
      fetchTask();
    } catch (err) {
      alert('Failed to post activity');
    } finally {
      setPosting(false);
    }
  };

  const handleDelete = async () => {
    if (!confirm('Are you sure you want to delete this task?')) return;

    try {
      await taskAPI.delete(id, 'delete');
      navigate('/tasks');
    } catch (err) {
      alert('Failed to delete task');
    }
  };

  if (loading) return <div className="loading">Loading task...</div>;
  if (error) return <div className="error">{error}</div>;
  if (!task) return null;

  return (
    <div>
      <button onClick={() => navigate('/tasks')} className="btn btn-secondary" style={{ marginBottom: '20px' }}>
        ← Back to Tasks
      </button>

      <div className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '20px' }}>
          <div>
            <h1 style={{ marginBottom: '10px' }}>{task.title}</h1>
            <div style={{ display: 'flex', gap: '10px' }}>
              <span className={`badge badge-${task.priority}`}>
                {task.priority}
              </span>
              <span className={`badge badge-${task.stage.replace(' ', '')}`}>
                {task.stage}
              </span>
            </div>
          </div>
          <button onClick={handleDelete} className="btn btn-danger">
            Delete Task
          </button>
        </div>

        {task.description && (
          <div style={{ marginBottom: '20px' }}>
            <h3 style={{ marginBottom: '10px', color: '#374151' }}>Description</h3>
            <p style={{ color: '#6b7280', lineHeight: '1.6' }}>{task.description}</p>
          </div>
        )}

        <div style={{ marginBottom: '20px' }}>
          <h3 style={{ marginBottom: '10px', color: '#374151' }}>Change Stage</h3>
          <div style={{ display: 'flex', gap: '10px' }}>
            <button
              onClick={() => handleStageChange('todo')}
              className={`btn ${task.stage === 'todo' ? 'btn-primary' : 'btn-secondary'}`}
            >
              Todo
            </button>
            <button
              onClick={() => handleStageChange('in progress')}
              className={`btn ${task.stage === 'in progress' ? 'btn-primary' : 'btn-secondary'}`}
            >
              In Progress
            </button>
            <button
              onClick={() => handleStageChange('completed')}
              className={`btn ${task.stage === 'completed' ? 'btn-success' : 'btn-secondary'}`}
            >
              Completed
            </button>
          </div>
        </div>

        {task.team && task.team.length > 0 && (
          <div style={{ marginBottom: '20px' }}>
            <h3 style={{ marginBottom: '10px', color: '#374151' }}>Team Members</h3>
            <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
              {task.team.map((member) => (
                <div
                  key={member.id}
                  style={{
                    padding: '8px 16px',
                    background: '#f3f4f6',
                    borderRadius: '20px',
                    fontSize: '14px'
                  }}
                >
                  {member.name} ({member.role})
                </div>
              ))}
            </div>
          </div>
        )}

        {task.subTasks && task.subTasks.length > 0 && (
          <div style={{ marginBottom: '20px' }}>
            <h3 style={{ marginBottom: '10px', color: '#374151' }}>Subtasks</h3>
            <ul style={{ listStyle: 'none' }}>
              {task.subTasks.map((subtask) => (
                <li
                  key={subtask.id}
                  style={{
                    padding: '10px',
                    background: '#f9fafb',
                    marginBottom: '8px',
                    borderRadius: '4px',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '10px'
                  }}
                >
                  <input
                    type="checkbox"
                    checked={subtask.completed}
                    readOnly
                    style={{ cursor: 'pointer' }}
                  />
                  <span style={{ textDecoration: subtask.completed ? 'line-through' : 'none' }}>
                    {subtask.title}
                  </span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {/* Activities */}
      <div className="card">
        <h2 style={{ marginBottom: '20px' }}>Activities</h2>

        <form onSubmit={handlePostActivity} style={{ marginBottom: '20px' }}>
          <textarea
            className="input"
            value={activity}
            onChange={(e) => setActivity(e.target.value)}
            placeholder="Add a comment..."
            rows="3"
          />
          <button
            type="submit"
            className="btn btn-primary"
            disabled={posting || !activity.trim()}
          >
            {posting ? 'Posting...' : 'Post Comment'}
          </button>
        </form>

        {task.activities && task.activities.length > 0 ? (
          <div>
            {task.activities.map((act) => (
              <div
                key={act.id}
                style={{
                  padding: '15px',
                  background: '#f9fafb',
                  borderRadius: '8px',
                  marginBottom: '10px'
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                  <strong style={{ color: '#111827' }}>{act.user.name}</strong>
                  <span style={{ fontSize: '12px', color: '#6b7280' }}>
                    {new Date(act.date).toLocaleString()}
                  </span>
                </div>
                <p style={{ color: '#374151' }}>{act.activity}</p>
              </div>
            ))}
          </div>
        ) : (
          <p style={{ color: '#6b7280' }}>No activities yet</p>
        )}
      </div>
    </div>
  );
}

export default TaskDetail;
