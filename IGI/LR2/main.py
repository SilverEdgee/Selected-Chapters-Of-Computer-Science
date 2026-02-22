import sys
import circle
import square

# Скрипт ожидает две строки: сначала радиус, потом сторону
lines = sys.stdin.readlines()
if len(lines) >= 2:
    r = float(lines[0].strip())
    a = float(lines[1].strip())
    print(f"Круг (из STDIN): {circle.area(r)}")
    print(f"Квадрат (из STDIN): {square.area(a)}")
