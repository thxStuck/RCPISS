from Crypto.Util.number import long_to_bytes

# Функция для вычисления целочисленного кубического корня (бинарный поиск)
# Это позволяет решить задачу без сторонних библиотек вроде gmpy2
def integer_cbrt(n):
    low = 0
    high = n
    while low < high:
        mid = (low + high) // 2
        if mid**3 < n:
            low = mid + 1
        else:
            high = mid
    return low

def solve():
    # Читаем данные из файла output.txt
    n, e, c = 0, 0, 0
    with open("output.txt", "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("n ="): n = int(line.split("=")[1].strip())
            if line.startswith("e ="): e = int(line.split("=")[1].strip())
            if line.startswith("c ="): c = int(line.split("=")[1].strip())

    print(f"[!] Публичный экспонент e = {e}")

    # Поскольку m^3 < N, мы просто извлекаем кубический корень из c
    m = integer_cbrt(c)

    # Проверка, что корень извлечен идеально точно
    if m**3 == c:
        print("[+] Кубический корень успешно извлечен!")
        # Конвертируем большое число обратно в байты (строку)
        flag = long_to_bytes(m).decode('utf-8')
        print(f"[+] Найден флаг: {flag}")
    else:
        print("[-] Ошибка: c не является точным кубом.")

if __name__ == "__main__":
    solve()
