import React, { useState, useRef } from 'react';
import { Specialist, Review } from '../types';
import { Star, MapPin, X, Shield, CheckCircle, Lock, Image as ImageIcon, Send, Camera } from 'lucide-react';
import { useApp } from '../contexts/AppContext';

interface SpecialistProfileProps {
  specialist: Specialist;
  onClose: () => void;
}

type DealStatus = 'idle' | 'escrow_pending' | 'work_in_progress' | 'completed';

export const SpecialistProfile: React.FC<SpecialistProfileProps> = ({ specialist, onClose }) => {
  const { t } = useApp();
  const [activeTab, setActiveTab] = useState<'portfolio' | 'reviews'>('portfolio');
  const [dealStatus, setDealStatus] = useState<DealStatus>('idle');
  const [newReviewText, setNewReviewText] = useState('');
  const [reviews, setReviews] = useState<Review[]>(specialist.reviews);
  const [currentAvatar, setCurrentAvatar] = useState(specialist.avatarUrl);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleHire = () => {
    // Simulate Secure Transaction Logic
    setDealStatus('escrow_pending');
    setTimeout(() => {
      setDealStatus('work_in_progress');
    }, 1500);
  };

  const handleCompleteDeal = () => {
    setDealStatus('completed');
  };

  const handleSubmitReview = () => {
    if (!newReviewText.trim()) return;
    
    const newReview: Review = {
      id: Math.random().toString(),
      author: 'Вы (Клиент)',
      date: new Date().toLocaleDateString('ru-RU'),
      rating: 5,
      text: newReviewText
    };
    
    setReviews([newReview, ...reviews]);
    setNewReviewText('');
  };

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        if (typeof reader.result === 'string') {
          setCurrentAvatar(reader.result);
        }
      };
      reader.readAsDataURL(file);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6">
      <div className="absolute inset-0 bg-slate-900/60 backdrop-blur-sm" onClick={onClose}></div>
      
      <div className="relative bg-white dark:bg-slate-900 rounded-2xl shadow-2xl w-full max-w-4xl max-h-[90vh] overflow-hidden flex flex-col md:flex-row animate-fade-in-up transition-colors duration-300">
        <button onClick={onClose} className="absolute top-4 right-4 z-10 p-2 bg-white/80 dark:bg-slate-800/80 rounded-full hover:bg-red-50 dark:hover:bg-red-900/20 hover:text-red-500 transition">
          <X className="w-5 h-5 text-slate-600 dark:text-slate-300" />
        </button>

        {/* Left Sidebar: Profile Info */}
        <div className="w-full md:w-1/3 bg-slate-50 dark:bg-slate-800 p-6 border-r border-slate-200 dark:border-slate-700 overflow-y-auto">
          <div className="flex flex-col items-center text-center">
            <div className="relative group cursor-pointer" onClick={() => fileInputRef.current?.click()}>
              <img 
                src={currentAvatar} 
                alt={specialist.name} 
                className="w-32 h-32 rounded-full object-cover border-4 border-white dark:border-slate-700 shadow-lg mb-4 group-hover:opacity-80 transition"
              />
              <div className="absolute inset-0 rounded-full flex items-center justify-center bg-black/30 opacity-0 group-hover:opacity-100 transition mb-4">
                 <Camera className="w-8 h-8 text-white" />
              </div>
              <div className="absolute bottom-4 right-2 bg-indigo-600 p-1.5 rounded-full text-white shadow-sm group-hover:scale-110 transition">
                 <Camera className="w-4 h-4" />
              </div>
              <input 
                type="file" 
                ref={fileInputRef} 
                className="hidden" 
                accept="image/*" 
                onChange={handleFileChange} 
              />
            </div>
            
            <h2 className="text-xl font-bold text-slate-900 dark:text-white">{specialist.name}</h2>
            <p className="text-indigo-600 dark:text-indigo-400 font-medium mb-2">{specialist.profession}</p>
            
            <button onClick={() => fileInputRef.current?.click()} className="text-xs text-slate-400 hover:text-indigo-600 dark:hover:text-indigo-400 mb-4 underline decoration-dashed">
                {t('changePhoto')}
            </button>
            
            <div className="flex items-center gap-1 bg-white dark:bg-slate-700 border border-slate-200 dark:border-slate-600 px-3 py-1 rounded-full mb-6 shadow-sm">
              <Star className="w-4 h-4 text-amber-500 fill-current" />
              <span className="font-bold text-slate-900 dark:text-white">{specialist.rating}</span>
              <span className="text-slate-400 dark:text-slate-300 text-xs">({reviews.length} {t('reviewsCountSuffix')})</span>
            </div>

            <div className="w-full text-left space-y-4">
              <div>
                <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1">{t('aboutSelf')}</h3>
                <p className="text-sm text-slate-600 dark:text-slate-300 leading-relaxed">{specialist.about}</p>
              </div>
              <div>
                <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1">Ставка</h3>
                <p className="text-lg font-semibold text-slate-900 dark:text-white">{t('fromRate')} {specialist.hourlyRate} {t('perHour')}</p>
              </div>
            </div>
          </div>

          {/* Safe Deal Widget */}
          <div className="mt-8 bg-white dark:bg-slate-700 border border-indigo-100 dark:border-slate-600 rounded-xl p-4 shadow-sm">
            <div className="flex items-center gap-2 mb-3">
              <Shield className={`w-5 h-5 ${dealStatus === 'completed' ? 'text-green-500' : 'text-indigo-600 dark:text-indigo-400'}`} />
              <span className="font-bold text-slate-900 dark:text-white">{t('safeDeal')}</span>
            </div>
            
            {dealStatus === 'idle' && (
              <>
                <p className="text-xs text-slate-500 dark:text-slate-300 mb-4">
                  {t('safeDealDesc')}
                </p>
                <button 
                  onClick={handleHire}
                  className="w-full bg-indigo-600 hover:bg-indigo-700 text-white py-2.5 rounded-lg text-sm font-semibold transition shadow-md"
                >
                  {t('offerOrder')}
                </button>
              </>
            )}

            {dealStatus === 'escrow_pending' && (
              <div className="flex flex-col items-center py-4">
                <div className="w-6 h-6 border-2 border-indigo-600 border-t-transparent rounded-full animate-spin mb-2"></div>
                <span className="text-sm font-medium text-indigo-800 dark:text-indigo-300">{t('reserving')}</span>
              </div>
            )}

            {dealStatus === 'work_in_progress' && (
              <div className="bg-green-50 dark:bg-green-900/30 border border-green-100 dark:border-green-800 rounded-lg p-3">
                <div className="flex items-center gap-2 mb-2">
                   <Lock className="w-4 h-4 text-green-600 dark:text-green-400" />
                   <span className="text-sm font-bold text-green-800 dark:text-green-200">{t('fundsLocked')}</span>
                </div>
                <p className="text-xs text-green-700 dark:text-green-300 mb-3">
                  {t('fundsLockedDesc')}
                </p>
                <button 
                  onClick={handleCompleteDeal}
                  className="w-full bg-green-600 hover:bg-green-700 text-white py-2 rounded-lg text-sm font-semibold transition"
                >
                  {t('confirmCompletion')}
                </button>
              </div>
            )}

            {dealStatus === 'completed' && (
              <div className="text-center py-2">
                <div className="w-10 h-10 bg-green-100 dark:bg-green-900/30 rounded-full flex items-center justify-center mx-auto mb-2">
                  <CheckCircle className="w-6 h-6 text-green-600 dark:text-green-400" />
                </div>
                <p className="text-sm font-bold text-slate-800 dark:text-white">{t('dealClosed')}</p>
                <p className="text-xs text-slate-500 dark:text-slate-400">Средства переведены исполнителю</p>
              </div>
            )}
          </div>
        </div>

        {/* Right Content: Tabs */}
        <div className="flex-1 flex flex-col h-full overflow-hidden">
          <div className="flex border-b border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 sticky top-0 z-10">
            <button 
              onClick={() => setActiveTab('portfolio')}
              className={`flex-1 py-4 text-sm font-semibold text-center transition ${activeTab === 'portfolio' ? 'text-indigo-600 dark:text-indigo-400 border-b-2 border-indigo-600 dark:border-indigo-400' : 'text-slate-500 dark:text-slate-400 hover:text-slate-800 dark:hover:text-white'}`}
            >
              {t('portfolio')} ({specialist.portfolio.length})
            </button>
            <button 
              onClick={() => setActiveTab('reviews')}
              className={`flex-1 py-4 text-sm font-semibold text-center transition ${activeTab === 'reviews' ? 'text-indigo-600 dark:text-indigo-400 border-b-2 border-indigo-600 dark:border-indigo-400' : 'text-slate-500 dark:text-slate-400 hover:text-slate-800 dark:hover:text-white'}`}
            >
              {t('reviews')} ({reviews.length})
            </button>
          </div>

          <div className="flex-1 overflow-y-auto p-6 bg-white dark:bg-slate-900">
            {activeTab === 'portfolio' && (
              <div className="space-y-6">
                 <div className="flex justify-between items-center">
                    <h3 className="font-bold text-slate-900 dark:text-white">Примеры работ</h3>
                    <button className="text-xs flex items-center gap-1 text-indigo-600 dark:text-indigo-400 font-medium hover:underline">
                        <ImageIcon className="w-3 h-3" />
                        {t('addWork')}
                    </button>
                 </div>
                 
                 {specialist.portfolio.length > 0 ? (
                   <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                      {specialist.portfolio.map(item => (
                        <div key={item.id} className="group relative rounded-xl overflow-hidden border border-slate-100 dark:border-slate-700 shadow-sm">
                          <img src={item.imageUrl} alt={item.title} className="w-full h-48 object-cover transition duration-500 group-hover:scale-105" />
                          <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity flex flex-col justify-end p-4">
                            <p className="text-white font-bold text-sm">{item.title}</p>
                            <p className="text-white/80 text-xs">{item.description}</p>
                          </div>
                        </div>
                      ))}
                   </div>
                 ) : (
                   <div className="text-center py-10 text-slate-400">
                     {t('noWorks')}
                   </div>
                 )}
              </div>
            )}

            {activeTab === 'reviews' && (
              <div className="space-y-6">
                 <div className="bg-slate-50 dark:bg-slate-800 p-4 rounded-xl border border-slate-100 dark:border-slate-700">
                    <h4 className="text-sm font-bold text-slate-900 dark:text-white mb-2">{t('leaveReview')}</h4>
                    <div className="flex gap-2">
                      <input 
                        type="text" 
                        value={newReviewText}
                        onChange={(e) => setNewReviewText(e.target.value)}
                        placeholder={t('reviewPlaceholder')}
                        className="flex-1 px-4 py-2 rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-900 dark:text-white focus:ring-2 focus:ring-indigo-500 outline-none text-sm"
                      />
                      <button 
                        onClick={handleSubmitReview}
                        disabled={!newReviewText.trim()}
                        className="bg-indigo-600 hover:bg-indigo-700 disabled:bg-slate-300 dark:disabled:bg-slate-700 text-white p-2 rounded-lg transition"
                      >
                        <Send className="w-5 h-5" />
                      </button>
                    </div>
                 </div>

                 <div className="space-y-4">
                    {reviews.map(review => (
                      <div key={review.id} className="border-b border-slate-100 dark:border-slate-800 last:border-0 pb-4 last:pb-0">
                        <div className="flex justify-between items-start mb-1">
                           <span className="font-bold text-slate-900 dark:text-white">{review.author}</span>
                           <span className="text-xs text-slate-400">{review.date}</span>
                        </div>
                        <div className="flex mb-2">
                          {[...Array(5)].map((_, i) => (
                            <Star 
                              key={i} 
                              className={`w-3 h-3 ${i < review.rating ? 'text-amber-400 fill-current' : 'text-slate-200 dark:text-slate-700'}`} 
                            />
                          ))}
                        </div>
                        <p className="text-slate-600 dark:text-slate-300 text-sm">{review.text}</p>
                      </div>
                    ))}
                 </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};