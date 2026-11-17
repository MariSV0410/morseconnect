"""Funciones de conversión entre texto y código Morse internacional."""

MORSE = {
    'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.',
    'F': '..-.', 'G': '--.', 'H': '....', 'I': '..', 'J': '.---',
    'K': '-.-', 'L': '.-..', 'M': '--', 'N': '-.', 'O': '---',
    'P': '.--.', 'Q': '--.-', 'R': '.-.', 'S': '...', 'T': '-',
    'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-', 'Y': '-.--',
    'Z': '--..',
    '0': '-----', '1': '.----', '2': '..---', '3': '...--',
    '4': '....-', '5': '.....', '6': '-....', '7': '--...',
    '8': '---..', '9': '----.',
    '.': '.-.-.-', ',': '--..--', '?': '..--..', "'": '.----.',
    '!': '-.-.--', '/': '-..-.', '(': '-.--.', ')': '-.--.-',
    '&': '.-...', ':': '---...', ';': '-.-.-.', '=': '-...-',
    '+': '.-.-.', '-': '-....-', '_': '..--.-', '"': '.-..-.',
    '$': '...-..-', '@': '.--.-.'
}
REVERSE = {value: key for key, value in MORSE.items()}


def text_to_morse(text: str) -> str:
    """Convierte texto a Morse. Separa letras con un espacio y palabras con / ."""
    words = []
    for word in text.upper().split():
        encoded = [MORSE.get(char) for char in word]
        if any(code is None for code in encoded):
            invalid = sorted({c for c in word if c not in MORSE})
            raise ValueError('Caracteres no soportados: ' + ', '.join(invalid))
        words.append(' '.join(encoded))
    return ' / '.join(words)


def morse_to_text(code: str) -> str:
    """Convierte Morse a texto. Usa espacios entre letras y / entre palabras."""
    result = []
    for word in code.strip().split('/'):
        letters = []
        for symbol in word.strip().split():
            if symbol not in REVERSE:
                raise ValueError(f'Código Morse no reconocido: {symbol}')
            letters.append(REVERSE[symbol])
        result.append(''.join(letters))
    return ' '.join(result)
