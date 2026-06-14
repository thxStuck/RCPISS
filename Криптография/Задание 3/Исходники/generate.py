from Crypto.Util.number import getPrime, bytes_to_long

def generate_task():
    # Флаг для шифрования
    flag = b"RCPISS{sm4ll_e_15_d4ng3r0u5_w1th0ut_p4dd1ng}"

    # Конвертируем строку флага в большое целое число (integer)
    m = bytes_to_long(flag)

    # Генерируем два больших простых числа (по 1024 бита) для N
    p = getPrime(1024)
    q = getPrime(1024)
    n = p * q

    # Выбираем малый открытый экспонент
    e = 3

    # Шифруем сообщение (RSA: c = m^e mod n)
    c = pow(m, e, n)

    print(f"[+] Размер модуля N (в битах): {n.bit_length()}")
    print(f"[+] Размер сообщения m^3 (в битах): {(m**3).bit_length()}")
    if (m**3) < n:
        print("[!] Уязвимость активна: m^3 меньше N. Операция по модулю не сработала.")

    # Сохраняем исходный код "шифратора" (task.py), чтобы игроки видели алгоритм
    with open("task.py", "w", encoding="utf-8") as f:
        f.write("from Crypto.Util.number import bytes_to_long\n\n")
        f.write('flag = b"RCPISS{...}"\n')
        f.write("m = bytes_to_long(flag)\n\n")
        f.write(f"n = {n}\n")
        f.write(f"e = {e}\n\n")
        f.write("c = pow(m, e, n)\n")
        f.write("print(f'Ciphertext: {c}')\n")

    # Сохраняем зашифрованные данные
    with open("output.txt", "w", encoding="utf-8") as f:
        f.write(f"n = {n}\n")
        f.write(f"e = {e}\n")
        f.write(f"c = {c}\n")

    print("[+] Готово! Файлы 'task.py' и 'output.txt' можно отдавать игрокам.")

if __name__ == "__main__":
    generate_task()
