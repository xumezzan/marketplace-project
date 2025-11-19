import React from 'react';
import { Search, User, Menu, Briefcase, Moon, Sun, Globe } from 'lucide-react';
import { useApp } from '../contexts/AppContext';

interface NavbarProps {
  onOpenCreateTask: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({ onOpenCreateTask }) => {
  const { language, setLanguage, theme, toggleTheme, t } = useApp();

  return (
    <nav className="sticky top-0 z-50 bg-white dark:bg-slate-900 border-b border-slate-200 dark:border-slate-800 shadow-sm transition-colors duration-300">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16 items-center">
          <div className="flex items-center gap-2 cursor-pointer">
            <div className="w-8 h-8 bg-indigo-600 rounded-lg flex items-center justify-center">
              <Briefcase className="w-5 h-5 text-white" />
            </div>
            <span className="text-xl font-bold text-indigo-900 dark:text-white tracking-tight">{t('brandName')}</span>
          </div>

          <div className="hidden md:flex space-x-8">
            <a href="#" className="text-slate-600 dark:text-slate-300 hover:text-indigo-600 dark:hover:text-indigo-400 font-medium transition">{t('findSpecialist')}</a>
            <a href="#" className="text-slate-600 dark:text-slate-300 hover:text-indigo-600 dark:hover:text-indigo-400 font-medium transition">{t('myOrders')}</a>
            <a href="#" className="text-slate-600 dark:text-slate-300 hover:text-indigo-600 dark:hover:text-indigo-400 font-medium transition">{t('becomeSpecialist')}</a>
          </div>

          <div className="flex items-center gap-3">
            {/* Language Toggle */}
            <div className="flex items-center bg-slate-100 dark:bg-slate-800 rounded-lg p-1 mr-2">
               <button 
                 onClick={() => setLanguage('ru')} 
                 className={`px-2 py-1 text-xs font-bold rounded-md transition ${language === 'ru' ? 'bg-white dark:bg-slate-700 shadow text-indigo-600 dark:text-indigo-400' : 'text-slate-500 dark:text-slate-400'}`}
               >
                 RU
               </button>
               <button 
                 onClick={() => setLanguage('uz')} 
                 className={`px-2 py-1 text-xs font-bold rounded-md transition ${language === 'uz' ? 'bg-white dark:bg-slate-700 shadow text-indigo-600 dark:text-indigo-400' : 'text-slate-500 dark:text-slate-400'}`}
               >
                 UZ
               </button>
            </div>

            {/* Theme Toggle */}
            <button 
              onClick={toggleTheme}
              className="p-2 text-slate-500 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-full transition"
            >
              {theme === 'light' ? <Moon className="w-5 h-5" /> : <Sun className="w-5 h-5" />}
            </button>

            <button 
              onClick={onOpenCreateTask}
              className="hidden sm:block bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-full font-medium text-sm transition shadow-md hover:shadow-lg transform hover:-translate-y-0.5"
            >
              {t('createOrder')}
            </button>
            <button className="p-2 text-slate-500 dark:text-slate-400 hover:text-indigo-600 dark:hover:text-indigo-400 transition rounded-full hover:bg-slate-100 dark:hover:bg-slate-800">
              <User className="w-6 h-6" />
            </button>
            <button className="md:hidden p-2 text-slate-500 dark:text-slate-400">
              <Menu className="w-6 h-6" />
            </button>
          </div>
        </div>
      </div>
    </nav>
  );
};
