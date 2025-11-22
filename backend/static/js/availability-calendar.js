class AvailabilityCalendar {
    constructor(specialistId) {
        this.specialistId = specialistId;
        this.currentDate = new Date();
        this.selectedDate = null;
        this.selectedTime = null;

        this.elements = {
            prevMonth: document.getElementById('prevMonth'),
            nextMonth: document.getElementById('nextMonth'),
            currentMonthYear: document.getElementById('currentMonthYear'),
            calendarDays: document.getElementById('calendarDays'),
            timeSlotsContainer: document.getElementById('timeSlotsContainer'),
            timeSlotsGrid: document.getElementById('timeSlotsGrid'),
            selectedDateDisplay: document.getElementById('selectedDateDisplay'),
            loading: document.getElementById('calendarLoading'),
            inputDate: document.getElementById('selectedDate'),
            inputTime: document.getElementById('selectedTime')
        };

        this.init();
    }

    init() {
        this.elements.prevMonth.addEventListener('click', () => this.changeMonth(-1));
        this.elements.nextMonth.addEventListener('click', () => this.changeMonth(1));
        this.renderCalendar();
    }

    changeMonth(delta) {
        this.currentDate.setMonth(this.currentDate.getMonth() + delta);
        this.renderCalendar();
    }

    async renderCalendar() {
        const year = this.currentDate.getFullYear();
        const month = this.currentDate.getMonth();

        this.elements.currentMonthYear.textContent = new Date(year, month).toLocaleString('ru', { month: 'long', year: 'numeric' });
        this.elements.calendarDays.innerHTML = '';

        // Get first day of month and days in month
        const firstDay = new Date(year, month, 1).getDay() || 7; // 1 (Mon) - 7 (Sun)
        const daysInMonth = new Date(year, month + 1, 0).getDate();

        // Empty slots for previous month
        for (let i = 1; i < firstDay; i++) {
            this.elements.calendarDays.innerHTML += '<div></div>';
        }

        // Fetch availability for this month
        const availability = await this.fetchAvailability(year, month + 1);

        // Render days
        for (let day = 1; day <= daysInMonth; day++) {
            const dateStr = `${year}-${String(month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
            const isAvailable = availability.dates.includes(dateStr);
            const isPast = new Date(dateStr) < new Date().setHours(0, 0, 0, 0);
            const isSelected = this.selectedDate === dateStr;

            const dayEl = document.createElement('div');
            dayEl.className = `
                aspect-square flex items-center justify-center rounded-lg text-sm font-medium transition cursor-pointer
                ${isSelected ? 'bg-indigo-600 text-white' : ''}
                ${!isPast && isAvailable && !isSelected ? 'hover:bg-indigo-50 text-slate-700 dark:text-slate-300 dark:hover:bg-slate-700' : ''}
                ${isPast || !isAvailable ? 'text-slate-300 dark:text-slate-600 cursor-not-allowed' : ''}
            `;
            dayEl.textContent = day;

            if (!isPast && isAvailable) {
                dayEl.onclick = () => this.selectDate(dateStr, dayEl);
            }

            this.elements.calendarDays.appendChild(dayEl);
        }
    }

    async fetchAvailability(year, month) {
        try {
            const response = await fetch(`/api/specialist/${this.specialistId}/availability/?year=${year}&month=${month}`);
            if (!response.ok) throw new Error('Failed to fetch availability');
            return await response.json();
        } catch (error) {
            console.error('Error fetching availability:', error);
            return { dates: [] };
        }
    }

    async selectDate(dateStr, element) {
        // Update UI
        document.querySelectorAll('#calendarDays > div').forEach(el => {
            el.classList.remove('bg-indigo-600', 'text-white');
            if (!el.classList.contains('text-slate-300')) {
                el.classList.add('hover:bg-indigo-50');
            }
        });
        element.classList.add('bg-indigo-600', 'text-white');
        element.classList.remove('hover:bg-indigo-50');

        this.selectedDate = dateStr;
        this.elements.inputDate.value = dateStr;
        this.elements.selectedDateDisplay.textContent = new Date(dateStr).toLocaleDateString('ru');

        // Hide booking form if open
        document.getElementById('bookingForm').classList.add('hidden');

        await this.loadTimeSlots(dateStr);
    }

    async loadTimeSlots(dateStr) {
        this.elements.timeSlotsContainer.classList.remove('hidden');
        this.elements.timeSlotsGrid.innerHTML = '<div class="col-span-3 text-center py-4"><div class="animate-spin rounded-full h-6 w-6 border-b-2 border-indigo-600 mx-auto"></div></div>';

        try {
            const response = await fetch(`/api/specialist/${this.specialistId}/availability/?date=${dateStr}`);
            if (!response.ok) throw new Error('Failed to fetch slots');
            const data = await response.json();
            const slots = data.slots || [];

            this.elements.timeSlotsGrid.innerHTML = '';

            if (slots.length === 0) {
                this.elements.timeSlotsGrid.innerHTML = '<div class="col-span-3 text-center py-2 text-slate-500 text-sm">Нет свободного времени</div>';
                return;
            }

            slots.forEach(time => {
                const slotBtn = document.createElement('button');
                slotBtn.type = 'button';
                slotBtn.className = `
                    py-2 px-3 rounded-lg border text-sm font-medium transition
                    ${this.selectedTime === time
                        ? 'bg-indigo-600 border-indigo-600 text-white'
                        : 'border-slate-200 text-slate-700 hover:border-indigo-600 hover:text-indigo-600 dark:border-slate-700 dark:text-slate-300'}
                `;
                slotBtn.textContent = time;
                slotBtn.onclick = () => this.selectTime(time, slotBtn);
                this.elements.timeSlotsGrid.appendChild(slotBtn);
            });
        } catch (error) {
            console.error('Error fetching slots:', error);
            this.elements.timeSlotsGrid.innerHTML = '<div class="col-span-3 text-center py-2 text-red-500 text-sm">Ошибка загрузки</div>';
        }
    }

    selectTime(time, element) {
        this.selectedTime = time;
        this.elements.inputTime.value = time;

        // Update UI
        this.elements.timeSlotsGrid.querySelectorAll('button').forEach(btn => {
            btn.className = 'py-2 px-3 rounded-lg border border-slate-200 text-slate-700 hover:border-indigo-600 hover:text-indigo-600 dark:border-slate-700 dark:text-slate-300 text-sm font-medium transition';
        });
        element.className = 'py-2 px-3 rounded-lg border border-indigo-600 bg-indigo-600 text-white text-sm font-medium transition';

        // Show booking form
        const bookingForm = document.getElementById('bookingForm');
        if (bookingForm) {
            bookingForm.classList.remove('hidden');
            document.getElementById('bookingDateDisplay').textContent = new Date(this.selectedDate).toLocaleDateString('ru');
            document.getElementById('bookingTimeDisplay').textContent = time;
            bookingForm.scrollIntoView({ behavior: 'smooth' });
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('booking-calendar-component')) {
        new AvailabilityCalendar(specialistId);
    }
});
