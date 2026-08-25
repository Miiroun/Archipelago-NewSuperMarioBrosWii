from Crypto.Cipher import AES

from wiithon.disc.structs.signature import KeyType

# "Normal" Common key. Used by the majority of Wii games
# 16 bytes AES-128 key, index 0 in the Ticket
COMMON_KEY_NORMAL = bytes([
    0xeb, 0xe4, 0x2a, 0x22, 0x5e, 0x85, 0x93, 0xe4,
    0x48, 0xd9, 0xc5, 0x45, 0x73, 0x81, 0xaa, 0xf7
])

# Korean Common key. Used for korean titles ofc
# index 1 in the Ticket
COMMON_KEY_KOREAN = bytes([
    0x63, 0xb8, 0x2b, 0xb4, 0xf4, 0x61, 0x4e, 0x2e,
    0x13, 0xf2, 0xfe, 0xfb, 0xba, 0x4c, 0x9b, 0x7e
])

# Indexed by the common_key_index field from the Ticket:
#   - 0 -> COMMON_KEY_NORMAL
#   - 1 -> COMMON_KEY_KOREAN
COMMON_KEYS = [COMMON_KEY_NORMAL, COMMON_KEY_KOREAN]


def decrypt_title_key(encrypted_key: bytes, common_key_index: int, title_id: bytes) -> bytes:
    """
    Decrypt the title key using the common key and title ID as IV

    - Build the IV: title_id (8 bytes) + 8 zero bytes
    - Select the right common key by index
    - Decrypt with AES-128-CBC

    The resulting title key will be used to decrypt all data block in the partition
    :param encrypted_key: Encrypted title key
    :param common_key_index: Common key index
    :param title_id: Title ID
    :return: Decrypted title key
    """
    iv: bytes = title_id + b'\x00' * 8 # 16 bytes and the first 8 are the title id
    cipher = AES.new(COMMON_KEYS[common_key_index], AES.MODE_CBC, iv)
    return cipher.decrypt(encrypted_key)

def encrypt_title_key(decrypted_key: bytes, common_key_index: int, title_id: bytes) -> bytes:
    """
    Encrypt the title key using the common key and title ID as IV

    :param decrypted_key: Decrypted title key
    :param common_key_index: Common key index
    :param title_id: Title ID
    :return: Decrypted title key
    """
    iv: bytes = title_id + b'\x00' * 8 # 16 bytes and the first 8 are the title id
    cipher = AES.new(COMMON_KEYS[common_key_index], AES.MODE_CBC, iv)
    return cipher.encrypt(decrypted_key)

def get_length_from_key_type(key_type: KeyType) -> tuple[int, int, int]:
    """
    Return (key_size, exponent_size, padding_size) for a certificate key type

    Used when reading/writing to know how many bytes to read/write and its padding

    :param key_type: Key type from the certificate
    :return: Tuple (key_size, exponent_size, padding_size)
    """
    match key_type:
        case KeyType.NONE:
            raise ValueError("Invalid key type")
        case KeyType.RSA_4096:
            return 0x200, 0x04, 0x34
        case KeyType.RSA_2048:
            return 0x100, 0x04, 0x34
        case KeyType.ECC_B233:
            return 0x3C, 0x00, 0x3C

    raise ValueError("Invalid key type")