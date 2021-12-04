# -*- coding: utf-8 -*-

# nuitka-project: --onefile
# nuitka-project: --onefile-windows-splash-screen-image=D:\\Jonathan\\Documents\\ming\\cornflower.png

"""
*** Description ***
    A pygame MIDI piano.
    This piano is completely controlled by the keyboard, no MIDI hardware is
    required. You only have to set the SF2 variable to a valid soundfont file.
*** Keys ****
    Base octave:
        z,x,c,v,b,n,m    C,D,E,F,G,A,B
        s,d,g,h,j    C#,D#,F#,G#,A#
    Octave higher:
        w,e,r,t,y,u,i   C,D,E,F,G,A,B
        3,4,6,7,8    C#,D#,F#,G#,A#
    Control octaves (default = 4):
        -        octave down
        =        octave up
    Control channels (default = 8):
        backspace    channel down
        \        channel up
"""
""" HOW TO BUILD
set input=ming.py
set output=%input%.exe
set debug=--show-scons --plugin-enable=pylint-warnings --show-progress --plugin-enable=pylint-warnings

python.exe -m nuitka --include-data-file=libfluidsynth.dll=mingus\midi\libfluidsynth.dll \
        --onefile-windows-splash-screen-image=D:\\Jonathan\\Documents\\ming\\cornflower.png \
        --include-data-file=local_pygame_menu\resources\fonts\*.ttf=pygame_menu\resources\fonts\ \
        --include-data-file=libfluidsynth.dll=libfluidsynth.dll \
        --include-data-file=soundfonts\*.sf2=soundfonts\ \
        --include-data-file=imgs\*=imgs\ \
        --include-data-file=dlls\*.dll=dlls\ \
        --windows-icon-from-ico=favicon.ico
        --include-package-data pygame_menu \
        --plugin-enable=numpy  --enable-plugin=anti-bloat \
        --noinclude-pytest-mode=nofollow --noinclude-setuptools-mode=nofollow \
        --python-flag=nosite \
        --onefile -j 5 -o \
        %output% %input% %debug%
"""
import os

basepath = os.path.dirname(os.path.abspath(__file__))
dllspath = os.path.join(basepath, 'dlls')
os.environ['PATH'] = dllspath + os.pathsep + os.environ['PATH']

import pygame
import pygame_menu
from pygame.locals import *
from mingus.core import chords
from mingus.containers import Note
from mingus.midi import fluidsynth
import sys
import time
import tempfile

# from urllib.request import urlopen

VERSION = "0.9.9"

def checkForUpdate():
    print("Checking for updates...")
    """f1 = urlopen("https://raw.githubusercontent.com/UFifty50/temp/main/ming.version").read()
    
    if f1 != VERSION:
        print("updates found.")
        print("updating...")
        update = urlopen("https://github.com/UFifty50/temp/blob/main/ming.py.exe?raw=true").read()
        with open(sys.argv[0], 'wb') as file: file.write(update)
        file.close
        print("updated!")
        os.execl(sys.argv[0], "")
    else:
        print("up to date.")"""
    print("Up to date.")

""" **- defines -** """
OCTAVES = 5  # number of octaves to show
LOWEST = 2  # lowest octave to show
P_FADEOUT = 0.5
G_FADEOUT = 0.12
WHITE_KEY = 0
BLACK_KEY = 1
WHITE_KEYS = [
    "C",
    "D",
    "E",
    "F",
    "G",
    "A",
    "B",
]
BLACK_KEYS = ["C#", "D#", "F#", "G#", "A#"]
UKE_STRINGS = ["G", "C", "E", "A"]
pth = os.path.dirname(os.path.abspath(__file__)).format()

""" **- window init -** """
pygame.init()
pygame.font.init()
font = pygame.font.SysFont("monospace", 12)
global screen
screen = pygame.display.set_mode((450, 325))

""" **- Menu Functions -** """
def start():
    widget = menu.get_widget("Instr")
    instr = widget.get_value()[0][0]
    pygame.display.set_caption(instr)
    if widget.get_value()[1] == 0: piano()
    elif widget.get_value()[1] == 1: ukulele()
    elif widget.get_value()[1] == 2: guitar()
    elif widget.get_value()[1] == 3: fhorn()
    else: pygame.quit(); main()
"""
    match widget.get_value()[1]:
        case 0:
            piano()
        case 1:
            ukulele()
        case 2:
            guitar()
        case 3:
            fhorn()
"""

def load_img(name):
    """Load image and return an image object"""

    fullname = name
    try:
        image = pygame.image.load(fullname)
        if image.get_alpha() is None:
            image = image.convert()
        else:
            image = image.convert_alpha()
    except pygame.error as message:
        print("Error: couldn't load image: ", fullname)
        raise SystemExit(message)
    return (image, image.get_rect())


""" **- Instruments - ** """


def piano():
    sf2 = f'{pth}/soundfonts/Piano.sf2'
    if not fluidsynth.init(sf2):
        print("Couldn't load soundfont", sf2)
        sys.exit(1)

    (key_graphic, kgrect) = load_img(f'{pth}/imgs/keys.png')
    (width, height) = (kgrect.width, kgrect.height)
    white_key_width = width / 7
    # pressed is a surface that is used to show where a key has been pressed
    pressed = pygame.Surface((white_key_width, height))
    pressed.fill((0, 230, 0))
    # text is the surface displaying the determined chord
    global text
    text = pygame.Surface((width * OCTAVES, 20))
    text.fill((255, 255, 255))
    pygame.display.set_mode((width*OCTAVES, height))
    playing_w = []
    playing_b = []
    quit = False
    tick = 0.0
    octave = 4
    channel = 8

    def play_note(note):
        """play_note determines the coordinates of a note on the keyboard image
        and sends a request to play the note to the fluidsynth server"""

        octave_offset = (note.octave - LOWEST) * width
        if note.name in WHITE_KEYS:

            # Getting the x coordinate of a white key can be done automatically

            w = WHITE_KEYS.index(note.name) * white_key_width
            w = w + octave_offset

            # Add a list containing the x coordinate, the tick at the current time
            # and of course the note itself to playing_w

            playing_w.append([w, tick, note])
        else:

            # For black keys I hard coded the x coordinates. It's ugly.

            i = BLACK_KEYS.index(note.name)
            if i == 0:
                w = 18
            elif i == 1:
                w = 58
            elif i == 2:
                w = 115
            elif i == 3:
                w = 151
            else:
                w = 187
            w = w + octave_offset
            playing_b.append([w, tick, note])

        # To find out what sort of chord is being played we have to look at both the
        # white and black keys, obviously:

        notes = playing_w + playing_b
        notes.sort()
        notenames = []
        for n in notes:
            notenames.append(n[2].name)

        # Determine the chord

        det = chords.determine(notenames)
        if det != []:
            det = det[0]
        else:
            det = ""

        # And render it onto the text surface

        t = font.render(det, 2, (0, 0, 0))
        text.fill((255, 255, 255))
        text.blit(t, (0, 0))

        # Play the note

        fluidsynth.play_Note(note, channel, 100)

    while not quit:

        # Blit the picture of one octave OCTAVES times.

        for x in range(OCTAVES):
            screen.blit(key_graphic, (x * width, 0))

        # Blit the text surface

        screen.blit(text, (0, height))

        # Check all the white keys

        for note in playing_w:
            diff = tick - note[1]

            # If a is past its prime, remove it, otherwise blit the pressed surface
            # with a 'cool' fading effect.

            if diff > P_FADEOUT:
                fluidsynth.stop_Note(note[2], channel)
                playing_w.remove(note)
            else:
                pressed.fill((0, ((P_FADEOUT - diff) / P_FADEOUT) * 255, 124))
                screen.blit(pressed, (note[0], 0), None, pygame.BLEND_SUB)

        # Now check all the black keys. This redundancy could have been prevented,
        # but it isn't any less clear like this

        for note in playing_b:
            diff = tick - note[1]

            # Instead of SUB we ADD this time, and change the coloration

            if diff > P_FADEOUT:
                fluidsynth.stop_Note(note[2], channel)
                playing_b.remove(note)
            else:
                pressed.fill((((P_FADEOUT - diff) / P_FADEOUT) * 125, 0, 125))
                screen.blit(pressed, (note[0], 1),
                            (0, 0, 19, 68), pygame.BLEND_ADD)

        # Check for keypresses

        for event in pygame.event.get():
            if event.type == QUIT:
                quit = True
                pygame.display.set_mode((450, 325))
            if event.type == KEYDOWN:
                print(event.key)
                if event.key == K_z:
                    play_note(Note("C", octave))
                elif event.key == K_s:
                    play_note(Note("C#", octave))
                elif event.key == K_x:
                    play_note(Note("D", octave))
                elif event.key == K_d:
                    play_note(Note("D#", octave))
                elif event.key == K_c:
                    play_note(Note("E", octave))
                elif event.key == K_v:
                    play_note(Note("F", octave))
                elif event.key == K_g:
                    play_note(Note("F#", octave))
                elif event.key == K_b:
                    play_note(Note("G", octave))
                elif event.key == K_h:
                    play_note(Note("G#", octave))
                elif event.key == K_n:
                    play_note(Note("A", octave))
                elif event.key == K_j:
                    play_note(Note("A#", octave))
                elif event.key == K_m:
                    play_note(Note("B", octave))
                elif event.key == K_COMMA:
                    play_note(Note("C", octave + 1))
                elif event.key == K_l:
                    play_note(Note("C#", octave + 1))
                elif event.key == K_PERIOD:
                    play_note(Note("D", octave + 1))
                elif event.key == K_SEMICOLON:
                    play_note(Note("D#", octave + 1))
                elif event.key == K_SLASH:
                    play_note(Note("E", octave + 1))
                elif event.key == K_q:
                    play_note(Note("B", octave))
                elif event.key == K_w:
                    play_note(Note("C", octave + 1))
                elif event.key == K_3:
                    play_note(Note("C#", octave + 1))
                elif event.key == K_e:
                    play_note(Note("D", octave + 1))
                elif event.key == K_4:
                    play_note(Note("D#", octave + 1))
                elif event.key == K_r:
                    play_note(Note("E", octave + 1))
                elif event.key == K_t:
                    play_note(Note("F", octave + 1))
                elif event.key == K_6:
                    play_note(Note("F#", octave + 1))
                elif event.key == K_y:
                    play_note(Note("G", octave + 1))
                elif event.key == K_7:
                    play_note(Note("G#", octave + 1))
                elif event.key == K_u:
                    play_note(Note("A", octave + 1))
                elif event.key == K_8:
                    play_note(Note("A#", octave + 1))
                elif event.key == K_i:
                    play_note(Note("B", octave + 1))
                elif event.key == K_o:
                    play_note(Note("C", octave + 2))
                elif event.key == K_0:
                    play_note(Note("C#", octave + 2))
                elif event.key == K_p:
                    play_note(Note("D", octave + 2))
                elif event.key == K_MINUS:
                    octave -= 1
                elif event.key == K_EQUALS:
                    octave += 1
                elif event.key == K_BACKSPACE:
                    channel -= 1
                elif event.key == K_BACKSLASH:
                    channel += 1
                elif event.key == K_ESCAPE:
                    quit = True
                    pygame.display.set_mode((450, 325))
        pygame.display.update()
        tick += 0.001


def fhorn():
    mytheme = pygame_menu.themes.THEME_DARK.copy()
    mytheme.widget_font = pygame_menu.font.FONT_OPEN_SANS
    pygame.display.set_mode((450, 325))
    hornmenu = pygame_menu.Menu('W.I.P.', 450, 325,
                            theme=mytheme)
    hornmenu.add.label("This Instrument is not yet")
    hornmenu.add.label("finished, please bear with me :)")
    hornmenu.add.selector(
    'Instrument :', [('Piano', f'{pth}/imgs/keys.png'), ('Ukulele', f'{pth}/imgs/keys.png'), ('Guitar', f'{pth}/imgs/keys.png'), ('French Horn', f'{pth}/imgs/keys.png')], selector_id="Instr")
    hornmenu.add.button('Start', start)
    hornmenu.add.button('Quit', pygame_menu.events.EXIT)
    hornmenu.mainloop(screen)
    
def ukulele():
    mytheme = pygame_menu.themes.THEME_DARK.copy()
    mytheme.widget_font = pygame_menu.font.FONT_OPEN_SANS
    pygame.display.set_mode((450, 325))
    ukemenu = pygame_menu.Menu('W.I.P.', 450, 325,
                            theme=mytheme)
    ukemenu.add.label("This Instrument is not yet")
    ukemenu.add.label("finished, please bear with me :)")
    ukemenu.add.selector(
    'Instrument :', [('Piano', f'{pth}/imgs/keys.png'), ('Ukulele', f'{pth}/imgs/keys.png'), ('Guitar', f'{pth}/imgs/keys.png'), ('French Horn', f'{pth}/imgs/keys.png')], selector_id="Instr")
    ukemenu.add.button('Start', start)
    ukemenu.add.button('Quit', pygame_menu.events.EXIT)
    ukemenu.mainloop(screen)


def guitar():
    sf2 = f'{pth}/soundfonts/Guitar.sf2'
    if not fluidsynth.init(sf2):
        print("Couldn't load soundfont", sf2)
        sys.exit(1)

    (key_graphic, kgrect) = load_img(f'{pth}/imgs/Guitar.png')
    (key_graphic2, kgrect2) = load_img(f'{pth}/imgs/Guitar2.png')
    (width, height) = (kgrect.width, kgrect.height)
    string_width = width / 7
    # pressed is a surface that is used to show where a key has been pressed
    pressed = pygame.Surface((string_width, height))
    pressed.fill((0, 230, 0))
    # text is the surface displaying the determined chord
    text = pygame.Surface((width, height))
    text.fill((255, 255, 255))
    pygame.display.set_mode((width, height))
    playing_strings = []
    playing_chords = []
    quit = False
    tick = 0.0
    strings = 6
    channel = 8
    while not quit:

        screen.blit(key_graphic, (0, 0))
        screen.blit(key_graphic2, (240, 90))

        # Blit the text surface

        screen.blit(text, (0, height))

        # Check all the white keys

        for note in playing_strings:
            diff = tick - note[1]

            # If a is past its prime, remove it, otherwise blit the pressed surface
            # with a 'cool' fading effect.

            if diff > G_FADEOUT:
                fluidsynth.stop_Note(note[2], channel)
                playing_strings.remove(note)
            else:
                pressed.fill((0, ((G_FADEOUT - diff) / G_FADEOUT) * 255, 124))
                screen.blit(pressed, (note[0], 0), None, pygame.BLEND_SUB)

        # Now check all the black keys. This redundancy could have been prevented,
        # but it isn't any less clear like this

        for note in playing_chords:
            diff = tick - note[1]

            # Instead of SUB we ADD this time, and change the coloration

            if diff > G_FADEOUT:
                fluidsynth.stop_Note(note[2], channel)
                playing_chords.remove(note)
            else:
                pressed.fill((((G_FADEOUT - diff) / G_FADEOUT) * 125, 0, 125))
                screen.blit(pressed, (note[0], 1),
                            (0, 0, 19, 68), pygame.BLEND_ADD)

        # Check for keypresses
        octave = 1
        for event in pygame.event.get():
            if event.type == QUIT:
                quit = True
                pygame.display.set_mode((450, 325))
            if event.type == KEYDOWN:
                print(event.key)
                if event.key == K_z:
                    Note("C", octave)
                elif event.key == K_s:
                    Note("C#", octave)
                elif event.key == K_x:
                    Note("D", octave)
                elif event.key == K_d:
                    Note("D#", octave)
                elif event.key == K_c:
                    Note("E", octave)
                elif event.key == K_v:
                    Note("F", octave)
                elif event.key == K_g:
                    Note("F#", octave)
                elif event.key == K_b:
                    Note("G", octave)
                elif event.key == K_h:
                    Note("G#", octave)
                elif event.key == K_n:
                    Note("A", octave)
                elif event.key == K_j:
                    Note("A#", octave)
                elif event.key == K_m:
                    Note("B", octave)
                elif event.key == K_COMMA:
                    Note("C", octave + 1)
                elif event.key == K_l:
                    Note("C#", octave + 1)
                elif event.key == K_PERIOD:
                    Note("D", octave + 1)
                elif event.key == K_SEMICOLON:
                    Note("D#", octave + 1)
                elif event.key == K_SLASH:
                    Note("E", octave + 1)
                elif event.key == K_q:
                    Note("B", octave)
                elif event.key == K_w:
                    Note("C", octave + 1)
                elif event.key == K_3:
                    Note("C#", octave + 1)
                elif event.key == K_e:
                    Note("D", octave + 1)
                elif event.key == K_4:
                    Note("D#", octave + 1)
                elif event.key == K_r:
                    Note("E", octave + 1)
                elif event.key == K_t:
                    Note("F", octave + 1)
                elif event.key == K_6:
                    Note("F#", octave + 1)
                elif event.key == K_y:
                    Note("G", octave + 1)
                elif event.key == K_7:
                    Note("G#", octave + 1)
                elif event.key == K_u:
                    Note("A", octave + 1)
                elif event.key == K_8:
                    Note("A#", octave + 1)
                elif event.key == K_i:
                    Note("B", octave + 1)
                elif event.key == K_o:
                    Note("C", octave + 2)
                elif event.key == K_0:
                    Note("C#", octave + 2)
                elif event.key == K_p:
                    Note("D", octave + 2)
                elif event.key == K_MINUS:
                    octave -= 1
                elif event.key == K_EQUALS:
                    octave += 1
                elif event.key == K_BACKSPACE:
                    channel -= 1
                elif event.key == K_BACKSLASH:
                    channel += 1
                elif event.key == K_ESCAPE:
                    quit = True
                    pygame.display.set_mode((450, 325))
        pygame.display.update()
        tick += 0.001

""" **- Menu init -** """
time.sleep(2)
mytheme = pygame_menu.themes.THEME_BLUE.copy()
mytheme.widget_font = pygame_menu.font.FONT_OPEN_SANS
pygame.display.set_mode((450, 325))
menu = pygame_menu.Menu('Welcome', 450, 325,
                        theme=mytheme)
menu.add.selector(
    'Instrument :', [('Piano', f'{pth}/imgs/keys.png'), ('Ukulele', f'{pth}/imgs/keys.png'), ('Guitar', f'{pth}/imgs/keys.png'), ('French Horn', f'{pth}/imgs/keys.png')], selector_id="Instr")
menu.add.button('Start', start)
menu.add.button('Quit', pygame_menu.events.EXIT)
        
def main():
    checkForUpdate()
    if "NUITKA_ONEFILE_PARENT" in os.environ:
        splash_filename = os.path.join(
            tempfile.gettempdir(),
            "onefile_%d_splash_feedback.tmp" % int(os.environ["NUITKA_ONEFILE_PARENT"]),
        )
        
        if os.path.exists(splash_filename):
            os.unlink(splash_filename)
    
    menu.mainloop(screen)

main()
