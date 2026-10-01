/**
 * Official AgentShield JavaScript / TypeScript SDK (Phase 9)
 */
class AgentShieldClient {
  constructor({ apiKey, endpoint = 'http://localhost:8000', agentKey = null }) {
    this.apiKey = apiKey;
    this.endpoint = endpoint.replace(/\/$/, '');
    this.agentKey = agentKey;
  }

  async execute({ tool, input, context = null }) {
    const url = `${this.endpoint}/v1/tool/execute`;
    const payload = { tool, input, context };
    if (this.agentKey) payload.agent_key = this.agentKey;

    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Agent-API-Key': this.apiKey
      },
      body: JSON.stringify(payload)
    });

    if (!response.ok) {
      const errText = await response.text();
      throw new Error(`AgentShield Gateway Error (${response.status}): ${errText}`);
    }

    return await response.json();
  }
}

module.exports = { AgentShieldClient };
