# Build kamek code
If you changed any cpp files in rom_file/Kamek-Ninja-Template-master/src you will have to recompile them
and then manually move the files in rom_file/Kamek-Ninja-Template-master/bin to rom_file/Riivolution_template/Code/. Be carful to not replaced the loader, it is not compiled here but is rather gotten from propellerparts.
To compile you have to:
1) run ```ninja``` from /rom_file/Kamek-Ninja-Template-master/
2) run ```Python ./configure.py```  from the same directory

However to accomplish this you need to have ninja, kamek and codewarior installed. 
To install them correctly follow the instructions in /rom_file/Kamek-Ninja-Template-master/readme.md