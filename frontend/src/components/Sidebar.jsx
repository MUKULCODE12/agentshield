import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  ShieldAlert,
  Bot,
  Sliders,
  ShieldCheck,
  FileCheck2,
  AlertTriangle,
  History,
  Grid,
  Sparkles,
  Terminal
} from 'lucide-react';

const navItems = [
  { path: '/', label: 'Overview', icon: Grid },
  { path: '/simulator', label: 'AI Agent Simulator', icon: Sparkles, badge: 'Phase 1' },
  { path: '/agents', label: 'Agent Identities', icon: Bot },
  { path: '/permissions', label: 'Authorization Matrix', icon: Sliders },
  { path: '/gateway', label: 'Gateway Console', icon: Terminal },
  { path: '/approvals', label: 'Human Approvals', icon: ShieldAlert, badge: 'Live Queue' },
  { path: '/policies', label: 'Policy Engine', icon: ShieldCheck },
  { path: '/verification', label: 'Verification Engine', icon: FileCheck2 },
  { path: '/events', label: 'Threat Monitor', icon: AlertTriangle },
  { path: '/audit', label: 'Audit Trail', icon: History },
];

export default function Sidebar() {
  return (
    <aside className="w-64 bg-white border-r border-slate-200 flex flex-col h-screen sticky top-0 shrink-0 select-none rillet-grid-bg">
      {/* Rillet Exact Logo Header (matching user uploaded image) */}
      <div className="p-6 border-b border-slate-200 bg-white/90 backdrop-blur-sm">
        <div className="space-y-1">
          <h1 className="font-mono text-2xl font-bold tracking-tight text-[#1A103C]">
            AgentShield
          </h1>
          <p className="text-[10px] font-mono tracking-widest text-[#53389E] font-semibold uppercase">
            AI-NATIVE ERP SECURITY
          </p>
        </div>
      </div>

      {/* Navigation Links */}
      <nav className="flex-1 p-3 space-y-1 overflow-y-auto">
        {navItems.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                `flex items-center justify-between px-3.5 py-2.5 rounded-lg text-xs font-medium transition-all duration-200 ${
                  isActive
                    ? 'bg-[#F4F0FF] text-[#53389E] border border-[#D8C7FF] shadow-xs font-bold'
                    : 'text-slate-600 hover:text-[#1A103C] hover:bg-slate-100/80'
                }`
              }
            >
              <div className="flex items-center gap-2.5">
                <Icon className="w-4 h-4 text-[#53389E]" />
                <span>{item.label}</span>
              </div>
              {item.badge && (
                <span className="px-2 py-0.5 text-[9px] font-mono font-bold rounded-full bg-[#53389E]/10 text-[#53389E] border border-[#53389E]/20">
                  {item.badge}
                </span>
              )}
            </NavLink>
          );
        })}
      </nav>

      {/* Rillet Engine Footer Card */}
      <div className="p-4 border-t border-slate-200 bg-white/90">
        <div className="p-3 rounded-xl bg-slate-50 border border-slate-200 space-y-2">
          <div className="flex items-center justify-between text-[11px]">
            <span className="flex items-center gap-1.5 font-semibold text-emerald-600">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
              Sentinel Guard Active
            </span>
            <span className="text-[10px] font-mono text-slate-400">v1.0</span>
          </div>
          <p className="text-[10px] text-slate-500 leading-relaxed font-mono">
            Zero-Trust Agent Verification & Policy Enforcement
          </p>
        </div>
      </div>
    </aside>
  );
}
