from rich.console import Console
from rich.table import Table
from rich import box

console = Console()

# 1. Создаем таблицу с закругленными границами (ROUNDED)
# show_lines=True добавляет горизонтальные перегородки между строками
table = Table(
    show_header=False,
    show_edge=True,
    show_lines=True,
    box=box.ROUNDED,
    padding=(0, 1)  # отступы внутри секций (вертикальный, горизонтальный)
)

# 2. Добавляем секции (строки)
table.add_row("Короткая строка")
table.add_row("Самая длинная строка в этом едином блоке")
table.add_row("Ещё одна секция снизу")

console.print(table)