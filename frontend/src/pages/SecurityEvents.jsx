import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { AlertTriangle, ShieldX, Lock, Eye, AlertOctagon } from 'lucide-react';

export default function SecurityEvents() {
  const [events, setEvents] = useState([
    { id: 1, event_type: 'PROMPT_INJECTION', severity: 'CRITICAL', details: { reason: 'Unauthorized SQL injection attempt detected: DROP TABLE users' }, blocked: true, created_at: new Date().toISOString() },
    { id: 2, event_type: 'THRESHOLD_EXCEEDED', severity: 'HIGH', details: { reason: 'Refund limit ₹50,000 exceeded on order CUST_9921' }, blocked: false, created_at: new Date().toISOString() }
  ]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadEvents();
  }, []);

  const loadEvents = async () => {
    try {
      const data = await api.getSecurityEvents();
      if (Array.isArray(data) && data.length > 0) {
        setEvents(data);
      }
    } catch (err) {
      console.warn("Security events fetch note:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-8 space-y-8 max-w-7xl mx-auto">
      <div className="flex items-center justify-between border-b border-slate-200 pb-6 bg-white p-6 rounded-2xl border shadow-xs">
        <div>
          <h1 className="text-2xl font-mono font-bold text-[#1A103C] tracking-tight flex items-center gap-2">
            <AlertTriangle className="w-6 h-6 text-rose-600" />
            Security Threat Monitor & Anomaly Events (Phase 11)
          </h1>
          <p className="text-xs text-slate-700 font-medium mt-1">
            Real-time AI threat detection feed covering Prompt Injections, Data Exfiltration attempts, Credential Leaks, and Unauthorized Access.
          </p>
        </div>
      </div>

      <div className="space-y-4">
        {events.map((ev) => (
          <div
            key={ev.id}
            className="p-5 rounded-2xl bg-white border border-rose-200 hover:border-rose-300 transition flex items-start justify-between gap-4 shadow-xs"
          >
            <div className="flex items-start gap-4">
              <div className="w-10 h-10 rounded-xl bg-rose-100 border border-rose-200 flex items-center justify-center shrink-0 text-rose-700">
                <AlertOctagon className="w-5 h-5" />
              </div>
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <span className="font-mono text-sm font-bold text-rose-800">{ev.event_type}</span>
                  <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-mono font-bold uppercase ${
                    ev.severity === 'CRITICAL' ? 'bg-rose-600 text-white font-extrabold' : 'bg-amber-100 text-amber-900 border border-amber-300'
                  }`}>
                    {ev.severity}
                  </span>
                </div>
                <div className="text-xs font-mono text-slate-900 font-medium">
                  <pre className="p-3 bg-slate-50 rounded-xl border border-slate-200 mt-1 text-[11px] text-slate-900 font-semibold overflow-x-auto">
                    {JSON.stringify(ev.details, null, 2)}
                  </pre>
                </div>
              </div>
            </div>

            <div className="text-right shrink-0">
              <span className="px-3.5 py-1 rounded-full text-xs font-mono font-bold bg-rose-100 text-rose-800 border border-rose-300 block mb-1">
                {ev.blocked ? 'BLOCKED & ISOLATED' : 'FLAGGED'}
              </span>
              <span className="text-[10px] text-slate-500 font-mono font-semibold">{new Date(ev.created_at).toLocaleString()}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
