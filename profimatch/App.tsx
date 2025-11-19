import React, { useState } from 'react';
import { Navbar } from './components/Navbar';
import { Hero } from './components/Hero';
import { TaskWizard } from './components/TaskWizard';
import { SpecialistsList } from './components/SpecialistsList';
import { SpecialistProfile } from './components/SpecialistProfile';
import { Task, Specialist } from './types';
import { Hammer, BookOpen, Sparkles, Truck, Monitor, Clock } from 'lucide-react';
import { AppProvider, useApp } from './contexts/AppContext';

// Inner App Component to consume context
const MainContent: React.FC = () => {
  const { t, language } = useApp();
  const [isWizardOpen, setIsWizardOpen] = useState(false);
  const [selectedSpecialist, setSelectedSpecialist] = useState<Specialist | null>(null);
  const [myTasks, setMyTasks] = useState<Task[]>([]);
  const [notification, setNotification] = useState<string | null>(null);

  // Category Data inside component to use translation
  const CATEGORIES = [
    { id: 'repair', name: t('catRepair'), icon: Hammer, color: 'bg-orange-100 text-orange-600 dark:bg-orange-900/30 dark:text-orange-400' },
    { id: 'education', name: t('catEducation'), icon: BookOpen, color: 'bg-blue-100 text-blue-600 dark:bg-blue-900/30 dark:text-blue-400' },
    { id: 'beauty', name: t('catBeauty'), icon: Sparkles, color: 'bg-pink-100 text-pink-600 dark:bg-pink-900/30 dark:text-pink-400' },
    { id: 'transport', name: t('catTransport'), icon: Truck, color: 'bg-green-100 text-green-600 dark:bg-green-900/30 dark:text-green-400' },
    { id: 'it', name: t('catIt'), icon: Monitor, color: 'bg-purple-100 text-purple-600 dark:bg-purple-900/30 dark:text-purple-400' },
    { id: 'other', name: t('catOther'), icon: Clock, color: 'bg-slate-100 text-slate-600 dark:bg-slate-700 dark:text-slate-300' },
  ];

  const handleCreateTask = (task: Task) => {
    setMyTasks([task, ...myTasks]);
    setNotification(language === 'ru' ? 'Заказ успешно создан! Ожидайте откликов.' : 'Buyurtma muvaffaqiyatli yaratildi! Javoblarni kuting.');
    setTimeout(() => setNotification(null), 4000);
  };

  return (
    <div className="min-h-screen bg-white dark:bg-slate-900 pb-20 transition-colors duration-300">
      <Navbar onOpenCreateTask={() => setIsWizardOpen(true)} />
      
      {notification && (
        <div className="fixed top-20 right-4 z-50 bg-green-600 text-white px-6 py-3 rounded-lg shadow-xl animate-bounce-in flex items-center gap-2">
          <span>✅</span> {notification}
        </div>
      )}

      <Hero onOpenCreateTask={() => setIsWizardOpen(true)} />

      {/* Categories Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 -mt-10 relative z-20">
        <div className="bg-white dark:bg-slate-800 rounded-2xl shadow-xl border border-slate-100 dark:border-slate-700 p-6 sm:p-10 transition-colors duration-300">
          <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-6">{t('catPopular')}</h3>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
            {CATEGORIES.map((cat) => (
              <div 
                key={cat.id} 
                onClick={() => setIsWizardOpen(true)}
                className="flex flex-col items-center gap-3 p-4 rounded-xl hover:bg-slate-50 dark:hover:bg-slate-700 transition cursor-pointer group"
              >
                <div className={`w-14 h-14 rounded-2xl flex items-center justify-center ${cat.color} group-hover:scale-110 transition duration-300 shadow-sm`}>
                  <cat.icon className="w-7 h-7" />
                </div>
                <span className="text-sm font-medium text-slate-700 dark:text-slate-300 group-hover:text-slate-900 dark:group-hover:text-white text-center">{cat.name}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      <SpecialistsList onSelectSpecialist={setSelectedSpecialist} />

      {/* My Tasks Preview (Conditional) */}
      {myTasks.length > 0 && (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 border-t border-slate-200 dark:border-slate-800">
          <h2 className="text-2xl font-bold text-slate-900 dark:text-white mb-6">{t('myOrders')}</h2>
          <div className="space-y-4">
            {myTasks.map(task => (
              <div key={task.id} className="bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl p-6 shadow-sm flex flex-col sm:flex-row justify-between sm:items-center gap-4">
                <div>
                  <div className="flex items-center gap-3 mb-1">
                    <h3 className="font-bold text-lg text-slate-900 dark:text-white">{task.title}</h3>
                    <span className="px-2 py-0.5 bg-green-100 text-green-700 text-xs font-semibold rounded-full">Активен</span>
                  </div>
                  <p className="text-slate-500 dark:text-slate-400 text-sm mb-2">{task.category} • {task.location}</p>
                  <p className="text-slate-700 dark:text-slate-300">{task.description}</p>
                </div>
                <div className="text-right min-w-[140px]">
                  <p className="font-bold text-lg text-indigo-600 dark:text-indigo-400">
                    {task.budgetMin ? `~${task.budgetMax} ₽` : t('byAgreement')}
                  </p>
                  <p className="text-xs text-slate-400">Бюджет</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
      
      {/* Features Section */}
      <div className="bg-slate-50 dark:bg-slate-800/50 py-24 mt-12 transition-colors duration-300">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
           <div className="text-center max-w-3xl mx-auto mb-16">
              <h2 className="text-3xl font-bold text-slate-900 dark:text-white">{t('howItWorks')}</h2>
              <p className="mt-4 text-lg text-slate-500 dark:text-slate-400">{t('howItWorksSub')}</p>
           </div>

           <div className="grid md:grid-cols-3 gap-12">
              <div className="text-center">
                  <div className="w-16 h-16 bg-white dark:bg-slate-800 rounded-2xl shadow-md flex items-center justify-center mx-auto mb-6 text-2xl font-bold text-indigo-600 dark:text-indigo-400">1</div>
                  <h3 className="text-xl font-bold text-slate-900 dark:text-white mb-3">{t('step1Title')}</h3>
                  <p className="text-slate-600 dark:text-slate-400">{t('step1Desc')}</p>
              </div>
              <div className="text-center">
                  <div className="w-16 h-16 bg-white dark:bg-slate-800 rounded-2xl shadow-md flex items-center justify-center mx-auto mb-6 text-2xl font-bold text-indigo-600 dark:text-indigo-400">2</div>
                  <h3 className="text-xl font-bold text-slate-900 dark:text-white mb-3">{t('step2Title')}</h3>
                  <p className="text-slate-600 dark:text-slate-400">{t('step2Desc')}</p>
              </div>
              <div className="text-center">
                  <div className="w-16 h-16 bg-white dark:bg-slate-800 rounded-2xl shadow-md flex items-center justify-center mx-auto mb-6 text-2xl font-bold text-indigo-600 dark:text-indigo-400">3</div>
                  <h3 className="text-xl font-bold text-slate-900 dark:text-white mb-3">{t('step3Title')}</h3>
                  <p className="text-slate-600 dark:text-slate-400">{t('step3Desc')}</p>
              </div>
           </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-slate-900 text-slate-400 py-12 border-t border-slate-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 grid grid-cols-1 md:grid-cols-4 gap-8">
           <div>
              <h4 className="text-white text-lg font-bold mb-4">{t('brandName')}</h4>
              <p className="text-sm">Сервис поиска специалистов №1. Надежно, быстро, удобно.</p>
           </div>
           <div>
              <h4 className="text-white font-medium mb-4">{t('footerClients')}</h4>
              <ul className="space-y-2 text-sm">
                  <li><a href="#" className="hover:text-white">{t('createOrder')}</a></li>
                  <li><a href="#" className="hover:text-white">{t('safeDeal')}</a></li>
              </ul>
           </div>
           <div>
              <h4 className="text-white font-medium mb-4">{t('footerSpecialists')}</h4>
              <ul className="space-y-2 text-sm">
                  <li><a href="#" className="hover:text-white">База заказов</a></li>
                  <li><a href="#" className="hover:text-white">Тарифы</a></li>
              </ul>
           </div>
           <div>
              <h4 className="text-white font-medium mb-4">{t('footerContacts')}</h4>
              <p className="text-sm">support@profimatch.ru</p>
              <p className="text-sm mt-2">Москва, ул. Лесная 5</p>
           </div>
        </div>
      </footer>

      <TaskWizard 
        isOpen={isWizardOpen} 
        onClose={() => setIsWizardOpen(false)} 
        onTaskCreated={handleCreateTask}
      />

      {selectedSpecialist && (
        <SpecialistProfile 
          specialist={selectedSpecialist} 
          onClose={() => setSelectedSpecialist(null)} 
        />
      )}
    </div>
  );
};

const App: React.FC = () => {
  return (
    <AppProvider>
      <MainContent />
    </AppProvider>
  );
};

export default App;
