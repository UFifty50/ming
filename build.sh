#!/bin/bash

echo "THIS SHOULD WORK, BUT I HAVENT TESTED IT YET"
echo "PROCEED WITH CAUTION"

which python > /dev/null 2>&1
if [ $? = 1 ]; then
    echo "Python is missing. Ensure it is installed and placed in your PATH."
    exit
else
    python="$(which python)"
    pyver="$($python -c "import sys; print(sys.version_info[0:2])")"
    required="(3, 9)"
    if $pyver != "$required"; then
        echo "Your python version is too old! Python 3.9 is required."
        exit
    else
        echo "Python found. Let's go!"
    fi
fi

input="ming.py"
debugargs="--windows-disable-console --windows-force-stderr-spec=err.txt"
verboseargs="--show-scons --plugin-enable=pylint-warnings --show-progress --plugin-enable=pylint-warnings"
speedargs="--enable-plugin=anti-bloat --noinclude-pytest-mode=nofollow --noinclude-setuptools-mode=nofollow --python-flag=nosite"
basecmd="$python -m nuitka --include-data-file=dlls/libfluidsynth.dll=mingus/midi/libfluidsynth.dll --include-data-file=local_pygame_menu/resources/fonts/*.ttf=pygame_menu/resources/fonts/ --include-data-file=dlls/libfluidsynth.dll=libfluidsynth.dll  --include-data-file=soundfonts/*.sf2=soundfonts/ --include-data-file=imgs/*=imgs/ --include-data-file=dlls/*.dll=dlls/ --windows-icon-from-ico=favicon.ico --include-package-data pygame_menu --plugin-enable=numpy  --onefile --onefile-windows-splash-screen-image=D:/Jonathan/Documents/ming/cornflower.png"


read -rp "What should the exe be named? " output
read -rp "Compile with debug options? (y/n) " debug
read -rp "Compile verbosely? (y/n) " verbose
read -rp "Compile with optimizations? (y/n, default is y) " speed

if [ "$speed" = y ]; then basecmd="$basecmd $speedargs"; fi
if [ "$debug" = y ]; then basecmd="$basecmd $debugargs"; fi
if [ "$verbose" = y ]; then basecmd="$basecmd $verboseargs"; fi
if [ "$(getconf _NPROCESSORS_ONLN)" = 1 ]; then
    cpus=1
elif [ "$(getconf _NPROCESSORS_ONLN)" = 2 ]; then
   cpus=1
else
    cpus=$(($(getconf _NPROCESSORS_ONLN) - 2))
fi

exec $basecmd --output-dir=build -j $cpus  -o build/"$output" $input
