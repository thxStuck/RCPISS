import base64
import string

# 1. Задаем стандартный алфавит Base64
STD_ALPHABET = string.ascii_uppercase + string.ascii_lowercase + string.digits + '+/'

# 2. Достаем кастомный алфавит из конфигурации
with open("config.txt", "r", encoding="utf-8") as f:
    for line in f:
        if line.startswith("CUSTOM_CHARSET="):
            custom_alphabet = line.strip()[15:]
            break

# 3. Читаем зашифрованный текст
with open("ciphertext.txt", "r", encoding="utf-8") as f:
    custom_b64 = f.read().strip()

# 4. Производим обратную замену символов
reverse_table = str.maketrans(custom_alphabet, STD_ALPHABET)
std_b64 = custom_b64.translate(reverse_table)

# 5. Раскодируем стандартный Base64
flag = base64.b64decode(std_b64).decode('utf-8')
print("Флаг:", flag)
