import string

def encrypt_vigenere(plaintext, key):
    ciphertext = []
    key = key.upper()
    key_index = 0

    for char in plaintext:
        if char.isalpha():
            # Определяем сдвиг относительно 'A' или 'a'
            shift = ord(key[key_index % len(key)]) - ord('A')
            base = ord('A') if char.isupper() else ord('a')

            # Сдвигаем символ
            encrypted_char = chr((ord(char) - base + shift) % 26 + base)
            ciphertext.append(encrypted_char)

            key_index += 1
        else:
            # Знаки препинания и пробелы оставляем без изменений
            ciphertext.append(char)

    return "".join(ciphertext)

def generate_task():
    # Длинный текст для хорошей работы частотного анализа
    text = (
        "Cryptography is the practice and study of techniques for secure communication "
        "in the presence of adversarial behavior. More generally, cryptography is about "
        "constructing and analyzing protocols that prevent third parties or the public "
        "from reading private messages. Modern cryptography exists at the intersection "
        "of the disciplines of mathematics, computer science, electrical engineering, "
        "communication science, and physics. Applications of cryptography include "
        "electronic commerce, chip-based payment cards, digital currencies, computer "
        "passwords, and military communications. "
        "By the way, here is your reward for reading this boring text. "
        "The flag is: RCPISS{v1g3n3r3_c1ph3r_b0w5_t0_st4t1st1cs} "
        "Please keep it secret and do not share it with the enemies."
    )

    key = "HACK"
    encrypted_text = encrypt_vigenere(text, key)

    print(f"[+] Ключ шифрования: {key}")
    print(f"[+] Зашифрованный текст сгенерирован (длина: {len(encrypted_text)} символов).")

    with open("message.txt", "w", encoding="utf-8") as f:
        f.write(encrypted_text)

    print("[+] Файл 'message.txt' сохранен. Его нужно отдать участникам.")

if __name__ == "__main__":
    generate_task()
