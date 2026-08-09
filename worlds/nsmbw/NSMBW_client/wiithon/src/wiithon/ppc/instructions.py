import struct

# TODO: Can have constants for some OPCODE ? just to remove numbers in the code

def _pack(word: int) -> bytes:
    """
    Pack a 32-bit integer as a big-endian 4-byte sequence
    Can use Utils.pack_32
    """
    return struct.pack('>I', word)


def _check_reg(r: int, name: str = "register") -> None:
    """Raise ValueError if r is not a valid GPR (General Purpose Registers) index (0–31)"""
    if not (0 <= r <= 31):
        raise ValueError(f"{name} must be in [0, 31], got {r}")


def _check_freg(r: int, name: str = "register") -> None:
    """Raise ValueError if r is not a valid FPR (Floating-Point Registers) index (0–31)"""
    if not (0 <= r <= 31):
        raise ValueError(f"{name} must be in [0, 31], got {r}")


def _check_crf(crf: int, name: str = "CR field") -> None:
    """Raise ValueError if crf is not a valid condition register field (0–7)"""
    if not (0 <= crf <= 7):
        raise ValueError(f"{name} must be in [0, 7], got {crf}")


def _check_signed_imm16(imm: int, name: str = "immediate") -> None:
    """Raise ValueError if imm does not fit in a signed 16-bit field"""
    if not (-32768 <= imm <= 32767):
        raise ValueError(f"{name} must be a signed 16-bit value [-32768, 32767], got {imm}")


def _check_unsigned_imm16(imm: int, name: str = "immediate") -> None:
    """Raise ValueError if imm does not fit in an unsigned 16-bit field"""
    if not (0 <= imm <= 65535):
        raise ValueError(f"{name} must be an unsigned 16-bit value [0, 65535], got {imm}")


def _check_mb_me(val: int, name: str) -> None:
    """Raise ValueError if val is not a valid mask-begin/end value (0–31)"""
    if not (0 <= val <= 31):
        raise ValueError(f"{name} must be in [0, 31], got {val}")


def _branch_offset(target: int, from_addr: int) -> int:
    """Compute and validate the PC-relative offset for a 26-bit unconditional branch"""
    offset = target - from_addr
    if offset % 4 != 0:
        raise ValueError(f"Branch offset must be a multiple of 4, got {offset}")
    if not (-33554432 <= offset <= 33554428):
        raise ValueError(f"Branch offset out of 26-bit range: {offset:#x}")
    return offset


def _bc_offset(target: int, from_addr: int) -> int:
    """Compute and validate the PC-relative offset for a 16-bit conditional branch"""
    offset = target - from_addr
    if offset % 4 != 0:
        raise ValueError(f"Branch offset must be a multiple of 4, got {offset}")
    if not (-32768 <= offset <= 32764):
        raise ValueError(f"Conditional branch offset out of 16-bit range: {offset:#x}")
    return offset


# ---------------------------------------------------------------------------
# Format I - unconditional branch (b, bl, ba, bla)
# opcode=18, [OPCD:5][LI:24][AA:1][LK:1]
# ---------------------------------------------------------------------------

def b(target: int, from_addr: int) -> bytes:
    """b target  - unconditional relative branch, no link"""
    offset = _branch_offset(target, from_addr)
    li = (offset >> 2) & 0xFFFFFF
    return _pack((18 << 26) | (li << 2) | 0)


def bl(target: int, from_addr: int) -> bytes:
    """bl target  - unconditional relative branch with link (saves return address in LR)"""
    offset = _branch_offset(target, from_addr)
    li = (offset >> 2) & 0xFFFFFF
    return _pack((18 << 26) | (li << 2) | 1)


def ba(target: int) -> bytes:
    """ba target  - unconditional absolute branch, no link"""
    if target % 4 != 0:
        raise ValueError(f"Absolute branch target must be a multiple of 4, got {target:#x}")
    li = (target >> 2) & 0xFFFFFF
    return _pack((18 << 26) | (li << 2) | 2)


def bla(target: int) -> bytes:
    """bla target  - unconditional absolute branch with link"""
    if target % 4 != 0:
        raise ValueError(f"Absolute branch target must be a multiple of 4, got {target:#x}")
    li = (target >> 2) & 0xFFFFFF
    return _pack((18 << 26) | (li << 2) | 3)


# ---------------------------------------------------------------------------
# Format B - conditional branch (bc, bcl)
# opcode=16, [OPCD:5][BO:5][BI:5][BD:14][AA:1][LK:1]
# BD is a signed 14-bit field; actual offset = BD * 4 (range: +/-32 KB).
# BO encodes the branch condition: bit 4 = ignore CTR, bit 2 = ignore CR,
#   bit 3 = decrement/test CTR, bit 1 = CR bit value to test, bit 0 = branch
#   prediction hint.  Common values: 12 = branch if CR bit set,
#   4 = branch if CR bit clear, 20 = always
# BI selects which CR bit to test (0–31)
# ---------------------------------------------------------------------------

def _fmt_b(bo: int, bi: int, bd: int, aa: int = 0, lk: int = 0) -> bytes:
    if not (0 <= bo <= 31):
        raise ValueError(f"BO must be in [0, 31], got {bo}")
    if not (0 <= bi <= 31):
        raise ValueError(f"BI must be in [0, 31], got {bi}")
    return _pack(( 16 << 26) | (bo << 21) | (bi << 16) | (bd << 2) | aa | lk )

def bc(bo: int, bi: int, target: int, from_addr: int) -> bytes:
    """bc bo, bi, target  - conditional relative branch, no link"""
    offset = _bc_offset(target, from_addr)
    bd = (offset >> 2) & 0x3FFF
    return _fmt_b(bo, bi, bd)


def bcl(bo: int, bi: int, target: int, from_addr: int) -> bytes:
    """bcl bo, bi, target  - conditional relative branch with link"""
    offset = _bc_offset(target, from_addr)
    bd = (offset >> 2) & 0x3FFF
    return _fmt_b(bo, bi, bd, lk=1)

# ---------------------------------------------------------------------------
# Format XL - conditional branch to link register
# ---------------------------------------------------------------------------
def _fmt_xl(opcode: int, bt: int, ba_: int, bb: int, subopcode: int, lk: int = 0) -> bytes:
    return _pack((opcode << 26) | (bt << 21) | (ba_ << 16) | (bb << 11) | (subopcode << 1) | lk)

def bclr(bo: int, bi: int):
    return _fmt_xl(19, bo, bi,0, 16)

def bclrl(bo: int, bi: int):
    return _fmt_xl(19, bo, bi, 0, 16, lk=1)

def blr():
    return bclr(20, 0)

def blrl():
    return bclrl(20, 0)
# ---------------------------------------------------------------------------
# Compare instructions
# cmp  - Format X, opcode=31, subopcode=0
# cmpi - Format D, opcode=11
# The CRF field (3 bits) selects which CR field (cr0–cr7) receives the result.
# L=0 for 32-bit comparison (always the case on 32-bit PowerPC / Wii).
# ---------------------------------------------------------------------------

def cmp(crfD: int, rA: int, rB: int, l: int = 0) -> bytes:
    """cmp crfD, rA, rB  - signed integer compare; result written to CR field crfD"""
    _check_crf(crfD, "crfD")
    _check_reg(rA, "rA")
    _check_reg(rB, "rB")

    # bits 25:21 = [BF:3][0:1][L:1]
    field = (crfD << 2) | (l & 1)
    return _pack((31 << 26) | (field << 21) | (rA << 16) | (rB << 11) | (0 << 1) | 0)


def cmpi(crfD: int, rA: int, imm: int, l: int = 0) -> bytes:
    """cmpi crfD, rA, imm  - signed compare immediate; result written to CR field crfD"""
    _check_crf(crfD, "crfD")
    _check_reg(rA, "rA")
    _check_signed_imm16(imm)
    field = (crfD << 2) | (l & 1)
    return _pack((11 << 26) | (field << 21) | (rA << 16) | (imm & 0xFFFF))


# ---------------------------------------------------------------------------
# Format D - immediate
# [opcode:6][rD:5][rA:5][SIMM:16]
# rD can be rT, rS, BF:3 /:1 L:1
# SIMM can be D, SI, UI
# ---------------------------------------------------------------------------

def _fmt_d(opcode: int, rD: int, rA: int, imm: int) -> bytes:
    """Encode a Format-D instruction with a signed 16-bit immediate"""
    _check_reg(rD, "rD")
    _check_reg(rA, "rA")
    _check_signed_imm16(imm)
    return _pack((opcode << 26) | (rD << 21) | (rA << 16) | (imm & 0xFFFF))


def _fmt_d_unsigned(opcode: int, rD: int, rA: int, imm: int) -> bytes:
    """Encode a Format-D instruction with an unsigned 16-bit immediate"""
    _check_reg(rD, "rD")
    _check_reg(rA, "rA")
    _check_unsigned_imm16(imm)
    return _pack((opcode << 26) | (rD << 21) | (rA << 16) | (imm & 0xFFFF))


def li(rD: int, imm: int) -> bytes:
    """li rD, imm  - load signed 16-bit immediate"""
    return _fmt_d(14, rD, 0, imm)


def lis(rD: int, imm: int) -> bytes:
    """lis rD, imm  - load immediate shifted left 16 (accepts signed or unsigned 16-bit)"""
    if 0x8000 <= imm <= 0xFFFF:
        imm -= 0x10000
    return _fmt_d(15, rD, 0, imm)


def addi(rD: int, rA: int, imm: int) -> bytes:
    """addi rD, rA, imm  - add signed 16-bit immediate; rA=r0 reads as 0"""
    return _fmt_d(14, rD, rA, imm)


def addis(rD: int, rA: int, imm: int) -> bytes:
    """addis rD, rA, imm  - add immediate shifted; imm is placed in the high halfword"""
    return _fmt_d(15, rD, rA, imm)


def mulli(rD: int, rA: int, imm: int) -> bytes:
    """mulli rD, rA, imm  - multiply rA by signed 16-bit immediate, store low 32 bits"""
    return _fmt_d(7, rD, rA, imm)


def lwz(rD: int, offset: int, rA: int) -> bytes:
    """lwz rD, offset(rA)  - load word and zero-extend from effective address"""
    return _fmt_d(32, rD, rA, offset)


def stw(rS: int, offset: int, rA: int) -> bytes:
    """stw rS, offset(rA)  - store 32-bit word to effective address"""
    return _fmt_d(36, rS, rA, offset)


def lbz(rD: int, offset: int, rA: int) -> bytes:
    """lbz rD, offset(rA)  - load byte and zero-extend"""
    return _fmt_d(34, rD, rA, offset)


def stb(rS: int, offset: int, rA: int) -> bytes:
    """stb rS, offset(rA)  - store byte (low 8 bits of rS)"""
    return _fmt_d(38, rS, rA, offset)


def lhz(rD: int, offset: int, rA: int) -> bytes:
    """lhz rD, offset(rA)  - load halfword and zero-extend"""
    return _fmt_d(40, rD, rA, offset)


def sth(rS: int, offset: int, rA: int) -> bytes:
    """sth rS, offset(rA)  - store halfword (low 16 bits of rS)"""
    return _fmt_d(44, rS, rA, offset)


def ori(rA: int, rS: int, imm: int) -> bytes:
    """ori rA, rS, imm  - bitwise OR with unsigned 16-bit immediate"""
    return _fmt_d_unsigned(24, rS, rA, imm)

def oris(rA: int, rS: int, imm: int):
    """oris rA, rS, imm  - bitwise OR with unsigned 16-bit immediate shifted"""
    return _fmt_d_unsigned(0x19, rS, rA, imm)

def nop() -> bytes:
    """nop  - no operation (pseudo: ori r0, r0, 0)"""
    return ori(0, 0, 0)

def andi(rA: int, rS: int, imm: int) -> bytes:
    """andi. rA, rS, imm  - rA = rS & imm (unsigned 16-bit); always updates CR0"""
    return _fmt_d_unsigned(28, rS, rA, imm)



# ---------------------------------------------------------------------------
# Floating-point memory - Format D
# lfs  opcode=48
# stfs opcode=52
# frD/frS are floating-point register indices (0–31).
# ---------------------------------------------------------------------------

def lfs(frD: int, offset: int, rA: int) -> bytes:
    """lfs frD, offset(rA)  - load single-precision float, convert to double in frD"""
    _check_freg(frD, "frD")
    _check_reg(rA, "rA")
    _check_signed_imm16(offset, "offset")
    return _pack((48 << 26) | (frD << 21) | (rA << 16) | (offset & 0xFFFF))


def stfs(frS: int, offset: int, rA: int) -> bytes:
    """stfs frS, offset(rA)  - convert frS to single precision and store to memory"""
    _check_freg(frS, "frS")
    _check_reg(rA, "rA")
    _check_signed_imm16(offset, "offset")
    return _pack((52 << 26) | (frS << 21) | (rA << 16) | (offset & 0xFFFF))


# ---------------------------------------------------------------------------
# Format XO - arithmetic register-register
# [opcode:6][rD:5][rA:5][rB:5][OE:1][subopcode:9][Rc:1]
# ---------------------------------------------------------------------------

def _fmt_xo(opcode: int, rD: int, rA: int, rB: int, subopcode: int, oe: int = 0, rc: int = 0) -> bytes:
    """Encode a Format-XO instruction (register arithmetic with optional OE/Rc)"""
    _check_reg(rD, "rD")
    _check_reg(rA, "rA")
    _check_reg(rB, "rB")
    return _pack((opcode << 26) | (rD << 21) | (rA << 16) | (rB << 11) | (oe << 10) | (subopcode << 1) | rc)


def add(rD: int, rA: int, rB: int) -> bytes:
    """add rD, rA, rB  - rD = rA + rB"""
    return _fmt_xo(31, rD, rA, rB, 266)


def subf(rD: int, rA: int, rB: int) -> bytes:
    """subf rD, rA, rB  - subtract from: rD = rB - rA"""
    return _fmt_xo(31, rD, rA, rB, 40)


# ---------------------------------------------------------------------------
# Format X - logical register-register
# [opcode:6][rS:5][rA:5][rB:5][subopcode:10][Rc:1]
# ---------------------------------------------------------------------------

def _fmt_x(opcode: int, rS: int, rA: int, rB: int, subopcode: int, rc: int = 0) -> bytes:
    """Encode a Format-X instruction (register-register logical/shift)"""
    _check_reg(rS, "rS")
    _check_reg(rA, "rA")
    _check_reg(rB, "rB")
    return _pack((opcode << 26) | (rS << 21) | (rA << 16) | (rB << 11) | (subopcode << 1) | rc)


def and_(rA: int, rS: int, rB: int) -> bytes:
    """and rA, rS, rB  - rA = rS & rB"""
    return _fmt_x(31, rS, rA, rB, 28)


def or_(rA: int, rS: int, rB: int) -> bytes:
    """or rA, rS, rB  - rA = rS | rB"""
    return _fmt_x(31, rS, rA, rB, 444)


def mr(rA: int, rS: int) -> bytes:
    """mr rA, rS  - copy register (pseudo: or rA, rS, rS)"""
    return or_(rA, rS, rS)

def cntlzw(rA: int, rS: int) -> bytes:
    return _fmt_x(0x1F, rS, rA, 0, 26)


# ---------------------------------------------------------------------------
# Format M - rotate and mask
# [opcode:6][rS:5][rA:5][rB:5][MB:5][ME:5][Rc:1]
# rlwnm: rotate rS left by the amount in rB, then AND with mask(MB, ME).
# MB and ME define the contiguous mask: bits MB through ME (inclusive,
# wrapping) are set to 1, all others 0.
# ---------------------------------------------------------------------------

def _fmt_m(opcode: int, rS: int, rA: int, rB: int, mb: int, me: int, rc: int = 0) -> bytes:
    """Encode a Format-M instruction (rotate-and-mask)"""
    _check_reg(rS, "rS")
    _check_reg(rA, "rA")
    _check_reg(rB, "rB")
    _check_mb_me(mb, "MB")
    _check_mb_me(me, "ME")
    return _pack((opcode << 26) | (rS << 21) | (rA << 16) | (rB << 11) | (mb << 6) | (me << 1) | rc)


def rlwnm(rA: int, rS: int, rB: int, mb: int, me: int) -> bytes:
    """rlwnm rA, rS, rB, MB, ME  - rotate rS left by rB bits, AND with mask(MB, ME), store in rA"""
    return _fmt_m(23, rS, rA, rB, mb, me)


# ---------------------------------------------------------------------------
# SPR - move to/from special-purpose registers
# mfspr / mtspr: [opcode:6][rD:5][SPR:10][subopcode:10][0:1]
# SPR is encoded as two 5-bit halves swapped: spr[4:0] in bits 15:11, spr[9:5] in bits 20:16
# ---------------------------------------------------------------------------

def _encode_spr(spr: int) -> int:
    """Encode a 10-bit SPR number with its two 5-bit halves swapped as required by the ISA"""
    return ((spr & 0x1F) << 5) | ((spr >> 5) & 0x1F)


def mfspr(rD: int, spr: int) -> bytes:
    """mfspr rD, spr  - move from special-purpose register into rD"""
    _check_reg(rD, "rD")
    return _pack((31 << 26) | (rD << 21) | (_encode_spr(spr) << 11) | (339 << 1))


def mtspr(spr: int, rS: int) -> bytes:
    """mtspr spr, rS  - move rS into special-purpose register"""
    _check_reg(rS, "rS")
    return _pack((31 << 26) | (rS << 21) | (_encode_spr(spr) << 11) | (467 << 1))


# SPR numbers
_SPR_XER = 1
_SPR_LR  = 8
_SPR_CTR = 9


def mflr(rD: int) -> bytes:
    """mflr rD  - move Link Register into rD"""
    return mfspr(rD, _SPR_LR)


def mtlr(rS: int) -> bytes:
    """mtlr rS  - move rS into Link Register"""
    return mtspr(_SPR_LR, rS)


def mfctr(rD: int) -> bytes:
    """mfctr rD  - move Count Register into rD"""
    return mfspr(rD, _SPR_CTR)


def mtctr(rS: int) -> bytes:
    """mtctr rS  - move rS into Count Register"""
    return mtspr(_SPR_CTR, rS)
