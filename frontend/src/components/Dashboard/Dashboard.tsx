import React, { useState, useEffect } from 'react';
import { statusApi, feedbackApi } from '../../services/api';
import './Dashboard.css';

interface Stats {
  totalFeedback: number;
  positive: number;
  negative: number;
  neutral: number;
  satisfactionRate: number;
}

/**
 * Dashboard component showing system status and statistics
 */
function Dashboard() {
  const [status, setStatus] = useState<{ status: string; version: string } | null>(null);
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        
        // Fetch status
        try {
          const statusData = await statusApi.getHealth();
          setStatus(statusData);
        } catch {
          setStatus(null);
        }
        
        // Fetch feedback stats
        try {
          const statsData = await feedbackApi.getStats() as unknown as Stats;
          setStats(statsData);
        } catch {
          setStats(null);
        }
        
        setError(null);
      } catch (err) {
        setError('Failed to load dashboard data');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
    
    // Refresh every 30 seconds
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="dashboard loading">
        <div className="loading-spinner">⏳</div>
        <p>Loading dashboard...</p>
      </div>
    );
  }

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <h1>📊 Dashboard</h1>
        <p>System status and statistics</p>
      </header>

      <div className="dashboard-grid">
        {/* System Status */}
        <div className="dashboard-card status-card">
          <h3>System Status</h3>
          <div className={`status-badge ${status ? 'healthy' : 'offline'}`}>
            {status ? '✅ Online' : '❌ Offline'}
          </div>
          {status && (
            <div className="status-details">
              <p><strong>Version:</strong> {status.version}</p>
              <p><strong>Status:</strong> {status.status}</p>
            </div>
          )}
          {!status && (
            <p className="status-error">
              Unable to connect to backend. Make sure the server is running.
            </p>
          )}
        </div>

        {/* LLM Status */}
        <div className="dashboard-card llm-card">
          <h3>🤖 Local LLM</h3>
          <div className="llm-info">
            <p><strong>Engine:</strong> Ollama</p>
            <p><strong>Model:</strong> Mistral 7B (Q4)</p>
            <p><strong>Type:</strong> Local Inference</p>
          </div>
          <div className="privacy-badge">
            🔒 100% Local - No External AI APIs
          </div>
        </div>

        {/* Feedback Stats */}
        <div className="dashboard-card stats-card">
          <h3>📈 Feedback Statistics</h3>
          {stats ? (
            <div className="stats-grid">
              <div className="stat">
                <span className="stat-value">{stats.totalFeedback || 0}</span>
                <span className="stat-label">Total Feedback</span>
              </div>
              <div className="stat positive">
                <span className="stat-value">👍 {stats.positive || 0}</span>
                <span className="stat-label">Positive</span>
              </div>
              <div className="stat negative">
                <span className="stat-value">👎 {stats.negative || 0}</span>
                <span className="stat-label">Negative</span>
              </div>
              <div className="stat">
                <span className="stat-value">{(stats.satisfactionRate || 0).toFixed(1)}%</span>
                <span className="stat-label">Satisfaction Rate</span>
              </div>
            </div>
          ) : (
            <p className="no-stats">No feedback data available yet.</p>
          )}
        </div>

        {/* Available Modules */}
        <div className="dashboard-card modules-card">
          <h3>🧩 Available Modules</h3>
          <div className="modules-list">
            <div className="module-item">
              <span className="module-icon">👨‍💻</span>
              <div>
                <strong>Developer Assistant</strong>
                <p>Code generation, debugging, best practices</p>
              </div>
            </div>
            <div className="module-item">
              <span className="module-icon">📈</span>
              <div>
                <strong>Trading Analyst</strong>
                <p>Technical analysis, indicators, market data</p>
              </div>
            </div>
            <div className="module-item">
              <span className="module-icon">🔬</span>
              <div>
                <strong>Research Engine</strong>
                <p>Web search, document analysis, RAG</p>
              </div>
            </div>
          </div>
        </div>

        {/* Security Info */}
        <div className="dashboard-card security-card">
          <h3>🔐 Security Features</h3>
          <ul className="security-list">
            <li>✅ All data stays local</li>
            <li>✅ No external AI API calls</li>
            <li>✅ Encrypted sensitive data</li>
            <li>✅ Input sanitization</li>
            <li>✅ Rate limiting enabled</li>
            <li>✅ Audit logging active</li>
          </ul>
        </div>

        {/* Quick Tips */}
        <div className="dashboard-card tips-card">
          <h3>💡 Quick Tips</h3>
          <ul className="tips-list">
            <li>Switch modules using the sidebar for specialized assistance</li>
            <li>Use 👍/👎 to help ARIA learn your preferences</li>
            <li>Trading analysis is for educational purposes only</li>
            <li>Upload documents for research via the Research module</li>
          </ul>
        </div>
      </div>

      {error && (
        <div className="dashboard-error">
          ⚠️ {error}
        </div>
      )}
    </div>
  );
}

export default Dashboard;
