#pragma once
#include <lib/egg/core/eggArchive.h>
#include <lib/egg/core/eggHeap.h>
#include <lib/egg/core/eggStreamDecomp.h>
#include <types.h>

class mDvd_command_c {
public:
    virtual ~mDvd_command_c();
    virtual void execute();
    virtual void init();

    void destroy();
    void waitDone() const;

    bool isDone() const { return mDone; }

    int mReadLength;
    bool mDone;
};

class mDvd_callback_c : public mDvd_command_c {
public:
    static mDvd_callback_c *create(void *(*callback)(void *), void *param);
    static mDvd_callback_c *createOrDie(void *(*callback)(void *), void *param);
};

class mDvd_mountMemArchive_c : public mDvd_command_c {
public:
    void *getArcBinary() const;

    static mDvd_mountMemArchive_c *create(const char *name, u8 allocDirection, EGG::Heap *heap);

    u8 mAllocDirection;
    u8 mCompressionType;
    int mEntryNum;
    EGG::Archive *mpArchive;
    EGG::Heap *mpHeap;
    unsigned long mArchiveSize;
};

class mDvd_toMainRam_c : public mDvd_command_c {
public:
    static mDvd_toMainRam_c *create(const char *path, u8 allocDirection, EGG::Heap *heap);

    u8 mPad[0x4];
    void *mpData;
};

namespace mDvd {

class UncompressInfo_c {
public:
    UncompressInfo_c(u8 type, const char *extension)
      : mType(type)
      , mExtension(extension) {
    }

    virtual ~UncompressInfo_c() {
    }

    virtual EGG::StreamDecomp *Construct() const = 0;
    virtual void Destruct() const = 0;

    u8 mType;
    const char *mExtension;

    static void *m_UnionObjectBuffer;
};

template <class T>
class TUncompressInfo_c : public UncompressInfo_c {
public:
    using UncompressInfo_c::UncompressInfo_c;

    virtual T *Construct() const override {
        return new (m_UnionObjectBuffer) T();
    }

    virtual void Destruct() const override {
    }
};

/// @unofficial
void initAutoStreamDecompInfo(
  const UncompressInfo_c *const *begin, const UncompressInfo_c *const *end
);

/// @unofficial
void initDefaultAutoStreamDecompInfo();

} // namespace mDvd
