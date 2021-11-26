@echo off

set input=ming.py
set debugargs=--windows-disable-console --windows-force-stderr-spec=err.txt 
set verboseargs=--show-scons --plugin-enable=pylint-warnings --show-progress --plugin-enable=pylint-warnings 
set speedargs=--enable-plugin=anti-bloat --noinclude-pytest-mode=nofollow --noinclude-setuptools-mode=nofollow --python-flag=nosite 
set basecmd=python.exe -m nuitka --include-data-file=dlls\libfluidsynth.dll=mingus\midi\libfluidsynth.dll --include-data-file=local_pygame_menu\resources\fonts\*.ttf=pygame_menu\resources\fonts\ --include-data-file=dlls\libfluidsynth.dll=libfluidsynth.dll  --include-data-file=soundfonts\*.sf2=soundfonts\ --include-data-file=imgs\*=imgs\ --include-data-file=dlls\*.dll=dlls\ --windows-icon-from-ico=favicon.ico --include-package-data pygame_menu --plugin-enable=numpy  --onefile --onefile-windows-splash-screen-image=D:\Jonathan\Documents\ming\cornflower.png 

set /p output="What should the exe be named? "
set /p debug="Compile with debug options? (y/n) "
set /p verbose="Compile verbosely? (y/n) "
set /p speed="Compile with optimizations? (y/n, default is y) "

if %speed% == y set basecmd=%basecmd%%speedargs%
if %debug% == y set basecmd=%basecmd%%debugargs%
if %verbose% == y set basecmd=%basecmd%%verboseargs%
if %NUMBER_OF_PROCESSORS% == 1 set cpus=1
if %NUMBER_OF_PROCESSORS% == 2 set cpus=1
if not %NUMBER_OF_PROCESSORS% == 1 set /A cpus=%NUMBER_OF_PROCESSORS%-2

%basecmd% --output-dir=build -j %cpus%  -o build\%output%.exe %input%
