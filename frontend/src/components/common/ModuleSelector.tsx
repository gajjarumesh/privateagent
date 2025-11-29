import React from 'react';
import { ModuleType } from '../../types';
import './ModuleSelector.css';

interface ModuleSelectorProps {
  currentModule: ModuleType;
  onModuleChange: (module: ModuleType) => void;
}

interface ModuleConfig {
  id: ModuleType;
  name: string;
  icon: string;
  description: string;
}

const modules: ModuleConfig[] = [
  {
    id: 'general',
    name: 'General',
    icon: '💬',
    description: 'General AI assistance',
  },
  {
    id: 'developer',
    name: 'Developer',
    icon: '👨‍💻',
    description: 'Code & debugging',
  },
  {
    id: 'trading',
    name: 'Trading',
    icon: '📈',
    description: 'Market analysis',
  },
  {
    id: 'research',
    name: 'Research',
    icon: '🔬',
    description: 'Search & RAG',
  },
];

/**
 * Module selector component
 */
function ModuleSelector({ currentModule, onModuleChange }: ModuleSelectorProps) {
  return (
    <div className="module-selector">
      {modules.map((module) => (
        <button
          key={module.id}
          className={`module-btn ${currentModule === module.id ? 'active' : ''}`}
          onClick={() => onModuleChange(module.id)}
        >
          <span className="module-icon">{module.icon}</span>
          <div className="module-info">
            <span className="module-name">{module.name}</span>
            <span className="module-desc">{module.description}</span>
          </div>
        </button>
      ))}
    </div>
  );
}

export default ModuleSelector;
