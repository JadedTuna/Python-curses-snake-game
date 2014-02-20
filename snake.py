## Snake - a very simple Python curses snake game.
## Copyright (C) 2014 Victor Kindhart (digitloft@gmail.com)
## 
## This program is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
## 
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
## 
## You should have received a copy of the GNU General Public License
## along with this program.  If not, see <http://www.gnu.org/licenses/>.

import curses
import time
import random
import traceback


__author__ = "Victor Kindhart (digitloft@gmail.com)"
__version__ = "0.2"

def load_settings():
    f = open("settings.txt")
    data = f.read()
    f.close()
    for line in data.splitlines():
        exec "%s = %s" % (line.split("=")[0], line.split("=")[1])
    assert isinstance(startlength, int)
    assert isinstance(acceleration, bool)
    assert isinstance(difficulty, str)
    assert isinstance(growlength, int)
    return startlength, acceleration, difficulty, growlength

global acceleration, growlength, difficulty, startlength, speeds, speedsl
speeds = {
    "Noob"       : 0.3,
    "Newbie"     : 0.2,
    "Easy"       : 0.1,
    "Medium"     : 0.06,
    "Hard"       : 0.04,
    "Ultra-Hard" : 0.02
}
speedsl = ("Noob", "Newbie", "Easy", "Medium", "Hard", "Ultra-Hard")
try:
    startlength, acceleration, difficulty, growlength = load_settings()
except:
    f = open("settings.txt", "w")
    f.write("startlength=5\nacceleration=True\ngrowlength=1\ndifficulty=\"Easy\"")
    startlength = 5
    acceleration = True
    growlength = 1
    difficulty = "Easy"

allowed_maxy = 12
allowed_maxx = 40

screen = curses.initscr()
maxy, maxx = screen.getmaxyx()
if (maxy < allowed_maxy) or (maxx < allowed_maxx):
    print "Screen is too small! It should be minimum %s by %s!" % (allowed_maxy, allowed_maxx)
    curses.endwin()
    raise SystemExit(1)
curses.start_color()
curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)  #Default
curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK) #Food
curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)    #Head
curses.init_pair(4, curses.COLOR_GREEN, curses.COLOR_BLACK)  #Body
screen.keypad(1)
curses.noecho()

def draw_title(title="Snake", screen=screen):
    screen.addstr(0, maxx/2-len(title)/2, title)

def draw(text, y, x, color_pair=None):
    if color_pair is None:
        screen.addstr(y, x, text)
    else:
        screen.addstr(y, x, text, curses.color_pair(color_pair))

def main():
    screen.nodelay(1)
    char = "X"
    food = "@"
    foodmade = False
    blank = " "
    heads = {
    0: ">",
    1: "<",
    2: "^",
    3: "v",
    }
    head = [1, 1]
    body = [head[:]] * startlength
    startbody = len(body)
    screen.border()
    direction = 0 #0:right 1:left 2:up 3:down
    gameover = 0
    speed = 1
    deadcell = body[-1][:]
    paused = 0
    while not gameover:
        if paused:
            if screen.getch() == ord("p"):
                screen.border()
                paused = 0
                continue
            time.sleep(0.1)
            continue
        while not foodmade:
            y, x = random.randrange(1, maxy - 1), random.randrange(1, maxy - 1)
            if screen.inch(y, x) == ord(' '):
                foodmade = True
                screen.addch(y, x, ord(food), curses.A_BOLD|curses.color_pair(2))
        if deadcell not in body:
            screen.addch(deadcell[0], deadcell[1], blank)

        action = screen.getch()
        if action == curses.KEY_UP and direction != 3:
            direction = 2
        elif action == curses.KEY_DOWN and direction != 2:
            direction = 3
        elif action == curses.KEY_RIGHT and direction != 1:
            direction = 0
        elif action == curses.KEY_LEFT and direction != 0:
            direction = 1

        elif action == ord('q'):
            gameover = True
            continue

        elif action == ord("p"):
            screen.addstr(maxy - 1, 1, "Paused. Press P to continue.")
            paused = 1
            #continue

        headchar = heads[direction]
        screen.addch(head[0], head[1], headchar, curses.A_BOLD|curses.color_pair(3))
        screen.addch(body[1][0], body[1][1], char, curses.color_pair(4))

        if direction == 0:
            head[1] += speed
        elif direction == 1:
            head[1] -= speed
        elif direction == 2:
            head[0] -= speed
        elif direction == 3:
            head[0] += speed

        deadcell = body[-1][:]
        for z in range(len(body) - 1, 0, -1):
            body[z] = body[z - 1]

        body[0] = head[:]

        nchar = screen.inch(head[0], head[1])
        if nchar == 2097728:
            foodmade = False
            for i in range(growlength):
                body.append(body[-1])
        elif nchar == ord(" "):
            pass
        else:
            gameover = True
        screen.addstr(0, 1, "Score:%s" % ((len(body) - startbody)/growlength))
        screen.move(maxy - 1, maxx - 1)
        screen.refresh()
        if not acceleration:
            t = speeds[difficulty]
        else:
            t = 15.0 * speeds[difficulty]/len(body)
        time.sleep(t)

    if gameover:
        screen.clear()
        screen.nodelay(0)
        options = (
        "Game Over!",
        "You got " + str((len(body) - startbody)/growlength) + " points",
        "Press Space to play again",
        "Press M to go to main menu",
        "Press Enter to quit")
        i = -(len(options)/2)
        for msg in options:
            screen.addstr(maxy/2 + i, (maxx - len(msg))/2, msg)
            i += 1
        screen.refresh()
        q = None
        while q not in (ord(" "), ord("\n"), ord("m")):
            q = screen.getch()
        screen.clear()
        if q == ord(" "):
            return "play"
        elif q == ord("m"):
            return "continue"
        elif q == ord("\n"):
            return

def help():
    str = "Welcome to Snake! You can control your snake using arrow keys."
    str2 = "Try to get as many points as you can to win! Good luck."
    draw_title()
    screen.addstr(maxy/2-1, maxx/2-len(str)/2, str)
    screen.addstr(maxy/2, maxx/2-len(str2)/2, str2)
    screen.addstr(maxy/2+5, maxx/4-2, "Back", curses.A_REVERSE)
    while True:
        action = screen.getch()
        if action == ord("\n"):
            screen.clear()
            return

def settings():
    options = (
    "Starting snake length: ",
    "Grow length: ",
    "Difficulty: ",
    "Acceleration: ",
    "Back"
    )
    global difficulty, acceleration, growlength, startlength, speedsl, speeds
    option = 0
    while True:
        screen.clear()
        graphics = [0] * len(options)
        graphics[option] = curses.A_REVERSE
        draw_title()
        screen.addstr(maxy/2-2, maxx/2-len(options[0])/2,   options[0] + str(startlength),     graphics[0])
        screen.addstr(maxy/2-1, maxx/2-len(options[1])/2,   options[1] + str(growlength),      graphics[1])
        screen.addstr(maxy/2,   maxx/2-len(options[2])/2-1, options[2] + str(difficulty),      graphics[2])
        screen.addstr(maxy/2+1, maxx/2-len(options[3])/2-1, options[3] + str(acceleration),    graphics[3])
        screen.addstr(maxy/2+2, maxx/2-len(options[4])/2+1, options[4],                        graphics[4])
        action = screen.getch()
        if action == curses.KEY_DOWN:
            option = (option + 1) % len(graphics)
        elif action == curses.KEY_UP:
            option = (option - 1) % len(graphics)
        elif action == ord("\n"):
            if option == 4:
                f = open("settings.txt", "w")
                f.write("startlength=%s\nacceleration=%s\ngrowlength=%s\ndifficulty=\"%s\"" % (startlength, acceleration, growlength, difficulty))
                f.close()
                screen.clear()
                return
            elif option == 3:
                if acceleration == True:
                    acceleration = False
                else:
                    acceleration = True
        elif action in (curses.KEY_LEFT, curses.KEY_RIGHT):
            if option == 4:
                continue
            if action == curses.KEY_LEFT: #Left arrow Key
                if option == 0 and startlength > 2:
                    startlength -= 1
                elif option == 1 and growlength > 1:
                    growlength -= 1
                elif option == 2:
                    index = speedsl.index(difficulty) - 1
                    if index < 0:
                        index = 5
                    difficulty = speedsl[index]
                elif option == 3:
                    if acceleration == True:
                        acceleration = False
                    else:
                        acceleration = True
                elif option == 4 and clients > 2:
                    clients -= 1
            elif action == curses.KEY_RIGHT: #Right arrow Key
                if option == 0 and startlength < 10:
                    startlength += 1
                elif option == 1 and growlength < 7:
                    growlength += 1
                elif option == 2:
                    index = speedsl.index(difficulty) + 1
                    if index > 5:
                        index = 0
                    difficulty = speedsl[index]
                elif option == 3:
                    if acceleration == True:
                        acceleration = False
                    else:
                        acceleration = True


def menu():
    screen.nodelay(0)
    option = 0
    while True:
        graphics = [0] * 4
        graphics[option] = curses.A_REVERSE
        draw_title()

        screen.addstr(maxy/2-2, maxx/2-2, "Play", graphics[0])
        screen.addstr(maxy/2-1, maxx/2-2, "Help", graphics[1])
        screen.addstr(maxy/2, maxx/2-4, "Settings", graphics[2])
        screen.addstr(maxy/2+1, maxx/2-2, "Exit", graphics[3])
        screen.refresh()
        action = screen.getch()
        if action == curses.KEY_UP:
            option = (option - 1) % len(graphics)
        elif action == curses.KEY_DOWN:
            option = (option + 1) % len(graphics)
        elif action == ord("\n"):
            screen.clear()
            if option == 0: #Play
                while True:
                    opt = main()
                    if opt == "play":
                        screen.clear()
                        opt = main()
                    elif opt == "continue":
                        break
                    else:
                        return
                screen.clear()
            elif option == 1: #Help menu
                help()
            elif option == 2: #Settings
                settings()
            elif option == 3: #Exit
                break

menu()
curses.endwin()
