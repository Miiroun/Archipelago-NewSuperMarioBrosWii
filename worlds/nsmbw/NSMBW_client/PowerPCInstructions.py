
instru_return   : bytes = b'\x4E\x80\x00\x20' #4e800020
instru_noop     : bytes = b'\x48\x00\x00\x28' #??? not sure if correct #48000028
instru_li  : bytes = b'\x38\x60'  #li 38 60 00 00 # 4 bits value that is set
#instru_lbz      : bytes = b"\x"
instru_stwu      : bytes = b"\x94\x21"
instru_check_eq : bytes = b"\x2c\x03"
instru_lbz_r3    : bytes = b"\x88\x63"
instru_bne      : bytes = b"\x40\x82" #branch if not equal
instru_beq      : bytes = b"\x41\x82" #branch if equal
instru_b        : bytes = b'\x48'
instru_bl       : bytes = b'\x4b\x83'
instru_lhz      : bytes = b"\xA0"

instru_6000     : bytes = b'\x60\x00\x00\x00'

reg_r0     : bytes = b'\x00\x00'
#reg_sp    : bytes = b'\xff\xf0'

val_0000   : bytes = b'\x00\x00'
val_0001   : bytes = b'\x00\x01'
val_0002   : bytes = b'\x00\x02'
val_0003   : bytes = b'\x00\x03'
val_0008   : bytes = b'\x00\x08'
val_0010   : bytes = b'\x00\x10'
val_0014   : bytes = b'\x00\x14'
val_0017   : bytes = b'\x00\x17'
val_0018   : bytes = b'\x00\x18'
val_0019   : bytes = b'\x00\x19'
val_ffc0   : bytes = b'\xff\xc0'
val_ffd0   : bytes = b'\xff\xd0'
val_ffe0   : bytes = b'\xff\xe0'
val_ffff   : bytes = b'\xff\xff'




