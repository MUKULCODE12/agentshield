import React from 'react';
import { Building2, Shield, Lock } from 'lucide-react';

export default function Header() {
  return (
    <header className="h-16 bg-white/90 backdrop-blur-md border-b border-slate-200 px-6 flex items-center justify-between sticky top-0 z-20">
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-slate-50 border border-slate-200 text-xs text-slate-700 font-mono">
          <Building2 className="w-3.5 h-3.5 text-[#53389E]" />
          <span className="font-bold text-[#1A103C]">Acme Corp Enterprise</span>
          <span className="text-slate-300">|</span>
          <span className="text-emerald-600 text-[11px]">Org: org_acme_891</span>
        </div>
      </div>

      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-[#F4F0FF] border border-[#D8C7FF] text-[#53389E] text-xs font-mono font-semibold">
          <Shield className="w-3.5 h-3.5" />
          RAG Policy Guard: ACTIVE
        </div>

        <div className="flex items-center gap-3 pl-4 border-l border-slate-200">
          <div className="w-8 h-8 rounded-full bg-[#1A103C] flex items-center justify-center text-white font-mono font-bold text-xs shadow-xs">
            SA
          </div>
          <div className="text-left hidden md:block">
            <p className="text-xs font-bold text-[#1A103C]">Security Admin</p>
            <p className="text-[10px] text-slate-500 font-mono">admin@agentshield.com</p>
          </div>
        </div>
      </div>
    </header>
  );
}
