from datetime import datetime

from src.services import utils


class RenderService:
    @staticmethod
    def render_menu(start: bool, name: str = "default") -> str:
        res = ""
        if start:
            res += f"🖖 Привет, {name}. Я <b>CheckCheque</b> бот, вот что я умею:\n"
        res += (
            "\n🔸Просмотр последнего чека\n"
            "🔸Статистика за неделю/месяц/год\n"
            "🔸Обработка новых чеков\n"
            "🔸Выгрузка существующей БД\n\n"
            "Для выбора действия нажми на соответствующую кнопку."
        )
        return res

    def render_statistics(self, items: list, period: str) -> str:
        months = utils.MONTHS

        if not items:
            return "За этот период статистики нет."
        res = ""
        match period:
            case "year":
                for month in items:
                    res += (
                        f"<b>{months[month[2]]}</b>\nПоходов в магаз: {month[1]}"
                        f"\nПотрачено: {month[0]}\n\n"
                    )
                res += (
                    f"------------------------------\nПотрачено за год: "
                    f"{sum([month[0] for month in items]):.2f}\n"
                )
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
                return self.render_checks(items, total=True)
            case "last":
                return self.render_checks(items)

    @staticmethod
    def render_checks(items: list[tuple], total: bool = False) -> str:
        result = ""
        num = _sum = 0
        if total:
            _total = 0
        for indx, item in enumerate(items):
            if indx == 0 or indx > 0 and items[indx - 1][4] != item[4]:
                if indx != 0:
                    result += (
                        f"------------------\n<b>Сумма: </b> "
                        f"{_sum:.2f}\n------------------\n\n"
                    )
                    if total:
                        _total += _sum
                    _sum = 0
                date, time = item[4].split()
                date = ".".join(date.split("-")[::-1])
                result += f"🗓️ {date}\n🕓 {time}\n\n"
                num = 0

            num += 1
            if item[2] != 1:
                result += (
                    f"<b>{num}) {item[0]}</b>\nЦена за ед.: {item[1]}\n"
                    f"Количество: {item[2]}\nСумма: {item[3]}\n\n"
                )

            else:
                result += f"<b>{num}) {item[0]}</b>\nЦена: {item[3]}\n\n"
            _sum += float(item[3])
        result += (
            f"------------------\n<b>Сумма: </b> {_sum:.2f}\n------------------\n\n"
        )
        if total:
            _total += _sum
            result += f"-----------------\n<b>Итого</b>: {_total:.2f}\n"
        return result
