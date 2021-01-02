package rsa

import (
    "math"
    "math/rand"
    "math/big"
    "errors"
)

type Key struct {
    key int
    n int
}

type KeyPair struct {
    Private Key
    Public Key
}

func isPrime(n int) bool {
    var k int = 2
    if (n == 0) || (n == 1) {
        return false
    }
    for k <= (n**0.5) {
        if n % k != 0 {
            k++
        }
        if n % k == 0 {
            return false
        }
    }
    return true
}


func gcd(a int, b int) int {
    if (a == 0) || (b == 0) {
        if a > b {
            return a
        }
        return b
    }
    for (a - b) != 0 {
        if a > b {
            a -= b
        }
        else { 
            b -= a
        }
    }
    return a
}


func multiplicativeInverse(e int, phi int) int {
    divs := make([]int, 0)
    var true_phi = phi
    for e % phi != 0 {
        divs = append(divs, e / phi)
        e, phi := phi, e % phi
    }
    var x := 0
    var y := 1
    for i := (len(divs) - 1); i > -1; i-- {
        y := x - (y * divs[i])
        x := y
    }
    return x % true_phi

}


func GenerateKeypair(p int, q int) (KeyPair, error) {
    if !isPrime(p) || !isPrime(q) {
        return KeyPair{}, errors.New("Both numbers must be prime.")
    } else if  p == q {
        return KeyPair{}, errors.New("p and q can't be equal.")
    }

    // n = pq
    n = p * q

    // phi = (p-1)(q-1)
    phi = (p - 1) * (q - 1)

    e := rand.Intn(phi - 1) + 1
    g := gcd(e, phi)
    for g != 1 {
        e = rand.Intn(phi - 1) + 1
        g = gcd(e, phi)
    }

    d := multiplicativeInverse(e, phi)
    return KeyPair{Key{e, n}, Key{d, n}}, nil
}


func Encrypt(pk Key, plaintext string) []int {
    cipher := []int{}
    n := new(big.Int)
    for _, ch := range plaintext {
        n = new(big.Int).Exp(
            big.NewInt(int64(ch)), big.NewInt(int64(pk.key)), nil)
        n = new(big.Int).Mod(n, big.NewInt(int64(pk.n)))
        cipher = append(cipher, int(n.Int64()))
    }
    return cipher
}


func Decrypt(pk Key, cipher []int) string {
    plaintext := ""
    n := new(big.Int)
    for _, ch := range cipher {
        n = new(big.Int).Exp(
            big.NewInt(int64(ch)), big.NewInt(int64(pk.key)), nil)
        n = new(big.Int).Mod(n, big.NewInt(int64(pk.n)))
        plaintext += string(rune(int(n.Int64())))
    }
    return plaintext
}
