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

    def render_statistics(self, items: list, period: str) -> str:
        months = utils.MONTHS

        if not items:
            return "За этот период статистики нет."
        strings_to_render = []
        match period:
            case "year":
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
                        item_str += f"   Количество: {item[1]}\n"
                    item_str += f"   Сумма: {item[2]}\n"
                    strings_to_render.append(item_str)
                strings_to_render.append(
                    f"-------------------------\n<b>Итого</b>: {total:.2f}"
                )

                return "".join(strings_to_render)
            case "week":
                return self.render_checks(items, total=True)
            case "last":
                return self.render_checks(items)
            case "day":
                return self.render_checks(items, total=True)

    @staticmethod
    def render_checks(items: list[tuple], total: bool = False) -> str:
        checks_to_render = []
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
        return "".join(checks_to_render)
