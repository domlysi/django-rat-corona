def PRGA(S):
    i = 0
    j = 0
    while True:
        i = (i + 1) % 256
        j = (j + S[i]) % 256
        S[i], S[j] = S[j], S[i]
        yield S[(S[i] + S[j]) % 256]


def encryptRC4(plaintext, key, hexformat=False):
    key, plaintext = bytearray(key.encode()), bytearray(plaintext.encode())  # necessary for py2, not for py3
    S = list(range(256))
    j = 0
    for i in range(256):
        j = (j + S[i] + key[i % len(key)]) % 256
        S[i], S[j] = S[j], S[i]
    keystream = PRGA(S)
    return b''.join(b"%02X" % (c ^ next(keystream)) for c in plaintext) if hexformat else bytearray(c ^ next(keystream) for c in plaintext)


if __name__ == '__main__':
    with open('client_linux.py', 'r') as file:
        content = file.read()
    script = encryptRC4(content, 'test')
    with open('stub.dat', 'wb') as file:
        file.write(script)
