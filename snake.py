## Snake - a very simple Python curses snake game.
## Copyright (C) 2014 Victor Kindhart
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
import re


__author__ = "Victor Kindhart"
__version__ = "0.2"

SETTINGS_DEFAULT = """
startlength  = 5
growlength   = 1
difficulty   = 2
acceleration = 1
"""

class Menu(object):
    """
    This class stores all the menu drawing functions and most of the
    needed variables.
    """
    loaded = False

    regex_settings_parser = re.compile("([\S]+)[\s]*\=[\s]*(.+)").findall

    RETURN = ord("\n")
    SPACE  = ord(" ")
    KEY_M  = ord("m")

    speeds = {
    "Noob"       : 0.3,
    "Newbie"     : 0.2,
    "Easy"       : 0.1,
    "Medium"     : 0.06,
    "Hard"       : 0.04,
    "Ultra-Hard" : 0.02
    }
    difficulties = ("Noob", "Newbie", "Easy", "Medium", "Hard", "Ultra-Hard")

    def settings_parser(self, settings):
        out = dict(self.regex_settings_parser(settings))
        for key, value in out.items():
            if value.isdigit():
                out[key] = int(value)
            elif value in ("True", "False"):
                out[key] = eval(value)
        return out

    def load_settings(self):
        try:
            f = open("settings.txt", "r")
            data = f.read()
            f.close()
        except:
            try:
                f = open("settings.txt", "w")
            except:
                self.default_settings() 
                return
            self.default_settings()

            f.write(SETTINGS_DEFAULT)
            f.close()
            return
        required = [
            "startlength",
            "growlength",
            "difficulty",
            "acceleration"
        ]
        required.sort()
        found = []
        settings = self.settings_parser(data)
        for key, value in settings.items():
            if key in required:
                found.append(key)

        found.sort()
        if not (required == found):
            self.default_settings()
            return
        self.settings = {
            "startlength"  : settings["startlength"],
            "growlength"   : settings["growlength"],
            "difficulty"   : settings["difficulty"],
            "acceleration" : settings["acceleration"]
        }

    def default_settings(self):
        self.settings = {
            "startlength"  : 5,
            "growlength"   : 1,
            "difficulty"   : 2,
            "acceleration" : 1
        }

    def generate_settings_string(self):
        string = ""
        for item, value in self.settings.items():
            string += item + "=" + str(value) + "\n"
        return string

    def load_screen(self):
        self.screen = curses.initscr()
        self.maxy, self.maxx = self.screen.getmaxyx()
        self.allowed_maxy = 12
        self.allowed_maxx = 40
        if (self.maxy < self.allowed_maxy) or (self.maxx < self.allowed_maxx):
            print "Screen is too small! It should be minimum %s by %s!" % \
            (self.allowed_maxy, self.allowed_maxx)
            self.unload_screen()
            raise SystemExit(1)
        curses.start_color()
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)  #Default
        curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK) #Food
        curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)    #Head
        curses.init_pair(4, curses.COLOR_GREEN, curses.COLOR_BLACK)  #Body
        self.screen.keypad(1)
        curses.noecho()
        loaded = True

    def unload_screen(self):
        curses.endwin()

    def refresh(self):
        self.screen.refresh()

    def getch(self):
        return self.screen.getch()

    def clear(self):
        self.screen.clear()

    def draw_title(self, title="Snake"):
        self.screen.addstr(0, self.maxx/2-len(title)/2, title)

    def draw_menu(self, menu_elements, graphics, refresh=True):
        z = -len ( min( (menu_elements, graphics) ) ) / 2
        for element, attr in zip(menu_elements, graphics):
            self.screen.addstr( self.maxy/2 + z,
                                self.maxx/2 - len(element)/2,
                                element,
                                attr )
            z += 1
        if refresh:
            self.refresh()

    def menu_mode(self):
        self.screen.nodelay(0)

    def game_mode(self):
        self.screen.nodelay(1)

    def handle_key_menu(self, stdoption, action, graphics):
        if action == curses.KEY_UP:
            return (stdoption - 1) % len(graphics)
        elif action == curses.KEY_DOWN:
            return (stdoption + 1) % len(graphics)
        else:
            return stdoption

    def help_menu(self):
        self.draw_title()
        elements = (
            "Welcome to Snake! Use arrow keys to control your snake.",
            "Try to get as many points as you can. And try not to",
            "hit walls or your snake's body.",
            "",
            "",
            "Press any key to go back."
        )
        graphics = (0, 0, 0, 0, 0, 0)
        self.draw_menu(elements, graphics)
        self.getch()
        self.clear()

    def gameover_menu(self, score):
        self.clear()
        self.draw_title("Game Over!")
        elements = (
            "You got " + str(score) + " points",
            "Press Return to play again",
            "Press M to go to main menu",
            "Press Q to quit"
        )
        self.draw_menu(elements, (0, 0, 0, 0))
        q = None
        while q not in (self.RETURN, self.KEY_M, ord("q")):
            q = self.getch()
            if q == ord("q"):
                option = "quit"
            elif q == self.RETURN:
                option = "play again"
            elif q == self.KEY_M:
                option = "menu"
        self.clear()
        return option

    def settings_menu(self):
        elements = (
            lambda: "Starting snake length: " + str(self.settings["startlength"]),
            lambda: "Grow length: " + str(self.settings["growlength"]),
            lambda: "Difficulty: " + self.difficulties[self.settings["difficulty"]],
            lambda: "Acceleration: " + str(self.settings["acceleration"]),
            lambda: "Back"
        )
        option = 0
        while True:
            self.clear()
            graphics = [0, 0, 0, 0, 0]
            graphics[option] = curses.A_REVERSE
            self.draw_title()
            self.draw_menu(tuple(i() for i in elements), graphics)
            action = self.getch()
            option = self.handle_key_menu(option, action, graphics)
            if option == 4:
                if action == self.RETURN:
                    self.save_settings()
                    break
            if action in (curses.KEY_LEFT, curses.KEY_RIGHT):
                if action == curses.KEY_LEFT:
                    if option == 0 and self.settings["startlength"] > 2:
                        self.settings["startlength"] -= 1
                    elif option == 1 and self.settings["growlength"] > 1:
                        self.settings["growlength"] -= 1
                    elif option == 2:
                        new_difficulty = (self.settings["difficulty"] - 1) % 6
                        value = self.difficulties[new_difficulty]
                        self.settings["difficulty"] = self.difficulties.index(value)
                    elif option == 3:
                        if self.settings["acceleration"]:
                            self.settings["acceleration"] = False
                        else:
                            self.settings["acceleration"] = True
                elif action == curses.KEY_RIGHT:
                    if option == 0 and self.settings["startlength"] < 10:
                        self.settings["startlength"] += 1
                    elif option == 1 and self.settings["growlength"] < 7:
                        self.settings["growlength"] += 1
                    elif option == 2:
                        new_difficulty = (self.settings["difficulty"] + 1) % 6
                        value = self.difficulties[new_difficulty]
                        self.settings["difficulty"] = self.difficulties.index(value)
                    elif option == 3:
                        if self.settings["acceleration"]:
                            self.settings["acceleration"] = False
                        else:
                            self.settings["acceleration"] = True
        self.clear()

    def save_settings(self):
        try:
            f = open("settings.txt", "w")
            f.write(self.generate_settings_string())
            f.close()
        except:
            pass

    def main_menu(self, scr=None):
        del scr
        if not self.loaded:
            self.load_screen()
        self.load_settings()
        self.menu_mode()
        option = 0
        while True:
            self.draw_title()
            elements = (
                "Play",
                "Help",
                "Settings",
                "Exit"
            )
            graphics = [0, 0, 0, 0]
            graphics[option] = curses.A_REVERSE
            self.draw_menu(elements, graphics)
            action = self.getch()
            option = self.handle_key_menu(option, action, graphics)
            if action == self.RETURN:
                self.clear()
                if option == 0:  #Play
                    while True:
                        self.game_mode()
                        snake = SnakeGameWindow(self)
                        score = snake.run()
                        del snake
                        self.menu_mode()
                        opt = self.gameover_menu(score)
                        if opt == "quit":
                            return self.unload_screen()
                        elif opt == "play again":
                            continue
                        elif opt == "menu":
                            break
                elif option == 1:  #Help menu
                    self.help_menu()
                elif option == 2:  #Settings menu
                    self.settings_menu()
                elif option == 3:  #Exit
                    break
        self.unload_screen()

class SnakeGameWindow(object):
    """
    This class actually has the code for the snake game.
    """
    def __init__(self, screen):
        self.screen = screen
    def run(self):
        self.screen.screen.border()

        screen = self.screen.screen

        startlength = self.screen.settings["startlength"]
        growlength = self.screen.settings["growlength"]
        difficulty = self.screen.difficulties[self.screen.settings["difficulty"]]
        acceleration = self.screen.settings["acceleration"]

        food = "@"
        char = "X"
        heads = (">", "<", "^", "v")
        head = [1, 1]
        foodmade = False
        blank = " "
        direction = 0  #0:right 1:left 2:up 3:down
        gameover = 0
        speed = 1
        paused = 0
        maxx, maxy = self.screen.maxx, self.screen.maxy

        body = [head[:]] * startlength
        deadcell = body[-1][:]
        startbody = len(body)
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

            sleep_speed = self.screen.speeds[difficulty]
            if direction in (2, 3):
                sleep_speed += sleep_speed/2
            if not acceleration:
                t = sleep_speed
            else:
                t = 15.0 * sleep_speed/len(body)
            time.sleep(t)
        self.screen.clear()
        self.screen.getch()
        return ((len(body) - startbody)/growlength)

menu = Menu()
import curses.wrapper
curses.wrapper(menu.main_menu)
