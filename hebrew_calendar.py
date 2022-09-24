import calendar
from telegram_bot_calendar import DetailedTelegramCalendar, DAY

class HebrewCalendar(DetailedTelegramCalendar):
    def __init__(self, calendar_id=0, current_date=None, additional_buttons=None, locale='he',
                 min_date=None, max_date=None, telethon=False, **kwargs):
        if locale == 'he':
            self.prev_button, self.next_button = self.next_button, self.prev_button
            calendar.setfirstweekday(calendar.SUNDAY)

        super(HebrewCalendar, self).__init__(
            calendar_id=calendar_id, current_date=current_date,
            additional_buttons=additional_buttons, locale=locale,
            min_date=min_date, max_date=max_date, telethon=telethon, **kwargs)

        self.months['he'] = ['יאנ', 'פבר', 'מרץ', 'אפר', 'מאי', 'יונ', 'יול', 'אוג', 'ספט', 'אוק', 'נוב', 'דצמ']
        self.days_of_week['he'] = ['א', 'ב', 'ג', 'ד', 'ה', 'ו', 'ש']
        self.first_step = DAY

    def _build_keyboard(self, buttons):
        if self.locale == 'he':
            buttons = [row[::-1] for row in buttons]

        return super(HebrewCalendar, self)._build_keyboard(buttons)
