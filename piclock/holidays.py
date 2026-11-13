"""
Holiday detection and countdown engine for PiClock.
Lightweight, 100% offline, zero-dependency.
Supports India (IN), United States (US), United Kingdom (UK), Canada (CA),
Australia (AU), Global holidays, and custom user-defined holidays (birthdays, etc.).
"""

import datetime
from typing import Dict, List, Optional, Tuple

# Precomputed movable festival dates for years 2024-2030 (India & Islamic & Lunar)
# Format: (year, month, day): "Holiday Name"
MOVABLE_FESTIVALS = {
    # 2024
    (2024, 3, 8): ("Maha Shivratri", "IN"),
    (2024, 3, 25): ("Holi", "IN"),
    (2024, 4, 11): ("Eid ul-Fitr", "IN"),
    (2024, 6, 17): ("Bakrid / Eid al-Adha", "IN"),
    (2024, 8, 19): ("Raksha Bandhan", "IN"),
    (2024, 8, 26): ("Janmashtami", "IN"),
    (2024, 9, 7): ("Ganesh Chaturthi", "IN"),
    (2024, 10, 12): ("Dussehra / Vijayadashami", "IN"),
    (2024, 10, 31): ("Diwali / Deepavali", "IN"),
    (2024, 11, 1): ("Govardhan Puja", "IN"),
    (2024, 11, 15): ("Guru Nanak Jayanti", "IN"),

    # 2025
    (2025, 2, 26): ("Maha Shivratri", "IN"),
    (2025, 3, 14): ("Holi", "IN"),
    (2025, 3, 31): ("Eid ul-Fitr", "IN"),
    (2025, 6, 7): ("Bakrid / Eid al-Adha", "IN"),
    (2025, 8, 9): ("Raksha Bandhan", "IN"),
    (2025, 8, 16): ("Janmashtami", "IN"),
    (2025, 8, 27): ("Ganesh Chaturthi", "IN"),
    (2025, 10, 2): ("Dussehra / Vijayadashami", "IN"),
    (2025, 10, 20): ("Diwali / Deepavali", "IN"),
    (2025, 11, 5): ("Guru Nanak Jayanti", "IN"),

    # 2026
    (2026, 2, 15): ("Maha Shivratri", "IN"),
    (2026, 3, 4): ("Holi", "IN"),
    (2026, 3, 20): ("Eid ul-Fitr", "IN"),
    (2026, 4, 3): ("Good Friday", "GLOBAL"),
    (2026, 4, 5): ("Easter Sunday", "GLOBAL"),
    (2026, 5, 27): ("Bakrid / Eid al-Adha", "IN"),
    (2026, 8, 28): ("Raksha Bandhan", "IN"),
    (2026, 9, 4): ("Janmashtami", "IN"),
    (2026, 9, 14): ("Ganesh Chaturthi", "IN"),
    (2026, 10, 20): ("Dussehra / Vijayadashami", "IN"),
    (2026, 11, 8): ("Diwali / Deepavali", "IN"),
    (2026, 11, 24): ("Guru Nanak Jayanti", "IN"),

    # 2027
    (2027, 3, 6): ("Maha Shivratri", "IN"),
    (2027, 3, 23): ("Holi", "IN"),
    (2027, 3, 10): ("Eid ul-Fitr", "IN"),
    (2027, 3, 26): ("Good Friday", "GLOBAL"),
    (2027, 3, 28): ("Easter Sunday", "GLOBAL"),
    (2027, 5, 17): ("Bakrid / Eid al-Adha", "IN"),
    (2027, 8, 17): ("Raksha Bandhan", "IN"),
    (2027, 8, 25): ("Janmashtami", "IN"),
    (2027, 9, 4): ("Ganesh Chaturthi", "IN"),
    (2027, 10, 9): ("Dussehra / Vijayadashami", "IN"),
    (2027, 10, 29): ("Diwali / Deepavali", "IN"),
    (2027, 11, 14): ("Guru Nanak Jayanti", "IN"),

    # 2028
    (2028, 2, 23): ("Maha Shivratri", "IN"),
    (2028, 3, 11): ("Holi", "IN"),
    (2028, 2, 27): ("Eid ul-Fitr", "IN"),
    (2028, 4, 14): ("Good Friday", "GLOBAL"),
    (2028, 4, 16): ("Easter Sunday", "GLOBAL"),
    (2028, 10, 17): ("Diwali / Deepavali", "IN"),
}

# Fixed calendar holidays: (month, day) -> [(name, country)]
FIXED_HOLIDAYS = [
    # Global / New Year
    (1, 1, "New Year's Day", "ALL"),
    (12, 31, "New Year's Eve", "ALL"),
    (12, 25, "Christmas Day", "ALL"),
    (12, 26, "Boxing Day", "UK,CA,AU"),
    (2, 14, "Valentine's Day", "GLOBAL"),
    (3, 8, "International Women's Day", "GLOBAL"),
    (4, 22, "Earth Day", "GLOBAL"),
    (5, 1, "International Workers' Day / Labor Day", "IN,GLOBAL"),
    (10, 31, "Halloween", "US,UK,CA,GLOBAL"),

    # India (IN)
    (1, 14, "Makar Sankranti / Pongal", "IN"),
    (1, 26, "Republic Day", "IN"),
    (4, 14, "Ambedkar Jayanti", "IN"),
    (8, 15, "Independence Day", "IN"),
    (10, 2, "Gandhi Jayanti", "IN"),
    (11, 14, "Children's Day", "IN"),
    (12, 25, "Christmas Day", "IN"),

    # United States (US)
    (6, 19, "Juneteenth National Independence Day", "US"),
    (7, 4, "Independence Day (4th of July)", "US"),
    (11, 11, "Veterans Day", "US"),

    # Canada (CA)
    (7, 1, "Canada Day", "CA"),
    (9, 30, "National Day for Truth and Reconciliation", "CA"),
    (11, 11, "Remembrance Day", "CA,UK"),

    # Australia (AU)
    (1, 26, "Australia Day", "AU"),
    (4, 25, "Anzac Day", "AU"),
]


def _get_nth_weekday_of_month(year: int, month: int, weekday: int, n: int) -> datetime.date:
    """Find the nth occurrence of a weekday in a month (0=Monday, 6=Sunday)."""
    count = 0
    for day in range(1, 32):
        try:
            d = datetime.date(year, month, day)
            if d.weekday() == weekday:
                count += 1
                if count == n:
                    return d
        except ValueError:
            break
    return None


def _get_last_weekday_of_month(year: int, month: int, weekday: int) -> datetime.date:
    """Find the last occurrence of a weekday in a month."""
    last_d = None
    for day in range(1, 32):
        try:
            d = datetime.date(year, month, day)
            if d.weekday() == weekday:
                last_d = d
        except ValueError:
            break
    return last_d


def get_floating_us_holidays(year: int) -> List[Tuple[datetime.date, str, str]]:
    """Calculates floating US holidays based on calendar rules."""
    holidays = []
    # MLK Day: 3rd Monday in January
    d = _get_nth_weekday_of_month(year, 1, 0, 3)
    if d: holidays.append((d, "Martin Luther King Jr. Day", "US"))

    # Washington's Birthday / Presidents' Day: 3rd Monday in February
    d = _get_nth_weekday_of_month(year, 2, 0, 3)
    if d: holidays.append((d, "Presidents' Day", "US"))

    # Memorial Day: Last Monday in May
    d = _get_last_weekday_of_month(year, 5, 0)
    if d: holidays.append((d, "Memorial Day", "US"))

    # Labor Day: 1st Monday in September
    d = _get_nth_weekday_of_month(year, 9, 0, 1)
    if d: holidays.append((d, "Labor Day", "US"))

    # Columbus Day / Indigenous Peoples' Day: 2nd Monday in October
    d = _get_nth_weekday_of_month(year, 10, 0, 2)
    if d: holidays.append((d, "Columbus / Indigenous Peoples' Day", "US"))

    # Thanksgiving: 4th Thursday in November
    d = _get_nth_weekday_of_month(year, 11, 3, 4)
    if d: holidays.append((d, "Thanksgiving Day", "US"))
    if d: holidays.append((d + datetime.timedelta(days=1), "Black Friday", "US"))

    return holidays


def get_floating_uk_holidays(year: int) -> List[Tuple[datetime.date, str, str]]:
    """Floating UK Bank Holidays."""
    holidays = []
    # Early May bank holiday: 1st Monday in May
    d = _get_nth_weekday_of_month(year, 5, 0, 1)
    if d: holidays.append((d, "Early May Bank Holiday", "UK"))

    # Spring bank holiday: Last Monday in May
    d = _get_last_weekday_of_month(year, 5, 0)
    if d: holidays.append((d, "Spring Bank Holiday", "UK"))

    # Summer bank holiday: Last Monday in August
    d = _get_last_weekday_of_month(year, 8, 0)
    if d: holidays.append((d, "Summer Bank Holiday", "UK"))

    return holidays


def get_floating_ca_holidays(year: int) -> List[Tuple[datetime.date, str, str]]:
    """Floating Canadian Holidays."""
    holidays = []
    # Victoria Day: Monday on or before May 24
    for day in range(24, 17, -1):
        d = datetime.date(year, 5, day)
        if d.weekday() == 0:
            holidays.append((d, "Victoria Day", "CA"))
            break

    # Labour Day: 1st Monday in September
    d = _get_nth_weekday_of_month(year, 9, 0, 1)
    if d: holidays.append((d, "Labour Day", "CA"))

    # Thanksgiving: 2nd Monday in October
    d = _get_nth_weekday_of_month(year, 10, 0, 2)
    if d: holidays.append((d, "Thanksgiving Day", "CA"))

    return holidays


def get_floating_au_holidays(year: int) -> List[Tuple[datetime.date, str, str]]:
    """Floating Australian Holidays."""
    holidays = []
    # King's Birthday: 2nd Monday in June (most states)
    d = _get_nth_weekday_of_month(year, 6, 0, 2)
    if d: holidays.append((d, "King's Birthday", "AU"))

    # Labour Day (NSW/ACT/SA): 1st Monday in October
    d = _get_nth_weekday_of_month(year, 10, 0, 1)
    if d: holidays.append((d, "Labour Day", "AU"))

    return holidays


class HolidayManager:
    """Manages holiday retrieval and countdowns."""
    COUNTRY_NAMES = {
        "IN": "India",
        "US": "United States",
        "UK": "United Kingdom",
        "CA": "Canada",
        "AU": "Australia",
        "GLOBAL": "Global / International",
        "ALL": "All Countries"
    }

    def __init__(self, country: str = "IN", custom_holidays: Optional[List[dict]] = None):
        self.country = country.upper() if country else "IN"
        self.custom_holidays = custom_holidays or []

    def set_country(self, country: str):
        self.country = country.upper() if country else "IN"

    def set_custom_holidays(self, holidays: List[dict]):
        self.custom_holidays = holidays or []

    def _matches_country(self, holiday_country: str) -> bool:
        if self.country == "ALL" or holiday_country in ("ALL", "GLOBAL"):
            return True
        target_countries = [c.strip() for c in holiday_country.split(",")]
        return self.country in target_countries

    def get_holidays_for_year(self, year: int) -> List[Dict]:
        """Aggregate all holidays for a given year matching the selected country."""
        all_holidays = []

        # 1. Fixed Calendar Holidays
        for month, day, name, c_code in FIXED_HOLIDAYS:
            if self._matches_country(c_code):
                try:
                    all_holidays.append({
                        "date": datetime.date(year, month, day),
                        "name": name,
                        "country": c_code
                    })
                except ValueError:
                    pass

        # 2. Movable / Lunar / Festival Calendar
        for (y, m, d), (name, c_code) in MOVABLE_FESTIVALS.items():
            if y == year and self._matches_country(c_code):
                all_holidays.append({
                    "date": datetime.date(year, m, d),
                    "name": name,
                    "country": c_code
                })

        # 3. Dynamic Floating Rule Holidays
        if self._matches_country("US"):
            for d, name, c_code in get_floating_us_holidays(year):
                all_holidays.append({"date": d, "name": name, "country": c_code})

        if self._matches_country("UK"):
            for d, name, c_code in get_floating_uk_holidays(year):
                all_holidays.append({"date": d, "name": name, "country": c_code})

        if self._matches_country("CA"):
            for d, name, c_code in get_floating_ca_holidays(year):
                all_holidays.append({"date": d, "name": name, "country": c_code})

        if self._matches_country("AU"):
            for d, name, c_code in get_floating_au_holidays(year):
                all_holidays.append({"date": d, "name": name, "country": c_code})

        # 4. Custom User Holidays (Birthdays, Anniversaries)
        for ch in self.custom_holidays:
            name = ch.get("name", "Special Event")
            m = ch.get("month", 1)
            d = ch.get("day", 1)
            try:
                all_holidays.append({
                    "date": datetime.date(year, m, d),
                    "name": f"⭐ {name}",
                    "country": "CUSTOM"
                })
            except ValueError:
                pass

        # Sort by date
        all_holidays.sort(key=lambda h: h["date"])
        return all_holidays

    def get_holiday_today(self, current_date: Optional[datetime.date] = None) -> Optional[str]:
        """Check if today is a holiday. Returns holiday name or None."""
        if current_date is None:
            current_date = datetime.date.today()

        year_holidays = self.get_holidays_for_year(current_date.year)
        todays = [h["name"] for h in year_holidays if h["date"] == current_date]
        if todays:
            return " & ".join(todays)
        return None

    def get_next_holiday(self, current_date: Optional[datetime.date] = None) -> Optional[Dict]:
        """Find the next upcoming holiday and calculate days remaining."""
        if current_date is None:
            current_date = datetime.date.today()

        # Check this year and next year
        holidays = self.get_holidays_for_year(current_date.year) + self.get_holidays_for_year(current_date.year + 1)
        for h in holidays:
            delta = (h["date"] - current_date).days
            if delta > 0:
                return {
                    "name": h["name"],
                    "date": h["date"],
                    "days_left": delta,
                    "date_str": h["date"].strftime("%b %d")
                }
        return None

    def get_status_string(self, current_date: Optional[datetime.date] = None) -> Tuple[str, bool]:
        """
        Returns a formatted string suitable for the clock display.
        Returns (display_text, is_today_holiday)
        """
        if current_date is None:
            current_date = datetime.date.today()

        today_name = self.get_holiday_today(current_date)
        if today_name:
            return (f"🎉 Holiday: {today_name}", True)

        next_h = self.get_next_holiday(current_date)
        if next_h:
            days = next_h["days_left"]
            if days == 1:
                return (f"✨ Tomorrow: {next_h['name']}", False)
            return (f"📅 Next: {next_h['name']} ({next_h['date_str']} • in {days}d)", False)

        return ("", False)
