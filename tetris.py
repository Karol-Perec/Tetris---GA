#######################################################################################################################
# czesc z gotowym kodem gry + GUI, ktore zostalo odpowiednio zmodyfikowane

# Tetromino (a Tetris clone)
# By Al Sweigart al@inventwithpython.com
# http://inventwithpython.com/pygame
# Released under a "Simplified BSD" license

# Imports
from genetic import *
import random
import time
import pygame
import sys
import copy
import numpy
import matplotlib.pyplot as plt
import pygame.locals as keys
import pyautogui
import win32gui

# Define settings and constants
pyautogui.PAUSE = 0
pyautogui.FAILSAFE = False

FPS = sys.maxsize
WINDOWWIDTH = 640
WINDOWHEIGHT = 480
BOXSIZE = 20
BOARDWIDTH = 10
BOARDHEIGHT = 20
BLANK = '0'
MOVESIDEWAYSFREQ = 0
MOVEDOWNFREQ = 0

XMARGIN = int((WINDOWWIDTH - BOARDWIDTH * BOXSIZE) / 2)
TOPMARGIN = WINDOWHEIGHT - (BOARDHEIGHT * BOXSIZE) - 5

# Define Color triplets in RGB
WHITE = (255, 255, 255)
GRAY = (185, 185, 185)
BLACK = (0, 0, 0)
RED = (155, 0, 0)
LIGHTRED = (175, 20, 20)
GREEN = (0, 155, 0)
LIGHTGREEN = (20, 175, 20)
BLUE = (0, 0, 155)
LIGHTBLUE = (20, 20, 175)
YELLOW = (155, 155, 0)
LIGHTYELLOW = (175, 175, 20)
CYAN = (0, 185, 185)
LIGHTCYAN = (0, 255, 255)
MAGENTA = (185, 0, 185)
LIGHTMAGENTA = (255, 0, 255)

BORDERCOLOR = BLACK
BGCOLOR = WHITE
TEXTCOLOR = BLACK
TEXTSHADOWCOLOR = (0, 0, 0) #GRAY
COLORS = ((135, 135, 135), BLUE, (135, 135, 135), GREEN, RED, YELLOW, CYAN, MAGENTA)
LIGHTCOLORS = ((185, 185, 185), LIGHTBLUE, (185, 185, 185), LIGHTGREEN, LIGHTRED, LIGHTYELLOW,
               LIGHTCYAN, LIGHTMAGENTA)

TEMPLATEWIDTH = 5
TEMPLATEHEIGHT = 5

S_SHAPE_TEMPLATE = [['00000', '00000', '00110', '01100', '00000'],
                    ['00000', '00100', '00110', '00010', '00000']]

Z_SHAPE_TEMPLATE = [['00000', '00000', '01100', '00110', '00000'],
                    ['00000', '00100', '01100', '01000', '00000']]

I_SHAPE_TEMPLATE = [['00100', '00100', '00100', '00100', '00000'],
                    ['00000', '00000', '11110', '00000', '00000']]

O_SHAPE_TEMPLATE = [['00000', '00000', '01100', '01100', '00000']]

J_SHAPE_TEMPLATE = [['00000', '01000', '01110', '00000',
                     '00000'], ['00000', '00110', '00100', '00100', '00000'],
                    ['00000', '00000', '01110', '00010',
                     '00000'], ['00000', '00100', '00100', '01100', '00000']]
L_SHAPE_TEMPLATE = [['00000', '00010', '01110', '00000',
                     '00000'], ['00000', '00100', '00100', '00110', '00000'],
                    ['00000', '00000', '01110', '01000',
                     '00000'], ['00000', '01100', '00100', '00100', '00000']]

T_SHAPE_TEMPLATE = [['00000', '00100', '01110', '00000',
                     '00000'], ['00000', '00100', '00110', '00100', '00000'],
                    ['00000', '00000', '01110', '00100',
                     '00000'], ['00000', '00100', '01100', '00100', '00000']]

PIECES = {
    'S': S_SHAPE_TEMPLATE,
    'Z': Z_SHAPE_TEMPLATE,
    'J': J_SHAPE_TEMPLATE,
    'L': L_SHAPE_TEMPLATE,
    'I': I_SHAPE_TEMPLATE,
    'O': O_SHAPE_TEMPLATE,
    'T': T_SHAPE_TEMPLATE
}


def run_game(weights, nr_pokolenia, nr_chromosomu, proba):
    # setup variables for the start of the game
    board = get_blank_board()
    moving_down = False  # note: there is no movingUp variable
    moving_left = False
    moving_right = False
    score = 0
    games_completed = 0
    current_move = [0, 0]  # Relative Rotation, lateral movement
    falling_piece = get_new_piece()
    next_piece = get_new_piece()

    while True:  # game loop
        if falling_piece is None:
            # No falling piece in play, so start a new piece at the top
            falling_piece = next_piece
            next_piece = get_new_piece()

            if not is_valid_position(board, falling_piece):
                # can't fit a new piece on the board, so game over
                return score, weights
            current_move, weights = gradient_descent(board, falling_piece, weights)

        current_move = make_move(current_move)
        for event in pygame.event.get():  # event handling loop
            if event.type == keys.KEYUP:
                if (event.key == keys.K_p):
                    # Pausing the game
                    DISPLAYSURF.fill(BGCOLOR)
                    show_text_screen('Paused')  # pause until a key press
                elif (event.key == keys.K_LEFT or event.key == keys.K_a):
                    moving_left = False
                elif (event.key == keys.K_RIGHT or event.key == keys.K_d):
                    moving_right = False
                elif (event.key == keys.K_DOWN or event.key == keys.K_s):
                    moving_down = False

            elif event.type == keys.KEYDOWN:
                # moving the piece sideways
                if (event.key == keys.K_LEFT or event.key == keys.K_a) and is_valid_position(
                            board, falling_piece, adj_x=-1):
                    falling_piece['x'] -= 1
                    moving_left = True
                    moving_right = False

                elif (event.key == keys.K_RIGHT or event.key == keys.K_d) and is_valid_position(
                          board, falling_piece, adj_x=1):
                    falling_piece['x'] += 1
                    moving_right = True
                    moving_left = False

                # rotating the piece (if there is room to rotate)
                elif (event.key == keys.K_UP or event.key == keys.K_w):
                    falling_piece[
                        'rotation'] = (falling_piece['rotation'] + 1) % len(
                            PIECES[falling_piece['shape']])
                    if not is_valid_position(board, falling_piece):
                        falling_piece[
                            'rotation'] = (falling_piece['rotation'] - 1) % len(
                                PIECES[falling_piece['shape']])
                elif (event.key == keys.K_q):  # rotate the other direction
                    falling_piece[
                        'rotation'] = (falling_piece['rotation'] - 1) % len(
                            PIECES[falling_piece['shape']])
                    if not is_valid_position(board, falling_piece):
                        falling_piece[
                            'rotation'] = (falling_piece['rotation'] + 1) % len(
                                PIECES[falling_piece['shape']])

                # making the piece fall faster with the down key
                elif (event.key == keys.K_DOWN or event.key == keys.K_s):
                    moving_down = True
                    if is_valid_position(board, falling_piece, adj_y=1):
                        falling_piece['y'] += 1

                # move the current piece all the way down
                elif event.key == keys.K_SPACE:
                    moving_down = False
                    moving_left = False
                    moving_right = False
                    for i in range(1, BOARDHEIGHT):
                        if not is_valid_position(board, falling_piece, adj_y=i):
                            break
                    falling_piece['y'] += i - 1

        # handle moving the piece because of user input
        if (moving_left or moving_right):
            if moving_left and is_valid_position(board, falling_piece, adj_x=-1):
                falling_piece['x'] -= 1
            elif moving_right and is_valid_position(board, falling_piece, adj_x=1):
                falling_piece['x'] += 1

        if moving_down and is_valid_position(board, falling_piece, adj_y=1):
            falling_piece['y'] += 1
            games_completed += 1

        # let the piece fall if it is time to fall

        # see if the piece has landed
        if not is_valid_position(board, falling_piece, adj_y=1):
            # falling piece has landed, set it on the board
            add_to_board(board, falling_piece)
            lines, board = remove_complete_lines(board)
            score += lines                                     # ilosc zbitych lini
            falling_piece = None
        else:
            # piece did not land, just move the piece down
            # wylaczone automatyczne opadanie dla AI
            games_completed += 1
    # drawing everything on the screen
        DISPLAYSURF.fill(BGCOLOR)
        draw_board(board)
        draw_status(score, weights, nr_pokolenia, nr_chromosomu, proba)
        draw_next_piece(next_piece)
        if falling_piece is not None:
            draw_piece(falling_piece)

        pygame.display.update()


def make_text_objs(text, font, color):
    surf = font.render(text, True, color)
    return surf, surf.get_rect()


def check_for_key_press():
    # Go through event queue looking for a KEYUP event.
    # Grab KEYDOWN events to remove them from the event queue.

    for event in pygame.event.get([keys.KEYDOWN, keys.KEYUP]):
        if event.type == keys.KEYDOWN:
            continue
        return event.key
    return None


def show_text_screen(text):
    # This function displays large text in the
    # center of the screen until a key is pressed.
    # Draw the text drop shadow
    title_surf, title_rect = make_text_objs(text, BIGFONT, BLACK)
    title_rect.center = (int(WINDOWWIDTH / 2), int(WINDOWHEIGHT / 2))
    DISPLAYSURF.blit(title_surf, title_rect)

    # Draw the text
    title_surf, title_rect = make_text_objs(text, BIGFONT, WHITE)
    title_rect.center = (int(WINDOWWIDTH / 2) - 3, int(WINDOWHEIGHT / 2) - 3)
    DISPLAYSURF.blit(title_surf, title_rect)

    # Draw the additional "Press a key to play." text.
    press_key_surf, press_key_rect = make_text_objs('Proszę wprowadzić parametry...',
                                                    BASICFONT, WHITE)
    press_key_rect.center = (int(WINDOWWIDTH / 2), int(WINDOWHEIGHT / 2) + 100)
    DISPLAYSURF.blit(press_key_surf, press_key_rect)

    pygame.display.update()
    FPSCLOCK.tick()
    time.sleep(0.5)


def get_new_piece():
    # return a random new piece in a random rotation and color
    shape = random.choice(list(PIECES.keys()))
    new_piece = {
        'shape': shape,
        'rotation': random.randint(0,
                                   len(PIECES[shape]) - 1),
        'x': int(BOARDWIDTH / 2) - int(TEMPLATEWIDTH / 2),
        'y': 0, # -2,  # start it above the board (i.e. less than 0)
                # zmienione ze wzgledu na bledy przy zatrzymanym dla AI opadaniu
        'color': random.randint(1,
                                len(COLORS) - 1)
    }
    return new_piece


def add_to_board(board, piece):
    # fill in the board based on piece's location, shape, and rotation
    for x in range(TEMPLATEWIDTH):
        for y in range(TEMPLATEHEIGHT):
            if PIECES[piece['shape']][piece['rotation']][y][x] != BLANK and x + piece['x'] < 10 and y + piece['y'] < 20:
                board[x + piece['x']][y + piece['y']] = piece['color']
                # DEBUGGING NOTE: SOMETIMES THIS IF STATEMENT ISN'T
                # SATISFIED, WHICH NORMALLY WOULD RAISE AN ERROR.
                # NOT SURE WHAT CAUSES THE INDICES TO BE THAT HIGH.
                # THIS IS A BAND-AID FIX


def get_blank_board():
    # create and return a new blank board data structure
    board = []
    for _ in range(BOARDWIDTH):
        board.append(['0'] * BOARDHEIGHT)
    return board


def is_on_board(x, y):
    return x >= 0 and x < BOARDWIDTH and y < BOARDHEIGHT


def is_valid_position(board, piece, adj_x=0, adj_y=0):
    # Return True if the piece is within the board and not colliding
    for x in range(TEMPLATEWIDTH):
        for y in range(TEMPLATEHEIGHT):
            is_above_board = y + piece['y'] + adj_y < 0
            if is_above_board or PIECES[piece['shape']][piece['rotation']][y][x] == BLANK:
                continue
            if not is_on_board(x + piece['x'] + adj_x, y + piece['y'] + adj_y):
                return False  # The piece is off the board
            if board[x + piece['x'] + adj_x][y + piece['y'] + adj_y] != BLANK:
                return False  # The piece collides
    return True


def is_complete_line(board, y):
    # Return True if the line filled with boxes with no gaps.
    for x in range(BOARDWIDTH):
        if board[x][y] == BLANK:
            return False
    return True


def remove_complete_lines(board):
    # Remove any completed lines on the board, move everything above them down, and return the number of complete lines.
    lines_removed = 0
    y = BOARDHEIGHT - 1  # start y at the bottom of the board
    while y >= 0:
        if is_complete_line(board, y):
            # Remove the line and pull boxes down by one line.
            for pull_down_y in range(y, 0, -1):
                for x in range(BOARDWIDTH):
                    board[x][pull_down_y] = board[x][pull_down_y - 1]
            # Set very top line to blank.
            for x in range(BOARDWIDTH):
                board[x][0] = BLANK
            lines_removed += 1
            # Note on the next iteration of the loop, y is the same.
            # This is so that if the line that was pulled down is also
            # complete, it will be removed.
        else:
            y -= 1  # move on to check next row up
    return lines_removed, board


def convert_to_pixel_coords(boxx, boxy):
    # Convert the given xy coordinates of the board to xy
    # coordinates of the location on the screen.
    return (XMARGIN + (boxx * BOXSIZE)), (TOPMARGIN + (boxy * BOXSIZE))


def draw_box(boxx, boxy, color, pixelx=None, pixely=None):
    # draw a single box (each tetromino piece has four boxes)
    # at xy coordinates on the board. Or, if pixelx & pixely
    # are specified, draw to the pixel coordinates stored in
    # pixelx & pixely (this is used for the "Next" piece).
    if color == BLANK:
        return
    if pixelx is None and pixely is None:
        pixelx, pixely = convert_to_pixel_coords(boxx, boxy)
    pygame.draw.rect(DISPLAYSURF, COLORS[color],
                     (pixelx + 1, pixely + 1, BOXSIZE - 1, BOXSIZE - 1))
    pygame.draw.rect(DISPLAYSURF, LIGHTCOLORS[color],
                     (pixelx + 1, pixely + 1, BOXSIZE - 4, BOXSIZE - 4))


def draw_board(board):
    # draw the border around the board
    pygame.draw.rect(DISPLAYSURF, BORDERCOLOR,
                     (XMARGIN - 3, TOPMARGIN - 7, (BOARDWIDTH * BOXSIZE) + 8,
                      (BOARDHEIGHT * BOXSIZE) + 8), 5)

    # fill the background of the board
    pygame.draw.rect(
        DISPLAYSURF, BGCOLOR,
        (XMARGIN, TOPMARGIN, BOXSIZE * BOARDWIDTH, BOXSIZE * BOARDHEIGHT))
    # draw the individual boxes on the board
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            draw_box(x, y, board[x][y])


def draw_status(score, weights, nr_pokolenia, nr_chromosomu, proba):
    # draw the score text
    score_surf = BASICFONT.render('Wynik: %s' % score, True, TEXTCOLOR)
    score_rect = score_surf.get_rect()
    score_rect.topleft = (WINDOWWIDTH/2-30, 40)
    DISPLAYSURF.blit(score_surf, score_rect)

    pokolenie_surf = BASICFONT.render('Pokolenie: %s' %nr_pokolenia, True, TEXTCOLOR)
    pokolenie_rect = pokolenie_surf.get_rect()
    pokolenie_rect.topleft = (WINDOWWIDTH - 170, 220)
    DISPLAYSURF.blit(pokolenie_surf, pokolenie_rect)

    chromosom_surf = BASICFONT.render('Chromosom: %s' %nr_chromosomu, True, TEXTCOLOR)
    chromosom_rect = chromosom_surf.get_rect()
    chromosom_rect.topleft = (WINDOWWIDTH - 170, 245)
    DISPLAYSURF.blit(chromosom_surf, chromosom_rect)

    proba_surf = BASICFONT.render('Gra próbna: %s' %proba, True, TEXTCOLOR)
    proba_rect = proba_surf.get_rect()
    proba_rect.topleft = (WINDOWWIDTH - 170, 270)
    DISPLAYSURF.blit(proba_surf, proba_rect)

    parametry_surf = BASICFONT.render('Parametry:', True, TEXTCOLOR)
    parametry_rect = chromosom_surf.get_rect()
    parametry_rect.topleft = (WINDOWWIDTH - 170, 325)
    DISPLAYSURF.blit(parametry_surf, parametry_rect)

    w1_surf = BASICFONT.render('[%s]' %round(weights[0], 18), True, TEXTCOLOR)
    w1_rect = w1_surf.get_rect()
    w1_rect.topleft = (WINDOWWIDTH - 205, 350)
    DISPLAYSURF.blit(w1_surf, w1_rect)

    w2_surf = BASICFONT.render('[%s]' %round(weights[1], 18), True, TEXTCOLOR)
    w2_rect = w2_surf.get_rect()
    w2_rect.topleft = (WINDOWWIDTH - 205, 375)
    DISPLAYSURF.blit(w2_surf, w2_rect)

    w3_surf = BASICFONT.render('[%s]' %round(weights[2], 18), True, TEXTCOLOR)
    w3_rect = w3_surf.get_rect()
    w3_rect.topleft = (WINDOWWIDTH - 205, 400)
    DISPLAYSURF.blit(w3_surf, w3_rect)

    w4_surf = BASICFONT.render('[%s]' %round(weights[3], 18), True, TEXTCOLOR)
    w4_rect = w4_surf.get_rect()
    w4_rect.topleft = (WINDOWWIDTH - 205, 425)
    DISPLAYSURF.blit(w4_surf, w4_rect)


def draw_piece(piece, pixelx=None, pixely=None):
    shape_to_draw = PIECES[piece['shape']][piece['rotation']]
    if pixelx is None and pixely is None:
        # if pixelx & pixely hasn't been specified, use the location stored in the piece data structure
        pixelx, pixely = convert_to_pixel_coords(piece['x'], piece['y'])

    # draw each of the boxes that make up the piece
    for x in range(TEMPLATEWIDTH):
        for y in range(TEMPLATEHEIGHT):
            if shape_to_draw[y][x] != BLANK:
                draw_box(None, None, piece['color'], pixelx + (x * BOXSIZE), pixely + (y * BOXSIZE))


def draw_next_piece(piece):
    # draw the "next" text
    next_surf = BASICFONT.render('Następny:', True, TEXTCOLOR)
    next_rect = next_surf.get_rect()
    next_rect.topleft = (WINDOWWIDTH - 170, 75)
    DISPLAYSURF.blit(next_surf, next_rect)
    # draw the "next" piece
    draw_piece(piece, pixelx=WINDOWWIDTH - 170, pixely=100)


def simulate_board(test_board, test_piece, move, weights):
    # This function simulates placing the current falling piece onto the
    # board, specified by 'move,' an array with two elements, 'rot' and 'sideways'.
    # 'rot' gives the number of times the piece is to be rotated ranging in [0:3]
    # 'sideways' gives the horizontal movement from the piece's current position, in [-9:9]
    # It removes complete lines and gives returns the next board state as well as the number
    # of lines cleared.

    rot = move[0]
    sideways = move[1]
    test_lines_removed = 0
    if test_piece is None:
        return None, None

    # Rotate test_piece to match the desired move
    for i in range(0, rot):
        test_piece['rotation'] = (test_piece['rotation'] + 1) % len(PIECES[test_piece['shape']]) #oblicza ile razy trzeba obrocic

    # Test for move validity!
    if not is_valid_position(test_board, test_piece, adj_x=sideways, adj_y=0):
        # The move itself is not valid!
        return None, None

    # Move the test_piece to collide on the board
    test_piece['x'] += sideways
    for i in range(0, BOARDHEIGHT):
        if is_valid_position(test_board, test_piece, adj_x=0, adj_y=1):
            test_piece['y'] = i

    # Place the piece on the virtual board
    if is_valid_position(test_board, test_piece, adj_x=0, adj_y=0):
        add_to_board(test_board, test_piece)
        test_lines_removed, test_board = remove_complete_lines(test_board)

    wartosc_funkcji_decyzyjnej = funkcja_decyzyjna(test_board, test_lines_removed, weights)

    return test_board, wartosc_funkcji_decyzyjnej


def find_best_move(board, piece, weights):
    move_list = []
    score_list = []
    for rot in range(0, len(PIECES[piece['shape']])):
        for sideways in range(-5, 6):
            move = [rot, sideways]
            test_board = copy.deepcopy(board)
            test_piece = copy.deepcopy(piece)
            test_board, wynik = simulate_board(test_board, test_piece, move, weights)
            if test_board is not None:
                move_list.append(move)
                score_list.append(wynik)
    best_score = max(score_list)
    best_move = move_list[score_list.index(best_score)]

    return best_move


def make_move(move):
    # This function will make the indicated move, with the first digit
    # representing the number of rotations to be made and the seconds
    # representing the column to place the piece in.
    rot = move[0]
    sideways = move[1]
    if rot != 0:
        pyautogui.press('up')
        rot -= 1
    else:
        if sideways == 0:
            pyautogui.press('space')
        if sideways < 0:
            pyautogui.press('left')
            sideways += 1
        if sideways > 0:
            pyautogui.press('right')
            sideways -= 1

    return [rot, sideways]


def gradient_descent(board, piece, weights):
    move = find_best_move(board, piece, weights)
    test_board = copy.deepcopy(board)
    test_piece = copy.deepcopy(piece)
    simulate_board(test_board, test_piece, move, weights)

    return move, weights

########################################################################################################################
# Karol Perec
# czesc wywolawcza main oraz algorytmu genetycznego




def genetic(rozmiar_populacji, rozmiar_chromosomu, liczba_pokolen, prawdopodobienstwo_mutacji, ilosc_prob_fp,czas_stop):
    # funkcja algorytmu genetycznego z zadanym rozmiarem populacji, rozmiarem chromosomu=4, liczba pokolen
    # prawdopodobienstwem mutacji, iloscia prob przy obliczaniu funkcji decyzyjnej oraz gornym progiem
    # czasu dzialania algorytmu
    # komunikaty w konsoli systemowej, przebieg algorytmu zapisywany do pliku *.txt
    # wyrysowany wykres krzywej uczacej

    t = time.time()
    plik_baza_danych = open("baza_danych.txt", "w")

    populacja = inicjalizacja(rozmiar_populacji, rozmiar_chromosomu)
    baza_danych = [[0] * rozmiar_populacji for i in range(liczba_pokolen)]

    for i in range(0, liczba_pokolen):
        print("-----------------------------------")
        for j in range(0, rozmiar_populacji):
            wartosc_funkcji_przystosowania = 0
            for ilosc_prob in range(ilosc_prob_fp):
                wartosc_fp, chromosom = run_game(populacja[j], i+1, j+1, ilosc_prob+1)
                print("Próba nr", ilosc_prob + 1, "zbitych lini: ", wartosc_fp)
                wartosc_funkcji_przystosowania += wartosc_fp
            wartosc_funkcji_przystosowania=wartosc_funkcji_przystosowania/ilosc_prob_fp

            baza_danych[i][j] = [wartosc_funkcji_przystosowania, chromosom]
            plik_baza_danych.write("Pokolenie " + repr(i + 1) + " osobnik " +
                                   repr(j + 1) + " chromosom " + repr(chromosom) +
                                    " Fp: " + repr(wartosc_funkcji_przystosowania) + "\n")
            print("Pokolenie ", i+1, "osobnik", j+1, "chromosom ", chromosom, " Fp: ", wartosc_funkcji_przystosowania)
        wyselekcjonowane, odrzucone = selekcja(baza_danych[i], rozmiar_populacji)
        rodzice, dzieci = krzyzowanie(wyselekcjonowane)
        populacja = [rodzice[0][1]] + [rodzice[1][1]] + dzieci
        populacja = mutacja(populacja, prawdopodobienstwo_mutacji)
        populacja = sukcesja(populacja, rozmiar_chromosomu)

        if (time.time() - t) > czas_stop:
            print("CZAS UPLYNĄŁ")
            break

    plik_baza_danych.close()

    maxx = [0] * (i + 1)
    for k in range(0, i + 1):
        maxx[k] = max([col[0] for col in baza_danych[k]])
    plt.figure(1)
    plt.plot(numpy.arange(1, k + 2), maxx, 'k-')
    plt.xlabel('Pokolenie')
    plt.ylabel('Przystosowanie najlepszego chromosomu')
    plt.xlim(1, k + 1)
    plt.ylim(0, max(maxx) * 1.1)
    plt.show()


if __name__ == '__main__':
    # program glowny, pobranie danych od uzytkownika, ustawienie parametrow algorytmu i programu
    # wywolanie gry z uczacym algorytmem genetycznym

    global FPSCLOCK, DISPLAYSURF, BASICFONT, BIGFONT
    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    BASICFONT = pygame.font.Font('MyriadPro.otf', 18)
    BIGFONT = pygame.font.Font('MyriadPro.otf', 100)
    pygame.display.set_caption('Tetris')
    show_text_screen('Tetris')

    print("\n")
    rozmiar_populacji = 10
    rozmiar_chromosomu = 4
    ilosc_prob_fp = int(input("Ilość prób dla funkcji przystosowania (optymalnie: 4-5): "))
    prawdopodobienstwo_mutacji = float(input("Prawdopodobieństwo mutacji [0.0-1.0] (optymalnie: 0.1-0.2): "))
    liczba_pokolen = int(input("Maksymalna liczba pokoleń: "))
    czas_stop = int(input("Maksymalny czas działania algorytmu [s]: "))

    hwndMain = win32gui.FindWindow(None, "Tetris")
    pyautogui.press('alt')
    win32gui.SetForegroundWindow(hwndMain)
    genetic(rozmiar_populacji, rozmiar_chromosomu, liczba_pokolen, prawdopodobienstwo_mutacji, ilosc_prob_fp, czas_stop)  # ALGORYTM GENETYCZNY
