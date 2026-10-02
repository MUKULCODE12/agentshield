import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { ShieldCheck, Plus, Check, X, Shield, Filter } from 'lucide-react';

export default function Policies() {
  const [policies, setPolicies] = useState([
    { id: 1, title: 'Max Refund Threshold Guard', category: 'Financial', description: 'Escalates refunds exceeding ₹50,000 for human security officer review.', rule_type: 'THRESHOLD', content: '50000', action_on_trigger: 'ESCALATE', risk_score_weight: 40, is_active: true, version: 1 },
    { id: 2, title: 'PII Exposure & Exfiltration Prevention', category: 'Privacy', description: 'Blocks tool executions attempting to dump or export raw customer SSN, credit cards, or passwords.', rule_type: 'KEYWORDS', content: 'ssn,credit_card,password,drop table', action_on_trigger: 'BLOCK', risk_score_weight: 90, is_active: true, version: 1 },
    { id: 3, title: 'System Mutation Rate Limiting', category: 'Operational', description: 'Requires approval for high-frequency bulk file modification tools.', rule_type: 'RATE_LIMIT', content: '10/min', action_on_trigger: 'ESCALATE', risk_score_weight: 25, is_active: true, version: 1 }
  ]);
  const [loading, setLoading] = useState(false);
  const [showCreateModal, setShowCreateModal] = useState(false);

  const [form, setForm] = useState({
    title: '',
    category: 'Security',
    description: '',
    rule_type: 'KEYWORDS',
    content: '',
    action_on_trigger: 'BLOCK',
    risk_score_weight: 30
  });

  useEffect(() => {
    loadPolicies();
  }, []);

  const loadPolicies = async () => {
    try {
      const data = await api.getPolicies();
      if (Array.isArray(data) && data.length > 0) {
        setPolicies(data);
      }
    } catch (err) {
      console.warn("Policies API fetch note:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleTogglePolicy = async (id) => {
    // Optimistic UI update
    setPolicies(prev => prev.map(p => p.id === id ? { ...p, is_active: !p.is_active } : p));
    try {
      await api.togglePolicy(id);
      loadPolicies();
    } catch (err) {
      console.warn("Policy toggled locally:", err);
    }
  };

  const handleCreatePolicy = async (e) => {
    e.preventDefault();
    try {
      await api.createPolicy(form);
      setShowCreateModal(false);
      setForm({ title: '', category: 'Security', description: '', rule_type: 'KEYWORDS', content: '', action_on_trigger: 'BLOCK', risk_score_weight: 30 });
      loadPolicies();
    } catch (err) {
      alert(err.message);
    }
  };

  return (
    <div className="p-8 space-y-8 max-w-7xl mx-auto">
      <div className="flex items-center justify-between border-b border-slate-200 pb-6 bg-white p-6 rounded-2xl border shadow-xs">
        <div>
          <h1 className="text-2xl font-mono font-bold text-[#1A103C] tracking-tight flex items-center gap-2">
            <ShieldCheck className="w-6 h-6 text-[#53389E]" />
            Security & Compliance Policy Engine
          </h1>
          <p className="text-xs text-slate-700 font-medium mt-1">
            Define organizational guardrails, prompt injection filters, financial threshold rules, and automatic action triggers.
          </p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="px-5 py-2.5 bg-[#53389E] hover:bg-[#432A85] text-white rounded-xl text-xs font-display font-bold flex items-center gap-2 transition shadow-xs"
        >
          <Plus className="w-4 h-4" />
          Create New Policy
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {policies.map((p) => (
          <div
            key={p.id}
            className={`p-6 rounded-2xl border transition space-y-3 ${
              p.is_active ? 'bg-white border-slate-200 shadow-xs' : 'bg-slate-100 border-slate-300 opacity-70'
            }`}
          >
            <div className="flex items-start justify-between">
              <div>
                <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-[#F4F0FF] text-[#53389E] border border-[#D8C7FF] uppercase font-mono">
                  {p.category}
                </span>
                <h3 className="font-mono font-bold text-sm text-[#1A103C] mt-2">{p.title}</h3>
              </div>

              <button
                onClick={() => handleTogglePolicy(p.id)}
                className={`px-3 py-1 rounded-full text-[11px] font-mono font-bold transition ${
                  p.is_active ? 'bg-emerald-100 text-emerald-800 border border-emerald-300' : 'bg-slate-200 text-slate-700'
                }`}
              >
                {p.is_active ? 'ACTIVE' : 'INACTIVE'}
              </button>
            </div>

            <p className="text-xs text-slate-700 font-medium leading-relaxed">{p.description}</p>

            <div className="pt-3 border-t border-slate-200 text-xs font-mono space-y-1.5 text-slate-800 font-semibold">
              <div className="flex justify-between">
                <span className="text-slate-500 font-normal">Rule Type:</span>
                <span className="text-[#1A103C]">{p.rule_type}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500 font-normal">Action on Trigger:</span>
                <span className={`font-bold ${
                  p.action_on_trigger === 'BLOCK' ? 'text-rose-700' : 'text-amber-700'
                }`}>
                  {p.action_on_trigger}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500 font-normal">Risk Weight:</span>
                <span className="text-indigo-700">+{p.risk_score_weight} pts</span>
              </div>
            </div>

            <div className="p-3 bg-slate-50 rounded-xl border border-slate-200 font-mono text-[11px] text-slate-900 truncate font-semibold">
              Rule: {p.content}
            </div>
          </div>
        ))}
      </div>

      {/* Modal for Creating Policy */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4 z-50">
          <div className="bg-white border border-slate-200 rounded-2xl max-w-md w-full p-6 space-y-4 shadow-xl">
            <h3 className="text-lg font-mono font-bold text-[#1A103C] flex items-center gap-2">
              <ShieldCheck className="w-5 h-5 text-[#53389E]" />
              Create Security Policy
            </h3>
            <form onSubmit={handleCreatePolicy} className="space-y-3 text-xs">
              <div>
                <label className="block text-slate-700 mb-1 font-semibold">Policy Title</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Prevent Unapproved SQL Execution"
                  value={form.title}
                  onChange={(e) => setForm({ ...form, title: e.target.value })}
                  className="w-full px-3 py-2 rounded-xl bg-slate-50 border border-slate-300 text-slate-900 focus:outline-none focus:border-[#53389E]"
                />
              </div>
              <div>
                <label className="block text-slate-700 mb-1 font-semibold">Category</label>
                <select
                  value={form.category}
                  onChange={(e) => setForm({ ...form, category: e.target.value })}
                  className="w-full px-3 py-2 rounded-xl bg-slate-50 border border-slate-300 text-slate-900 focus:outline-none focus:border-[#53389E]"
                >
                  <option value="Security">Security</option>
                  <option value="Compliance">Compliance</option>
                  <option value="Financial">Financial</option>
                  <option value="Data Leakage">Data Leakage</option>
                </select>
              </div>
              <div>
                <label className="block text-slate-700 mb-1 font-semibold">Rule Type</label>
                <select
                  value={form.rule_type}
                  onChange={(e) => setForm({ ...form, rule_type: e.target.value })}
                  className="w-full px-3 py-2 rounded-xl bg-slate-50 border border-slate-300 text-slate-900 focus:outline-none focus:border-[#53389E] font-mono"
                >
                  <option value="KEYWORDS">KEYWORDS (Comma-separated)</option>
                  <option value="THRESHOLD">THRESHOLD (Numeric Limit)</option>
                  <option value="REGEX">REGEX Pattern</option>
                </select>
              </div>
              <div>
                <label className="block text-slate-700 mb-1 font-semibold">Rule Content Pattern</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. drop table, truncate, delete from"
                  value={form.content}
                  onChange={(e) => setForm({ ...form, content: e.target.value })}
                  className="w-full px-3 py-2 rounded-xl bg-slate-50 border border-slate-300 text-slate-900 focus:outline-none focus:border-[#53389E] font-mono"
                />
              </div>
              <div>
                <label className="block text-slate-700 mb-1 font-semibold">Action on Trigger</label>
                <select
                  value={form.action_on_trigger}
                  onChange={(e) => setForm({ ...form, action_on_trigger: e.target.value })}
                  className="w-full px-3 py-2 rounded-xl bg-slate-50 border border-slate-300 text-slate-900 focus:outline-none focus:border-[#53389E]"
                >
                  <option value="BLOCK">BLOCK (Immediate Denial)</option>
                  <option value="ESCALATE">ESCALATE (Human Approval Queue)</option>
                  <option value="ALERT">ALERT (Allow & Flag)</option>
                </select>
              </div>
              <div className="flex justify-end gap-2 pt-3">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-xl font-semibold border border-slate-300"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-[#53389E] hover:bg-[#432A85] text-white rounded-xl font-semibold"
                >
                  Create Policy
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
