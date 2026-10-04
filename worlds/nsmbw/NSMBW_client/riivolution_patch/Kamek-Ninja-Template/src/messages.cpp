// [Gecko]
// $Death Messages [mkwcat]
// *Adds a witty death message to the bottom left of the screen when a player
// *takes damage. Unlike what the title suggests, you don't actually have to die
// *for a message to display. That was the original idea but I never got around
// *to doing that.
// *
// *This code is long, and won't load using a standard gecko codehandler (such
// *as the one in Dolphin). To resolve this, I've created a gecko code to load
// *more gecko codes (see [Load-More-Gecko-Codes](Load-More-Gecko-Codes.md)).

//#include <gct-use-cpp.h>
//#include <gct.h>

//#include <algorithm>
//#include <array>
//#include <d_player/d_a_player.h>
//#include <d_system/d_game_com.h>
#include <egg/core/eggHeap.h>
#include <msl.h>
#include <new>
//#include <numeric>
#include <nw4r/lyt/lyt_resourceAccessor.h>

#include <nw4r/lyt/lyt_resources.h>
#include <nw4r/lyt/lyt_textBox.h>
#include <profiles.hpp>
#include <types.h>


#include <bases/d_actor.hpp>
#include <bases/d_game_com.hpp>

enum DamageType_e {
    DAMAGE_NORMAL = 0,
    DAMAGE_NORMAL2 = 1,
    DAMAGE_KNOCKBACK_AND_HURT = 2,
    DAMAGE_KNOCKBACK_LONG = 3, // Player does not take damage
    DAMAGE_KNOCKBACK_LONG2 = 4, // Player does not take damage
    DAMAGE_KNOCKBACK_SHORT = 5, // Player does not take damage
    DAMAGE_KNOCKBACK_SHORT2 = 6, // Player does not take damage
    DAMAGE_LAVA = 7,
    DAMAGE_FIRE = 8, // Looks the same as DAMAGE_NORMAL?
    DAMAGE_ELEC_SHOCK = 9,
    DAMAGE_POISON_WATER = 10,
    DAMAGE_CRUSH = 11,
    DAMAGE_EAT_DIE = 12,
    DAMAGE_EAT_DIE2 = 13, // Like DAMAGE_EAT_DIE but does not stop the music
    DAMAGE_UNKNOWN = 14,
    DAMAGE_FREEZE = 15,
    DAMAGE_FREEZE2 = 16,
    DAMAGE_BOUNCE = 17, // Makes the player do a squishy animation
    DAMAGE_POISON_FOG = 18,
};

class dAcPy_c_extended : public dActor_c {
    // Added for Death-Messages
    void setDeathMessage(const char* message, const char* enemy);

    // Used for functions outside of Death-Messages to override the current
    // message. Uses function alignment padding to add a new global variable.
    static const char* sDeathMessageOverride;

    void setBalloonInDispOut_Override(int type);
    bool setDamage2_Override(dActor_c* source, DamageType_e type);

    s32 mCharacter;

    bool setDamage2__IMPL(dActor_c* source, DamageType_e type);
};

/*
GCT_ASM(
    // clang-format off

GCT_INSERT(0x801589B0, dGameDisplay_Setup)
    lwz     r3, 0x70 + 0x84(r30);
    lwz     r3, 0x4(r3);
    addi    r4, r30, 0x70 + 0x30;
    bl      dGameDisplay_InitDeathMsg;
GCT_INSERT_END(dGameDisplay_Setup)

    // clang-format on
) // GCT_ASM
*/



struct ActorName {
    ProfileNameEnum profile;
    char name[256];
};

//constexpr ActorName s_names[] = {
ActorName s_names[] = {
/*
    {ProfileNameEnum::EN_KURIBO, "Goomba"},
    {ProfileNameEnum::EN_PATA_KURIBO, "Paragoomba"},
    {ProfileNameEnum::EN_MAME_KURIBO, "Mini Goomba"},
    {ProfileNameEnum::EN_NOKONOKO, "Koopa Troopa"},
    {ProfileNameEnum::EN_PATAPATA, "Paratroopa"},
    {ProfileNameEnum::EN_MET, "Buzzy Beetle"},
    {ProfileNameEnum::EN_TOGEZO, "Spiny"},
    {ProfileNameEnum::EN_SAKASA_TOGEZO, "Upside-down Spiny"},
    {ProfileNameEnum::EN_BUBBLE, "Lava Bubble"},
    {ProfileNameEnum::EN_DOSUN, "Thwomp"},
    {ProfileNameEnum::EN_BIGDOSUN, "Big Thwomp"},
    {ProfileNameEnum::EN_JUGEM, "Lakitu"},
    {ProfileNameEnum::EN_JUGEM_COIN, "Lakitu"},
    {ProfileNameEnum::EN_EATJUGEM, "Lakitu"},
    {ProfileNameEnum::EN_JUGEM_BODY, "Lakitu"},
    {ProfileNameEnum::EN_TOGEMET, "Spike Top"},
    {ProfileNameEnum::EN_FIREBAR, "Fire Bar"},
    {ProfileNameEnum::EN_TOGETEKKYU, "Spike Ball"},
    {ProfileNameEnum::EN_BIG_TOGETEKKYU, "Big Spike Ball"},
    {ProfileNameEnum::EN_UP_DOKAN_PAKKUN, "Piranha Plant"},
    {ProfileNameEnum::EN_DOWN_DOKAN_PAKKUN, "Piranha Plant"},
    {ProfileNameEnum::EN_RIGHT_DOKAN_PAKKUN, "Piranha Plant"},
    {ProfileNameEnum::EN_LEFT_DOKAN_PAKKUN, "Piranha Plant"},
    {ProfileNameEnum::EN_UP_DOKAN_FPAKKUN, "Fire Piranha Plant"},
    {ProfileNameEnum::EN_DOWN_DOKAN_FPAKKUN, "Fire Piranha Plant"},
    {ProfileNameEnum::EN_RIGHT_DOKAN_FPAKKUN, "Fire Piranha Plant"},
    {ProfileNameEnum::EN_LEFT_DOKAN_FPAKKUN, "Fire Piranha Plant"},
    {ProfileNameEnum::EN_JIMEN_PAKKUN, "Piranha Plant"},
    {ProfileNameEnum::EN_JIMEN_BIG_PAKKUN, "Big Guy"},
    {ProfileNameEnum::EN_JIMEN_FPAKKUN, "Fire Piranha Plant"},
    {ProfileNameEnum::EN_JIMEN_BIG_FPAKKUN, "Big Fire Guy"},
    {ProfileNameEnum::EN_WALK_PAKKUN, "Stalking Piranha Plant"},
    {ProfileNameEnum::ICEBALL, "Ice Ball"},
    {ProfileNameEnum::PL_FIREBALL, "Fireball"},
    {ProfileNameEnum::PAKKUN_FIREBALL, "Piranha Plant Fireball"},
    {ProfileNameEnum::BROS_FIREBALL, "Fire Bro Fireball"},
    {ProfileNameEnum::BOOMERANG, "Boomerang"},
    {ProfileNameEnum::EN_FIREBROS, "Fire Bro"},
    {ProfileNameEnum::EN_BOOMERANGBROS, "Boomerang Bro"},
    {ProfileNameEnum::EN_HAMMERBROS, "Hammer Bro"},
    {ProfileNameEnum::EN_LIFT_HAMMERBROS, "Hammer Bro"},
    {ProfileNameEnum::EN_ICEBROS, "Ice Bro"},
    {ProfileNameEnum::HAMMER, "Hammer"},
    {ProfileNameEnum::EN_HIMANBROS, "Sledge Bro"},
    {ProfileNameEnum::MEGA_HAMMER, "Sledge Bro Hammer"},
    {ProfileNameEnum::BROS_ICEBALL, "Ice Bro Iceball"},
    {ProfileNameEnum::EN_KILLER, "Bullet Bill"},
    {ProfileNameEnum::EN_SEARCH_KILLER, "Bullseye Bill"},
    {ProfileNameEnum::EN_MAGNUM_KILLER, "Banzai Bill"},
    {ProfileNameEnum::EN_SEARCH_MAGNUM_KILLER, "Bullseye Banzai Bill"},
    {ProfileNameEnum::EN_BASABASA, "Swoop"},
    {ProfileNameEnum::WAKI_PARABOM, "Parabomb"},
    {ProfileNameEnum::EN_PARA_BOMHEI, "Parabomb"},
    {ProfileNameEnum::EN_BOMHEI, "Bob-omb"},
    {ProfileNameEnum::EN_MECHA_KOOPA, "Mechakoopa"},
    {ProfileNameEnum::EN_MOUSE, "Scaredy Rat"},
    {ProfileNameEnum::EN_BIRIKYU, "Amp"},
    {ProfileNameEnum::EN_LINE_BIRIKYU, "Amp"},
    {ProfileNameEnum::EN_CHOROBON, "Fuzzy"},
    {ProfileNameEnum::EN_SANBO, "Pokey"},
    {ProfileNameEnum::EN_SANBO_PARTS, "Pokey"},
    {ProfileNameEnum::EN_SANBO_EL, "Pokey"},
    {ProfileNameEnum::EN_GURUGURU, "Ball and Chain"},
    {ProfileNameEnum::EN_SYNCRO_BARNAR, "Burner"},
    {ProfileNameEnum::EN_BARNAR, "Burner"},
    {ProfileNameEnum::EN_LARGE_BARNAR, "Burner"},
    {ProfileNameEnum::ROT_BARNAR, "Burner"},
    {ProfileNameEnum::EN_GESSO, "Blooper"},
    {ProfileNameEnum::EN_BARAMAKI_GESSO, "Blooper Nanny"},
    {ProfileNameEnum::EN_GESSO_CHILD, "Blooper Baby"},
    {ProfileNameEnum::EN_PUKUPUKU_PARENT, "Cheep Cheep"},
    {ProfileNameEnum::EN_PUKUPUKU, "Cheep Cheep"},
    {ProfileNameEnum::EN_TOGEPUKU, "Spiny Cheep Cheep"},
    {ProfileNameEnum::EN_MIDDLE_PUKU, "Big Cheep Cheep"},
    {ProfileNameEnum::EN_KARON, "Dry Bones"},
    {ProfileNameEnum::EN_BIGKARON, "Big Dry Bones"},
    {ProfileNameEnum::EN_NET_NOKONOKO_LR, "Climbing Koopa"},
    {ProfileNameEnum::EN_NET_NOKONOKO_UD, "Climbing Koopa"},
    {ProfileNameEnum::EN_HANACHAN, "Wiggler"},
    {ProfileNameEnum::EN_BIG_HANACHAN, "Big Wiggler"},
    {ProfileNameEnum::EN_TERESA, "Boo"},
    {ProfileNameEnum::EN_BIG_TERESA, "Big Boo"},
    {ProfileNameEnum::EN_CROW, "Crowber"},
    {ProfileNameEnum::EN_BIGPILE_UNDER, "Skewer"},
    {ProfileNameEnum::EN_BIGPILE_UPPER, "Skewer"},
    {ProfileNameEnum::EN_BIGPILE_RIGHT, "Skewer"},
    {ProfileNameEnum::EN_BIGPILE_LEFT, "Skewer"},
    {ProfileNameEnum::EN_SUPER_BIGPILE_RIGHT, "Skewer"},
    {ProfileNameEnum::EN_SUPER_BIGPILE_LEFT, "Skewer"},
    {ProfileNameEnum::EN_GOKUBUTO_BIGPILE_UNDER, "Skewer"},
    {ProfileNameEnum::EN_GOKUBUTO_BIGPILE_UPPER, "Skewer"},
    {ProfileNameEnum::EN_WANWAN, "Chain Chomp"},
    {ProfileNameEnum::EN_JUMPPUKU, "Jumping Cheep Cheep"},
    {ProfileNameEnum::EN_TOBIPUKU, "Jumping Cheep Cheep"},
    {ProfileNameEnum::EN_IGAPUKU, "Porcupuffer"},
    {ProfileNameEnum::EN_FIRESNAKE, "Fire Snake"},
    {ProfileNameEnum::EN_BOSS_KAMECK, "Kamek"},
    {ProfileNameEnum::EN_SLIP_PENGUIN, "Cooligan"},
    {ProfileNameEnum::EN_SLIP_PENGUIN2, "Cooligan"},
    {ProfileNameEnum::EN_IGA_KURIBO, "Prickly Goomba"},
    {ProfileNameEnum::KAMECK_MAGIC, "Kamek's Magic"},
    {ProfileNameEnum::EN_KERONPA, "Fire Chomp"},
    {ProfileNameEnum::KERONPA_FIRE, "Fire Chomp"},
    {ProfileNameEnum::EN_BAKUBAKU, "Cheep Chomp"},
    {ProfileNameEnum::EN_BOSS_LARRY, "Larry Koopa"},
    {ProfileNameEnum::EN_BOSS_CASTLE_LARRY, "Larry Koopa"},
    {ProfileNameEnum::OBJ_LARRY, "Larry Koopa"},
    {ProfileNameEnum::EN_BOSS_WENDY, "Wendy O. Koopa"},
    {ProfileNameEnum::EN_BOSS_CASTLE_WENDY, "Wendy O. Koopa"},
    {ProfileNameEnum::OBJ_WENDY, "Wendy O. Koopa"},
    {ProfileNameEnum::EN_BOSS_IGGY, "Iggy Koopa"},
    {ProfileNameEnum::EN_BOSS_CASTLE_IGGY, "Iggy Koopa"},
    {ProfileNameEnum::EN_BOSS_LEMMY, "Lemmy Koopa"},
    {ProfileNameEnum::EN_BOSS_CASTLE_LEMMY, "Lemmy Koopa"},
    {ProfileNameEnum::EN_BOSS_MORTON, "Morton Koopa Jr."},
    {ProfileNameEnum::EN_BOSS_CASTLE_MORTON, "Morton Koopa Jr."},
    {ProfileNameEnum::OBJ_MORTON, "Morton Koopa Jr."},
    {ProfileNameEnum::EN_BOSS_ROY, "Roy Koopa"},
    {ProfileNameEnum::EN_BOSS_CASTLE_ROY, "Roy Koopa"},
    {ProfileNameEnum::OBJ_ROY, "Roy Koopa"},
    {ProfileNameEnum::EN_BOSS_LUDWIG, "Ludwig von Koopa"},
    {ProfileNameEnum::EN_BOSS_CASTLE_LUDWIG, "Ludwig von Koopa"},
    {ProfileNameEnum::OBJ_LUDWIG, "Ludwig von Koopa"},
    {ProfileNameEnum::EN_BOSS_KOOPA, "Bowser"},
    {ProfileNameEnum::KOOPA_FIRE, "Bowser Fire Breath"},
    {ProfileNameEnum::LARRY_FIRE, "Magic Fireball"},
    {ProfileNameEnum::KOKOOPA_RING, "Wendy Ring"},
    {ProfileNameEnum::OBJ_IGGY_WANWAN, "Iggy Chain Chomp"},
    {ProfileNameEnum::CASTLE_LUDWIG_BLITZ, "Ludwig's Magic"},
    {ProfileNameEnum::FIRE_BLITZ, "Magic Fire"},
    {ProfileNameEnum::EN_UNIZOO, "Urchin"},
    {ProfileNameEnum::EN_UNIRA, "Big Urchin"},
    {ProfileNameEnum::EN_KANIBO, "Huckit Crab"},
    {ProfileNameEnum::EN_KANITAMA, "a rock"},
    {ProfileNameEnum::EN_KOPONE, "Fish Bones"},
    {ProfileNameEnum::EN_AKOYA, "Clampy"},
    {ProfileNameEnum::EN_MIDDLE_KURIBO, "Giant Goomba"},
    {ProfileNameEnum::EN_LARGE_KURIBO, "Mega Goomba"},
    {ProfileNameEnum::EN_BEANS_KURIBO, "Micro Goomba"},
    {ProfileNameEnum::JR_CLOWN_A, "Junior Clown Car"},
    {ProfileNameEnum::JR_CLOWN_B, "Junior Clown Car"},
    {ProfileNameEnum::JR_CLOWN_C, "Junior Clown Car"},
    {ProfileNameEnum::JR_CLOWN_FOR_PLAYER, "Junior Clown Car"},
    {ProfileNameEnum::BOMB_JR_C, "Bowser Jr. Bomb"},
    {ProfileNameEnum::EN_BOSS_KOOPA_JR_A, "Bowser Jr."},
    {ProfileNameEnum::EN_BOSS_KOOPA_JR_B, "Bowser Jr."},
    {ProfileNameEnum::EN_BOSS_KOOPA_JR_C, "Bowser Jr."},
    {ProfileNameEnum::JR_FIRE, "Bowser Jr. Fire Breath"},
    {ProfileNameEnum::JR_FLOOR_FIRE, "Bowser Jr. Floor Fire"},
    {ProfileNameEnum::YOGAN_INTERMITTENT, "Lava Geyser"},
    {ProfileNameEnum::EN_IBARAMUSHI, "Bramball"},
    {ProfileNameEnum::EN_CHOCHIN_ANKOH, "Bulber"},
    {ProfileNameEnum::EN_MISTMAN, "Foo"},
    {ProfileNameEnum::EN_ROT_PAKKUN, "Rotating Piranha Plant"},
    {ProfileNameEnum::EN_POLTER, "Silly Flying Thing"},
    {ProfileNameEnum::EN_ICICLE, "Icicle"},
    {ProfileNameEnum::EN_CANNON_BULLET, "Cannonball"},
    {ProfileNameEnum::KAZAN_ROCK, "Volcano Rock"},
    {ProfileNameEnum::EN_CHOROPU, "Monty Mole"},
    {ProfileNameEnum::EN_MANHOLE_CHOROPU, "Monty Mole"},
    {ProfileNameEnum::EN_JELLY_FISH, "Jellybeam"},
    {ProfileNameEnum::EN_GABON, "Spike"},
    {ProfileNameEnum::GABON_ROCK, "Spike Rock"},
    {ProfileNameEnum::EN_KING_KILLER, "King Bill"},
    {ProfileNameEnum::EN_PATAMET, "Para-Beetle"},
    {ProfileNameEnum::EN_BIG_PATAMET, "Heavy Para-Beetle"},
    {ProfileNameEnum::EN_BIG_ICICLE, "Falling Big Icicle"},
    {ProfileNameEnum::EN_BARREL, "Barrel"},
    {ProfileNameEnum::LIFT_ZEN_TOGE, "Spiky Wall from 5-Tower"},

#ifdef NON_ESSENTIAL_ACTORS
    {ProfileNameEnum::CASTLE_BOSS_DOOR, "FNAF 1 Style Door"},
    {ProfileNameEnum::CASTLE_BOSS_KEY, "Castle Boss Key"},
    {ProfileNameEnum::EN_DOOR, "Door"},
    {ProfileNameEnum::EN_SWITCHDOOR, "Door"},
    {ProfileNameEnum::EN_OBAKEDOOR, "Ghost House Door"},
    {ProfileNameEnum::EN_TORIDEDOOR, "Tower Boss Door"},
    {ProfileNameEnum::EN_CASTLEDOOR = "Castle Boss Door"},
    {ProfileNameEnum::EN_KOOPADOOR = "Final Boss Door"},
    {ProfileNameEnum::PALM_TREE = "Palm Tree"},
    {ProfileNameEnum::NICE_BOAT = "NICE_BOAT"},
    {ProfileNameEnum::LADDER = "Ladder"},
    {ProfileNameEnum::EN_REDRING, "Red Coin Ring"},
    {ProfileNameEnum::EN_SNAKEBLOCK, "Snake Block"},
    {ProfileNameEnum::SLIP_PENGUIN2_GLASSES, "Cooligan Glasses"},
#endif
*/
};


template <u32 N>
struct PackedActorNames {
    char names[N];

    u32 getSize() const
    {
        return N;
    }
};

template <u32 P, u32 N>
PackedActorNames<P> ProcessPackActorNames(const ActorName (&names)[N], u32& offset)
{

    PackedActorNames<P> packedNames = {};
    /*
    // writeByte = [&](char byte) { packedNames.names[offset++] = byte; };

    // Sort names by longest to shortest
    std::array<u32, N> indices;
    std::iota(indices.begin(), indices.end(), 0);
    std::sort(indices.begin(), indices.end(), [&](u32 a, u32 b) {
        u32 i = 0;
        for (i = 0; names[a].name[i] != '\0' && names[b].name[i] != '\0'; i++) {
        }
        return names[a].name[i] > names[b].name[i];
    });

    for (u32 i = 0; i < N; i++) {
        const ActorName& name = names[indices[i]];

        //writeByte(char(u16(name.profile) >> 2));
        //writeByte(char(u16(name.profile) << 6));

        // Search back to see if we have a copy of the same name
        s32 foundOffset = -1;
        for (u32 jo = 0; jo < offset - 2; jo++) {
            for (u32 j = 0;; j++) {
                if (packedNames.names[jo + j] != name.name[j]) {
                    break;
                }
                if (name.name[j] == '\0') {
                    foundOffset = s32(jo);
                    break;
                }
            }
        }

        if (foundOffset != -1) {
            packedNames.names[offset - 1] |= 0x20 | ((foundOffset >> 8) & 0x1F);
            //writeByte(foundOffset);
            continue;
        }

        u32 loc = offset++;
        for (u32 j = 0; name.name[j] != '\0'; j++) {
            writeByte(name.name[j]);
        }
        //writeByte('\0');
        packedNames.names[loc] = offset - loc - 1;
    }
    */
    return packedNames;
}
/*
template <u32 N>
constexpr u32 GetPackedSize(const ActorName (&names)[N])
{
    u32 offset = 0;
    ProcessPackActorNames<0x1000>(names, offset);
    return offset;
}
*/

template <u32 P, u32 N>
PackedActorNames<P> PackActorNames(const ActorName (&names)[N])
{
    u32 offset = 0;
    return ProcessPackActorNames<P>(names, offset);
}

PackedActorNames<100> s_packedNames =
    PackActorNames<100>(s_names);

const char* getActorFormattedName(dActor_c* actor)
{
    if (actor == nullptr) {
        return nullptr;
    }

    ProfileNameEnum name = ProfileNameEnum(actor->mProfName);
    //auto names = s_packedNames.names;
    char *  names = new char[100]();

    for (u32 i = 0; i < s_packedNames.getSize();) {
        u32 info = *(u32*) (names + i);
        u32 len = (info >> 8) & 0x1FFF;
        bool match = name == ProfileNameEnum(info >> 22);
        if (info & 0x200000) {
            if (match) {
                return &names[len];
            }
            i += 3;
            continue;
        }

        if (match) {
            return &names[i + 3];
        }
        i += 3 + len;
    }

    //return actor->mpNameString != nullptr ? actor->mpNameString : "an unknown force";
    return "an unknown force";

}


nw4r::lyt::res::TextureList s_txl1 = {
    .blockHeader =
        {
            .kind = 0x74786C31, // "txl1"
            .size = sizeof(nw4r::lyt::res::TextureList),
        },
    .texNum = 0,
    .PADDING_0xA = 0,
};


struct FontList1 {
    nw4r::lyt::res::FontList main;
    u32 offset1;
    nw4r::lyt::res::Font font;
    char fontName[0x20];
};


FontList1 s_fnl1 = {
    .main =
        {
            .blockHeader =
                {
                    .kind = 0x666E6C31, // "fnl1"
                    .size = sizeof(FontList1),
                },
            .fontNum = 1,
            .PADDING_0xA = 0,
        },
    .offset1 = offsetof(FontList1, font),
    .font =
        {
            .nameStrOffset = offsetof(FontList1, fontName),
            .PADDING_0x5 = 0,
        },
    .fontName = "mj2d00_MessageFont_32_I4.brfnt",
};


struct Material {
    /* 0x00 */ char materialName[0x14];
    /* 0x14 */ s16 foreColor[4]; // RGBA
    /* 0x1C */ s16 backColor[4]; // RGBA
    /* 0x24 */ s16 colorReg3[4]; // RGBA
    /* 0x2C */ u8 tevColor1[4]; // RGBA
    /* 0x30 */ u8 tevColor2[4]; // RGBA
    /* 0x34 */ u8 tevColor3[4]; // RGBA
    /* 0x38 */ u8 tevColor4[4]; // RGBA
    /* 0x3C */ u32 flags;
};

struct MaterialList1 {
    nw4r::lyt::res::MaterialList main;
    u32 offset1;
    Material material;
};

MaterialList1 s_mat1 = {
    .main =
        {
            .blockHeader =
                {
                    .kind = 0x6D617431, // "mat1"
                    .size = sizeof(MaterialList1),
                },
            .materialNum = 1,
            .PADDING_0xA = 0,
        },
    .offset1 = offsetof(MaterialList1, material),
    .material =
        {
            .materialName = "Mat_DeathMsg",
            .foreColor = {0x00, 0x00, 0x00, 0x00},
            .backColor = {0xFF, 0xFF, 0xFF, 0xFF},
            .colorReg3 = {0x00, 0x00, 0x00, 0x00},
            .tevColor1 = {0x00, 0x00, 0x00, 0x00},
            .tevColor2 = {0x00, 0x00, 0x00, 0x00},
            .tevColor3 = {0x00, 0x00, 0x00, 0x00},
            .tevColor4 = {0x00, 0x00, 0x00, 0x00},
            .flags = 0,

        },

};

nw4r::lyt::ResBlockSet s_resBlockSet = {
    .pTextureList = &s_txl1,
    .pFontList = &s_fnl1.main,
    .pMaterialList = &s_mat1.main,
    .pResAccessor = nullptr,
};

struct SectionHeader {
    /* 0x00 */ u32 magic;
    /* 0x04 */ u32 size;
};


struct Pane {
    // https://wiki.tockdom.com/wiki/BRLYT_(File_Format)#pan1
    /* 0x00 */ SectionHeader header;
    /* 0x08 */ u8 flags;
    /* 0x09 */ u8 originType;
    /* 0x0A */ u8 alpha;
    /* 0x0B */ u8 pad_0xB;
    /* 0x0C */ char name[0x10];
    /* 0x1C */ char userData[0x8];
    /* 0x24 */ float translation[3];
    /* 0x30 */ float rotation[3];
    /* 0x3C */ float scale[2];
    /* 0x44 */ float width;
    /* 0x48 */ float height;
};

struct TextBox {
    // https://wiki.tockdom.com/wiki/BRLYT_(File_Format)#txt1
    /* 0x00 */ Pane pane;
    /* 0x4C */ u16 stringSize;
    /* 0x4E */ u16 maxStringSize;
    /* 0x50 */ u16 matIndex;
    /* 0x52 */ u16 fontIndex;
    /* 0x54 */ u8 stringOrigin;
    /* 0x55 */ u8 lineAlignment;
    /* 0x56 */ u16 pad_0x56;
    /* 0x58 */ u32 textOffset;
    /* 0x5C */ u8 topColor[4]; // RGBA
    /* 0x60 */ u8 bottomColor[4]; // RGBA
    /* 0x64 */ float fontSizeX;
    /* 0x68 */ float fontSizeY;
    /* 0x6C */ float characterSize;
    /* 0x70 */ float lineSize;
};

struct TextBox1 {
    TextBox main;
    wchar_t message[128];
};

TextBox s_txt1 = {
    .pane =
        {
            .header =
                {
                    .magic = 0x74787431, // "txt1"
                    .size = sizeof(TextBox1),
                },

            .flags = 0x5,
            .originType = 0,
            .alpha = 0xFF,
            .pad_0xB = 0,
            .name = "Txt_DeathMsg",
            .userData = {},
            .translation = {-250.0, 0.0, 0.0},
            .rotation = {0.0, 0.0, 0.0},
            .scale = {1.0, 1.0},
            .width = 800.0,
            .height = 45.0,
        },

    .stringSize = 127,
    .maxStringSize = 127,
    .matIndex = 0,
    .fontIndex = 0,
    .stringOrigin = 0,
    .lineAlignment = 2,
    .pad_0x56 = 0,
    .textOffset = offsetof(TextBox1, message),
    .topColor = {0xFF, 0x7F, 0x7F, 0xFF},
    .bottomColor = {0xFF, 0x30, 0x30, 0xFF},
    .fontSizeX = 25.0,
    .fontSizeY = 25.0,
    .characterSize = 1.0,
    .lineSize = 1.0,
};

void* s_drawInfo = nullptr;

const char* const s_playerNames[4] = {
    "Mario",
    "Luigi",
    "Bload",
    "Yoad",
};

const u32 s_playerColors[4] = {
    0xFF7F7FFF,
    0x7FFF7FFF,
    0x7F7FFFFF,
    0xFFFF7FFF,
};

class DeathMsgMgr
{
public:

    void NewMessage(TextBox* res)
    {
        if (m_count >= 12) {
            DeleteFromFront();
        }

        u32 index = (m_index + m_count) % 12;
        m_count++;

        //new (&u.m_textBox[index]) TextBox(res, s_resBlockSet);
        m_timeToLive[index] = 8 * 60;
    }

    void DeleteFromFront()
    {
        //u.m_textBox[m_index].__dt(0);
        m_index = (m_index + 1) % 12;
        m_count--;
    }

    union U {
        u8 m_data[sizeof(TextBox) * 12];
        TextBox m_textBox[12];

        U()
        {
            // Prevent calling constructor yet
            (void) m_data;
        }
    } u;

    u32 m_index;
    u32 m_count;
    u32 m_timeToLive[12];
};

DeathMsgMgr* s_deathMsgMgr = nullptr;

void dAcPy_c_extended::setDeathMessage(const char* message, const char* enemy)
{
    if (message == nullptr || message[0] == '\0') {
        return;
    }

    TextBox1 textBoxRes = {};
    s32 player = this->mCharacter < 4 ? this->mCharacter : 0;

    memcpy(&textBoxRes.main, &s_txt1, sizeof(nw4r::lyt::res::TextBox));
    *(u32*) &textBoxRes.main.topColor = s_playerColors[player];
    *(u32*) &textBoxRes.main.bottomColor = s_playerColors[player];

    char formatted[128] = {0};
    snprintf(formatted, sizeof(formatted), message, s_playerNames[player], enemy);

    mbstowcs(textBoxRes.message, formatted, 128);

    s_deathMsgMgr->NewMessage(&textBoxRes.main);
}

/*
cGCT_INSERT_POINTER( //
    0x80325BB8
)
*/
/*
bool dAcPy_c_extended::setDamage2_Override(dActor_c* source, DamageType_e type)
{
    const char* enemy = getActorFormattedName(source);

    if (dAcPy_c_extended::sDeathMessageOverride != nullptr) {
        setDeathMessage(dAcPy_c_extended::sDeathMessageOverride, enemy);
        dAcPy_c_extended::sDeathMessageOverride = nullptr;

        return dAcPy_c_extended::setDamage2__IMPL(source, type);
    }

    switch (type) {
    case DAMAGE_KNOCKBACK_LONG:
    case DAMAGE_KNOCKBACK_LONG2:
    case DAMAGE_KNOCKBACK_SHORT:
    case DAMAGE_KNOCKBACK_SHORT2:
    case DAMAGE_BOUNCE:
        return dAcPy_c_extended::setDamage2__IMPL(source, type);
    }

    const char* message = nullptr;

    switch (type) {
    default:
        if (enemy == nullptr) {
            message = "%s came into contact with something deadly";
            break;
        }

        switch (ProfileNameEnum(source->mProfName)) {
        default:
            message = "%s lost it to %s";
            break;

    setDeathMessage(message, enemy);

    return dAcPy_c_extended::setDamage2__IMPL(source, type);
}
*/

/*
void dAcPy_c_extended::setBalloonInDispOut_Override(int type)
{
    char message[128] = {0};
    const char* name = s_playerNames[this->mCharacter];

    switch (type) {
    default:
        snprintf(message, sizeof(message), "%s fell out of the world (type %d)", name, type);
        break;

    case 2:
        snprintf(message, sizeof(message), "%s was left behind", name);
        snprintf(
            message, sizeof(message),
            (const char*[]) {
                "%s was left behind",
                "%s mysteriously vanished",
                "%s was crushed between the screen and a heavy object",
            }[dGameCom::rndInt(3)],
            name
        );
        break;

    case 3:
        snprintf(
            message, sizeof(message),
            (const char*[]) {
                "%s fell out of the world",
                "%s mysteriously vanished",
            }[dGameCom::rndInt(2)],
            name
        );
        break;
    }

    setDeathMessage(message, "");

    dAcPy_c_extended::setBalloonInDispOut__IMPL(type);
}

extern "C" bool dGameDisplay_InitDeathMsg(void* resourceAccessor, void* drawInfo)
{
    s_deathMsgMgr = new DeathMsgMgr();
    s_resBlockSet.resourceAccessor = resourceAccessor;
    s_drawInfo = drawInfo;

    return true;
}
*/

//extern "C" Pane_CalculateMtx(nw4r::lyt::Pane* pane, void* drawInfo);
//extern "C" (0x802ABEA0) void Pane_Draw(nw4r::lyt::Pane* pane, void* drawInfo);

u32 drawDeathMsgs()
{
    DeathMsgMgr* mgr = s_deathMsgMgr;
    u32 count = mgr->m_count;

    float position = -170.0 + 35.0 * count;
    void* drawInfo = s_drawInfo;

    for (s32 i = 0; i < count; i++) {
        position -= 35.0;
        u32 index = 0;//(mgr->m_index + i) % mgr->12;
        TextBox * textBox = &mgr->u.m_textBox[index];

        u32 ttl = --mgr->m_timeToLive[index];
        //textBox->m_alpha = std::min<u32>(ttl * 255 / 30, 255);

        //textBox->m_translation[1] = position;

        //Pane_CalculateMtx(textBox, drawInfo);
        //Pane_Draw(textBox, drawInfo);

        if (ttl == 0) {
            mgr->DeleteFromFront();
            count--;
            i--;
        }
    }

    return 0;
}