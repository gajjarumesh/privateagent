import React, { useState } from 'react';
import { ModuleType } from './types';
import Sidebar from './components/Sidebar/Sidebar';
import ChatWindow from './components/Chat/ChatWindow';
import Dashboard from './components/Dashboard/Dashboard';
import './styles/globals.css';

/**
 * Main Application Component
 */
function App() {
  const [currentModule, setCurrentModule] = useState<ModuleType>('general');
  const [showDashboard, setShowDashboard] = useState(false);

  const handleModuleChange = (module: ModuleType) => {
    setCurrentModule(module);
    setShowDashboard(false);
  };

  const handleDashboardClick = () => {
    setShowDashboard(true);
  };

  const handleNewChat = () => {
    setShowDashboard(false);
    // ChatWindow will handle resetting the chat
    window.dispatchEvent(new CustomEvent('newChat'));
  };

  return (
    <div className="app-container">
      <Sidebar
        currentModule={currentModule}
        onModuleChange={handleModuleChange}
        onDashboardClick={handleDashboardClick}
        onNewChat={handleNewChat}
      />
      <main className="main-content">
        {showDashboard ? (
          <Dashboard />
        ) : (
          <ChatWindow module={currentModule} />
        )}
      </main>
    </div>
  );
}

export default App;
