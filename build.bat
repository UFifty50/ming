@echo off

set input=ming.py
set debugargs=--show-scons --plugin-enable=pylint-warnings --show-progress --plugin-enable=pylint-warnings --windows-disable-console --windows-force-stderr-spec=err.txt 
set speedargs=--enable-plugin=anti-bloat --noinclude-pytest-mode=nofollow --noinclude-setuptools-mode=nofollow --python-flag=nosite 
set basecmd=python.exe -m nuitka --include-data-file=dlls\libfluidsynth.dll=mingus\midi\libfluidsynth.dll --include-data-file=local_pygame_menu\resources\fonts\*.ttf=pygame_menu\resources\fonts\ --include-data-file=dlls\libfluidsynth.dll=libfluidsynth.dll  --include-data-file=soundfonts\*.sf2=soundfonts\ --include-data-file=imgs\*=imgs\ --include-data-file=dlls\*.dll=dlls\ --windows-icon-from-ico=favicon.ico --include-package-data pygame_menu --plugin-enable=numpy  --onefile --onefile-windows-splash-screen-image=D:\Jonathan\Documents\ming\cornflower.png 

set /p output="What should the exe be named? "
set /p debug="Compile with debug options? (y/n) "
set /p speed="Compile with optimizations? (y/n, default is y) "

if %speed% == y set basecmd=%basecmd%%speedargs%
if %debug% == y set basecmd=%basecmd%%debugargs%

%basecmd% --output-dir=build -j 5  -o build\%output%.exe %input%
