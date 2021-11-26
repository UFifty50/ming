# THIS IS ALL BATCH AT THE MOMENT, DO NOT RUN
# IT WONT WORK

which /q python3.9
IF ERRORLEVEL 1 (
    ECHO Python is missing. Ensure it is installed and placed in your PATH.
    EXIT /B
) ELSE (
    for /F "tokens=*" %%A in ('where python') do set python=%AA
    for /F "tokens=*" %%A in ('%python% --version') do set pyver=%%A
    for /F "tokens=*" %%A in ("%pyver%") do (
        set "pyver=%%A"
    )
    set py=%pyver:~0,1%
    IF NOT py == 3 (
        ECHO Your python version is too old! Python 3.9 is required.
        EXIT /B
    ) ELSE (
        ECHO Python found. Let's go!
    )
)

set input=ming.py
set debugargs=--windows-disable-console --windows-force-stderr-spec=err.txt 
set verboseargs=--show-scons --plugin-enable=pylint-warnings --show-progress --plugin-enable=pylint-warnings 
set speedargs=--enable-plugin=anti-bloat --noinclude-pytest-mode=nofollow --noinclude-setuptools-mode=nofollow --python-flag=nosite 
set basecmd=%python% -m nuitka --include-data-file=dlls\libfluidsynth.dll=mingus\midi\libfluidsynth.dll --include-data-file=local_pygame_menu\resources\fonts\*.ttf=pygame_menu\resources\fonts\ --include-data-file=dlls\libfluidsynth.dll=libfluidsynth.dll  --include-data-file=soundfonts\*.sf2=soundfonts\ --include-data-file=imgs\*=imgs\ --include-data-file=dlls\*.dll=dlls\ --windows-icon-from-ico=favicon.ico --include-package-data pygame_menu --plugin-enable=numpy  --onefile --onefile-windows-splash-screen-image=D:\Jonathan\Documents\ming\cornflower.png 


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
