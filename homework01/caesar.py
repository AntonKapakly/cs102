import typing as tp


def encrypt_caesar(plaintext: str, shift: int = 3) -> str:
    """
    Encrypts plaintext using a Caesar cipher.

    >>> encrypt_caesar("PYTHON")
    'SBWKRQ'
    >>> encrypt_caesar("python")
    'sbwkrq'
    >>> encrypt_caesar("Python3.6")
    'Sbwkrq3.6'
    >>> encrypt_caesar("")
    ''
    """
    ciphertext = ""
    for i in plaintext:
        if ord("A") <= ord(i) <= ord("Z"):
            ciphertext += chr(ord("A") + (ord(i) - ord("A") + shift) % 26)
        elif ord("a") <= ord(i) <= ord("z"):
            ciphertext += chr(ord("a") + (ord(i) - ord("a") + shift) % 26)
        else:
            ciphertext += i

    return ciphertext


def decrypt_caesar(ciphertext: str, shift: int = 3) -> str:
    """
    Decrypts a ciphertext using a Caesar cipher.

    >>> decrypt_caesar("SBWKRQ")
    'PYTHON'
    >>> decrypt_caesar("sbwkrq")
    'python'
    >>> decrypt_caesar("Sbwkrq3.6")
    'Python3.6'
    >>> decrypt_caesar("")
    ''
    """
    plaintext = ""
    for i in ciphertext:
        if ord("A") <= ord(i) <= ord("Z"):
            plaintext += chr(((ord(i) - ord("A")) - shift) % 26 + ord("A"))
        elif ord("a") <= ord(i) <= ord("z"):
            plaintext += chr(((ord(i) - ord("a")) - shift) % 26 + ord("a"))
        else:
            plaintext += i
    return plaintext


def caesar_breaker_brute_force(ciphertext: str, dictionary: tp.Set[str]) -> int:
    """
    Brute force breaking a Caesar cipher.
    """
    best_shift = 0
    # PUT YOUR CODE HERE
    return best_shift
