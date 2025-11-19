import React from 'react';
import { Search, Shield, Star, Users } from 'lucide-react';
import { useApp } from '../contexts/AppContext';

interface HeroProps {
  onOpenCreateTask: () => void;
}

export const Hero: React.FC<HeroProps> = ({ onOpenCreateTask }) => {
  const { t } = useApp();

  return (
    <div className="relative bg-white dark:bg-slate-900 overflow-hidden transition-colors duration-300">
      <div className="max-w-7xl mx-auto">
        <div className="relative z-10 pb-8 bg-white dark:bg-slate-900 sm:pb-16 md:pb-20 lg:max-w-2xl lg:w-full lg:pb-28 xl:pb-32 pt-20 px-4 sm:px-6 lg:px-8 transition-colors duration-300">
          <main className="mt-10 mx-auto max-w-7xl sm:mt-12 md:mt-16 lg:mt-20 xl:mt-28">
            <div className="sm:text-center lg:text-left">
              <h1 className="text-4xl tracking-tight font-extrabold text-slate-900 dark:text-white sm:text-5xl md:text-6xl">
                <span className="block xl:inline">{t('heroTitle1')}</span>
                <span className="block text-indigo-600 dark:text-indigo-400 xl:inline"> {t('heroTitle2')}</span>
              </h1>
              <p className="mt-3 text-base text-slate-500 dark:text-slate-400 sm:mt-5 sm:text-lg sm:max-w-xl sm:mx-auto md:mt-5 md:text-xl lg:mx-0">
                {t('heroSubtitle')}
              </p>
              
              <div className="mt-8 flex flex-col sm:flex-row gap-4 sm:justify-center lg:justify-start">
                <div className="relative rounded-md shadow-sm flex-grow max-w-lg">
                   <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                      <Search className="h-5 w-5 text-slate-400" aria-hidden="true" />
                    </div>
                    <input
                      type="text"
                      className="focus:ring-indigo-500 focus:border-indigo-500 block w-full pl-10 sm:text-sm border-slate-300 dark:border-slate-700 rounded-xl py-4 bg-slate-50 dark:bg-slate-800 dark:text-white dark:placeholder-slate-500"
                      placeholder={t('searchPlaceholder')}
                    />
                </div>
                <button
                  onClick={onOpenCreateTask}
                  className="flex items-center justify-center px-8 py-4 border border-transparent text-base font-medium rounded-xl text-white bg-indigo-600 hover:bg-indigo-700 md:py-4 md:text-lg shadow-lg shadow-indigo-200 dark:shadow-none transition transform hover:-translate-y-0.5"
                >
                  {t('findButton')}
                </button>
              </div>

              <div className="mt-8 flex items-center gap-6 text-sm text-slate-500 dark:text-slate-400 sm:justify-center lg:justify-start">
                  <div className="flex items-center gap-1.5">
                      <Shield className="w-4 h-4 text-green-500" />
                      <span>{t('verifiedProfiles')}</span>
                  </div>
                  <div className="flex items-center gap-1.5">
                      <Star className="w-4 h-4 text-yellow-500" />
                      <span>{t('honestReviews')}</span>
                  </div>
                  <div className="flex items-center gap-1.5">
                      <Users className="w-4 h-4 text-blue-500" />
                      <span>{t('profiCount')}</span>
                  </div>
              </div>
            </div>
          </main>
        </div>
      </div>
      <div className="lg:absolute lg:inset-y-0 lg:right-0 lg:w-1/2 bg-slate-50 dark:bg-slate-800 transition-colors duration-300">
        <img
          className="h-56 w-full object-cover sm:h-72 md:h-96 lg:w-full lg:h-full opacity-90 dark:opacity-60"
          src="https://images.unsplash.com/photo-1581578731117-104f2a863a30?ixlib=rb-1.2.1&auto=format&fit=crop&w=1350&q=80"
          alt="Repair specialist working"
        />
        <div className="absolute inset-0 bg-gradient-to-l from-transparent to-white dark:to-slate-900 lg:via-white/20 dark:via-slate-900/20"></div>
      </div>
    </div>
  );
};
