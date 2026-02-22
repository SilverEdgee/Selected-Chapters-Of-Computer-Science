import circle

# Скрипт просто читает файл по заранее известному пути
with open("/data/input.txt", "r") as f:
    val = float(f.read().strip())
    print(f"Area from file: {circle.area(val)}")
