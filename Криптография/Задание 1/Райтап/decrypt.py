import base64
import string

STD_ALPHABET = string.ascii_uppercase + string.ascii_lowercase + string.digits + '+/'

def solve():
    with open("ciphertext.txt", "r", encoding="utf-8") as f:
        custom_b64 = f.read().strip()

    with open("config.txt", "r", encoding="utf-8") as f:
        lines = f.readlines()
        for line in lines:
            if line.startswith("CUSTOM_CHARSET="):
                custom_alphabet = line.strip()[15:]
                break

    reverse_translation_table = str.maketrans(custom_alphabet, STD_ALPHABET)

    std_b64 = custom_b64.translate(reverse_translation_table)

    print(f"[!] Восстановленный стандартный Base64:\n{std_b64}\n")

    try:
        flag = base64.b64decode(std_b64).decode('utf-8')
        print(f"[+] Флаг успешно получен: {flag}")
    except Exception as e:
        print(f"[-] Ошибка при декодировании: {e}")

if __name__ == "__main__":
    solve()
