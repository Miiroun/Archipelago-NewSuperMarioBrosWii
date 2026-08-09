# ArenaLo Research Notes

## Signature Pattern

```
3c 60 ?? ?? 38 63 ?? ?? 38 03 ?? ?? 54 03
```

If someone found a game with this sequence but it's not the setter of arenaLo (or arenaHi, since it uses the same thing), ping me !
This pattern always corresponds to the following sequence:

```asm
lis    r3, HI      ; 3c 60 ?? ??   <- instruction to patch
addi   r3, r3, LO  ; 38 63 ?? ??
addi   r0, r3, 31  ; 38 03 ?? ??
rlwinm r3, r0, …   ; 54 03 ?? ??
```

> **Key observation:** `arenaLo − DOL_bss_end ~ 0x10000` across all tested games.
> The DOL header `bss_end` field is **not** the real arenaLo - it is always ~64 KB below.
> Never use `bss_start + bss_size` to compute a safe injection address.

---

## Summary Table

| Game               | ID     | arenaLo      | arenaLo -  bss_end | Instruction to patch |
|--------------------|--------|--------------|--------------------|----------------------|
| Skyward Sword      | SOUE01 | `0x806882C0` | `+0x10000`         | `0x803A2AF0`         |
| Super Mario Galaxy | RMGE01 | `0x806BDFA0` | `+0x10010`         | `0x804A16BC`         |
| Mario Strikers     | RSBE01 | `0x806F6D20` | `+0x1001C`         | `0x803B1F74`         |
| Mario Kart Wii     | RMCE01 | `0x80394E00` | `+0x10004`         | `0x8019FD28`         |
| Wii Sports (Rev1)  | RSPE01 | `0x804D6A20` | `+0x10004`         | `0x800EC978`         |
| Wii Sports (Rev0)  | RSPE01 | —            | `+0x1000C`         | `0x800C65B4`         |

---

## Game Details

### Skyward Sword — SOUE01 (USA, v1.0)

| Field                    | Value                                   |
|--------------------------|-----------------------------------------|
| BSS                      | `80574FA0 — 806782C0` (size `00103320`) |
| arenaLo                  | `0x806882C0`                            |
| arenaLo - BSS_end        | `+0x10000`                              |
| `OSSetMEM1ArenaLo`       | `0x803A4010`                            |
| Called by                | `0x803A2B08`                            |
| **Instruction to patch** | **`0x803A2AF0`**                        |

<details>
<summary>DOL sections</summary>

```
entry:  80004050
bss:    80574FA0 — 806782C0  (size: 00103320)

text[0]: 80004000 — 80006720  (size: 00002720)
text[1]: 80006C20 — 804DB640  (size: 004D4A20)
data[0]: 80006720 — 80006920  (size: 00000200)
data[1]: 80006920 — 80006C20  (size: 00000300)
data[2]: 804DB640 — 804DB9E0  (size: 000003A0)
data[3]: 804DB9E0 — 804DBA00  (size: 00000020)
data[4]: 804DBA00 — 804FD060  (size: 00021660)
data[5]: 804FD060 — 80571440  (size: 000743E0)
data[6]: 80571440 — 80574FA0  (size: 00003B60)
data[7]: 805769C0 — 8057FFA0  (size: 000095E0)
```
</details>

---

### Super Mario Galaxy — RMGE01 (USA, v1.0)

| Field                    | Value                                   |
|--------------------------|-----------------------------------------|
| BSS                      | `805F5A40 — 806ADF90` (size `000B8550`) |
| arenaLo                  | `0x806BDFA0`                            |
| arenaLo - BSS_end        | `+0x10010`                              |
| `OSSetMEM1ArenaLo`       | —                                       |
| Called by                | `0x804A16D4`                            |
| **Instruction to patch** | **`0x804A16BC`**                        |

<details>
<summary>DOL sections</summary>

```
entry:  8000403C
bss:    805F5A40 — 806ADF90  (size: 000B8550)

text[0]: 80004000 — 800064E0  (size: 000024E0)
text[1]: 800070A0 — 8052D280  (size: 005261E0)
data[0]: 800064E0 — 800069A0  (size: 000004C0)
data[1]: 800069A0 — 800070A0  (size: 00000700)
data[2]: 8052D280 — 8052DEE0  (size: 00000C60)
data[3]: 8052DEE0 — 8052DF00  (size: 00000020)
data[4]: 8052DF00 — 8054EE20  (size: 00020F20)
data[5]: 8054EE20 — 805F5A20  (size: 000A6C00)
data[6]: 8069CCA0 — 8069E4A0  (size: 00001800)
data[7]: 806A3280 — 806ADF60  (size: 0000ACE0)
```
</details>

---

### Mario Strikers Charged — RSBE01 (Europe, v1.02)

| Field                    | Value                                   |
|--------------------------|-----------------------------------------|
| BSS                      | `80567880 — 806E6D04` (size `0017F484`) |
| arenaLo                  | `0x806F6D20`                            |
| arenaLo - BSS_end        | `+0x1001C`                              |
| `OSSetMEM1ArenaLo`       | `0x803B31EC`                            |
| Called by                | `0x803B1F8C`                            |
| **Instruction to patch** | **`0x803B1F74`**                        |

<details>
<summary>DOL sections</summary>

```
entry:  80006124
bss:    80567880 — 806E6D04  (size: 0017F484)

text[0]: 80004000 — 800064E0  (size: 000024E0)
text[1]: 80007400 — 804DAC60  (size: 004D3860)
data[0]: 800064E0 — 80006B00  (size: 00000620)
data[1]: 80006B00 — 80007400  (size: 00000900)
data[2]: 804DAC60 — 804DB340  (size: 000006E0)
data[3]: 804DB340 — 804DB360  (size: 00000020)
data[4]: 804DB380 — 804F3A20  (size: 000186A0)
data[5]: 804F3A20 — 80567880  (size: 00073E60)
data[6]: 806DA540 — 806DFCE0  (size: 000057A0)
data[7]: 806E21C0 — 806E6CC0  (size: 00004B00)
```
</details>

---

### Mario Kart Wii — RMCE01 (USA, Disc 1, Rev 0)

| Field                    | Value                                   |
|--------------------------|-----------------------------------------|
| BSS                      | `8029FD00 — 80384DFC` (size `000E50FC`) |
| arenaLo                  | `0x80394E00`                            |
| arenaLo - BSS_end        | `+0x10004`                              |
| `OSSetMEM1ArenaLo`       | `0x801A104C`                            |
| Called by                | `0x8019FD40`                            |
| **Instruction to patch** | **`0x8019FD28`**                        |

<details>
<summary>DOL sections</summary>

```
entry:  800060A4
bss:    8029FD00 — 80384DFC  (size: 000E50FC)

text[0]: 80004000 — 80006460  (size: 00002460)
text[1]: 800072C0 — 80244D40  (size: 0023DA80)
data[0]: 80006460 — 80006A20  (size: 000005C0)
data[1]: 80006A20 — 800072C0  (size: 000008A0)
data[2]: 80244D40 — 80244E00  (size: 000000C0)
data[3]: 80244E00 — 80244E20  (size: 00000020)
data[4]: 80244E40 — 80258260  (size: 00013420)
data[5]: 80258260 — 8029FD00  (size: 00047AA0)
data[6]: 80380880 — 80381C40  (size: 000013C0)
data[7]: 80382C20 — 80384DC0  (size: 000021A0)
```
</details>

---

### Wii Sports — RSPE01 (USA, Disc 1, Rev 1)

| Field                    | Value                                   |
|--------------------------|-----------------------------------------|
| BSS                      | `803CAF00 — 804C6A1C` (size `000FBB1C`) |
| arenaLo                  | `0x804D6A20`                            |
| arenaLo - BSS_end        | `+0x10004`                              |
| `OSSetMEM1ArenaLo`       | `0x800EDBF0`                            |
| Called by                | `0x800EC990`                            |
| **Instruction to patch** | **`0x800EC978`**                        |

<details>
<summary>DOL sections</summary>

```
entry:  80006124
bss:    803CAF00 — 804C6A1C  (size: 000FBB1C)

text[0]: 80004000 — 800064E0  (size: 000024E0)
text[1]: 800076E0 — 80355080  (size: 0034D9A0)
data[0]: 800064E0 — 80006C20  (size: 00000740)
data[1]: 80006C20 — 800076E0  (size: 00000AC0)
data[2]: 80355080 — 80355260  (size: 000001E0)
data[3]: 80355260 — 80355280  (size: 00000020)
data[4]: 80355280 — 80375780  (size: 00020500)
data[5]: 80375780 — 80393A80  (size: 0001E300)
data[6]: 80393A80 — 803CAF00  (size: 00037480)
data[7]: 804BD380 — 804BE9E0  (size: 00001660)
data[8]: 804BFA20 — 804C69E0  (size: 00006FC0)
```
</details>

---

### Wii Sports — RSPE01 (USA, Disc 1, Rev 0)

| Field                    | Value                                   |
|--------------------------|-----------------------------------------|
| BSS                      | `80392E80 — 804E6D78` (size `00153EF8`) |
| arenaLo                  | —                                       |
| arenaLo - BSS_end        | `+0x1000C`                              |
| `OSSetMEM1ArenaLo`       | —                                       |
| Called by                | —                                       |
| **Instruction to patch** | **`0x800C65B4`**                        |

<details>
<summary>DOL sections</summary>

```
entry:  80006124
bss:    80392E80 — 804E6D78  (size: 00153EF8)

text[0]: 80004000 — 800064E0  (size: 000024E0)
text[1]: 800074A0 — 803300A0  (size: 00328C00)
data[0]: 800064E0 — 80006B40  (size: 00000660)
data[1]: 80006B40 — 800074A0  (size: 00000960)
data[2]: 803300A0 — 80330280  (size: 000001E0)
data[3]: 80330280 — 803302A0  (size: 00000020)
data[4]: 803302A0 — 80340E80  (size: 00010BE0)
data[5]: 80340E80 — 8035D800  (size: 0001C980)
data[6]: 8035D800 — 80392E40  (size: 00035640)
data[7]: 804DDAE0 — 804DF0A0  (size: 000015C0)
data[8]: 804E0020 — 804E6D40  (size: 00006D20)
```
</details>
