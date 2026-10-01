import React, { useState } from 'react';
import { api } from '../services/api';
import { Terminal, Play, ShieldCheck, AlertCircle, ArrowRight, ShieldAlert, CheckCircle } from 'lucide-react';

export default function SecurityGateway() {
  const [agentKey, setAgentKey] = useState('agent_support_001');
  const [toolName, setToolName] = useState('refund_customer');
  const [payloadJson, setPayloadJson] = useState('{\n  "customer_id": "CUST_9921",\n  "amount": 75000,\n  "reason": "Customer VIP refund request"\n}');
  const [apiKey, setApiKey] = useState('');
  
  const [response, setResponse] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleExecuteGateway = async () => {
    setLoading(true);
    setResponse(null);
    try {
      const parsedInput = JSON.parse(payloadJson);
      const res = await api.executeToolGateway({
        agent_key: agentKey,
        tool: toolName,
        input: parsedInput
      }, apiKey || null);
      setResponse(res);
    } catch (err) {
      setResponse({ error: err.message });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-8 space-y-8 max-w-7xl mx-auto">
      <div className="flex items-center justify-between border-b border-slate-200 pb-6 bg-white p-6 rounded-2xl border shadow-xs">
        <div>
          <h1 className="text-2xl font-mono font-bold text-[#1A103C] tracking-tight flex items-center gap-2">
            <Terminal className="w-6 h-6 text-[#53389E]" />
            AgentShield Security Gateway Console (/v1/tool/execute)
          </h1>
          <p className="text-xs text-slate-700 font-medium mt-1">
            Interactive Gateway evaluation pipeline (Phase 4). Test raw agent tool invocations against Identity, Permission, Policy Engine, AI Threat Detection, and Verification.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Input Sandbox */}
        <div className="p-6 rounded-2xl bg-white border border-slate-200 space-y-4 shadow-xs">
          <h3 className="font-mono font-bold text-sm text-[#1A103C] flex items-center gap-2 border-b border-slate-200 pb-3">
            <Play className="w-4 h-4 text-emerald-600" />
            Simulate Tool Call Request
          </h3>

          <div className="space-y-3 text-xs">
            <div>
              <label className="block text-slate-700 mb-1 font-semibold">Agent Key (Identity)</label>
              <input
                type="text"
                value={agentKey}
                onChange={(e) => setAgentKey(e.target.value)}
                className="w-full px-3 py-2 rounded-xl bg-slate-50 border border-slate-300 text-slate-900 focus:outline-none focus:border-[#53389E] font-mono font-semibold"
              />
            </div>

            <div>
              <label className="block text-slate-700 mb-1 font-semibold">Tool Name</label>
              <select
                value={toolName}
                onChange={(e) => setToolName(e.target.value)}
                className="w-full px-3 py-2 rounded-xl bg-slate-50 border border-slate-300 text-slate-900 focus:outline-none focus:border-[#53389E] font-mono font-semibold"
              >
                <option value="search_customer">search_customer</option>
                <option value="update_customer">update_customer</option>
                <option value="send_email">send_email</option>
                <option value="refund_customer">refund_customer</option>
                <option value="send_slack_alert">send_slack_alert</option>
                <option value="execute_raw_sql">execute_raw_sql</option>
              </select>
            </div>

            <div>
              <label className="block text-slate-700 mb-1 font-semibold">Optional Agent API Key Header (X-Agent-API-Key)</label>
              <input
                type="text"
                placeholder="sk_live_..."
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
                className="w-full px-3 py-2 rounded-xl bg-slate-50 border border-slate-300 text-slate-900 focus:outline-none focus:border-[#53389E] font-mono"
              />
            </div>

            <div>
              <label className="block text-slate-700 mb-1 font-semibold">Tool Input JSON Payload</label>
              <textarea
                rows={6}
                value={payloadJson}
                onChange={(e) => setPayloadJson(e.target.value)}
                className="w-full px-3 py-2 rounded-xl bg-slate-50 border border-slate-300 text-slate-900 focus:outline-none focus:border-[#53389E] font-mono text-xs font-semibold"
              />
            </div>

            <button
              onClick={handleExecuteGateway}
              disabled={loading}
              className="w-full py-3 bg-[#53389E] hover:bg-[#432A85] text-white font-display font-bold rounded-xl transition flex items-center justify-center gap-2 shadow-xs"
            >
              {loading ? 'Evaluating Gateway Pipeline...' : 'Send Request to Security Gateway'}
            </button>
          </div>
        </div>

        {/* Output & Pipeline Inspector */}
        <div className="p-6 rounded-2xl bg-white border border-slate-200 space-y-4 flex flex-col justify-between shadow-xs">
          <h3 className="font-mono font-bold text-sm text-[#1A103C] flex items-center gap-2 border-b border-slate-200 pb-3">
            <ShieldCheck className="w-4 h-4 text-[#53389E]" />
            Gateway Evaluation Output & Inspection
          </h3>

          {!response ? (
            <div className="py-24 text-center text-slate-600 text-xs font-mono font-semibold">
              Click "Send Request to Security Gateway" to evaluate pipeline.
            </div>
          ) : response.error ? (
            <div className="p-4 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 text-xs font-mono font-bold">
              Gateway Error: {response.error}
            </div>
          ) : (
            <div className="space-y-4 text-xs font-mono">
              {/* Decision Badge */}
              <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 flex items-center justify-between">
                <div>
                  <span className="text-slate-500 text-[10px] uppercase font-semibold block">FINAL DECISION</span>
                  <span className={`text-xl font-bold uppercase tracking-wider ${
                    response.decision === 'ALLOW' ? 'text-emerald-700' :
                    response.decision === 'BLOCK' ? 'text-rose-700' : 'text-amber-700'
                  }`}>
                    {response.decision}
                  </span>
                </div>
                <div className="text-right">
                  <span className="text-slate-500 text-[10px] uppercase font-semibold block">RISK SCORE</span>
                  <span className="text-lg font-bold text-amber-800">{response.risk_score} / 100</span>
                </div>
              </div>

              {/* Step Flow */}
              <div className="space-y-2 text-[11px] text-slate-900 font-semibold">
                <div className="p-3 rounded-xl bg-slate-50 border border-slate-200 flex items-center justify-between">
                  <span>1. Identity Verification</span>
                  <span className="text-emerald-700 font-bold">AUTHENTICATED</span>
                </div>

                <div className="p-3 rounded-xl bg-slate-50 border border-slate-200 flex items-center justify-between">
                  <span>2. Tool Permission Matrix</span>
                  <span className="text-emerald-700 font-bold">CHECKED</span>
                </div>

                <div className="p-3 rounded-xl bg-slate-50 border border-slate-200 flex items-center justify-between">
                  <span>3. Policy & AI Threat Engine</span>
                  <span className={response.risk_factors?.length ? 'text-amber-800 font-bold' : 'text-emerald-700 font-bold'}>
                    {response.risk_factors?.length ? `${response.risk_factors.length} Triggers` : 'CLEAN'}
                  </span>
                </div>

                <div className="p-3 rounded-xl bg-slate-50 border border-slate-200 flex items-center justify-between">
                  <span>4. Post-Execution Verification</span>
                  <span className="text-indigo-700 font-bold">
                    {response.verification ? `${response.verification.status} (${response.verification.confidence * 100}%)` : 'N/A'}
                  </span>
                </div>
              </div>

              {/* Raw JSON */}
              <div className="pt-2">
                <span className="text-slate-500 text-[10px] font-bold block mb-1 uppercase">RAW GATEWAY RESPONSE</span>
                <pre className="p-4 bg-slate-900 text-cyan-300 rounded-xl border border-slate-800 text-[11px] overflow-x-auto max-h-48 font-semibold">
                  {JSON.stringify(response, null, 2)}
                </pre>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
