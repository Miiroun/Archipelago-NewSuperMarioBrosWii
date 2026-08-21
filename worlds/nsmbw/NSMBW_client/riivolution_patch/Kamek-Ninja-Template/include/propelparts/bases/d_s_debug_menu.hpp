#pragma once
#include <game/bases/d_scene.hpp>
#include <propelparts/bases/d_debug_text_writer.hpp>

// Debug Menu

class dScDebugMenu_c : public dScene_c {
public:
    enum DEBUG_MENU_OPTION_e {
        LEVEL_PICKER,
        GOTO_LEVEL,
        SOUND_PICKER,
        SOUND_TEST,

        CHOICE_COUNT,

        PICK_WORLD,
        PICK_LEVEL,
        PICK_AREA,
        PICK_ENTRANCE,
        PICK_SOUND,

        OPTION_COUNT
    };

    dScDebugMenu_c();
    virtual ~dScDebugMenu_c();

    // fBase_c overrides
    virtual int create();
    virtual int execute();
    virtual int draw();

    int mCurrentSelection;
    u8 mWorld, mLevel, mArea, mEntrance;
    u32 mSound;

    dDebugTextWriter_c *mpTextWriter;

    static dScDebugMenu_c *m_instance;
};

struct dDebugCursorInfo {
    f32 x, y;
    const char *character;
};