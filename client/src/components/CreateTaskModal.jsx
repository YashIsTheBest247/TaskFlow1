import { useState, useEffect } from 'react';
import { taskAPI, userAPI } from '../api';

function CreateTaskModal({ onClose, onSuccess }) {
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    priority: 'normal',
    stage: 'todo',
    team: [],
    date: '',
  });
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    try {
      const response = await userAPI.getTeam();
      setUsers(response.data || []);
    } catch (err) {
      console.error('Failed to fetch users:', err);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await taskAPI.create(formData);
      onSuccess();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create task');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleTeamChange = (e) => {
    const options = e.target.options;
    const selected = [];
    for (let i = 0; i < options.length; i++) {
      if (options[i].selected) {
        selected.push(parseInt(options[i].value));
      }
    }
    setFormData(prev => ({ ...prev, team: selected }));
  };

  return (
    <div className="modal" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2 className="modal-title">Create New Task</h2>
          <button onClick={onClose} className="close-btn">&times;</button>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="label">Title *</label>
            <input
              type="text"
              name="title"
              className="input"
              value={formData.title}
              onChange={handleChange}
              required
            />
          </div>

          <div className="form-group">
            <label className="label">Description</label>
            <textarea
              name="description"
              className="input"
              value={formData.description}
              onChange={handleChange}
              rows="4"
            />
          </div>

          <div className="form-group">
            <label className="label">Priority</label>
            <select
              name="priority"
              className="input"
              value={formData.priority}
              onChange={handleChange}
            >
              <option value="low">Low</option>
              <option value="normal">Normal</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
            </select>
          </div>

          <div className="form-group">
            <label className="label">Stage</label>
            <select
              name="stage"
              className="input"
              value={formData.stage}
              onChange={handleChange}
            >
              <option value="todo">Todo</option>
              <option value="in progress">In Progress</option>
              <option value="completed">Completed</option>
            </select>
          </div>

          <div className="form-group">
            <label className="label">Due Date</label>
            <input
              type="date"
              name="date"
              className="input"
              value={formData.date}
              onChange={handleChange}
            />
          </div>

          <div className="form-group">
            <label className="label">Team Members (Hold Ctrl/Cmd to select multiple)</label>
            <select
              multiple
              className="input"
              value={formData.team}
              onChange={handleTeamChange}
              style={{ minHeight: '100px' }}
            >
              {users.map((user) => (
                <option key={user.id} value={user.id}>
                  {user.name} ({user.role})
                </option>
              ))}
            </select>
          </div>

          {error && <div className="error">{error}</div>}

          <div className="flex flex-end mt-20">
            <button
              type="button"
              onClick={onClose}
              className="btn btn-secondary"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="btn btn-primary"
              disabled={loading}
            >
              {loading ? 'Creating...' : 'Create Task'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default CreateTaskModal;
