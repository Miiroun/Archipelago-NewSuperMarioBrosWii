
# Playtesting
* Check out the playtest list on the dev branch (NSMBW_miiroun_dev) to see want needs playtested
* Here is a shortened list
  - Deathlink (make sure it functions properly, ie sends and recives when it should)
  - None US rev 2 (please report everything that doesnt function)
  - Hintmovies (That they unlock when they should)
  - Test so nothing brakes with starcoins disabled
* Report issues that are found in the AP-discord thread (or GitHub)

## Instructions for how to contribute code
* Either for the github repository or ask me (miiroun) to give you a branch. The latter is prefered.
* Create your changes.
* Make a pull request towards my dev branch ( NSMBW_miiroun_dev)



# Logic
* If you want to help with logic then check out instruction for contribute code
* Look at raw_rules.py -> specific_level_requierments
* in this function you can find a header and 2 big lists. 
* the lists are easy and hard logic respectively. If easy logic is enabled the code will look at both lists and "and" them together. If hard logic is enabled then only the hard logic is required.
  * -> if something is needed put in hard logic, if it requies a specific hard trick then put in easy logic
* The lists have sublists for each world with sublist for each level
* the level list is structured like \[level cleared, \[SC1, SC2, SC3\], optional secret exit\]
* To change a rule replace rules.true() with the varible defined in the header. (if something is missing you can add a varible or message me on discord)
* you can either and & or | together rules. gp | wj will required either ground pound or wall jump
* You can test your logic with universal tracker. Just open an already generated game and see what you can access. Then cheat in items from the consol and see if that enables your location
* Then make a pull request with your changes to the dev branch on GitHub (NSMBW_miiroun_dev)