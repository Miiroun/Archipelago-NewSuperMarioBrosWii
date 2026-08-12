import hashlib

from Crypto.Cipher import AES

from wiithon.crypto.layout import (
    SHA1_SIZE,

    BLOCK_HEADER_SIZE, BLOCK_PER_GROUP, BLOCK_SIZE,
    SUBGROUP_BY_GROUP, SUBBLOCK_SIZE, SUBBLOCK_BY_BLOCK,
    BLOCK_BY_SUBGROUP, SUBGROUP_SIZE, IV_OFFSET, IV_SIZE, H1_OFFSET, H2_OFFSET, H1_SIZE
)


def decrypt_block(block: bytes, title_key: bytes) -> bytes:
    """
    Decrypt a single 0x8000-byte block

    - Extracts the IV at offset: 0x3D0 of the block header (16 bytes)
    - Decrypts the data section (0x400 to end) with AES-128-CBC
    - Returns the 0x7C00 bytes, decrypted

    See: https://wiibrew.org/wiki/Wii_disc#Encrypted
    :param block: Raw encrypted block
    :param title_key: 16-byte title key
    :return: decrypted data (0x7C00)
    """
    data_iv = block[IV_OFFSET:IV_OFFSET + IV_SIZE]
    data_cipher = AES.new(title_key, AES.MODE_CBC, data_iv)
    data_section = data_cipher.decrypt(block[BLOCK_HEADER_SIZE:])

    return data_section

def decrypt_group(group_data: bytes, title_key: bytes) -> bytes:
    """
    Decrypt an entire group of 64 blocks.
    Iterates over all 64 blocks in the group, decrypt each one and concatenates

    :param group_data: Raw encrypted group
    :param title_key: 16-byte title key
    :return: Decrypted group
    """
    result = bytearray()
    for i in range(BLOCK_PER_GROUP):
        current_block_start = i * BLOCK_SIZE
        current_block = group_data[current_block_start: current_block_start + BLOCK_SIZE]
        result.extend(decrypt_block(current_block, title_key))

    return result


def encrypt_group(group_data: bytes | bytearray, title_key: bytes, h3_ref: bytearray | None = None) -> bytes:
    """
    Hash and encrypt a full 2MB group
    Reference: https://wiibrew.org/wiki/Wii_disc#Encrypted

    :param group_data: 2MB bytes/bytearray to be hashed and encrypted
    :param title_key: 16-byte decrypted title key
    :param h3_ref: Optional bytearray of length 20 where the H3 hash will be stored
    :return: The encrypted 2MB data as bytes
    """
    buffer = bytearray(group_data)

    hasher = hashlib.sha1
    h2 = bytearray(SHA1_SIZE * SUBGROUP_BY_GROUP)

    # H2 loop
    for subgroup_index in range(SUBGROUP_BY_GROUP):
        h1 = bytearray(SHA1_SIZE * BLOCK_BY_SUBGROUP)

        # H1 loop
        for block_index in range(BLOCK_BY_SUBGROUP):
            block_start = subgroup_index * SUBGROUP_SIZE + block_index * BLOCK_SIZE
            h0 = bytearray(SHA1_SIZE * SUBBLOCK_BY_BLOCK)

            # H0 loop: all "subblock" hashes
            for j in range(SUBBLOCK_BY_BLOCK):
                data_subblock = buffer[
                                    block_start + (j + 1) * SUBBLOCK_SIZE:
                                    block_start + (j + 2) * SUBBLOCK_SIZE
                                ]

                # Putting the hash of the subblock in the right place in the h0 table
                h0[j * SHA1_SIZE:(j + 1) * SHA1_SIZE] = hasher(data_subblock).digest()

            # Hashing h0 and placing it in the right place in the h1 table
            h1[block_index * SHA1_SIZE:(block_index + 1) * SHA1_SIZE] = hasher(h0).digest()

            # Placing H0 in the block header then the padding
            buffer[block_start: block_start + len(h0)] = h0
            buffer[block_start + len(h0): block_start + H1_OFFSET] = b'\x00' * 0x14

        # Hashing h1 and placing it in the right place
        h2[subgroup_index * SHA1_SIZE:(subgroup_index + 1) * SHA1_SIZE] = hasher(h1).digest()

        # Placing H1 in the block header
        for block_index in range(BLOCK_BY_SUBGROUP):
            block_start = subgroup_index * SUBGROUP_SIZE + block_index * BLOCK_SIZE
            buffer[block_start + H1_OFFSET: block_start + H1_OFFSET + len(h1)] = h1
            buffer[block_start + H1_OFFSET + H1_SIZE: block_start + H2_OFFSET] = b'\x00' * (H2_OFFSET - H1_OFFSET - H1_SIZE)

    # Calculate H3
    if h3_ref is not None:
        h3_ref[:] = hasher(h2).digest()

    # Placing H2 and encrypt
    for subgroup_index in range(SUBGROUP_BY_GROUP):
        for block_index in range(BLOCK_BY_SUBGROUP):
            block_start = subgroup_index * SUBGROUP_SIZE + block_index * BLOCK_SIZE

            # Placing H2 in the block header
            buffer[block_start + H2_OFFSET: block_start + H2_OFFSET + len(h2)] = h2
            buffer[block_start + IV_OFFSET + IV_SIZE: block_start + BLOCK_HEADER_SIZE] = b'\x00' * (BLOCK_HEADER_SIZE - IV_OFFSET - IV_SIZE)

            cipher = AES.new(title_key, AES.MODE_CBC, b'\x00' * IV_SIZE)
            buffer[block_start: block_start + BLOCK_HEADER_SIZE] = cipher.encrypt(bytes(buffer[block_start: block_start + BLOCK_HEADER_SIZE]))

            # Encrypt data with the last 16 bytes (before padding) of encrypted header
            iv = buffer[block_start + IV_OFFSET: block_start + IV_OFFSET + IV_SIZE]
            cipher2 = AES.new(title_key, AES.MODE_CBC, bytes(iv))
            buffer[block_start + BLOCK_HEADER_SIZE: block_start + BLOCK_SIZE] = cipher2.encrypt(
                bytes(buffer[block_start + BLOCK_HEADER_SIZE: block_start + BLOCK_SIZE])
            )

    return bytes(buffer)