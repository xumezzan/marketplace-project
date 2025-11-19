import React from 'react';
import { Specialist } from '../types';
import { Star, MapPin, MessageSquare } from 'lucide-react';
import { useApp } from '../contexts/AppContext';

const MOCK_SPECIALISTS: Specialist[] = [
  {
    id: '1',
    name: 'Ашур Ахмедов',
    profession: 'Дизайнер архитектур (Зирабад)',
    rating: 4.9,
    reviewsCount: 142,
    // Updated avatar URL as requested
    avatarUrl: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?ixlib=rb-1.2.1&auto=format&fit=crop&w=256&q=80',
    categories: ['Ремонт', 'Дизайн'],
    about: 'Лучший дизайнер из Зирабада. Делаю элитные проекты, проектирую дворцы и современные коттеджи. Индивидуальный подход к каждому кирпичу.',
    hourlyRate: 5000,
    portfolio: [
      { id: 'p1', title: 'Проект виллы', description: 'Дизайн проект дома в горах', imageUrl: 'https://images.unsplash.com/photo-1600596542815-e4959b4820cf?auto=format&fit=crop&w=400&q=80' },
      { id: 'p2', title: 'Интерьер гостиной', description: 'Классический стиль', imageUrl: 'https://images.unsplash.com/photo-1600210492486-724fe5c67fb0?auto=format&fit=crop&w=400&q=80' }
    ],
    reviews: [
      { id: 'r1', author: 'Джамшид К.', rating: 5, date: '12.05.2024', text: 'Ашур ака мастер своего дела! Сделал проект дома, все соседи завидуют.' },
      { id: 'r2', author: 'Гульнара В.', rating: 5, date: '10.05.2024', text: 'Очень креативный подход. Зирабадская школа дизайна на высоте!' }
    ]
  },
  {
    id: '2',
    name: 'Нилюфар Каримова',
    profession: 'Репетитор по английскому',
    rating: 5.0,
    reviewsCount: 89,
    avatarUrl: 'https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?ixlib=rb-1.2.1&auto=format&fit=crop&w=256&q=80',
    categories: ['Обучение', 'Языки'],
    about: 'Преподаватель ВУЗа. Готовлю к IELTS, CEFR. Индивидуальный подход к каждому ученику. Первое занятие - бесплатно.',
    hourlyRate: 2000,
    portfolio: [
      { id: 'p3', title: 'Сертификат IELTS', description: 'Мой результат 8.5 баллов', imageUrl: 'https://images.unsplash.com/photo-1546410531-bb4caa6b424d?auto=format&fit=crop&w=400&q=80' }
    ],
    reviews: [
        { id: 'r3', author: 'Сардор М.', rating: 5, date: '15.04.2024', text: 'Дочь поступила в Вестминстер! Спасибо огромное Нилюфар.' }
    ]
  },
  {
    id: '3',
    name: 'Сардор Умаров',
    profession: 'Электрик профи',
    rating: 4.8,
    reviewsCount: 215,
    avatarUrl: 'https://images.unsplash.com/photo-1537511446984-935f663eb1f4?ixlib=rb-1.2.1&auto=format&fit=crop&w=256&q=80',
    categories: ['Электрика', 'Ремонт'],
    about: 'Все виды электромонтажных работ. Замена проводки, установка розеток, люстр. Работаю аккуратно и быстро.',
    hourlyRate: 1800,
    portfolio: [
        { id: 'p4', title: 'Сборка электрощита', description: 'Трехфазный щит для коттеджа', imageUrl: 'https://images.unsplash.com/photo-1621905251189-08b45d6a269e?auto=format&fit=crop&w=400&q=80' }
    ],
    reviews: [
        { id: 'r4', author: 'Игорь П.', rating: 4, date: '20.03.2024', text: 'Сделал хорошо, но опоздал на 15 минут.' }
    ]
  },
    {
    id: '4',
    name: 'Зарина Юсупова',
    profession: 'Косметолог, Визажист',
    rating: 4.9,
    reviewsCount: 56,
    avatarUrl: 'https://images.unsplash.com/photo-1580489944761-15a19d654956?ixlib=rb-1.2.1&auto=format&fit=crop&w=256&q=80',
    categories: ['Красота', 'Макияж'],
    about: 'Дипломированный специалист. Использую только профессиональную косметику. Принимаю в салоне и выезжаю на дом.',
    hourlyRate: 3000,
    portfolio: [
        { id: 'p5', title: 'Свадебный макияж', description: 'Нежный образ невесты', imageUrl: 'https://images.unsplash.com/photo-1487412720507-e7ab37603c6f?auto=format&fit=crop&w=400&q=80' },
        { id: 'p6', title: 'Вечерний образ', description: 'Смоки айс', imageUrl: 'https://images.unsplash.com/photo-1596704017254-9b121068fb31?auto=format&fit=crop&w=400&q=80' }
    ],
    reviews: [
        { id: 'r5', author: 'Азиза К.', rating: 5, date: '01.06.2024', text: 'Макияж продержался весь день! Зарина волшебница.' }
    ]
  }
];

interface SpecialistsListProps {
  onSelectSpecialist: (specialist: Specialist) => void;
}

export const SpecialistsList: React.FC<SpecialistsListProps> = ({ onSelectSpecialist }) => {
  const { t } = useApp();

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
      <div className="flex justify-between items-end mb-8">
        <div>
            <h2 className="text-3xl font-bold text-slate-900 dark:text-white">{t('recSpecialists')}</h2>
            <p className="text-slate-500 dark:text-slate-400 mt-2">{t('recSubtitle')}</p>
        </div>
        <button className="text-indigo-600 dark:text-indigo-400 font-medium hover:text-indigo-700 dark:hover:text-indigo-300 hidden sm:block">{t('viewAll')} &rarr;</button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {MOCK_SPECIALISTS.map((specialist) => (
          <div 
            key={specialist.id} 
            onClick={() => onSelectSpecialist(specialist)}
            className="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm hover:shadow-xl hover:-translate-y-1 transition duration-300 flex flex-col overflow-hidden group cursor-pointer"
          >
            <div className="p-6 flex flex-col items-center text-center border-b border-slate-50 dark:border-slate-700 flex-grow">
              <div className="relative">
                <img 
                  src={specialist.avatarUrl} 
                  alt={specialist.name} 
                  className="w-24 h-24 rounded-full object-cover border-4 border-white dark:border-slate-700 shadow-md mb-4 group-hover:scale-105 transition duration-300"
                />
                <div className="absolute bottom-4 right-0 bg-green-500 w-4 h-4 rounded-full border-2 border-white dark:border-slate-700"></div>
              </div>
              
              <h3 className="text-lg font-bold text-slate-900 dark:text-white">{specialist.name}</h3>
              <p className="text-sm text-slate-500 dark:text-slate-400 mb-3">{specialist.profession}</p>
              
              <div className="flex items-center gap-1 bg-amber-50 dark:bg-amber-900/30 px-2 py-1 rounded-md mb-4">
                <Star className="w-4 h-4 text-amber-500 fill-current" />
                <span className="font-bold text-slate-900 dark:text-amber-100 text-sm">{specialist.rating}</span>
                <span className="text-slate-400 dark:text-slate-400 text-xs">({specialist.reviews.length} {t('reviewsCountSuffix')})</span>
              </div>

              <p className="text-sm text-slate-600 dark:text-slate-300 line-clamp-3 mb-4">{specialist.about}</p>
              
              <div className="mt-auto flex gap-2 text-xs text-slate-400 dark:text-slate-500 w-full justify-center border-t border-slate-50 dark:border-slate-700 pt-3">
                 <span className="flex items-center gap-1"><MessageSquare className="w-3 h-3" /> {specialist.reviews.length}</span>
                 <span>•</span>
                 <span>{specialist.portfolio.length} {t('worksCount')}</span>
              </div>
            </div>
            
            <div className="p-4 bg-slate-50 dark:bg-slate-800/50 flex justify-between items-center">
                <span className="font-semibold text-slate-900 dark:text-white">{t('fromRate')} {specialist.hourlyRate} {t('perHour')}</span>
                <div className="p-2 bg-white dark:bg-slate-700 border border-slate-200 dark:border-slate-600 rounded-full text-indigo-600 dark:text-indigo-400 group-hover:bg-indigo-600 group-hover:text-white transition-colors">
                    <span className="text-sm font-medium px-2 group-hover:hidden">{t('profile')}</span>
                    <span className="text-sm font-medium px-2 hidden group-hover:inline">{t('openProfile')}</span>
                </div>
            </div>
          </div>
        ))}
      </div>
       <div className="mt-6 sm:hidden text-center">
        <a href="#" className="text-indigo-600 font-medium hover:text-indigo-700">{t('viewAll')} &rarr;</a>
      </div>
    </div>
  );
};