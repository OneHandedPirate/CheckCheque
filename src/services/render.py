from datetime import datetime

from src.config import DATE_FORMAT
from src.services import utils


class RenderService:
    # TODO: make method to render individual checks

    @staticmethod
    def render_menu(start: bool, name: str = "default") -> str:
        res = ""
        if start:
            res += f"🖖 Привет, {name}. Я <b>CheckCheque</b> бот, вот что я умею:\n"
        res += (
            "\n🔸Просмотр последнего чека\n"
            "🔸Статистика за год/месяц/неделю\n"
            "🔸Обработка новых чеков\n"
            "🔸Выгрузка существующей БД\n\n"
            "Для выбора действия нажми на соответствующую кнопку."
        )
        return res

    @staticmethod
    def render_statistics(items: list, period: str) -> str:
        months = utils.MONTHS

        if not items:
            return "За этот период статистики нет."
        res = ""
        match period:
            case "year":
                for month in items:
                    res += f"<b>{months[month[2]]}</b>\nПоходов в магаз: {month[1]}\nПотрачено: {month[0]}\n\n"
                res += f"------------------------------\nПотрачено за год: {sum([month[0] for month in items]):.2f}\n"
                return res
            case "month":
                res = f'{months[str(datetime.now().month).rjust(2, "0")]}\n\n'
                summ = 0
                for indx, item in enumerate(items, 1):
                    summ += item[2]
                    res += (
                        f"<b>{item[0]}</b>\nКоличество: {item[1]}\nСумма: {item[2]}\n\n"
                    )
                res += f"-------------------------\n<b>Итого</b>: {summ:.2f}"

                return res
            case "week":
                n, summ, total = 0, 0, 0
                for indx, item in enumerate(items):
                    if indx == 0 or indx > 0 and items[indx - 1][4] != item[4]:
                        if indx != 0:
                            res += f"------------------\n<b>Сумма: </b> {summ:.2f}\n------------------\n\n"
                            total += summ
                            summ = 0
                        date, time = item[4].split()
                        date = ".".join(date.split("-")[::-1])
                        res += f"🗓️ {date}\n🕓 {time}\n\n"
                        n = 0

                    n += 1
                    if item[2] != 1:
                        res += f"<b>{n}) {item[0]}</b>\nЦена за ед.: {item[1]}\nКоличество: {item[2]}\nСумма: {item[3]}\n\n"

                    else:
                        res += f"<b>{n}) {item[0]}</b>\nЦена: {item[3]}\n\n"
                    summ += float(item[3])
                res += f"------------------\n<b>Сумма: </b> {summ:.2f}\n------------------\n\n"
                total += summ
                res += f"-----------------\n<b>Итого</b>: {total:.2f}\n"
                return res
            case "last":
                date, time = (
                    datetime.strptime(items[0][4], "%Y-%m-%d %H:%M")
                    .strftime(DATE_FORMAT)
                    .split()
                )
                res = f"🗓️{date}\n🕓{time}\n\n"
                for item in items:
                    res += f"<b>{item[0]}</b>\nЦена за ед.: {item[1]}\nКоличество: {item[2]}\nСумма: {item[3]}\n\n"
                res += f"---------------------\n<b>Итого</b>: {sum([item[3] for item in items])}\n---------------------\n"
                return res
