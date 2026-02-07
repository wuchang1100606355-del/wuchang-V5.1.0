import React, { useState } from 'react';
import { Send, Heart, Shield, Sparkles, Mic } from 'lucide-react';

const LittleJChat: React.FC = () => {
  const [message, setMessage] = useState('');
  const [chatHistory, setChatHistory] = useState<{ role: 'user' | 'ai'; content: string }[]>([
    { role: 'ai', content: '你好！我是小j (Little J)。我是我們社區的數位守護者。告訴我，你夢想中的五常社區是什麼樣子的？' }
  ]);
  const [isListening, setIsListening] = useState(false);

  const handleSend = () => {
    if (!message.trim()) return;

    const userMsg = message;
    setChatHistory(prev => [...prev, { role: 'user', content: userMsg }]);
    setMessage('');

    // Simulate AI response
    setTimeout(() => {
      setChatHistory(prev => [...prev, { 
        role: 'ai', 
        content: `謝謝你告訴我！「${userMsg}」是一個很棒的想法。我已經將這個夢想記錄在社區願景資料庫中。作為您的 AI 守護者，我會努力學習如何讓這個夢想成真！` 
      }]);
    }, 1000);
  };

  const handleVoiceInput = () => {
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (!SpeechRecognition) {
      alert('目前裝置或瀏覽器暫不支援語音輸入，請改用文字輸入。');
      return;
    }
    try {
      const recognition = new SpeechRecognition();
      recognition.lang = 'zh-TW';
      recognition.continuous = false;
      recognition.interimResults = false;
      setIsListening(true);
      recognition.onresult = (event: any) => {
        const transcript = event.results[0][0].transcript;
        setMessage(prev => (prev ? prev + ' ' + transcript : transcript));
      };
      recognition.onerror = () => {
        setIsListening(false);
      };
      recognition.onend = () => {
        setIsListening(false);
      };
      recognition.start();
    } catch {
      setIsListening(false);
    }
  };

  return (
    <div className="bg-white rounded-2xl shadow-xl overflow-hidden border border-earth-200 max-w-2xl mx-auto">
      <div className="bg-tech-600 p-4 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-full bg-white flex items-center justify-center">
            <Sparkles className="text-tech-600 w-6 h-6" />
          </div>
          <div>
            <h3 className="text-white font-bold text-lg">小j (Little J)</h3>
            <p className="text-tech-50 text-xs">數位 AI 社區守護者 • 線上</p>
          </div>
        </div>
        <div className="bg-white/20 px-3 py-1 rounded-full text-white text-xs backdrop-blur-sm">
           守護值: Lv.5
        </div>
      </div>

      <div className="h-96 p-6 overflow-y-auto bg-stone-50 space-y-4">
        {chatHistory.map((msg, idx) => (
          <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[80%] p-4 rounded-2xl ${
              msg.role === 'user' 
                ? 'bg-earth-600 text-white rounded-tr-none' 
                : 'bg-white border border-earth-200 text-stone-800 rounded-tl-none shadow-sm'
            }`}>
              <p className="text-sm md:text-base leading-relaxed">{msg.content}</p>
            </div>
          </div>
        ))}
      </div>

      <div className="p-4 bg-white border-t border-earth-100">
        <div className="flex items-center space-x-2">
          <button
            type="button"
            onClick={handleVoiceInput}
            className={`p-3 rounded-xl border transition-colors shadow-md flex items-center justify-center ${
              isListening ? 'bg-earth-600 border-earth-600 text-white' : 'bg-white border-earth-300 text-earth-700 hover:bg-earth-50'
            }`}
          >
            <Mic className="w-5 h-5" />
          </button>
          <input
            type="text"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSend()}
            placeholder="可以用語音或文字，和小j 訴說今天的心情與夢想..."
            className="flex-1 p-3 border border-earth-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-tech-600 focus:border-transparent transition-all placeholder-earth-400"
          />
          <button 
            type="button"
            onClick={handleSend}
            className="bg-tech-600 hover:bg-tech-700 text-white p-3 rounded-xl transition-colors shadow-md flex items-center justify-center"
          >
            <Send className="w-5 h-5" />
          </button>
        </div>
        <p className="text-center text-xs text-earth-500 mt-2">
          您的每一個夢想，都是小j 成長的養分
        </p>
      </div>
    </div>
  );
};

export default LittleJChat;
