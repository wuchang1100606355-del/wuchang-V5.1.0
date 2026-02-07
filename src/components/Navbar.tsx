import React from 'react';
import { Menu, X } from 'lucide-react';

const Navbar: React.FC = () => {
  const [isOpen, setIsOpen] = React.useState(false);

  return (
    <nav className="bg-white/90 backdrop-blur-md border-b border-earth-200 sticky top-0 z-50">
      <div className="container mx-auto px-4 md:px-8">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center space-x-2">
            <span className="text-2xl font-bold text-earth-800 tracking-tight">五常社區</span>
            <span className="text-sm bg-vitality-100 text-vitality-700 px-2 py-0.5 rounded-full border border-vitality-200">V5.1.0</span>
          </div>

          <div className="hidden md:flex space-x-8">
            <a href="#" className="text-stone-600 hover:text-earth-800 font-medium transition-colors">首頁</a>
            <a href="#" className="text-stone-600 hover:text-earth-800 font-medium transition-colors">物業服務</a>
            <a href="#" className="text-stone-600 hover:text-earth-800 font-medium transition-colors">商業專區</a>
            <a href="#" className="text-stone-600 hover:text-earth-800 font-medium transition-colors">社區照護</a>
            <a href="#" className="text-stone-600 hover:text-earth-800 font-medium transition-colors">關於小j</a>
          </div>

          <div className="md:hidden">
            <button onClick={() => setIsOpen(!isOpen)} className="text-stone-600">
              {isOpen ? <X /> : <Menu />}
            </button>
          </div>
        </div>
      </div>

      {isOpen && (
        <div className="md:hidden bg-white border-t border-earth-100 p-4">
          <div className="flex flex-col space-y-4">
            <a href="#" className="text-stone-600 hover:text-earth-800 font-medium">首頁</a>
            <a href="#" className="text-stone-600 hover:text-earth-800 font-medium">物業服務</a>
            <a href="#" className="text-stone-600 hover:text-earth-800 font-medium">商業專區</a>
            <a href="#" className="text-stone-600 hover:text-earth-800 font-medium">社區照護</a>
            <a href="#" className="text-stone-600 hover:text-earth-800 font-medium">關於小j</a>
          </div>
        </div>
      )}
    </nav>
  );
};

export default Navbar;
