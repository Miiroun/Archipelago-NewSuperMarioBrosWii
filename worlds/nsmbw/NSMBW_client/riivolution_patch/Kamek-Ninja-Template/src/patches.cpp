#include <kamek.h>
#include <kamek_sdk.h>


// Writes that riivolution is active to mem, to verify in client
kmWrite32(0x80BBB01C, 0xFFFFFFFF);


// Skip Wii Remote Strap Screen PAL by CLF78
//kmWrite32(0x803286C0, 0x8015D0A0);
//kmWrite32(0x803286CC, 0x8015D010);
//kmWrite32(0x803286D8, 0x8015CFC0);
// does not work

// - exception handler // Disable the button sequence
kmWrite32(0x802D7528, 0x48000060);


// from pipe rando

// Skip opening cutscene
kmWrite32(0x809191C4, 0x48000018);

// Skip title screen movies
kmWrite32(0x80781FB8, 0x60000000);
kmWrite32(0x80781FBC, 0x38600000);