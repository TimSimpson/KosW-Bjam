Boost Build for KOS using Cygwin
--------------------------------

Installed the latest KallistiOS Dreamcast toolchain using Cygwin, and now
want to use it from Boost Build? I can't even count the number of times
I've met people in this situation!

Thankfully, this project will allow you to do just that.


Instructions
------------

First, make sure you have the Dreamcast toolchain set up on Windows and can
at least use the makefiles in the Cygwin terminal to create Dreamcast
executables.

You'll need to make sure Python scripts can run without the .py extension;
otherwise Boost Build won't be able to call the binary files it's looking for.

Make sure your PATHEXT environment variable includes the .PY extensions.
If it doesn't, you can add it with the following:

SET PATHEXT=%PATHEXT%;.PY

Next, you'll need to edit your site-config.jam. Don't have a site-config.jam?
Add one. It should live in your %HOME% directory (since Vista this has been
C:\Users\YourName). Put this inside it, only change the file paths from the
ones on my system to ones on yours:

```
# Optional: This tells Boost Build what compiler to use by default.
#           Change it to "using gcc ;" if you want to use the normal
#           MinGW compiler instead.
using msvc
  ;

# Tell Boost Build about our tool chain.
using gcc
   : dreamcast
   # The path to the python script. Be aware Boost Build uses Linux style
   # slashes.
   : C:/Tools/KosW-Bjam/sh-elf-g++.py
   : # <linker>/home/tim/Tools/dreamcast/KallistiOS/utils/gnu_wrappers/kos-ld
     # The root directory of all the other bin scripts.
     <root>C:/cygwin/opt/toolchains/dc/sh-elf/sh-elf/bin/
     # C flags - these get passed when the compiler is invoked.
     #           I stole this from $KOS_CFLAGS which is defined by
     #           the environ.sh script the KOS docs ask you to write.
     <cxxflags>"-O2 -fomit-frame-pointer -ml -m4-single-only -ffunction-sections -fdata-sections -I/home/Tim/Tools/dreamcast/KallistiOS/../kos-ports/include -I/home/Tim/Tools/dreamcast/KallistiOS/include -I/home/Tim/Tools/dreamcast/KallistiOS/kernel/arch/dreamcast/include -I/home/Tim/Tools/dreamcast/KallistiOS/addons/include -D_arch_dreamcast -D_arch_sub_pristine -Wall -g -fno-builtin -fno-strict-aliasing"
     # Taken from $KOS_CPPFLAGS (modified a bit to allow for excetions
     # and turn on C++11 support.
     <cxxflags>"-DCOMPILE_TARGET_DREAMCAST -fno-operator-names -std=c++11"
     # Taken from $KOS_LIBS
     <linkflags>"-lstdc++ -Wl,--start-group -lkallisti -lc -lgcc -Wl,--end-group"
     <linkflags>"-ml -m4-single-only -Wl,-Ttext=0x8c010000 -Wl,--gc-sections -T/home/Tim/Tools/dreamcast/KallistiOS/utils/ldscripts/shlelf.xc -nodefaultlibs -L/home/Tim/Tools/dreamcast/KallistiOS/lib/dreamcast -L/home/Tim/Tools/dreamcast/KallistiOS/addons/lib/dreamcast"
     <archiver>"C:\\cygwin\\opt\\toolchains\\dc\\sh-elf\\sh-elf\\bin\\ar.exe"
     <ranlib>"C:\\cygwin\\opt\\toolchains\\dc\\sh-elf\\sh-elf\\bin\\ranlib.exe"
   ;


Now, to build with Boost Build, just add "--toolset=gcc-dreamcast" to the
command line when you call bjam.


How it Works
------------

Boost Build can use the version of GCC that builds Dreamcast binaries. You
just need to tell it where it lives and how to do things. This is what the
using statement in site-config.jam is for (Boost Build always looks for
the presence of a site-config.jam file in the user's home directory and invokes
it first if it finds one).

This using statement specifies both the compiler location and a lot of flags.
The flags actually come into play when building executables. This presents
a problem as Boost Build will try to invoke them when creating a shared library.
However, there's a second problem, which is that if Boost Build is building a
shared library, it will pass MinGW / Windows specific flags.

To get around both issues, the sh-elf-g++ impostor Python script looks for the
presence of these flags. If none are found, it forwards the call to the real
sh-elf-g++.

If it finds them, it assumes Boost Build is trying to create a shared library,
and takes matters into its own hands by calling "ar" with its own set of
arguments. It looks at the arguments Boost was trying to send to figure out
the existing object files that will go into the shared library, as well as
the shared library name. It also finds the name of the export library created
in Windows- this file is never used by Boost Build except if the "install" rule
is invoked, in which case it will try to copy it. To trick Boost Build into
thinking that file exists, the Python script makes a dummy file.


Wait, what's the point of this? Why don't I just use Makefiles?
---------------------------------------------------------------

You can do that, but then that Makefile isn't going to work very well if you
try to compile on Windows. Of course, you could ultimately make the Makefile
work by tricking out environment variables and adding a lot of logic to it.
Boost Build already handles most cross-platform / cross-toolset portability
concerns, though, so to my tastes this is much easier.
