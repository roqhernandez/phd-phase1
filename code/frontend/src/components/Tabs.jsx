import { useState } from 'react';

export default function Tabs({ children, defaultTab = 0 }) {
  const [activeTab, setActiveTab] = useState(defaultTab);
  
  const tabs = children.map((child, index) => ({
    label: child.props.label,
    content: child,
    index
  }));

  return (
    <div className="tabs-container">
      <div className="tabs-header">
        {tabs.map((tab) => (
          <button
            key={tab.index}
            className={`tab-button ${activeTab === tab.index ? 'active' : ''}`}
            onClick={() => setActiveTab(tab.index)}
          >
            {tab.label}
          </button>
        ))}
      </div>
      <div className="tabs-content">
        {tabs[activeTab]?.content}
      </div>
    </div>
  );
}

export function Tab({ children }) {
  return <div>{children}</div>;
}

