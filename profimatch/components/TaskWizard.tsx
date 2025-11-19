import React, { useState } from 'react';
import { X, Wand2, Loader2, MapPin, Calendar, Wallet, CheckCircle } from 'lucide-react';
import { analyzeTaskDescription } from '../services/geminiService';
import { Task } from '../types';
import { useApp } from '../contexts/AppContext';

interface TaskWizardProps {
  isOpen: boolean;
  onClose: () => void;
  onTaskCreated: (task: Task) => void;
}

export const TaskWizard: React.FC<TaskWizardProps> = ({ isOpen, onClose, onTaskCreated }) => {
  const { t, language } = useApp();
  const [step, setStep] = useState(1);
  const [rawInput, setRawInput] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [taskData, setTaskData] = useState<Partial<Task>>({
    location: language === 'ru' ? 'Москва' : 'Moskva',
    date: language === 'ru' ? 'В ближайшее время' : 'Tez orada'
  });

  if (!isOpen) return null;

  const handleAIAnalysis = async () => {
    if (!rawInput.trim()) return;
    
    setIsAnalyzing(true);
    const result = await analyzeTaskDescription(rawInput, language);
    setIsAnalyzing(false);

    if (result) {
      setTaskData(prev => ({
        ...prev,
        title: result.suggestedTitle,
        description: result.refinedDescription,
        category: result.suggestedCategory,
        budgetMin: result.estimatedBudgetMin,
        budgetMax: result.estimatedBudgetMax,
      }));
      setStep(2);
    }
  };

  const handleSubmit = () => {
    const newTask: Task = {
      id: Math.random().toString(36).substr(2, 9),
      title: taskData.title || 'Новая задача',
      description: taskData.description || '',
      category: taskData.category || 'Разное',
      budgetMin: taskData.budgetMin,
      budgetMax: taskData.budgetMax,
      location: taskData.location || 'Удаленно',
      date: taskData.date || 'По договоренности',
      status: 'open',
      createdAt: new Date(),
    };
    onTaskCreated(newTask);
    onClose();
    // Reset state
    setStep(1);
    setRawInput('');
    setTaskData({ 
        location: language === 'ru' ? 'Москва' : 'Moskva',
        date: language === 'ru' ? 'В ближайшее время' : 'Tez orada'
    });
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6">
      <div className="absolute inset-0 bg-slate-900/60 backdrop-blur-sm" onClick={onClose}></div>
      
      <div className="relative bg-white dark:bg-slate-900 rounded-2xl shadow-2xl w-full max-w-2xl flex flex-col max-h-[90vh] overflow-hidden animate-fade-in-up transition-colors duration-300">
        <div className="flex justify-between items-center p-6 border-b border-slate-100 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-800/50">
          <h2 className="text-xl font-bold text-slate-800 dark:text-white">
            {step === 1 ? t('wizardTitle1') : step === 2 ? t('wizardTitle2') : t('wizardTitle3')}
          </h2>
          <button onClick={onClose} className="p-2 text-slate-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-full transition">
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="p-6 overflow-y-auto flex-1">
          {step === 1 && (
            <div className="space-y-6">
              <div className="bg-indigo-50 dark:bg-indigo-900/20 border border-indigo-100 dark:border-indigo-800 p-4 rounded-xl flex gap-3">
                <Wand2 className="w-6 h-6 text-indigo-600 dark:text-indigo-400 flex-shrink-0 mt-0.5" />
                <div>
                  <p className="text-indigo-900 dark:text-indigo-200 font-medium">{t('useAiHelper')}</p>
                  <p className="text-indigo-700 dark:text-indigo-300 text-sm mt-1">{t('aiHelperDesc')}</p>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">{t('whatToDo')}</label>
                <textarea
                  value={rawInput}
                  onChange={(e) => setRawInput(e.target.value)}
                  placeholder={t('inputPlaceholder')}
                  className="w-full p-4 h-40 rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 resize-none text-slate-800 dark:text-white placeholder:text-slate-400"
                />
              </div>

              <div className="flex justify-end">
                <button
                  onClick={handleAIAnalysis}
                  disabled={isAnalyzing || !rawInput.trim()}
                  className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-3 rounded-xl font-semibold transition disabled:opacity-70 disabled:cursor-not-allowed shadow-lg shadow-indigo-200 dark:shadow-none"
                >
                  {isAnalyzing ? (
                    <>
                      <Loader2 className="w-5 h-5 animate-spin" />
                      {t('analyzing')}
                    </>
                  ) : (
                    <>
                      <Wand2 className="w-5 h-5" />
                      {t('continue')}
                    </>
                  )}
                </button>
              </div>
            </div>
          )}

          {step === 2 && (
            <div className="space-y-6 animate-fade-in">
              <div>
                <label className="block text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-1">{t('labelTitle')}</label>
                <input
                  type="text"
                  value={taskData.title}
                  onChange={(e) => setTaskData({...taskData, title: e.target.value})}
                  className="w-full px-4 py-3 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 focus:bg-white dark:focus:bg-slate-700 focus:ring-2 focus:ring-indigo-500 outline-none font-medium text-slate-800 dark:text-white"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-1">{t('labelCategory')}</label>
                <input
                  type="text"
                  value={taskData.category}
                  onChange={(e) => setTaskData({...taskData, category: e.target.value})}
                  className="w-full px-4 py-3 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 focus:bg-white dark:focus:bg-slate-700 focus:ring-2 focus:ring-indigo-500 outline-none text-slate-800 dark:text-white"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-1">{t('labelDesc')}</label>
                <textarea
                  value={taskData.description}
                  onChange={(e) => setTaskData({...taskData, description: e.target.value})}
                  rows={4}
                  className="w-full px-4 py-3 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 focus:bg-white dark:focus:bg-slate-700 focus:ring-2 focus:ring-indigo-500 outline-none text-slate-800 dark:text-white resize-none"
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-1">{t('labelBudget')} (₽)</label>
                  <div className="flex gap-2 items-center">
                    <input
                      type="number"
                      placeholder="От"
                      value={taskData.budgetMin || ''}
                      onChange={(e) => setTaskData({...taskData, budgetMin: parseInt(e.target.value)})}
                      className="w-full px-4 py-3 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 focus:ring-2 focus:ring-indigo-500 outline-none text-slate-800 dark:text-white"
                    />
                    <span className="text-slate-400">-</span>
                    <input
                      type="number"
                      placeholder="До"
                      value={taskData.budgetMax || ''}
                      onChange={(e) => setTaskData({...taskData, budgetMax: parseInt(e.target.value)})}
                      className="w-full px-4 py-3 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 focus:ring-2 focus:ring-indigo-500 outline-none text-slate-800 dark:text-white"
                    />
                  </div>
                </div>
                
                <div>
                   <label className="block text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-1">{t('labelDate')}</label>
                   <input
                      type="text"
                      value={taskData.date}
                      onChange={(e) => setTaskData({...taskData, date: e.target.value})}
                      className="w-full px-4 py-3 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 focus:ring-2 focus:ring-indigo-500 outline-none text-slate-800 dark:text-white"
                    />
                </div>
              </div>

              <div className="flex justify-between pt-4">
                <button 
                  onClick={() => setStep(1)}
                  className="text-slate-500 dark:text-slate-400 hover:text-indigo-600 font-medium px-4 py-2"
                >
                  {t('back')}
                </button>
                <button
                  onClick={() => setStep(3)}
                  className="bg-indigo-600 hover:bg-indigo-700 text-white px-8 py-3 rounded-xl font-semibold transition shadow-lg shadow-indigo-200 dark:shadow-none"
                >
                  {t('next')}
                </button>
              </div>
            </div>
          )}

          {step === 3 && (
             <div className="space-y-6 animate-fade-in text-center py-4">
                <div className="w-16 h-16 bg-green-100 dark:bg-green-900/30 rounded-full flex items-center justify-center mx-auto mb-4">
                  <CheckCircle className="w-8 h-8 text-green-600 dark:text-green-400" />
                </div>
                <h3 className="text-2xl font-bold text-slate-900 dark:text-white">{t('readyToPublish')}</h3>
                <p className="text-slate-600 dark:text-slate-400 max-w-md mx-auto">
                  {t('publishDesc')}
                </p>
                
                <div className="bg-slate-50 dark:bg-slate-800 p-4 rounded-xl text-left max-w-lg mx-auto border border-slate-200 dark:border-slate-700 space-y-3">
                    <div className="flex items-start gap-3">
                        <Wallet className="w-5 h-5 text-slate-400 mt-0.5" />
                        <div>
                            <p className="text-sm text-slate-500 dark:text-slate-400">{t('labelBudget')}</p>
                            <p className="font-medium text-slate-800 dark:text-slate-200">
                              {taskData.budgetMin && taskData.budgetMax 
                                ? `${taskData.budgetMin} - ${taskData.budgetMax} ₽`
                                : t('byAgreement')}
                            </p>
                        </div>
                    </div>
                    <div className="flex items-start gap-3">
                        <MapPin className="w-5 h-5 text-slate-400 mt-0.5" />
                        <div>
                            <p className="text-sm text-slate-500 dark:text-slate-400">Место</p>
                            <p className="font-medium text-slate-800 dark:text-slate-200">{taskData.location}</p>
                        </div>
                    </div>
                    <div className="flex items-start gap-3">
                        <Calendar className="w-5 h-5 text-slate-400 mt-0.5" />
                        <div>
                            <p className="text-sm text-slate-500 dark:text-slate-400">{t('labelDate')}</p>
                            <p className="font-medium text-slate-800 dark:text-slate-200">{taskData.date}</p>
                        </div>
                    </div>
                </div>

                <div className="flex justify-center gap-4 pt-6">
                   <button 
                    onClick={() => setStep(2)}
                    className="text-slate-500 dark:text-slate-400 hover:text-slate-800 dark:hover:text-white font-medium px-6 py-3"
                  >
                    {t('change')}
                  </button>
                  <button
                    onClick={handleSubmit}
                    className="bg-green-600 hover:bg-green-700 text-white px-10 py-3 rounded-xl font-bold transition shadow-lg shadow-green-200 dark:shadow-none"
                  >
                    {t('publishOrder')}
                  </button>
                </div>
             </div>
          )}
        </div>
        
        {step < 3 && (
            <div className="p-4 bg-slate-50 dark:bg-slate-800 border-t border-slate-100 dark:border-slate-700 flex justify-center">
                <div className="flex gap-2">
                    <div className={`w-2.5 h-2.5 rounded-full transition-colors ${step === 1 ? 'bg-indigo-600' : 'bg-slate-300 dark:bg-slate-600'}`}></div>
                    <div className={`w-2.5 h-2.5 rounded-full transition-colors ${step === 2 ? 'bg-indigo-600' : 'bg-slate-300 dark:bg-slate-600'}`}></div>
                    <div className={`w-2.5 h-2.5 rounded-full transition-colors ${step === 3 ? 'bg-indigo-600' : 'bg-slate-300 dark:bg-slate-600'}`}></div>
                </div>
            </div>
        )}
      </div>
    </div>
  );
};
