#pragma once

#include <types.h>
#include <propelparts/course_actor_name.hpp>
#include <game/framework/f_profile.hpp>
#include <game/bases/d_actor_data.hpp>

// All the neccessary code for profile/actor expansion
// Check d_a_spawner.cpp for a usage example

class dCustomProfile_c {
public:
    // Stage actor with sprite
    dCustomProfile_c(fProfile::fActorProfile_c *profile, const char* name, CourseActorName courseActorId, const dActorData_c *dActorData_c, const char** files=NULL);
    // Stage actor without sprite
    dCustomProfile_c(fProfile::fActorProfile_c *profile, const char* name, ProfileName profileId);
    // Non-stage actors (scenes, bases, etc)
    dCustomProfile_c(fProfile::fBaseProfile_c *profile, const char* name, ProfileName profileId);
    // Existing actor, new sprite
    dCustomProfile_c(CourseActorName courseActorId, const dActorData_c *dActorData_c, const char** files=NULL);

    fProfile::fActorProfile_c mProfile;
};

