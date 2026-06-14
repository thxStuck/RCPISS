def decrypt_vigenere(ciphertext, key):
    plaintext = []
    key = key.upper()
    key_index = 0

    for char in ciphertext:
        if char.isalpha():
            shift = ord(key[key_index % len(key)]) - ord('A')
            base = ord('A') if char.isupper() else ord('a')

            # Обратный сдвиг
            decrypted_char = chr((ord(char) - base - shift) % 26 + base)
            plaintext.append(decrypted_char)

            key_index += 1
        else:
            plaintext.append(char)

    return "".join(plaintext)

def solve():
    try:
        with open("message.txt", "r", encoding="utf-8") as f:
            ciphertext = f.read()
    except FileNotFoundError:
        print("[-] Файл message.txt не найден!")
        return

    # Предположим, участник нашел ключ с помощью частотного анализа или dCode
    key = "HACK"

    print(f"[!] Используем найденный ключ: {key}")
    plaintext = decrypt_vigenere(ciphertext, key)

    print(f"[+] Расшифрованный текст:\n\n{plaintext}\n")

    # Ищем флаг в тексте
    if "RCPISS{" in plaintext:
        start = plaintext.find("RCPISS{")
        end = plaintext.find("}", start) + 1
        print(f"[+] Найден флаг: {plaintext[start:end]}")

if __name__ == "__main__":
    solve()
