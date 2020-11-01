import numpy as np


def strhex_to_bin_array(s):
    b = bin(int(s, 16))[2:]
    a = np.array(list(b), dtype=int)
    return a


def bin_array_to_strhex(a):
    b = ""
    for x in a:
        b += str(x)
    h = hex(int(b, 2))
    return h


def key_gen(i, k):
    l_k = k.shape[0]
    key = np.zeros((l_k,), dtype=int)

    for j in range(1, l_k+1):
        index = ((5 * i + j - 1) % l_k) + 1  # the formula in the slide is 1-indexed
        key[j-1] = k[index-1]

    return key


def f(k, i, y):
    l = y.shape[0]
    w = np.zeros((l+1,), dtype=int)  # w is starts from index 1 for easier computation
    for j in range(1, l+1):
        if j <= l / 2:
            w[j] = y[j-1] ^ k[4*j - 3 -1]
        else:
            w[j] = y[j-1] ^ k[4*j - 2*l -1]
    return w[1:]


def encrypt(u, k, r):
    y = u[:16]
    z = u[16:]

    for i in range(r):
        round_key = key_gen(i+1, k)
        w = f(round_key, i, y)
        v = np.bitwise_xor(w, z)
        z = y
        y = v

    x = np.append(z, y)  # wrong way around since we did one more T in the for loop
    return x


def decrypt(x, k, r):
    y = x[:16]
    z = x[16:]

    for i in range(r):
        round_key = key_gen(r-i, k)  # inverted key sequence
        w = f(round_key, i, y)
        v = np.bitwise_xor(w, z)
        z = y
        y = v

    u = np.append(z, y)  # wrong way around since we did one more T in the for loop
    return u


def main():
    k = strhex_to_bin_array('0x80000000')
    u = strhex_to_bin_array('0x80000000')

    x = encrypt(u, k, 17)
    uu = decrypt(x, k, 17)

    print(x)
    print(bin_array_to_strhex(x))

    print(uu)
    print(bin_array_to_strhex(uu))


if __name__ == "__main__":
    main()