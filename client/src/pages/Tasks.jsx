import { useState, useEffect } from 'react';
import { taskAPI, userAPI } from '../api';
import { Link } from 'react-router-dom';
import CreateTaskModal from '../components/CreateTaskModal';

function Tasks() {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [filter, setFilter] = useState('');
  const [showModal, setShowModal] = useState(false);

  useEffect(() => {
    fetchTasks();
  }, [filter]);

  const fetchTasks = async () => {
    try {
      const response = await taskAPI.getAll({ stage: filter });
      setTasks(response.data.tasks || []);
    } catch (err) {
      setError('Failed to load tasks');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleTaskCreated = () => {
    setShowModal(false);
    fetchTasks();
  };

  if (loading) return <div className="loading">Loading tasks...</div>;

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '30px' }}>
        <h1 style={{ color: '#111827' }}>Tasks</h1>
        <button onClick={() => setShowModal(true)} className="btn btn-primary">
          + Create Task
        </button>
      </div>

      {/* Filters */}
      <div className="card">
        <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
          <button
            onClick={() => setFilter('')}
            className={`btn ${filter === '' ? 'btn-primary' : 'btn-secondary'}`}
          >
            All
          </button>
          <button
            onClick={() => setFilter('todo')}
            className={`btn ${filter === 'todo' ? 'btn-primary' : 'btn-secondary'}`}
          >
            Todo
          </button>
          <button
            onClick={() => setFilter('in progress')}
            className={`btn ${filter === 'in progress' ? 'btn-primary' : 'btn-secondary'}`}
          >
            In Progress
          </button>
          <button
            onClick={() => setFilter('completed')}
            className={`btn ${filter === 'completed' ? 'btn-primary' : 'btn-secondary'}`}
          >
            Completed
          </button>
        </div>
      </div>

      {error && <div className="error">{error}</div>}

      {/* Task List */}
      {tasks.length > 0 ? (
        <ul className="task-list">
          {tasks.map((task) => (
            <li key={task.id} className={`task-item ${task.priority}`}>
              <Link to={`/tasks/${task.id}`} style={{ textDecoration: 'none', color: 'inherit' }}>
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
                {task.description && (
                  <div style={{ fontSize: '14px', color: '#6b7280', marginTop: '8px' }}>
                    {task.description.substring(0, 100)}
                    {task.description.length > 100 ? '...' : ''}
                  </div>
                )}
                <div style={{ fontSize: '14px', color: '#6b7280', marginTop: '8px' }}>
                  Team: {task.team.map(m => m.name).join(', ') || 'No team assigned'}
                </div>
              </Link>
            </li>
          ))}
        </ul>
      ) : (
        <div className="card">
          <p style={{ textAlign: 'center', color: '#6b7280' }}>
            No tasks found. Create your first task!
          </p>
        </div>
      )}

      {showModal && (
        <CreateTaskModal
          onClose={() => setShowModal(false)}
          onSuccess={handleTaskCreated}
        />
      )}
    </div>
  );
}

export default Tasks;
