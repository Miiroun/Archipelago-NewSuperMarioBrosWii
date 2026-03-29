#include <kamek.h>

// Faster timer countdown speed
kmWrite32(0x800e3ab8, 0x3403fe90);  // 92 -> 368