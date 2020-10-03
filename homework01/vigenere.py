def encrypt_vigenere(plaintext: str, keyword: str) -> str:
    """
    Encrypts plaintext using a Vigenere cipher.

    >>> encrypt_vigenere("PYTHON", "A")
    'PYTHON'
    >>> encrypt_vigenere("python", "a")
    'python'
    >>> encrypt_vigenere("ATTACKATDAWN", "LEMON")
    'LXFOPVEFRNHR'
    """
    ciphertext = ""
    j = 0
    for i in plaintext:
        if 65 <= ord(i) <= 90:
            shift = ord(keyword[j % len(keyword)]) - ord("A")
            ciphertext += chr(ord("A") + (ord(i) - ord("A") + shift) % 26)
        elif 97 <= ord(i) <= 122:
            shift = ord(keyword[j % len(keyword)]) - ord("a")
            ciphertext += chr(ord("a") + (ord(i) - ord("a") + shift) % 26)
        else:
            ciphertext += i
        j += 1
    return ciphertext


def decrypt_vigenere(ciphertext: str, keyword: str) -> str:
    """
    Decrypts a ciphertext using a Vigenere cipher.

    >>> decrypt_vigenere("PYTHON", "A")
    'PYTHON'
    >>> decrypt_vigenere("python", "a")
    'python'
    >>> decrypt_vigenere("LXFOPVEFRNHR", "LEMON")
    'ATTACKATDAWN'
    """
    plaintext = ""
    j = 0
    for i in ciphertext:
        if 65 <= ord(i) <= 90:
            shift = ord(keyword[j % len(keyword)]) - ord("A")
            plaintext += chr(ord("A") + (ord(i) - ord("A") - shift) % 26)
        elif 97 <= ord(i) <= 122:
            shift = ord(keyword[j % len(keyword)]) - ord("a")
            plaintext += chr(ord("a") + (ord(i) - ord("a") - shift) % 26)
        else:
            plaintext += i
        j += 1
    return plaintext
