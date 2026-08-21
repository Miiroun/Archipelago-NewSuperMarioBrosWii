#include <kamek.h>
#include <kamek_sdk.h>


// Skip Wii Remote Strap Screen PAL by CLF78
kmWrite32(0x803286C0, 0x8015D0A0);
kmWrite32(0x803286CC, 0x8015D010);
kmWrite32(0x803286D8, 0x8015CFC0);

// - exception handler // Disable the button sequence
kmWrite32(0x802D7528, 0x48000060);
