// based mostly on mkwcat's pipe randomizer
//https://github.com/mkwcat/nsmbw-pipe-randomizer/blob/master/src/nsmbw-random-pipe.cpp


#include "SndSceneMgr.hpp"
#include "d_actor.hpp"
#include "d_cs_seq_mgr.hpp"
#include "d_fader.hpp"
#include "d_game_com.hpp"
#include "d_info.hpp"
#include "d_next.hpp"
#include "d_pl_base.hpp"
#include "d_save_mng.hpp"
#include "d_sc_crsin.hpp"
#include "d_sc_stage.hpp"
#include "d_sc_wmap.hpp"
#include "d_scene.hpp"
#include "d_stage.hpp"
#include "dvd.h"
#include "dvdfs.h"
#include "lyt_base.hpp"
#include "m_fader.hpp"

#include "pipe_entry_list.h"
#include "types.h"

#include <kamek.h>
//#include <kameksdk.h>
#include "mem.h"

#define DVDRead(fileInfo, addr, length, offset)                                \
    DVDReadPrio((fileInfo), (addr), (length), (offset), 2)



extern "C" __attribute__((noreturn)) void
OSPanic(const char* file, int line, const char* format, ...);

#ifndef assert
#  ifdef NDEBUG
#    define assert(cond) ((void) 0)
#  else
#    define assert(cond)                                                       \
        ((void) ((cond) || (OSPanic(                                           \
                                "nsmbw-random-pipe.cpp", __LINE__,             \
                                "Failed assertion %s", #cond                   \
                            ),                                                 \
                            0)))
#  endif
#endif

enum RandBase {
    RAND_BASE_BOOT = 0, // Randomize on starting the game
    RAND_BASE_COURSE = 1, // Randomize on entering a course
    RAND_BASE_ALWAYS = 2, // Randomize on entering a pipe
    RAND_BASE_FILE = 3, // Use seed.txt
    RAND_BASE_NEVER = 4, // rando turned off
};

extern RandBase g_randBase;
u16 g_entryLookup[PipeEntryCount];
bool g_madeEntryTable = false;



class EntranceSorter
{
public:
    EntranceSorter(u16* lookupTable, u32 seed)
    {
        m_entryLookup = lookupTable;
        m_seed = seed;

        m_excEntIndex = 0;
        m_excEntCount = 0;
        m_curGroupEnd = 0;

        m_entCount = 0;
        m_ptrEntList = m_entList;

        // Add grouped entries to the list first
        bool inGroup = false;
        for (u32 i = 0; i < PipeEntryCount; i++) {
            u32 entry = i | ((PipeEntryList[i] & 0xF000) << 16);
            u8 flags = (entry >> 28);
            if (!inGroup && flags == 0x0) {
                continue;
            }

            // Write index and group flags
            m_entList[m_entCount++] = entry;

            if (flags & 0x2) {
                inGroup = false;
            } else if (flags & 0x1) {
                inGroup = true;
            } else if (flags & 0x3) {
                // If the entrance is by itself in a group then move it to
                // exclusive
                MoveToExclusive(m_entCount - 1);
            }

            m_entryLookup[i] = 0;
        }

        // Add non-grouped entries to the list
        inGroup = false;
        u32 lastGroupedEnt = m_entCount;
        for (u32 i = 0; i < PipeEntryCount; i++) {
            // Write index and copy group flags
            u32 entry = i | ((PipeEntryList[i] & 0xF000) << 16);
            u8 flags = (entry >> 28);
            if (inGroup || flags != 0x0) {
                if (flags & 0x2) {
                    inGroup = false;
                } else if (flags & 0x1) {
                    inGroup = true;
                }

                continue;
            }

            // Write index
            m_entList[m_entCount++] = entry;
        }

        // Reserve a random non-exclusive entrance for the last link
        u32 idx = lastGroupedEnt +
                  getRandomFromSeed(&m_seed, m_entCount - lastGroupedEnt);
        m_lastEntrance = m_entList[idx];
        Remove(idx);
    }

    void CreateLookupTable()
    {
        while (m_entCount > 0) {
            u32 ent1 = SelectEntrance1();
            u32 ent2 = SelectEntrance2() & 0x0FFFFFFF;

            bool exc = (ent1 >> 28) == 0x3;
            ent1 &= 0x0FFFFFFF;

            m_entryLookup[ent1] = ent2;
            m_entryLookup[ent2] = ent1;

#if 0
            if (exc) {
                dInfo_c::StartGameInfo_s sginfo;
                dInfo_c::StartGameInfo_s sginfo2;

                u32 entry = ent1;
                sginfo.world1 = (PipeEntryList[entry] >> 24) & 0xFF;
                sginfo.level1 = (PipeEntryList[entry] >> 16) & 0xFF;
                sginfo.entrance = PipeEntryList[entry] & 0xFF;
                sginfo.area = (PipeEntryList[entry] >> 8) & 0x0F;

                entry = ent2;
                sginfo2.world1 = (PipeEntryList[entry] >> 24) & 0xFF;
                sginfo2.level1 = (PipeEntryList[entry] >> 16) & 0xFF;
                sginfo2.entrance = PipeEntryList[entry] & 0xFF;
                sginfo2.area = (PipeEntryList[entry] >> 8) & 0x0F;

                OSReport(
                    "%d-%d area %d ent %d: %d-%d area %d ent %d\n",
                    sginfo.world1 + 1, sginfo.level1 + 1, sginfo.area + 1,
                    sginfo.entrance, sginfo2.world1 + 1, sginfo2.level1 + 1,
                    sginfo2.area + 1, sginfo2.entrance
                );
            }
#endif
        }
    }

private:
    u32 SelectEntrance1()
    {
        // Exclusive entrances always go first
        if (m_excEntCount != 0) {
            m_excEntCount--;
            return m_excEntList[m_excEntIndex++];
        }

        assert(m_entCount > 0);

        // Reset exclusive index
        m_excEntIndex = 0;

        if (m_curGroupEnd == 0) {
            // Not in a group
            u32 val = m_ptrEntList[0];
            if ((val >> 28) != 0x1) {
                RemoveEntrance(0);
                return val;
            }

            // Start of a group, let's find the end
            for (u32 i = 0; i < m_entCount; i++) {
                if ((m_ptrEntList[i] >> 28) == 0x2) {
                    m_curGroupEnd = i + 1;
                    break;
                }
            }

            // Then fall through to the group code
        }

        // Randomly select an entrance within the group. This will make sure
        // that which entry ends up exclusive will be evenly distributed.
        u32 i = getRandomFromSeed(&m_seed, m_curGroupEnd);
        u32 val = m_ptrEntList[i];
        RemoveEntrance(i);

        return val;
    }

    u32 SelectEntrance2()
    {
        if (m_entCount == 0) {
            // No more entrances, return the reserved one
            int lastEntrance = m_lastEntrance;
            assert(lastEntrance >= 0);
            m_lastEntrance = -1;
            return lastEntrance;
        }

        // Entrance 2 cannot be an exclusive entrance
        u32 i = getRandomFromSeed(&m_seed, m_entCount);
        u32 val = m_ptrEntList[i];
        RemoveEntrance(i);

        return val;
    }

    void MoveToExclusive(u32 idx)
    {
        u32 val = m_ptrEntList[idx];
        Remove(idx);
        m_excEntList[m_excEntIndex + m_excEntCount] = val;
        m_excEntCount++;
    }

    void Remove(u32 idx)
    {
        if (idx < m_curGroupEnd) {
            m_curGroupEnd--;
        }

        if (idx == 0) {
            m_ptrEntList += 1;
            m_entCount -= 1;
            return;
        }

        if (idx == (m_entCount - 1)) {
            m_entCount -= 1;
            return;
        }

        memmove(
            m_ptrEntList + idx, m_ptrEntList + idx + 1,
            (m_entCount - idx - 1) * sizeof(u32)
        );
        m_entCount -= 1;
    }

    void RemoveEntrance(u32 idx)
    {
        u32 val = m_ptrEntList[idx];

        if ((val >> 28) == 0x1) {
            // Start of group
            m_ptrEntList[idx + 1] |= 0x1 << 28;
            if ((m_ptrEntList[idx + 1] >> 28) == 0x3) {
                MoveToExclusive(idx + 1);
            }
        }

        if ((val >> 28) == 0x2) {
            // End of group
            m_ptrEntList[idx - 1] |= 0x2 << 28;
            if ((m_ptrEntList[idx - 1] >> 28) == 0x3) {
                MoveToExclusive(idx - 1);
                idx--;
            }
        }

        Remove(idx);
    }

    u32 m_entList[PipeEntryCount];
    u32 m_entCount;
    u32* m_ptrEntList;

    u32 m_excEntList[PipeEntryCount];
    u32 m_excEntCount;
    u32 m_excEntIndex;

    u32 m_curGroupEnd;

    u32 m_lastEntrance;

    u16* m_entryLookup;
    u32 m_seed;
};


void MakeEntryTable(u32 seed)
{
    EntranceSorter sorter(g_entryLookup, seed);
    sorter.CreateLookupTable();
}

extern "C" {
s32 atoi(const char* str);
extern int errno;
}

u16 LoadSeedTxt()
{

    s32 entryNum = DVDConvertPathToEntrynum("/seed.txt");
    if (entryNum == -1) {
        OSReport("seed.txt not found\n");
        return 0;
    }

    DVDFileInfo fileInfo;
    if (!DVDFastOpen(entryNum, &fileInfo)) {
        OSReport("Failed to open seed.txt\n");
        return 0;
    }

    if (fileInfo.size > 0x7DF) {
        OSReport("seed.txt is too big\n");
        DVDClose(&fileInfo);
        return 0;
    }

    static char seedDataSym[0x800];
    memset(seedDataSym, 0, sizeof(seedDataSym));
    // iirc Kamek doesn't care for symbol alignment
    char* seedData = (char*) (((u32) seedDataSym + 31) & ~31);

    DVDRead(&fileInfo, seedData, fileInfo.size, 0);
    DVDClose(&fileInfo);

    // Ignore whitespace characters and lines starting with #
    char* ptr = seedData;
    while (*ptr == ' ' || *ptr == '\t' || *ptr == '\n' || *ptr == '\r' ||
           *ptr == '#') {
        if (*ptr == '#') {
            while (*ptr != '\n' && *ptr != '\0') {
                ptr++;
            }
        }
        ptr++;
    }

    while (*ptr != '\0') {
        errno = 0;
        u32 value = u32(atoi(ptr));

        if (errno == 0) {
            return value;
        }

        ptr++;
    }

    return 0;

}

u32 g_playerStarTimer[4] = {0, 0, 0, 0};

void GoToNewStage(u32 index, dNext_c* next)
{
    dActor_c::mExecStopReq |= 0xF;

    // The fog is coming
    if (dScStage_c::m_gameMode == 4) {
        dFader_c::setFader(dFader_c::unk_fade_1);
    } else {
        dFader_c::setFader(next->fadeType);
    }

    dScCrsin_c::m_isDispOff = true;
    dScStage_c::m_exitMode = 4;

    // Save player star timer
    for (u32 i = 0; i < 4; i++) {
        g_playerStarTimer[i] = 0;

        daPlBase_c* ply = daPyMng_c::getPlayer(i);
        if (ply) {
            g_playerStarTimer[i] = ply->starTimer;
        }
    }

    u32 entry = 0;

    switch (g_randBase) {
    default: // Boot / Course
        // Not actually done on boot but it's indistinguishable
        if (!g_madeEntryTable) {
            MakeEntryTable(
                dGameCom::getRandom(0x10000) |
                (dGameCom::getRandom(0x10000) << 16)
            );
            g_madeEntryTable = true;
        }
        entry = g_entryLookup[index];
        break;

    case RAND_BASE_ALWAYS:
        entry = dGameCom::getRandom(PipeEntryCount);
        break;

    case RAND_BASE_FILE:
        if (!g_madeEntryTable) {
            MakeEntryTable(LoadSeedTxt());
            g_madeEntryTable = true;
        }
        entry = g_entryLookup[index];
        break;

    case RAND_BASE_NEVER:
        entry = index;
        break;
    }

    u32 entData = PipeEntryList[entry];

    dInfo_c::StartGameInfo_s sginfo;
    sginfo.unk_0 = 0;
    sginfo.replayType = 0;
    sginfo.entrance = entData & 0xFF;
    sginfo.area = (entData >> 8) & 0x0F;
    sginfo.unk_7 = 0;
    sginfo.purpose = 0;
    sginfo.world1 = (entData >> 24) & 0xFF;
    sginfo.level1 = (entData >> 16) & 0xFF;
    sginfo.world2 = (entData >> 24) & 0xFF;
    sginfo.level2 = (entData >> 16) & 0xFF;

    dInfo_c::instance()->startGame(sginfo);
}

kmBranchDefCpp(0x800D03B8, 0, void, dNext_c* next)
{
    // TODO: binary search maybe?
    u32 world = dInfo_c::m_startGameInfo.world1;
    u32 stage = dInfo_c::m_startGameInfo.level1;
    u32 area = (dScene_c::mPara >> 8) & 0xFF;
    u32 entrance = next->entrance.entryId;

    u32 entData = (world << 24) | (stage << 16) | (area << 8) | entrance;
    for (u32 i = 0; i < PipeEntryCount; i++) {
        if ((PipeEntryList[i] & 0xFFFF0FFF) == entData) {
            // This is one of our entrances!
            if (g_randBase != RAND_BASE_NEVER) {
                GoToNewStage(i, next);
                return;
            }
        }
    }

    next->changeScene();
}
