import base64
import random
import string

# Стандартный алфавит Base64 по спецификации RFC 4648
STD_ALPHABET = string.ascii_uppercase + string.ascii_lowercase + string.digits + '+/'

def generate_task():
    flag = b"RPCISS{b4s364_w1th_cu5t0m_4lph4b3t_15_345y}"
    custom_alphabet_list = list(STD_ALPHABET)
    random.shuffle(custom_alphabet_list)
    custom_alphabet = ''.join(custom_alphabet_list)

    std_b64 = base64.b64encode(flag).decode('utf-8')

    translation_table = str.maketrans(STD_ALPHABET, custom_alphabet)
    custom_b64 = std_b64.translate(translation_table)

    print(f"[+] Сгенерированный алфавит: {custom_alphabet}")
    print(f"[+] Зашифрованный текст:   {custom_b64}")

    with open("ciphertext.txt", "w", encoding="utf-8") as f:
        f.write(custom_b64)

    with open("config.txt", "w", encoding="utf-8") as f:
        f.write("DEBUG_MODE=False\n")
        f.write(f"CUSTOM_CHARSET={custom_alphabet}\n")
        f.write("USE_ENCRYPTION=True\n")

    print("\n[+] Готово! Файлы 'ciphertext.txt' и 'config.txt' можно отдавать игрокам.")

if __name__ == "__main__":
    generate_task()
