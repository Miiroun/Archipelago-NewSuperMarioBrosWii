#pragma once

#include <constants/message_list.h>

enum NEW_BMG_GROUPS_e {
    BMG_CATEGORY_PICTUREFONT_ICONS = 0x00,
    BMG_CATEGORY_NEWER_FILE_SELECT = 0x01,
    BMG_CATEGORY_MESSAGE_BOX_TITLE = 0x02,
    BMG_CATEGORY_MESSAGE_BOX_TEXT = 0x03,
    BMG_CATEGORY_LEVEL_NAMES = 0x100,
    BMG_CATEGORY_WORLD_NAMES = 0x200,
};

// Level names use format:
// Category: BMG_CATEGORY_LEVEL_NAMES + world number
// ID: level number

// World names use format:
// Category: BMG_CATEGORY_WORLD_NAMES
// ID: world number