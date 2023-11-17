from functools import reduce

from src.services import utils


class RenderService:
    @staticmethod
    def render_menu_text(start: bool, name: str = "default") -> str:
        strings_to_render = []
        if start:
            strings_to_render.append(
                f"🖖 Привет, {name}. Я <b>CheckCheque</b> бот, вот что я умею:\n"
            )
        strings_to_render.append(
            "\n🔸Просмотр последнего чека\n"
            "🔸Статистика за неделю/месяц/год\n"
            "🔸Обработка новых чеков\n"
            "🔸Выгрузка существующей БД\n\n"
            "Для выбора действия нажми на соответствующую кнопку."
        )
        return "".join(strings_to_render)

    def render_statistics(self, items: list, period: str) -> str | list:
        months = utils.MONTHS

        if not items:
            return "За этот период статистики нет."
        strings_to_render = []
        match period:
            case "year":
                strings_to_render.append(f"📅 <b>{items[0][3]}</b>\n\n")
                for month in items:
                    strings_to_render.append(
                        f"<b>{months[month[2]]}</b>\nПоходов в магаз: {month[1]}"
                        f"\nПотрачено: {month[0]}\n\n"
                    )
                strings_to_render.append(
                    f"------------------------------\nПотрачено за год: "
                    f"{sum([month[0] for month in items]):.2f}\n"
                )
                return "".join(strings_to_render)

            case "month":
                month, year = items[0][-1].split(".")
                strings_to_render.append(f"{months[month]} {year}г.\n\n")
                total = 0
                for indx, item in enumerate(items, 1):
                    item_str = ""
                    total += item[2]
                    item_str += f"<b>- {item[0]}</b>\n"
                    if item[1] != 1:
                        item_str += f"   Количество: {round(item[1], 3)}\n"
                    item_str += f"   Сумма: {item[2]}\n"
                    strings_to_render.append(item_str)
                strings_to_render.append(
                    f"-------------------------\n<b>Итого</b>: {total:.2f}"
                )
                return self.paginate_results_if_needed(strings_to_render)

            case "week":
                return self.render_checks(
                    items, first_string="🛒 Ваши покупки за неделю:\n\n", total=True
                )

            case "last":
                return self.render_checks(
                    items, first_string="🛒 Ваш последний чек:\n\n"
                )

            case "day":
                return self.render_checks(
                    items,
                    first_string="🛒 Ваши покупки за такой-то день:\n\n",
                    total=True,
                )

    def render_checks(
        self,
        items: list[tuple],
        first_string: str,
        total: bool = False,
    ) -> str:
        checks_to_render = [first_string]
        num = _sum = 0
        if total:
            _total = 0
        check_str = ""
        for indx, item in enumerate(items):
            if indx == 0 or indx > 0 and items[indx - 1][4] != item[4]:
                if indx != 0:
                    check_str += (
                        f"------------------\n<b>Сумма: </b> "
                        f"{_sum:.2f}\n------------------\n\n"
                    )
                    if total:
                        _total += _sum
                    _sum = 0
                    checks_to_render.append(check_str)
                    check_str = ""
                date, time = item[4].split()
                date = ".".join(date.split("-")[::-1])
                check_str += f"🗓️ {date}\n🕓 {time}\n\n"
                num = 0

            num += 1
            if item[2] != 1:
                check_str += (
                    f"<b>{num}) {item[0]}</b>\nЦена за ед.: {item[1]}\n"
                    f"Количество: {item[2]}\nСумма: {item[3]}\n\n"
                )

            else:
                check_str += f"<b>{num}) {item[0]}</b>\nЦена: {item[3]}\n\n"

            _sum += float(item[3])
        check_str += (
            f"------------------\n<b>Сумма: </b> {_sum:.2f}\n------------------\n\n"
        )
        checks_to_render.append(check_str)
        if total:
            _total += _sum
            checks_to_render.append(f"-----------------\n<b>Итого</b>: {_total:.2f}\n")
        return self.paginate_results_if_needed(checks_to_render, total)

    @staticmethod
    def paginate_results_if_needed(
        strings_to_render: list[str], total: bool = True
    ) -> str | list[str]:
        if reduce(lambda x, y: x + len(y), strings_to_render, 0) > 1600:
            paginated_results = []
            current_page = 1
            current_string = (
                strings_to_render[0] + f"--- Страница {current_page} ---\n\n"
            )
            items = strings_to_render[1:-1] if total else strings_to_render[1:]
            for indx, item in enumerate(items):
                if len(current_string) + len(item) < 1200:
                    current_string += item
                else:
                    if total:
                        current_string += strings_to_render[-1]
                    paginated_results.append(current_string)
                    current_page += 1
                    current_string = (
                        strings_to_render[0] + f"--- Страница {current_page} ---\n\n"
                    )
                    current_string += item
            if total:
                current_string += strings_to_render[-1]
            paginated_results.append(current_string)
            return paginated_results
        return "".join(strings_to_render)
