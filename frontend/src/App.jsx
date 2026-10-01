import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import Header from './components/Header';

import Overview from './pages/Overview';
import AgentSimulator from './pages/AgentSimulator';
import Agents from './pages/Agents';
import ToolsPermissions from './pages/ToolsPermissions';
import SecurityGateway from './pages/SecurityGateway';
import Approvals from './pages/Approvals';
import Policies from './pages/Policies';
import VerificationEngine from './pages/VerificationEngine';
import SecurityEvents from './pages/SecurityEvents';
import AuditTrail from './pages/AuditTrail';

export default function App() {
  return (
    <Router>
      <div className="flex h-screen bg-[#FAFAFA] text-slate-900 overflow-hidden font-sans rillet-grid-bg">
        {/* Sidebar */}
        <Sidebar />

        {/* Main Content Workspace */}
        <div className="flex-1 flex flex-col min-w-0 overflow-y-auto">
          <Header />
          <main className="flex-1 bg-[#FAFAFA]/90">
            <Routes>
              <Route path="/" element={<Overview />} />
              <Route path="/simulator" element={<AgentSimulator />} />
              <Route path="/agents" element={<Agents />} />
              <Route path="/permissions" element={<ToolsPermissions />} />
              <Route path="/gateway" element={<SecurityGateway />} />
              <Route path="/approvals" element={<Approvals />} />
              <Route path="/policies" element={<Policies />} />
              <Route path="/verification" element={<VerificationEngine />} />
              <Route path="/events" element={<SecurityEvents />} />
              <Route path="/audit" element={<AuditTrail />} />
            </Routes>
          </main>
        </div>
      </div>
    </Router>
  );
}
