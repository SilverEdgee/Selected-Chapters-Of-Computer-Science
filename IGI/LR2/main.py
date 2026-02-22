import os
import sys
import circle
import square

# Читаем переменные из окружения
r = os.getenv("r")
a = os.getenv("a")

if r:
    print(f"Круг: Площадь = {circle.area(float(r))}, Периметр = {circle.perimeter(float(r))}")
if a:
    print(f"Квадрат: Площадь = {square.area(float(a))}, Периметр = {square.perimeter(float(a))}")
