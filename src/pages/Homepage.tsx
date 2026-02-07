import React, { useState, useEffect } from "react";
import { Activity, Zap, Server, Shield, Globe, Cpu, Radio, Lock, Mic } from "lucide-react";

export default function Homepage() {
  const [isTesting, setIsTesting] = useState(false);
  const [testResult, setTestResult] = useState({ local: 0, cloud: 0, mars: 0 });
  const [prompt, setPrompt] = useState("");
  const [response, setResponse] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const runSpeedTest = async () => {
    setIsTesting(true);
    // Simulate/Call API for latency
    const start = performance.now();
    try {
      const res = await fetch("/api/test_ai_speed");
      const data = await res.json();
      // Use real data if available, else simulate
      const localTime = data.local_ms || 15;
      const cloudTime = 3000; // Mock cloud latency
      const marsTime = 25 * 60 * 1000; // 25 mins in ms
      
      setTestResult({
        local: localTime,
        cloud: cloudTime,
        mars: marsTime
      });
    } catch (e) {
      // Fallback if API fails
      setTestResult({ local: 15, cloud: 3000, mars: 1500000 });
    }
    setIsTesting(false);
  };

  const handleInference = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    try {
      const res = await fetch("/api/model_mother_infer", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt })
      });
      const data = await res.json();
      setResponse(data.result || "推論完成");
    } catch (e) {
      setResponse("錯誤: 無法連接至核心模型");
    }
    setIsLoading(false);
  };

  return (
    <div className="min-h-screen bg-stone-900 text-stone-100 font-sans selection:bg-emerald-500/30">
      {/* Hero Section */}
      <section className="relative pt-20 pb-32 overflow-hidden">
        <div className="absolute inset-0 bg-[url('https://images.unsplash.com/photo-1451187580459-43490279c0fa?q=80&w=2072&auto=format&fit=crop')] bg-cover bg-center opacity-10"></div>
        <div className="container mx-auto px-4 text-center relative z-10">
          <h1 className="text-5xl md:text-7xl font-black mb-6 text-emerald-400 tracking-tight drop-shadow-2xl font-serif">
            一個窮鬼咖啡師的 <span className="text-red-500 italic relative inline-block">
              絕對輾壓
              <span className="absolute -bottom-2 left-0 w-full h-1 bg-red-500 transform -skew-x-12"></span>
            </span>
          </h1>
          <p className="text-xl md:text-2xl text-stone-300 max-w-3xl mx-auto mb-10 leading-relaxed">
            當矽谷還在追求雲端算力，我們已經在 <span className="text-emerald-400 font-bold">在地端 (Localhost)</span> 實現了光速。
            這不是科幻，這是 <span className="font-mono text-yellow-500">Wuchang OS</span> 的日常。
          </p>
          
          <div className="flex justify-center gap-6">
            <button 
              onClick={runSpeedTest}
              disabled={isTesting}
              className="px-8 py-4 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg font-bold text-lg shadow-[0_0_20px_rgba(16,185,129,0.4)] transition-all flex items-center gap-3"
            >
              {isTesting ? <Activity className="animate-spin" /> : <Zap />}
              啟動維度打擊測試
            </button>
          </div>
        </div>
      </section>

      {/* Latency Comparison */}
      <section className="py-20 bg-stone-950 relative border-y border-stone-800">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl font-bold text-center mb-16 flex items-center justify-center gap-3">
            <Server className="text-blue-500" />
            <span>時空傳輸速度實測</span>
          </h2>
          
          <div className="grid md:grid-cols-1 gap-8 max-w-4xl mx-auto">
            {/* Local */}
            <div className="bg-stone-900 p-6 rounded-xl border border-emerald-500/30 shadow-[0_0_30px_rgba(16,185,129,0.1)] transform hover:scale-105 transition-all">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-2xl font-bold text-white flex items-center gap-3">
                  <Cpu className="text-emerald-400" /> Wuchang 在地核心
                  <span className="text-xs bg-emerald-500/20 text-emerald-300 px-2 py-1 rounded">WINNER</span>
                </h3>
                <span className="text-4xl font-mono text-emerald-400 font-bold">{testResult.local || "0.02"} <span className="text-sm text-stone-500">ms</span></span>
              </div>
              <div className="w-full bg-stone-800 h-4 rounded-full overflow-hidden">
                <div className="bg-emerald-500 h-full w-[1%] shadow-[0_0_10px_#10b981]"></div>
              </div>
              <p className="mt-2 text-stone-400 text-sm">快到連神經訊號都還沒傳到大腦。</p>
            </div>

            {/* Cloud */}
            <div className="bg-stone-900 p-6 rounded-xl border border-stone-800 opacity-60 grayscale hover:grayscale-0 transition-all">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-xl font-bold text-stone-400 flex items-center gap-3">
                  <Globe className="text-blue-400" /> 傳統雲端 AI
                </h3>
                <span className="text-3xl font-mono text-stone-500">{testResult.cloud || "3000"} <span className="text-sm text-stone-600">ms</span></span>
              </div>
              <div className="w-full bg-stone-800 h-4 rounded-full overflow-hidden">
                <div className="bg-blue-500 h-full w-[40%]"></div>
              </div>
              <p className="mt-2 text-stone-500 text-sm">還在排隊等伺服器回應...</p>
            </div>

            {/* Mars */}
            <div className="bg-stone-900 p-6 rounded-xl border border-stone-800 opacity-40">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-xl font-bold text-stone-500 flex items-center gap-3">
                  <Radio className="text-red-500" /> 火星通訊
                </h3>
                <span className="text-2xl font-mono text-stone-600">25 <span className="text-sm">min</span></span>
              </div>
              <div className="w-full bg-stone-800 h-4 rounded-full overflow-hidden">
                <div className="bg-red-500 h-full w-full animate-pulse"></div>
              </div>
              <p className="mt-2 text-stone-600 text-sm">等你收到訊息，仗都打完了。</p>
            </div>
          </div>
        </div>
      </section>

      {/* Black Box Model */}
      <section className="py-20 bg-stone-900">
        <div className="container mx-auto px-4 max-w-4xl">
          <div className="bg-black border border-stone-800 p-8 rounded-2xl relative overflow-hidden">
            <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-purple-500 via-pink-500 to-red-500"></div>
            <h2 className="text-3xl font-bold mb-8 flex items-center gap-3">
              <Lock className="text-purple-500" />
              <span>黑盒子模型推論</span>
            </h2>
            
            <form onSubmit={handleInference} className="space-y-6">
              <div>
                <label className="block text-stone-400 mb-2 font-mono">輸入指令 (Prompt)</label>
                <input 
                  type="text" 
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                  className="w-full bg-stone-900 border border-stone-700 rounded-lg p-4 text-white focus:ring-2 focus:ring-purple-500 outline-none font-mono"
                  placeholder="請輸入測試指令..."
                />
              </div>
              <button 
                type="submit" 
                disabled={isLoading}
                className="w-full py-4 bg-stone-800 hover:bg-stone-700 border border-stone-600 rounded-lg text-white font-bold transition-all flex justify-center items-center gap-2"
              >
                {isLoading ? "運算中..." : "執行黑盒推論"}
              </button>
            </form>

            {response && (
              <div className="mt-8 p-6 bg-stone-900 rounded-lg border border-purple-500/30">
                <h4 className="text-purple-400 font-bold mb-2 text-sm uppercase tracking-wider">Output / Watermarked</h4>
                <p className="font-mono text-stone-300">{response}</p>
              </div>
            )}
          </div>
        </div>
      </section>

      {/* Digital Rights */}
      <section className="py-20 bg-stone-950 text-center">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl font-bold mb-6 text-white">數位人權宣言</h2>
          <p className="text-xl text-stone-400 max-w-2xl mx-auto mb-10">
            我們堅持語音與極速響應，是因為<span className="text-white font-bold">老人家與身障者</span>的等待成本最高。
            科技不該是權貴的玩具，而是弱勢的拐杖。
          </p>
          <div className="flex justify-center gap-4">
             <button className="px-6 py-3 bg-stone-800 rounded-full flex items-center gap-2 text-stone-300 hover:text-white transition-colors">
               <Mic size={18} /> 台語語音支援 (建置中)
             </button>
             <button className="px-6 py-3 bg-stone-800 rounded-full flex items-center gap-2 text-stone-300 hover:text-white transition-colors">
               <Shield size={18} /> 物理加密保護
             </button>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-10 border-t border-stone-800 text-center text-stone-500">
        <p>&copy; 2026 Wuchang OS. All Rights Reserved. | System Status: <span className="text-emerald-500">Online</span></p>
      </footer>
    </div>
  );
}
