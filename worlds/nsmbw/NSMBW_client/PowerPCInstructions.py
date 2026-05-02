
instru_return   : bytes = b'\x4E\x80\x00\x20' #4e800020
instru_noop     : bytes = b'\x48\x00\x00\x28' #??? not sure if correct #48000028
instru_load_im  : bytes = b'\x38\x60'  #li 38 60 00 00 # 4 bits value that is set
#instru_lbz      : bytes = b"\x"
intru_stwu      : bytes = b"\x94\x21"
instru_check_eq : bytes = b"\x2c\x03"
intru_lbz_r3    : bytes = b"\x88\x63"
intru_b         : bytes = b"\x4b\xff"
instru_bne      : bytes = b"\x40\x82" #branch if not equal
instru_beq      : bytes = b"\x41\x82" #branch if equal
instru_lhz      : bytes = b"\xA0"


reg_r0     : bytes = b'\x00\x00'
#reg_sp    : bytes = b'\xff\xf0'


val_0000   : bytes = b'\x00\x00'
val_0017   : bytes = b'\x00\x17'
val_ffc0   : bytes = b'\xff\xc0'
val_ffd0   : bytes = b'\xff\xd0'
val_ffe0   : bytes = b'\xff\xe0'
val_ffff   : bytes = b'\xff\xff'