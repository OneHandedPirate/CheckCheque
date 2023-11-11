import datetime

MONTHS = {
    "01": "❄️ Январь",
    "02": "🌨 Февраль",
    "03": "🌷 Март",
    "04": "🌺 Апрель",
    "05": "🌻 Май",
    "06": "🍹 Июнь",
    "07": "👙 Июль",
    "08": "🏖 Август",
    "09": "🍁 Сентябрь",
    "10": "🎃 Октябрь",
    "11": "☕ Ноябрь",
    "12": "🎄 Декабрь",
}


def validate_date_input(date_string):
    current_date = datetime.datetime.today()

    formats = ["%d.%m.%Y", "%m.%Y", "%Y"]

    for date_format in formats:
        try:
            date = datetime.datetime.strptime(date_string, date_format)
            if current_date < date or date.year < 2020:
                raise ValueError
            return True
        except ValueError:
            pass

    return False
