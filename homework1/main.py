import curses
import random
import typer
import os.path
import pickle
import keyboard
from typing import List

VERTICAL = 1
HORIZONTAL = 2
INSTRUCTIONS_HEIGHT = 14
INSTRUCTIONS_LENGTH = 7

SCREEN_ADDITIONAL_HEIGHT = 31
SCREEN_ADDITIONAL_WIDTH = 10


def check_saves() -> list:
    """
    Checks if any saves are available

    :return: list with 0s and 1s, where 1 means that save exists
    """
    save_list = list()
    for i in range(1, 6):
        check_file = os.path.exists(f'save{i}.pickle')
        if check_file:
            save_list.append(1)
        else:
            save_list.append(0)
    return save_list


def get_player_name(number: int) -> str:
    """
    Get player name from standard input

    :param number: number of player
    :return: player name
    """
    player_name = input(f"Insert Player{number} nickname: ")
    return player_name


def show_welcome(player_name_0: str, player_name_1: str, screen, moved: bool, n: int, k: int) -> None:
    """
    Shows "welcome" screen

    :param player_name_0: Name of Player1
    :param player_name_1: Name of Player2
    :param screen: Screen
    :param moved:
    :return: None
    """
    welcome_str = '#####################################\n' \
                  + '#       WELCOME TO BATTLESHIP       #\n' \
                  + '#####################################\n\n'
    player_names_str = 'Player 1: {}\n'.format(player_name_0) \
                       + 'Player 2: {}\n'.format(player_name_1)
    instructions_str = '\nPress p to play a new game.\nPress q to quit.'
    if moved:
        instructions_str += f'\nWarning. N or K was too big or too small. Values were changed to optimal sizes: {n}, {k} '
    screen.refresh()
    screen.addstr(0, 0, welcome_str + player_names_str + instructions_str)


def end_game(player1_win, player2_win, winner: int) -> None:
    """
    Clears all windows and shows who have won the game

    :param player1_win: window of P1
    :param player2_win: window of P2
    :param winner: number of winner
    :return: None
    """
    player1_win.clear()
    player2_win.clear()
    if winner == 1:
        player1_win.addstr("YOU WON!\nUSE q TO FINISH")
        player2_win.addstr("YOU LOST!")
    else:
        player2_win.addstr("YOU WON!")
        player1_win.addstr("YOU LOST!\nUSE q TO FINISH")
    player1_win.refresh()
    player2_win.refresh()


def is_ship(a: int):
    """
    Checks if it is a ship

    :param a: any number in [0,1,2,3,4]
    :return: 1 if it is a ship, 0 if it is not
    """
    if a == 1 or a == 2 or a == 3 or a == 4:
        return 1
    return 0


def main(screen, n: int, k: int):
    """
    Main function of program

    :param screen:  main window
    :param n: n
    :param k: k
    :return: None
    """
    moved = False
    maxy, maxx = screen.getmaxyx()
    if n > maxy - SCREEN_ADDITIONAL_HEIGHT:
        n = maxy - SCREEN_ADDITIONAL_HEIGHT
        # screen.addstr(f'n was changed to {n} - maximal possible for your size of monitor')
        moved = True
    if k > (maxx - SCREEN_ADDITIONAL_WIDTH) // 2:
        k = (maxx - SCREEN_ADDITIONAL_WIDTH) // 2
        screen.addstr(f'k was changed to {k} - maximal possible for your size of monitor')
        moved = True
    if n < 5:
        n = 5
        moved = True
    if k < 5:
        k = 5
        moved = True

    curses.curs_set(0)
    # print(screen.getmaxyx())
    save_list = check_saves()
    screen.clear()
    screen.refresh()
    while True:
        show_welcome(PLAYER_NAME_0, PLAYER_NAME_1, screen, moved, n, k)
        key = screen.getkey()
        if key == 'q':
            break
        elif key == 'p':
            screen.clear()
            screen.refresh()
            choose_option = ord('n')
            if save_list.count(1) >= 1:
                screen.addstr('Would you like to load a save? Y/N\n')
                choose_option = screen.getch()
            while True:
                if choose_option == ord('y'):
                    # print("YES")
                    screen.addstr("Use digits to choose a save\n")
                    for i in range(0, 5):
                        if save_list[i] == 1:
                            screen.addstr(f'save{i + 1}\n')
                    screen.refresh()
                    while True:
                        while (True):
                            choose_option = screen.getch() - 48
                            if 1 <= choose_option and choose_option <= 5:
                                break
                            else:
                                continue
                        screen.clear()
                        screen.refresh()
                        if choose_option <= 5 and save_list[choose_option - 1] == 1:
                            with open(f'save{choose_option}.pickle', 'rb') as f:
                                data = pickle.load(f)
                                player1_field, player1_ships, player2_field, player2_ships = data
                                n = len(player1_field)
                                k = len(player1_field[0])
                                player1_win = make_window(n, k, 6, 0, 1, player1_field, player1_ships)[0]
                                player2_win = make_window(n, k, 6, maxx - (k + 8), 2, player2_field, player2_ships)[0]
                            break
                    break
                elif choose_option == ord('n'):
                    screen.clear()
                    screen.refresh()
                    player1_win, player1_ships, player1_field = make_window(n, k, 6, 0, 1)
                    player2_win, player2_ships, player2_field = make_window(n, k, 6, maxx - (k + 8), 2)
                    break
                else:
                    choose_option = screen.getch()
            player1_win.refresh()
            player2_win.refresh()
            y = 0
            x = 0
            screen.refresh()
            player1_win.refresh()
            player2_win.refresh()
            screen.addstr(0, 0, """===CONTROLS===
Move cursor: WASD
Fire: F
Quit: Q
Save and Exit: Z""")
            while True:
                while True:
                    x_last = x
                    y_last = y
                    if player2_field[y][x] == "X" or player2_field[y][x] == "O":
                        tmp = player2_field[y][x]
                    else:
                        tmp = "."
                    key = screen.getch()
                    if key == ord("d"):
                        x = min(x + 1, len(player2_field[0]) - 1)
                    elif key == ord("a"):
                        x = max(x - 1, 0)
                    elif key == ord("w"):
                        y = max(y - 1, 0)
                    elif key == ord("s"):
                        y = min(y + 1, len(player2_field) - 1)
                    elif key == ord("f"):
                        if is_ship(player2_field[y][x]) == 1:
                            player2_field[y][x] = "X"
                            check_if_destroyed(y, x, player2_field, player2_win, player2_ships)
                            ender = check_for_end(player2_ships)
                            if ender == 1:
                                end_game(player1_win, player2_win, 1)
                                key = screen.getch()
                                while key != ord("q"):
                                    key = screen.getch()
                                return
                            else:
                                player2_win.addstr(y, x, "X")
                                player2_win.refresh()
                                break
                        elif player2_field[y][x] == "X" or player2_field[y][x] == "O":
                            continue
                        else:
                            player2_field[y][x] = "O"
                            player2_win.addstr(y, x, "O")
                            player2_win.refresh()
                            break
                    elif key == ord("q"):
                        keyboard.press('f11')
                        return
                    elif key == ord("z"):
                        save_game(screen, save_list, player1_field, player1_ships, player2_field, player2_ships)
                        keyboard.press('f11')
                        return

                    player2_win.addstr(y_last, x_last, tmp)
                    player2_win.addstr(y, x, "#")
                    player2_win.refresh()
                while True:
                    y_bot = random.randint(0, n - 1)
                    x_bot = random.randint(0, k - 1)
                    if is_ship(player1_field[y_bot][x_bot]) == 1:
                        player1_field[y_bot][x_bot] = "X"
                        check_if_destroyed(y_bot, x_bot, player1_field, player1_win, player1_ships)
                        ender = check_for_end(player1_ships)
                        if ender == 1:
                            end_game(player1_win, player2_win, 2)
                            key = screen.getch()
                            while key != ord("q"):
                                key = screen.getch()
                            keyboard.press('f11')
                            return
                        else:
                            player1_win.addstr(y_bot, x_bot, "X")
                            player1_win.refresh()
                            break
                    elif player1_field[y_bot][x_bot] == "X" or player1_field[y_bot][x_bot] == "O":
                        continue
                    else:
                        player1_field[y_bot][x_bot] = "O"
                        player1_win.addstr(y_bot, x_bot, "O")
                        player1_win.refresh()
                        break


def save_game(screen, save_list, player1_field: List[List[int]],
              player1_ships: List[int], player2_field: List[List[int]], player2_ships: List[int]) -> None:
    """
    Saves game

    :param screen: main window
    :param save_list: list of existing saves
    :param player1_field: matrix of player1's field
    :param player1_ships: list of player1's ships
    :param player2_field: matrix of player2's field
    :param player2_ships: list of player2's ships
    :return: None
    """
    instructions_and_decorations_height = 21
    saves_win = curses.newwin(10, len('Use WS to choose a save slot'),
                              len(player1_field) + instructions_and_decorations_height, 0)
    saves_win.addstr("Use digits to choose a save slot")
    screen.refresh()
    saves_win.refresh()
    for number in range(0, 5):
        if save_list[number] == 1:
            saves_win.addstr(number + 1, 0, f'save{number + 1}')
        else:
            saves_win.addstr(number + 1, 0, 'empty')
        saves_win.refresh()
    save_key = 0
    while True:
        save_key = screen.getch()
        save_key -= 48
        if 1 <= save_key and save_key <= 5:
            break
        else:
            continue
    data = player1_field, player1_ships, player2_field, player2_ships
    with open(f'save{save_key}.pickle', 'wb') as f:
        pickle.dump(data, f)


def make_window(n: int, k: int, posy: int, posx: int, num: int, field=0, ship_list=0):
    """
    makes player window

    :param n: heigth
    :param k: length
    :param posy: position (where 0 is upper bound)
    :param posx: position (where 0 is left bound)
    :param num: number of player
    :param field: matrix of player's field (can be generated automatically)
    :param ship_list: list of player's ships (can be generated automatically)
    :return:
    """
    player_win = curses.newwin(n + INSTRUCTIONS_HEIGHT, k + INSTRUCTIONS_LENGTH, posy, posx)
    if num == 1:
        player_win.addstr(n + 1, 0, "YOUR FIELD\n")
    else:
        player_win.addstr(n + 1, 0, "ENEMY FIELD\n")
    amount_of_decorators = (k - 2) // 2
    player_win.addstr(n + 2, 0,
                      '=' * k + '\n' + amount_of_decorators * '~' + f'P{num}' +
                      amount_of_decorators * '~' + '\n' + '=' * k + '\n')
    player_win.refresh()
    if ship_list == 0:
        ship_list = count_amount_of_ships(n, k)
    if field == 0:
        field = generate_field(n, k, count_amount_of_ships(n, k))
    if num == 1:
        for i in range(len(field)):
            string = ""
            for j in range(0, len(field[i])):
                if field[i][j] == 0:
                    string += '.'
                elif field[i][j] == '0':
                    string += '0'
                elif field[i][j] == 'X':
                    string += 'X'
                else:
                    string += str(field[i][j])
                player_win.addstr(i, 0, string)
                player_win.refresh()
    else:
        for i in range(0, len(field)):
            string = ""
            for j in range(0, len(field[i])):
                if field[i][j] == 'O':
                    string += 'O'
                elif field[i][j] == 'X':
                    string += 'X'
                else:
                    string += '.'
                player_win.addstr(i, 0, string)
                player_win.refresh()

    build_ships_tab(n, k, ship_list, player_win)
    return player_win, ship_list, field


def check_for_end(ship_list: List[int]) -> int:
    """
    Checks if any ships left
    :param ship_list: list of player's ships
    :return:
    """
    if ship_list.count(0) == 4:
        return 1
    return 0


###########################
def check_horizontal_if_destroyed(y: int, x: int, player_field: List[List[int]]) -> int:
    """
    checks for ship destruction in x axis

    :param y: vertical position in matrix
    :param x: horizontal position in matrix
    :param player_field: matrix of player's field
    :return: -1 if ship is not destroyed or size of ship if it is
    """
    x_beg = x
    counter = 0
    while player_field[y][x] == "X" and x < len(player_field[0]) - 1:
        x += 1
        if player_field[y][x] == 1 or player_field[y][x] == 2 or player_field[y][x] == 3 or player_field[y][x] == 4:
            return -1
        if player_field[y][x] == "X":
            counter += 1
    x = x_beg
    while x > 0 and player_field[y][x] == "X":
        x -= 1
        if player_field[y][x] == 1 or player_field[y][x] == 2 or player_field[y][x] == 3 or player_field[y][x] == 4:
            return -1
        if player_field[y][x] == "X":
            counter += 1
    return counter


def check_vertical_if_destroyed(y: int, x: int, player_field: List[List[int]]) -> int:
    """
    checks for ship destruction in y axis

    :param y: vertical position in matrix
    :param x: horizontal position in matrix
    :param player_field: matrix of player's field
    :return: -1 if ship is not destroyed or size of ship if it is
    """
    y_beg = y
    counter = 0
    while player_field[y][x] == "X" and y < len(player_field) - 1:
        y += 1
        if player_field[y][x] == 1 or player_field[y][x] == 2 or player_field[y][x] == 3 or player_field[y][x] == 4:
            return -1
        if player_field[y][x] == "X":
            counter += 1
    y = y_beg
    while y > 0 and player_field[y][x] == "X":
        y -= 1
        if player_field[y][x] == 1 or player_field[y][x] == 2 or player_field[y][x] == 3 or player_field[y][x] == 4:
            return -1
        if player_field[y][x] == "X":
            counter += 1
    return counter


def encircle_size1_ship(y: int, x: int, player_field: List[List[int]], player_win):
    """
    encircles size1 ship
    :param y: vertical position in matrix
    :param x: horizontal position in matrix
    :param player_field: matrix of player's field
    :param player_win: player's window
    :return:
    """
    x_left = max(0, x - 1)
    x_right = min(len(player_field[0]) - 1, x + 1)
    y_up = max(0, y - 1)
    y_down = min(len(player_field) - 1, y + +1)
    if player_field[y][x_left] != 'X':
        player_field[y][x_left] = 'O'
        player_win.addstr(y, x_left, 'O')
    if player_field[y][x_right] != 'X':
        player_field[y][x_right] = 'O'
        player_win.addstr(y, x_right, 'O')
    if player_field[y_down][x] != 'X':
        player_field[y_down][x] = 'O'
        player_win.addstr(y_down, x, 'O')
    if player_field[y_up][x] != 'X':
        player_field[y_up][x] = 'O'
        player_win.addstr(y_up, x, 'O')


def encircle_horizontal_ship(y: int, x: int, player_field: List[List[int]], player_win, checker: int):
    """
        encircles size1 ship
        :param y: vertical position in matrix
        :param x: horizontal position in matrix
        :param player_field: matrix of player's field
        :param player_win: player's window
        :param checker: value from main program, length of ship - 1
        :return:
    """
    length = checker + 1
    y_up = max(0, y - 1)
    y_down = min(len(player_field) - 1, y + 1)
    while player_field[y][x - 1] == 'X' and x > 0:
        x -= 1
    x_left = max(0, x - 1)
    x_right = min(len(player_field[0]) - 1, x + length)
    if player_field[y][x_left] != 'X':
        player_field[y][x_left] = 'O'
        player_win.addstr(y, x_left, 'O')
    for pos in range(x, x + length):
        if player_field[y_up][pos] != 'X':
            player_field[y_up][pos] = 'O'
            player_win.addstr(y_up, pos, 'O')
        if player_field[y_down][pos] != 'X':
            player_field[y_down][pos] = 'O'
            player_win.addstr(y_down, pos, 'O')
    if player_field[y][x_right] != 'X':
        player_field[y][x_right] = 'O'
        player_win.addstr(y, x_right, 'O')


def encircle_vertical_ship(y: int, x: int, player_field: List[List[int]], player_win, checker: int):
    """
        encircles size1 ship
        :param y: vertical position in matrix
        :param x: horizontal position in matrix
        :param player_field: matrix of player's field
        :param player_win: player's window
        :param checker: value from main program, length of ship - 1
        :return:
    """
    length = checker + 1
    x_left = max(0, x - 1)
    x_right = min(len(player_field[0]) - 1, x + 1)
    while player_field[y - 1][x] == 'X' and y > 0:
        y -= 1
    y_up = max(0, y - 1)
    y_down = min(len(player_field) - 1, y + length)
    if player_field[y_up][x] != 'X':
        player_field[y_up][x] = 'O'
        player_win.addstr(y_up, x, 'O')
    for pos in range(y, y + length):
        if player_field[pos][x_left] != 'X':
            player_field[pos][x_left] = 'O'
            player_win.addstr(pos, x_left, 'O')
        if player_field[pos][x_right] != 'X':
            player_field[pos][x_right] = 'O'
            player_win.addstr(pos, x_right, 'O')
    if player_field[y_down][x] != 'X':
        player_field[y_down][x] = 'O'
        player_win.addstr(y_down, x, 'O')


def check_if_destroyed(y, x, player_field, player_win, ship_list):
    """
    Checks if ship destroyed. If it is, function changes ship_list
    :param y: vertical position in matrix
    :param x: horizontal position in matrix
    :param player_field: matrix of player's field
    :param player_win: player's window
    :param ship_list: list of player's ships
    :return: None
    """
    k = len(player_field[0])
    n = len(player_field)
    checker1 = check_horizontal_if_destroyed(y, x, player_field)
    checker2 = check_vertical_if_destroyed(y, x, player_field)
    # checker = 0
    if checker1 == -1 or checker2 == -1:
        checker = -1
    elif checker1 == 0 and checker2 == 0:
        checker = 0
        encircle_size1_ship(y, x, player_field, player_win)
    elif checker1 > 0:
        checker = checker1
        encircle_horizontal_ship(y, x, player_field, player_win, checker)
    else:
        checker = checker2
        encircle_vertical_ship(y, x, player_field, player_win, checker)
    if checker != -1:
        ship_list[checker] -= 1
        build_ships_tab(n, k, ship_list, player_win)


def build_ships_tab(n, k, ship_list, player_win):
    """
    Builds a tab with ships amount

    :param n: height
    :param k: width
    :param ship_list: list of ships
    :param player_win: player's window
    :return:
    """
    for_ship_decorators = [(k - len('SHIPS LEFT')) // 2, (k - len(f'SIZE_1:{ship_list[0]}')) // 2,
                           (k - len(f'SIZE_2:{ship_list[1]}')) // 2, (k - len(f'SIZE_3:{ship_list[2]}')) // 2,
                           (k - len(f'SIZE_4:{ship_list[3]}')) // 2]
    player_win.addstr(n + 5, 0, for_ship_decorators[0] * " " + f"SHIPS LEFT" + for_ship_decorators[0] * " " + "\n" +
                      for_ship_decorators[1] * " " + f"SIZE_1: {ship_list[0]}" + for_ship_decorators[
                          1] * " " + "\n" +
                      for_ship_decorators[2] * " " + f"SIZE_2: {ship_list[1]}" + for_ship_decorators[
                          2] * " " + "\n" +
                      for_ship_decorators[3] * " " + f"SIZE_3: {ship_list[2]}" + for_ship_decorators[
                          3] * " " + "\n" +
                      for_ship_decorators[4] * " " + f"SIZE_4: {ship_list[3]}" + for_ship_decorators[4] * " " + (
                              "\n" +
                              k * "=") * 3
                      )
    player_win.refresh()


def count_amount_of_ships(n: int, k: int) -> list:
    """
    Counts amount of ships, that depends on field size (n*k)
    :param n: height of field
    :param k: length of field
    :return: list of ships [amt_of_1, amt_of_2, amt_of_3, amt_of_4]
    """
    ships = [0, 0, 0, 0]
    square = n * k
    for i in range(1, 5):
        ships[i - 1] = square * i // 100
    ships.reverse()
    return ships


def check_around(y: int, x: int, field: list):
    """
    Checks if there is a place for a ship

    :param y: vertical position
    :param x: horizontal position
    :param field: matrix of player's field
    :return: 0 if is not any place and 1 if it is
    """
    if y < len(field) - 1:
        if field[y + 1][x] != 0:
            return 0
    if y > 0:
        if field[y - 1][x] != 0:
            return 0
    if x < len(field[y]) - 1:
        if field[y][x + 1] != 0:
            return 0
    if x > 0:
        if field[y][x - 1] != 0:
            return 0
    return 1


def check_vertical(i: int, field: list) -> (int, int):
    """
    looks for a place for a vertical ship placement

    :param i: size of ship
    :param field: matrix of player's ships
    :return: a pair of coordinates
    """
    c = 1
    while c > 0:
        x = random.randint(0, len(field[0]) - 1)
        y = random.randint(0, len(field) - 1 - i)
        c += 1
        if field[y][x] != 0:
            continue
        flag = 2
        for b in range(y, y + i + 1):
            if field[b][x] != 0 or check_around(b, x, field) == 0:
                flag = 1
                break
        if flag == 2:
            return x, y


def check_horizontal(i: int, field: list) -> (int, int):
    """
        looks for a place for a horizontal ship placement

        :param i: size of ship
        :param field: matrix of player's ships
        :return: pair of coordinates
        """
    c = 1
    while c > 0:
        x = random.randint(0, len(field[0]) - 1 - i)  # 4
        y = random.randint(0, len(field) - 1)  # 9
        if field[y][x] != 0:
            continue
        flag = 2
        c += 1
        for b in range(x, x + i + 1):
            if field[y][b] != 0 or check_around(y, b, field) == 0:
                flag = 1
                break
        if flag == 2:
            return x, y
        # print(flag)


def generate_field(n: int, k: int, ships: list) -> List[List[int]]:
    """
    Randomly generates matrix of player's field

    :param n: height
    :param k: length
    :param ships: list of amounts of ships
    :return: matrix of player's field
    """
    field = [[0 for _ in range(0, k)] for _ in range(0, n)]
    for i in range(0, 4):
        for a in range(0, ships[i]):
            orientation = random.randint(1, 2)
            if orientation == VERTICAL and i >= n:
                orientation = HORIZONTAL
            elif orientation == HORIZONTAL and i >= k:
                orientation = VERTICAL
            if orientation == VERTICAL:
                x, y = check_vertical(i, field)
                for j in range(y, y + i + 1):
                    field[j][x] = i + 1
            elif orientation == HORIZONTAL:
                x, y = check_horizontal(i, field)
                for j in range(x, x + i + 1):
                    field[y][j] = i + 1
    ################################################################
    return field


#########################

def launcher(n: str, k: str):
    """
    launches the game
    :param n: height
    :param k: length
    :return:
    """
    curses.wrapper(main, int(n), int(k))
    keyboard.press('f11')


if __name__ == "__main__":
    keyboard.press('f11')
    random.seed()
    print("Playing a game of Battleship...\n It is recommended to use full screen mode \n to avoid errors and crashes")
    # Ask for user to input names
    PLAYER_NAME_0 = get_player_name(1)
    PLAYER_NAME_1 = get_player_name(2)
    # print(count_amount_of_ships(10, 10))
    # generate_field(10, 10, count_amount_of_ships(10, 10))
    typer.run(launcher)
