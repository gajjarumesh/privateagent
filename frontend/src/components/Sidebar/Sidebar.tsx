import React from 'react';
import { ModuleType } from '../../types';
import ModuleSelector from '../common/ModuleSelector';
import './Sidebar.css';

interface SidebarProps {
  currentModule: ModuleType;
  onModuleChange: (module: ModuleType) => void;
  onDashboardClick: () => void;
  onNewChat: () => void;
}

/**
 * Sidebar component with navigation and module selection
 */
function Sidebar({ currentModule, onModuleChange, onDashboardClick, onNewChat }: SidebarProps) {
  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <h1 className="logo">
          <span className="logo-icon">🤖</span>
          <span className="logo-text">ARIA</span>
        </h1>
        <p className="logo-subtitle">AI Agent</p>
      </div>

      <div className="sidebar-content">
        <button className="new-chat-btn" onClick={onNewChat}>
          <span className="btn-icon">+</span>
          New Chat
        </button>

        <div className="module-section">
          <h3 className="section-title">Modules</h3>
          <ModuleSelector
            currentModule={currentModule}
            onModuleChange={onModuleChange}
          />
        </div>
      </div>

      <div className="sidebar-footer">
        <button className="dashboard-btn" onClick={onDashboardClick}>
          <span className="btn-icon">📊</span>
          Dashboard
        </button>
        <div className="status-indicator">
          <span className="status-dot"></span>
          <span className="status-text">Local AI Active</span>
        </div>
      </div>
    </aside>
  );
}

export default Sidebar;
