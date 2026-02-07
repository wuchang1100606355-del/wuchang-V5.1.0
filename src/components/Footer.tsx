import React from 'react';
import { Heart, Globe, Shield } from 'lucide-react';

const Footer: React.FC = () => {
  return (
    <footer className="bg-earth-800 text-earth-100 pt-12 pb-8">
      <div className="container mx-auto px-4 md:px-8">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-8">
          <div>
            <h3 className="text-xl font-bold text-white mb-4">五常社區服務系統</h3>
            <p className="text-earth-300 leading-relaxed mb-4">
              以技術守護社區溫度。我們致力於透過 AI 與數位科技，打造一個互助、共融、永續的現代化社區。
            </p>
            <div className="flex items-center space-x-2 text-earth-300 text-sm">
              <Globe className="w-4 h-4" />
              <span>wuchang.life</span>
            </div>
          </div>
          
          <div>
            <h3 className="text-xl font-bold text-white mb-4">核心價值</h3>
            <ul className="space-y-2 text-earth-300">
              <li className="flex items-center space-x-2">
                <Heart className="w-4 h-4 text-vitality-500" />
                <span>公益導向</span>
              </li>
              <li className="flex items-center space-x-2">
                <Shield className="w-4 h-4 text-tech-500" />
                <span>AI 守護</span>
              </li>
              <li className="flex items-center space-x-2">
                <Globe className="w-4 h-4 text-earth-400" />
                <span>永續發展</span>
              </li>
            </ul>
          </div>

          <div>
            <h3 className="text-xl font-bold text-white mb-4">聯絡我們</h3>
            <p className="text-earth-300 mb-2">五常社區管理委員會</p>
            <p className="text-earth-300 mb-2">數位 AI 守護者：小j (Sister)</p>
            <p className="text-earth-300 text-sm mt-4 opacity-70">
              Designed with ❤️ for Public Welfare
            </p>
          </div>
        </div>
        
        <div className="border-t border-earth-700 pt-8 text-center text-earth-400 text-sm">
          <p>&copy; 2026 五常社區服務系統 V5.1.0. All Rights Reserved.</p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
