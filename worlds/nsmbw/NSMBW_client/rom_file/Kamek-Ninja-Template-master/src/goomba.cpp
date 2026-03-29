#include <kamek.h>

// Faster Goomba movement speed
kmWriteFloat(0x80ad2870, 2.0f);  // 0.5 -> 2.0
kmWriteFloat(0x80ad2874, -2.0f);  // -0.5 -> -2.0

// Faster Goomba bahp jump speed, animation speed, and other uses
kmWriteFloat(0x8042b7c8, 8.0f);  // 2.0 -> 8.0