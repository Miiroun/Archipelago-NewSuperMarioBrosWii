from enum import IntEnum
from io import BytesIO
from typing import NamedTuple, Union
from abc import ABC, abstractmethod

from wiithon.binary.reader import BinaryReader
from wiithon.binary.writer import BinaryWriter
from wiithon.exceptions import InvalidFormatError, CorruptedDataError, BCSVFileError

BCSV_HEADER_SIZE: int = 0x10
BCSV_FIELD_SIZE: int = 0xC
BCSV_MAX_STRING_LENGTH: int = 0x20

STRING_FORMAT: str = "utf-8"

BCSVValue = int | str | float

class BCSVKey(ABC):
    """Abstract Base Class for all BCSV Keys."""
    
    @abstractmethod
    def resolve_name(self) -> str:
        """
        Subclass must implement this to provide a str key used in the BCSVEntry dict.
        
        Returns:
            str: key to be used in a BCSVEntry.
        """
        pass

    @staticmethod
    def create(key: Union[str, int, 'BCSVField']) -> 'BCSVKey':
        """
        Creates a BCSVKey from one of the support input types.
        
        Returns:
            BCSVKey: Key of sub-type X, which implements its own str key used in BCSVEntry
        """
        if isinstance(key, str):
            return BCSVNameKey(key)
        elif isinstance(key, int):
            return BCSVHashKey(key)
        elif isinstance(key, BCSVField): 
            return BCSVFieldKey(key)
        else:
            raise TypeError(
                f"Unsupported key type: '{type(key).__name__}'.\n"
                f"Please use one of the following: {', '.join(['str', 'int', 'BCSVField'])}"
            )


class BCSVNameKey(BCSVKey):
    """ BCSVKey that uses the field name directly as an input string. """

    def __init__(self, name: str):
        """
        Args:
            name (str): name directly used to resolve
        """
        self.name = name

    def resolve_name(self) -> str:
        """
        Returns the internal name of the key/field
        
        Returns:
            str: Direct key/field name.
        """
        return self.name


class BCSVHashKey(BCSVKey):
    """ BCSVKey that uses the field hash as the key string. """

    def __init__(self, hash_val: int):
        """
        Args:
            hash_val (str): name directly used to resolve
        """
        self.hash_val = hash_val

    def resolve_name(self) -> str:
        """
        Returns the stringified version of the hash_val
        
        Returns:
            str: stringified hashed value.
        """
        return str(self.hash_val)


class BCSVFieldKey(BCSVKey):
    """ BCSVKey that uses the entire directly to get the key string. """

    def __init__(self, field: 'BCSVField'):
        """
        Args:
            field (BCSVField): Direct field to get the field name from.
        """
        self.field = field

    def resolve_name(self) -> str:
        """
        Returns the field's field_name value
        
        Returns:
            str: Provided field's field_name.
        """
        return self.field.field_name


def calculate_field_hash(field_name: str) -> int:
    """
    Field names are stored internally in RAM for GC/Wii games as hashes, as they are faster lookup tables. So, we will
    calculate the hast and the resulting hash is a 32-bit value. Breaks on first null byte (if any)

    Args:
        field_name (str): name of the field to calculate a hash for.
    """
    field_hash: int = 0

    for ch in field_name.encode(STRING_FORMAT):
        if ch == 0:
            break
        ch = ch - 256 if ch >= 128 else ch
        field_hash = (field_hash * 0x1F) + ch

    return field_hash & 0xFFFFFFFF


class BCSVType(IntEnum):
    """
    Indicates the type of data that will be stored in each field type.
    Strings are deprecated and should use of type STRING_OFFSET instead.
    Longs, Short, and Byte should all AND the read value with the field's bitmask and then
        shift the result by the field's shift amount.
    LONG and UNSIGNED_LONG are 32-bit integers. (Signedness not specified, as it can be both)
    FLOAT are 32-bit. (Signedness not specified, as it can be both)
    Short are 16-bit integers (Signedness not specified, as it can be both)
    BYTE is single char/8-bit integers (Signedness not specified, as it can be both)
    Floats are read and written as is.
    String_Offset return the offset from the start of the string pool table where the string can be found.
    """
    LONG = 0 # 32-bit integer.
    STRING = 1 # Embedded string. Deprecated.
    FLOAT = 2 # Single-precision floating-point value.
    UNSIGNED_LONG = 3 # 32-bit integer.
    SHORT = 4 # 16-bit integer.
    BYTE = 5 # Single char/8-bit integers
    STRING_OFFSET = 6 # 32-bit offset into string table.


class BCSVTypeSize(IntEnum):
    """Returns the size of the field based on its BCSVType."""
    WORD = 4
    HALF_WORD = 2
    BYTE = 1
    STRING = 32


class StringPoolElement(NamedTuple):
    """Contains a single element when writing to the output string pool table."""
    value: str
    offset: int


class BCSVField:
    """
    Represents a singular field of data in a BCSV file. Similar to a column in a data table.
    Fields are indexed by hashes and its named are defaulted to its hash stringified, however a
        field_hash->name converter function is provided.

    BCSV File Headers are comprised of 12 bytes in total.
    The first 4 bytes represent the field's hash. Currently, it is unknown how a field's name becomes a hash.
    The second 4 bytes represent the field's bitmask.
    The next 2 bytes represent the starting byte for the field within a given data line in the BCSV file.
    The second to last byte represents shift amount used on the field's value.
    The last byte represents the data type, see BCSVType for value -> type conversion.
    """
    field_hash: int = 0
    field_name: str = None
    field_bitmask: int = 0
    field_offset: int = 0
    field_shift: int = 0
    field_type: BCSVType = None


    def __init__(self, field_hash: int, field_bitmask: int, field_offset: int, data_shift: int, data_type: int):
        """
        Represents a single field/header of a BCSV file.
        
        Args:
            field_hash (int): 32-bit unsigned integer hash of a given field
            field_bitmask (int): 32-bit unsigned integer bitmask, can be 0
            field_offset (int): 16-bit unsigned integer offset within a given BCSV row to load data
            data_shift (int): 8-bit unsigned integer to shift a read value with
            data_type (int): 8-bit unsigned integer to signify the data value. See BCSVType
        """
        self.field_hash = field_hash
        self.field_name = str(self.field_hash)
        self.field_bitmask = field_bitmask
        self.field_offset = field_offset
        self.field_shift = data_shift
        self.field_type = BCSVType(data_type)


    @classmethod
    def import_field(cls, raw_bytes: BytesIO):
        """
        Creates a given field/header from the raw BytesIO (should be 12 bytes)

        Args:
            raw_bytes (BytesIO): Field bytes
        """
        reader = BinaryReader(raw_bytes)
        field_hash: int = reader.u32()
        field_bitmask: int = reader.u32()
        field_offset: int = reader.u16()
        field_shift: int = reader.u8()
        field_type: int = reader.u8()
        return cls(field_hash, field_bitmask, field_offset, field_shift, field_type)


    def export_field(self) -> bytes:
        """
        Exports a given field back to bytes (size: 0xC)

        Return:
            bytes: The field object back in its bytes format.
        """
        field_bytes: BytesIO = BytesIO()
        writer = BinaryWriter(field_bytes)
        writer.u32(self.field_hash)
        writer.u32(self.field_bitmask)
        writer.u16(self.field_offset)
        writer.u8(self.field_shift)
        writer.u8(self.field_type)
        return field_bytes.getvalue()


    def get_value_from_bytes(self, reader: BinaryReader) -> BCSVValue:
        """
        Gets the field's value from a given BCSV entry's bytes.
        
        Args:
            reader (BinaryReader): The reader

        Returns:
            BCSVValue: Converted object from bytes into its field_type format.
        """
        value: int | None = None
        reader.seek(self.field_offset)
        match self.field_type:
            case BCSVType.LONG | BCSVType.UNSIGNED_LONG:
                value = reader.s32()
                if self.field_bitmask == 0xFFFFFFFF and self.field_shift == 0:
                    return value
            case BCSVType.SHORT:
                value = reader.s16()
                if self.field_bitmask == 0xFFFF and self.field_shift == 0:
                    return value
            case BCSVType.BYTE:
                value = reader.s8()
                if self.field_bitmask == 0xFF and self.field_shift == 0:
                    return value
            case BCSVType.FLOAT:
                return reader.float()
            case BCSVType.STRING_OFFSET:
                return reader.u32()
            case BCSVType.STRING:
                return reader.string(BCSV_MAX_STRING_LENGTH)
            case _:
                raise TypeError(f"Unsupported BCSV Field type: {self.field_type}")

        return (value & self.field_bitmask) >> self.field_shift


    def set_value_in_buffer(self, reader: BinaryReader, writer: BinaryWriter, entry_value: BCSVValue, string_pool: list[StringPoolElement]):
        """
        Sets the field's value into a given BCSV entry's bytes.
        
        Args:
            reader (BinaryReader): The Binary reader
            writer (BinaryWriter): The Binary writer
            entry_value (BCSVValue): Value to transwer back to bytes.
            string_pool (list[StringPoolElement]): List of strings to write back into the string pool
        """
        reader.seek(self.field_offset)
        match self.field_type:
            case BCSVType.LONG | BCSVType.UNSIGNED_LONG:
                value = entry_value
                if not (self.field_bitmask == 0xFFFFFFFF and self.field_shift == 0):
                    value: int = reader.s32()
                    value |= (int(entry_value) << int(self.field_shift)) & int(self.field_bitmask)
                writer.seek(self.field_offset)
                writer.s32(value)
            case BCSVType.SHORT:
                value = entry_value
                if not (self.field_bitmask == 0xFFFF and self.field_shift == 0):
                    value: int = reader.s16()
                    value |= (int(entry_value) << int(self.field_shift)) & int(self.field_bitmask)
                writer.seek(self.field_offset)
                writer.s16(value)
            case BCSVType.BYTE:
                value = entry_value
                if not (self.field_bitmask == 0xFF and self.field_shift == 0):
                    value: int = reader.s8()
                    value |= (int(entry_value) << int(self.field_shift)) & int(self.field_bitmask)
                writer.seek(self.field_offset)
                writer.s8(value)
            case BCSVType.FLOAT:
                writer.seek(self.field_offset)
                writer.float(float(entry_value))
            case BCSVType.STRING:
                writer.seek(self.field_offset)
                writer.string(str(entry_value), BCSVTypeSize.STRING)
            case BCSVType.STRING_OFFSET:
                value: str = str(entry_value)
                pool_element: StringPoolElement = next((element for element in string_pool if
                    element.value == value), None)
                if pool_element is None:
                    pool_offset: int = 0
                    if string_pool:
                        highest_pair: StringPoolElement = string_pool[-1]
                        # + 1 because null byte terminated
                        pool_offset: int = highest_pair.offset + len(highest_pair.value.encode(writer.encoding)) + 1

                    pool_element = StringPoolElement(value, pool_offset)
                    string_pool.append(pool_element)
                writer.seek(self.field_offset)
                writer.s32(pool_element.offset)
            case _:
                raise TypeError(f"Unsupported BCSV Field type: {self.field_type}")


    def get_field_size(self) -> int:
        """
        Gets the expected field size of a BCSVValue type.
        
        Returns:
            int: Size of the field.
        """
        match self.field_type:
            case BCSVType.LONG | BCSVType.UNSIGNED_LONG | BCSVType.FLOAT | BCSVType.STRING_OFFSET:
                return BCSVTypeSize.WORD
            case BCSVType.SHORT:
                return BCSVTypeSize.HALF_WORD
            case BCSVType.BYTE:
                return BCSVTypeSize.BYTE
            case BCSVType.STRING:
                return BCSVTypeSize.STRING
            case _:
                raise TypeError(f"Unsupported BCSV Field type: {self.field_type}")

class BCSVEntry(dict[str, BCSVValue]):
    """BCSV entry class which allows for lookup as a string, int (field hash), or as a field directly."""
    hash_names: dict[int, str] = {}

    def __getitem__(self, key: int | str | BCSVField) -> BCSVValue:
        """
        Gets a given BCSVValue from a given key. Creates a BSCVKey from the input key provided to verify the field exists first.
        
        Args:
            key (BCSVKey): Key used find the related field's value

        Returns:
            BCSVValue: Field_type format's value.
        """
        bcsvField: str = BCSVKey.create(key).resolve_name()
        return super().__getitem__(bcsvField)


    def __setitem__(self, key: int | str | BCSVField, value: BCSVValue):
        """
        Sets a given BCSVValue from a given key. Creates a BSCVKey from the input key provided to verify the field exists first.
        
        Args:
            key (BCSVKey): Key used find the related field
        """
        if not isinstance(value, int | str | float):
            raise TypeError(f"Provided value {value} is not of valid types: {type(BCSVValue)}")

        bcsvField: str = BCSVKey.create(key).resolve_name()
        super().__setitem__(bcsvField, value)


class BCSV:
    """
    BCSV Files are table-structured format files that contain a giant header block and data entry block.
    These files remark a similar structure to modern day data tables, with one key difference
        The header block contains the definition of all field headers (columns) and field data
            Definition of these headers does not matter.
        The data block contains the table row data one line at a time. Each row is represented as a single list index,
            where a dictionary maps the key (column) to the value.
        And lastly, all strings are defined in a string table that is appended at the end of the data itself.
    BCSV Files also start with 16 bytes that are useful to explain the rest of the structure of the file.
    """
    fields: list[BCSVField]
    entries: list[BCSVEntry]
    str_fmt: str


    def __init__(self, fields: list[BCSVField] = None, entries: list[BCSVEntry] = None):
        """
        Represents a given BCSV file in its enterity.

        Args:
            fields (list[BCSVFields]): One or more fields/headers within a BCSV file.
            entries (list[BCSVEntry]): One or more entries within a BCSV file.
        """

        if fields is None:
            fields = []

        if entries is None:
            entries = []

        self.verify_fields_and_entries(fields, entries)

        self.fields = fields
        self.entries = entries
        self.str_fmt = STRING_FORMAT


    @classmethod
    def import_bcsv(cls, raw_data: BytesIO, field_names: dict[int, str] = None, str_fmt: str = STRING_FORMAT):
        """
        Takes an input stream of BCSV data and converts it into a BCSV object.

        Args:
            raw_data (BytesIO): raw stream of a file
            field_names (dict[int, str]): Contains the field_hash -> name quick lookup reference. 
                By default, a field's name is the same as the hash, this allows for human-readable names to be used instead.
            str_fmt (str): Output decoding format.
        """
        data_length: int = raw_data.seek(0, 2)
        raw_data.seek(0)
        if data_length < BCSV_HEADER_SIZE:
            raise InvalidFormatError("Provided BCSV BytesIO is not in a valid format.")

        if field_names is None:
            BCSVEntry.hash_names = {}
        else:
            BCSVEntry.hash_names = field_names

        bcsv: BCSV = cls() # initialize the class with some empty entry/field lists.
        reader = BinaryReader(raw_data, encoding=str_fmt)
        bcsv.str_fmt = str_fmt
        entry_count: int = reader.u32()
        field_count: int = reader.u32()
        entry_data_offset: int = reader.u32()
        entry_size_bytes: int = reader.u32()

        # Load all headers of this file
        fields_size: int = entry_data_offset - BCSV_HEADER_SIZE # BCSV Field details start after the above 16 bytes
        remainder_bytes: int = fields_size % BCSV_FIELD_SIZE
        read_field_count: int = int(fields_size / BCSV_FIELD_SIZE)
        if remainder_bytes != 0 or not read_field_count == field_count: # Make sure there is no extra space between fields and entries
            raise CorruptedDataError("When trying to read the fields block of the BCSV file, field block has an "
                f"incorrect size.\nExpected field count: {field_count}\nExpected Byte count: {fields_size}\n"
                f"Remainder Bytes: {remainder_bytes}\nAmount of fields found: {read_field_count}")

        # Load all data entries / rows of this table.
        calc_data_size: int = entry_data_offset + (entry_size_bytes * entry_count)
        if calc_data_size > data_length: # Simple check, doesn't take into account the string pool
            raise CorruptedDataError("When trying to read the data entries block of the BCSV file, the entry size "
                f"was incorrect.\nExpected data size: {data_length}\nCalculated data size: {calc_data_size}")

        offset: int = BCSV_HEADER_SIZE
        for _ in range(field_count):
            reader.seek(offset)
            field_bytes: BytesIO = BytesIO(reader.raw(BCSV_FIELD_SIZE))
            bcsv_field: BCSVField = BCSVField.import_field(field_bytes)
            if bcsv_field.field_hash in BCSVEntry.hash_names: # Replace hashes with field names if provided
                bcsv_field.field_name = field_names[bcsv_field.field_hash]
            bcsv.fields.append(bcsv_field)
            offset += BCSV_FIELD_SIZE

        # Read everything after the calculated data size until the end of the BCSV byte data.
        reader.seek(calc_data_size)

        offset = entry_data_offset
        for _ in range(entry_count):
            bcsv_entry: BCSVEntry = BCSVEntry()
            reader.seek(offset)
            entry_reader = BinaryReader(BytesIO(reader.raw(entry_size_bytes)), encoding=str_fmt)

            for bcsv_field in bcsv.fields:
                value: BCSVValue = bcsv_field.get_value_from_bytes(entry_reader)
                if bcsv_field.field_type == BCSVType.STRING_OFFSET:
                    reader.seek(calc_data_size + value)
                    value = reader.string_until_null()
                bcsv_entry[bcsv_field] = value
            bcsv.entries.append(bcsv_entry)
            offset += entry_size_bytes

        return bcsv


    def export_bcsv(self, str_fmt: str = STRING_FORMAT) -> BytesIO:
        """
        Converts this object back into a file stream.

        Args:
            str_fmt (str): Output decoding format.

        Returns:
            BytesIO: output BCSV object.
        """
        self.verify_fields_and_entries()

        field_count: int = len(self.fields)
        entry_count: int = len(self.entries)
        entry_data_offset: int  = BCSV_HEADER_SIZE + (BCSV_FIELD_SIZE * field_count)
        entry_size: int = self.calculate_data_entry_size()

        bcsv_data: BytesIO = BytesIO()
        writer = BinaryWriter(bcsv_data)
        writer.u32(entry_count)
        writer.u32(field_count)
        writer.u32(entry_data_offset)
        writer.u32(entry_size)

        # Write the header data back into the bcsv file
        offset = BCSV_HEADER_SIZE
        for field in self.fields:
            if not isinstance(field, BCSVField):
                raise TypeError(f"Field provided is not of type 'BCSVField'.\nReceived field type: {type(field)}\n"
                    f"Field: {field}\nField Index: {self.fields.index(field)}")

            writer.seek(offset)
            writer.raw(field.export_field())
            offset += BCSV_FIELD_SIZE

        # Now write the entries back into the bcsv file
        # String pool will contain a list
        string_pool: list[StringPoolElement] = []
        for entry in self.entries:
            if not isinstance(entry, BCSVEntry):
                raise TypeError(f"Entry provided is not of type 'BCSVEntry'.\nReceived entry type: {type(entry)}\n"
                    f"Entry: {entry}\nEntry Index: {self.entries.index(entry)}")

            entry_bytes: BytesIO = BytesIO(bytearray(entry_size))
            # Loop through all fields to write into the bcsv for each entry
            entry_reader = BinaryReader(entry_bytes, encoding=str_fmt)
            entry_writer = BinaryWriter(entry_bytes, encoding=str_fmt)
            for field in self.fields:
                field.set_value_in_buffer(entry_reader, entry_writer, entry[field], string_pool)

            # Update the entry bytes into the BCSV data object.
            writer.seek(offset)
            writer.raw(entry_bytes.getvalue())
            offset += entry_size

        # Create an empty string pool to write data to and eventually append to the end.
        string_pool_bytes: BytesIO = BytesIO()
        pool_writer = BinaryWriter(string_pool_bytes, encoding=str_fmt)
        for pool_element in string_pool:
            pool_writer.seek(pool_element.offset)
            pool_writer.string(pool_element.value,
                               size=len(pool_element.value.encode(str_fmt)),
                               add_null_byte=True)

        # Add the string pool bytes into BCSV data.
        writer.seek(offset)
        writer.raw(string_pool_bytes.getvalue())

        # BCSV Files are then padded with @ if their file size are not divisible by 32.
        curr_length = writer.size()
        if curr_length % 32 > 0:
            bcsv_data.seek(curr_length)
            writer.pad(32 - (curr_length % 32), b"@")

        return bcsv_data


    def calculate_data_entry_size(self) -> int:
        """
        Calculates the size of the entry based on the field's data type.
        Order of the entry size calculation is the following:
            STRING < FLOAT < LONG < LONG_2 < SHORT < BYTE < STRING_OFFSET

        Returns:
            int: Max field size thats required when writing.
        """
        return max([field.field_offset + field.get_field_size() for field in self.fields])


    def add_bcsv_field(self, bcsv_field: BCSVField, default_value: BCSVValue):
        """
        Adds a new BCSVField and a default value to all existing data entries.
        
        Args:
            bcsv_field (BCSVField): field to add into a given file.
            default_value (BCSVValue): Default value to use for all entries.
        """
        if bcsv_field.field_hash in [field.field_hash for field in self.fields]:
            raise BCSVFileError(f"BCSVField with hash '{bcsv_field.field_hash}' already exists as a field.")

        self.fields.append(bcsv_field)
        for data_entry in self.entries:
            data_entry[bcsv_field] = default_value


    def remove_bcsv_field(self, key: int | str | BCSVField):
        """
        Removes a new BCSVField and a default value to all existing data entries.
        
        Args:
            key (BCSVKey): field to add into a given file.
        """
        keyName = BCSVKey.create(key).resolve_name()
        field_found: BCSVField = next((field for field in self.fields if field.field_name == keyName), None)
        if field_found is None:
            raise ValueError(f"No BCSVField was found with key: {key}")

        for entry in self.entries:
            del entry[keyName]

        self.fields.remove(field_found)

    def add_bcsv_entry(self, bcsv_entry: BCSVEntry):
        """
        Adds a new data entry using field names or hashes as keys with complete field validation.
        
        Args:
            bcsv_entry (BCSVEntry): entry to add into the BCSV
        """
        if not self.fields:
            raise KeyError("Cannot add a BCSVEntry to a BCSV with no defined fields.")
        elif bcsv_entry is None or len(bcsv_entry.keys()) == 0:
            raise ValueError("Cannot add an empty BCSVEntry to the BCSV.")

        self.entries.append(bcsv_entry)


    def remove_bcsv_entry(self, bcsv_entry: int | BCSVEntry):
        """
        Deletes a BCSVEntry by either the Entry itself or the index number.
        
        Args:
            bcsv_entry (int | BCSVEntry): entry (or index) to remove from the BCSV
        """
        if isinstance(bcsv_entry, int):
            entry: BCSVEntry = self.entries[bcsv_entry]
        elif isinstance(bcsv_entry, BCSVEntry):
            entry: BCSVEntry = bcsv_entry
        else:
            raise ValueError(f"Cannot index BCSVEntry with value of type {type(bcsv_entry)}")

        self.entries.remove(entry)

    def verify_fields_and_entries(self, fields: list[BCSVField] = None, entries: list[BCSVEntry] = None):
        """
        Verifies if all the BCSV Fields are in fact properly defined keys/fields. Similarly validates entries.

        Args:
            fields (list[BCSVField]): A list of headers/fields for a BCSV file
            entries (list[BCSVEntry]): A list of rows/entries for a BCSV file
        """

        if fields is None:
            fields = self.fields
        
        if entries is None:
            entries = self.entries

        for bcsv_field in fields:
            if not isinstance(bcsv_field, BCSVField):
                raise BCSVFileError(f"Fields provided is not of type 'BCSVField'.\nReceived field type: {type(bcsv_field)}")
            
        for bcsv_entry in entries:
            if not isinstance(bcsv_entry, BCSVEntry):
                raise BCSVFileError(f"Entries provided is not of type 'BCSVEntry'.\nReceived field type: {type(bcsv_entry)}")

    @classmethod
    def read(cls, stream: BytesIO, **kwargs) -> "BCSV":
        return cls.import_bcsv(stream, **kwargs)

    def write(self, stream: BytesIO) -> None:
        stream.write(self.export_bcsv(self.str_fmt).getvalue())
