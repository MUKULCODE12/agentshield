import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { Sliders, Wrench, Shield, Check, X, Lock, Plus } from 'lucide-react';

export default function ToolsPermissions() {
  const [matrix, setMatrix] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showToolModal, setShowToolModal] = useState(false);

  const [toolForm, setToolForm] = useState({
    name: '',
    display_name: '',
    category: 'General',
    description: '',
    is_sensitive: false
  });

  useEffect(() => {
    loadMatrix();
  }, []);

  const loadMatrix = async () => {
    try {
      const data = await api.getPermissionMatrix();
      setMatrix(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleToggleAllowed = async (agentId, toolId, currentVal) => {
    try {
      await api.updatePermission({
        agent_id: agentId,
        tool_id: toolId,
        is_allowed: !currentVal
      });
      loadMatrix();
    } catch (err) {
      alert(err.message);
    }
  };

  const handleRegisterTool = async (e) => {
    e.preventDefault();
    try {
      await api.registerTool(toolForm);
      setShowToolModal(false);
      setToolForm({ name: '', display_name: '', category: 'General', description: '', is_sensitive: false });
      loadMatrix();
    } catch (err) {
      alert(err.message);
    }
  };

  if (loading) return <div className="p-8 text-center text-slate-700 font-mono text-xs">Loading Tool Authorization Matrix...</div>;

  return (
    <div className="p-8 space-y-8 max-w-7xl mx-auto">
      <div className="flex items-center justify-between border-b border-slate-200 pb-6 bg-white p-6 rounded-2xl border shadow-xs">
        <div>
          <h1 className="text-2xl font-mono font-bold text-[#1A103C] tracking-tight flex items-center gap-2">
            <Sliders className="w-6 h-6 text-[#53389E]" />
            Tool Authorization Matrix (Phase 3)
          </h1>
          <p className="text-xs text-slate-700 font-medium mt-1">
            Enforce granular tool access control, sensitive action privileges, and monetary limit safeguards per AI agent.
          </p>
        </div>
        <button
          onClick={() => setShowToolModal(true)}
          className="px-5 py-2.5 bg-[#53389E] hover:bg-[#432A85] text-white rounded-xl text-xs font-display font-bold flex items-center gap-2 transition shadow-xs"
        >
          <Plus className="w-4 h-4" />
          Register New Tool
        </button>
      </div>

      {/* Permission Grid per Agent */}
      <div className="space-y-6">
        {matrix.map((agentGroup) => (
          <div key={agentGroup.agent_id} className="rounded-2xl bg-white border border-slate-200 overflow-hidden shadow-xs">
            <div className="p-4 bg-slate-50 border-b border-slate-200 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <span className="font-mono text-[#53389E] font-bold text-sm">{agentGroup.agent_key}</span>
                <span className="text-[#1A103C] font-semibold text-sm">({agentGroup.agent_name})</span>
                <span className="text-xs text-slate-600 font-medium">Owner: {agentGroup.owner}</span>
              </div>
              <span className="px-3 py-1 rounded-full text-[10px] font-mono bg-[#F4F0FF] text-[#53389E] border border-[#D8C7FF] font-bold">
                {agentGroup.environment}
              </span>
            </div>

            <div className="p-6 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
              {agentGroup.permissions.map((perm) => (
                <div
                  key={perm.tool_id}
                  className={`p-5 rounded-2xl border transition space-y-3 ${
                    perm.is_allowed
                      ? 'bg-white border-slate-200 hover:border-[#53389E]'
                      : 'bg-rose-50 border-rose-200'
                  }`}
                >
                  <div className="flex items-start justify-between">
                    <div>
                      <div className="font-mono text-xs font-bold text-[#1A103C] flex items-center gap-1.5">
                        {perm.tool_name}
                        {perm.is_sensitive && (
                          <span className="px-2 py-0.5 rounded-full text-[9px] font-bold bg-rose-100 text-rose-800 border border-rose-300">
                            SENSITIVE
                          </span>
                        )}
                      </div>
                      <div className="text-[11px] font-medium text-slate-700 mt-0.5">{perm.tool_display}</div>
                    </div>

                    <button
                      onClick={() => handleToggleAllowed(agentGroup.agent_id, perm.tool_id, perm.is_allowed)}
                      className={`px-3 py-1 rounded-full text-xs font-bold font-mono transition flex items-center gap-1 ${
                        perm.is_allowed
                          ? 'bg-emerald-100 text-emerald-800 border border-emerald-300'
                          : 'bg-rose-100 text-rose-800 border border-rose-300'
                      }`}
                    >
                      {perm.is_allowed ? <Check className="w-3.5 h-3.5" /> : <X className="w-3.5 h-3.5" />}
                      {perm.is_allowed ? 'ALLOWED' : 'DENIED'}
                    </button>
                  </div>

                  {/* Limits and Details */}
                  {perm.is_allowed && (
                    <div className="pt-3 border-t border-slate-200 text-[11px] space-y-1 text-slate-700 font-medium">
                      <div className="flex justify-between">
                        <span>Privileges:</span>
                        <span className="text-[#1A103C] font-mono font-bold">
                          {perm.can_read ? 'READ ' : ''}
                          {perm.can_write ? '+ WRITE' : ''}
                        </span>
                      </div>
                      {perm.max_amount_limit && (
                        <div className="flex justify-between">
                          <span>Max Monetary Limit:</span>
                          <span className="text-amber-800 font-mono font-bold">
                            ₹{perm.max_amount_limit.toLocaleString()}
                          </span>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>

      {/* Modal to Register Tool */}
      {showToolModal && (
        <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4 z-50">
          <div className="bg-white border border-slate-200 rounded-2xl max-w-md w-full p-6 space-y-4 shadow-xl">
            <h3 className="text-lg font-mono font-bold text-[#1A103C] flex items-center gap-2">
              <Wrench className="w-5 h-5 text-[#53389E]" />
              Register New Business Tool
            </h3>
            <form onSubmit={handleRegisterTool} className="space-y-3 text-xs">
              <div>
                <label className="block text-slate-700 mb-1 font-semibold">Tool Identifier (Name)</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. process_payout"
                  value={toolForm.name}
                  onChange={(e) => setToolForm({ ...toolForm, name: e.target.value })}
                  className="w-full px-3 py-2 rounded-xl bg-slate-50 border border-slate-300 text-slate-900 focus:outline-none focus:border-[#53389E] font-mono"
                />
              </div>
              <div>
                <label className="block text-slate-700 mb-1 font-semibold">Display Title</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Process Vendor Payout"
                  value={toolForm.display_name}
                  onChange={(e) => setToolForm({ ...toolForm, display_name: e.target.value })}
                  className="w-full px-3 py-2 rounded-xl bg-slate-50 border border-slate-300 text-slate-900 focus:outline-none focus:border-[#53389E]"
                />
              </div>
              <div>
                <label className="block text-slate-700 mb-1 font-semibold">Category</label>
                <select
                  value={toolForm.category}
                  onChange={(e) => setToolForm({ ...toolForm, category: e.target.value })}
                  className="w-full px-3 py-2 rounded-xl bg-slate-50 border border-slate-300 text-slate-900 focus:outline-none focus:border-[#53389E]"
                >
                  <option value="Customer">Customer</option>
                  <option value="Finance">Finance</option>
                  <option value="Communication">Communication</option>
                  <option value="Database">Database</option>
                  <option value="Developer">Developer</option>
                </select>
              </div>
              <div className="flex items-center gap-2 pt-1">
                <input
                  type="checkbox"
                  id="is_sensitive"
                  checked={toolForm.is_sensitive}
                  onChange={(e) => setToolForm({ ...toolForm, is_sensitive: e.target.checked })}
                  className="rounded bg-slate-50 border-slate-300 text-[#53389E]"
                />
                <label htmlFor="is_sensitive" className="text-slate-800 font-semibold cursor-pointer">
                  Classify as Sensitive Tool (Requires write privilege)
                </label>
              </div>
              <div className="flex justify-end gap-2 pt-3">
                <button
                  type="button"
                  onClick={() => setShowToolModal(false)}
                  className="px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-xl font-semibold border border-slate-300"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-[#53389E] hover:bg-[#432A85] text-white rounded-xl font-semibold"
                >
                  Register Tool
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
