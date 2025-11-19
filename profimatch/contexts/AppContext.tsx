import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

type Language = 'ru' | 'uz';
type Theme = 'light' | 'dark';

interface Translations {
  [key: string]: {
    ru: string;
    uz: string;
  };
}

const dictionary: Translations = {
  // Navbar
  brandName: { ru: 'ProfiMatch', uz: 'ProfiMatch' },
  findSpecialist: { ru: 'Найти специалиста', uz: 'Mutaxassis topish' },
  myOrders: { ru: 'Мои заказы', uz: 'Buyurtmalarim' },
  becomeSpecialist: { ru: 'Стать специалистом', uz: 'Mutaxassis bo\'lish' },
  createOrder: { ru: 'Создать заказ', uz: 'Buyurtma yaratish' },

  // Hero
  heroTitle1: { ru: 'Найдите профи', uz: 'O\'z ishingiz ustasini' },
  heroTitle2: { ru: 'для любой задачи', uz: 'tez va oson toping' },
  heroSubtitle: { ru: 'Миллионы специалистов готовы помочь с ремонтом, обучением, красотой и другими услугами. Создайте заказ за пару минут.', uz: 'Ta\'mirlash, ta\'lim, go\'zallik va boshqa xizmatlar bo\'yicha millionlab mutaxassislar yordam berishga tayyor. Bir necha daqiqada buyurtma yarating.' },
  searchPlaceholder: { ru: 'Репетитор по английскому, сантехник...', uz: 'Ingliz tili repetitori, santexnik...' },
  findButton: { ru: 'Найти специалиста', uz: 'Mutaxassis topish' },
  verifiedProfiles: { ru: 'Проверенные анкеты', uz: 'Tasdiqlangan anketalar' },
  honestReviews: { ru: 'Честные отзывы', uz: 'Haqiqiy sharhlar' },
  profiCount: { ru: '2.5 млн профи', uz: '2.5 mln mutaxassis' },

  // Categories
  catRepair: { ru: 'Ремонт и стройка', uz: 'Ta\'mirlash va qurilish' },
  catEducation: { ru: 'Репетиторы', uz: 'Repetitorlar' },
  catBeauty: { ru: 'Красота', uz: 'Go\'zallik' },
  catTransport: { ru: 'Перевозки', uz: 'Yuk tashish' },
  catIt: { ru: 'IT и фриланс', uz: 'IT va frilans' },
  catOther: { ru: 'Мастер на час', uz: 'Bir soatlik usta' },
  catPopular: { ru: 'Популярные категории', uz: 'Ommabop toifalar' },

  // Specialist List
  recSpecialists: { ru: 'Рекомендуемые специалисты', uz: 'Tavsiya etilgan mutaxassislar' },
  recSubtitle: { ru: 'Профессионалы с высоким рейтингом, готовые помочь', uz: 'Yuqori reytingli, yordamga tayyor professionallar' },
  viewAll: { ru: 'Смотреть всех', uz: 'Barchasini ko\'rish' },
  fromRate: { ru: 'от', uz: 'boshlab' },
  perHour: { ru: '₽/ч', uz: 'so\'m/soat' },
  openProfile: { ru: 'Открыть', uz: 'Ochish' },
  profile: { ru: 'Профиль', uz: 'Profil' },
  worksCount: { ru: 'работ', uz: 'ishlar' },
  reviewsCountSuffix: { ru: 'отзывов', uz: 'sharh' },

  // Wizard
  wizardTitle1: { ru: 'Опишите задачу', uz: 'Vazifani tavsiflang' },
  wizardTitle2: { ru: 'Уточнение деталей', uz: 'Tafsilotlarni aniqlashtirish' },
  wizardTitle3: { ru: 'Проверка', uz: 'Tekshirish' },
  useAiHelper: { ru: 'Используйте ИИ для помощи', uz: 'AI yordamidan foydalaning' },
  aiHelperDesc: { ru: 'Просто напишите своими словами, что нужно сделать. Мы автоматически заполним детали, категорию и предложим цену.', uz: 'Shunchaki nima qilish kerakligini o\'z so\'zlaringiz bilan yozing. Biz tafsilotlarni, toifani avtomatik to\'ldiramiz va narx taklif qilamiz.' },
  whatToDo: { ru: 'Что нужно сделать?', uz: 'Nima qilish kerak?' },
  inputPlaceholder: { ru: 'Например: Нужно починить протекающий кран на кухне...', uz: 'Masalan: Oshxonadagi oqayotgan kranni tuzatish kerak...' },
  analyzing: { ru: 'Анализируем...', uz: 'Tahlil qilinmoqda...' },
  continue: { ru: 'Продолжить', uz: 'Davom etish' },
  
  labelTitle: { ru: 'Заголовок', uz: 'Sarlavha' },
  labelCategory: { ru: 'Категория', uz: 'Toifa' },
  labelDesc: { ru: 'Подробное описание', uz: 'Batafsil tavsif' },
  labelBudget: { ru: 'Бюджет', uz: 'Byudjet' },
  labelDate: { ru: 'Когда', uz: 'Qachon' },
  back: { ru: 'Назад', uz: 'Orqaga' },
  next: { ru: 'Далее', uz: 'Keyingisi' },
  
  readyToPublish: { ru: 'Всё готово к публикации!', uz: 'Chop etishga tayyor!' },
  publishDesc: { ru: 'Ваша задача будет видна тысячам специалистов. Обычно первые отклики приходят в течение 15 минут.', uz: 'Vazifangiz minglab mutaxassislarga ko\'rinadi. Odatda birinchi javoblar 15 daqiqa ichida keladi.' },
  change: { ru: 'Изменить', uz: 'O\'zgartirish' },
  publishOrder: { ru: 'Опубликовать заказ', uz: 'Buyurtmani chop etish' },
  byAgreement: { ru: 'По договоренности', uz: 'Kelishuv bo\'yicha' },

  // Profile & Safe Deal
  aboutSelf: { ru: 'О себе', uz: 'O\'zi haqida' },
  portfolio: { ru: 'Портфолио', uz: 'Portfolio' },
  reviews: { ru: 'Отзывы', uz: 'Sharhlar' },
  safeDeal: { ru: 'Безопасная сделка', uz: 'Xavfsiz bitim' },
  safeDealDesc: { ru: 'Деньги резервируются на счете и переводятся исполнителю только после того, как вы подтвердите выполнение работы.', uz: 'Pillar hisobda band qilinadi va faqat ish bajarilganini tasdiqlaganingizdan so\'ng ijrochiga o\'tkaziladi.' },
  offerOrder: { ru: 'Предложить заказ', uz: 'Buyurtma taklif qilish' },
  reserving: { ru: 'Резервирование средств...', uz: 'Mablag\'lar band qilinmoqda...' },
  fundsLocked: { ru: 'Средства заблокированы', uz: 'Mablag\'lar bloklandi' },
  fundsLockedDesc: { ru: 'Исполнитель работает. Нажмите кнопку ниже, когда работа будет выполнена.', uz: 'Ijrochi ishlamoqda. Ish bajarilganda quyidagi tugmani bosing.' },
  confirmCompletion: { ru: 'Подтвердить выполнение', uz: 'Bajarilganini tasdiqlash' },
  dealClosed: { ru: 'Сделка закрыта', uz: 'Bitim yopildi' },
  leaveReview: { ru: 'Оставить отзыв', uz: 'Sharh qoldirish' },
  reviewPlaceholder: { ru: 'Как прошла работа со специалистом?', uz: 'Mutaxassis bilan ishlash qanday o\'tdi?' },
  addWork: { ru: 'Добавить работу', uz: 'Ish qo\'shish' },
  noWorks: { ru: 'Нет загруженных работ', uz: 'Yuklangan ishlar yo\'q' },
  changePhoto: { ru: 'Сменить фото', uz: 'Rasmni o\'zgartirish' },

  // How it works
  howItWorks: { ru: 'Как это работает', uz: 'Bu qanday ishlaydi' },
  howItWorksSub: { ru: 'Мы сделали процесс поиска максимально простым и безопасным для обеих сторон.', uz: 'Biz qidiruv jarayonini har ikki tomon uchun maksimal darajada sodda va xavfsiz qildik.' },
  step1Title: { ru: 'Создайте задачу', uz: 'Vazifa yarating' },
  step1Desc: { ru: 'Опишите, что нужно сделать. Искусственный интеллект поможет сформулировать требования и оценить бюджет.', uz: 'Nima qilish kerakligini tavsiflang. Sun\'iy intellekt talablarni shakllantirish va byudjetni baholashda yordam beradi.' },
  step2Title: { ru: 'Получите отклики', uz: 'Takliflarni oling' },
  step2Desc: { ru: 'Специалисты сами предложат свои услуги и цены. Вам останется только сравнить отзывы и выбрать.', uz: 'Mutaxassislar o\'zlari xizmat va narxlarini taklif qilishadi. Siz faqat sharhlarni taqqoslab, tanlashingiz kerak.' },
  step3Title: { ru: 'Договоритесь о работе', uz: 'Ish haqida kelishing' },
  step3Desc: { ru: 'Обсудите детали в чате. Оплата производится напрямую специалисту после выполнения работы.', uz: 'Tafsilotlarni chatda muhokama qiling. To\'lov ish bajarilgandan so\'ng to\'g\'ridan-to\'g\'ri mutaxassisga amalga oshiriladi.' },
  
  // Footer
  footerClients: { ru: 'Клиентам', uz: 'Mijozlarga' },
  footerSpecialists: { ru: 'Специалистам', uz: 'Mutaxassislarga' },
  footerContacts: { ru: 'Контакты', uz: 'Aloqa' },
};

interface AppContextType {
  language: Language;
  setLanguage: (lang: Language) => void;
  theme: Theme;
  toggleTheme: () => void;
  t: (key: string) => string;
}

const AppContext = createContext<AppContextType | undefined>(undefined);

export const AppProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [language, setLanguage] = useState<Language>('ru');
  const [theme, setTheme] = useState<Theme>('light');

  useEffect(() => {
    // Load saved preferences
    const savedLang = localStorage.getItem('app_lang') as Language;
    if (savedLang) setLanguage(savedLang);

    const savedTheme = localStorage.getItem('app_theme') as Theme;
    if (savedTheme) {
      setTheme(savedTheme);
    } else if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
      setTheme('dark');
    }
  }, []);

  useEffect(() => {
    localStorage.setItem('app_lang', language);
  }, [language]);

  useEffect(() => {
    localStorage.setItem('app_theme', theme);
    if (theme === 'dark') {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [theme]);

  const toggleTheme = () => {
    setTheme(prev => prev === 'light' ? 'dark' : 'light');
  };

  const t = (key: string): string => {
    if (!dictionary[key]) return key;
    return dictionary[key][language];
  };

  return (
    <AppContext.Provider value={{ language, setLanguage, theme, toggleTheme, t }}>
      {children}
    </AppContext.Provider>
  );
};

export const useApp = () => {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useApp must be used within an AppProvider');
  }
  return context;
};