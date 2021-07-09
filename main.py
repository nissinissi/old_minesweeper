#credit to Gangetsha Lyx for the font Mine-Sweeper and to Sizenko Alexander for digit-7-mono

'''
MINESWEEPER by Lael Israel

character keys:
'-' unopened cell
'0' a cell with no bombs around it
'1' a cell with a single bomb aroud it
...
'8' a cell that is surrounded by 8 bombs
'x' a mine
'+' a flag
'w' a cell without a bomb that has been flagged
'r' the bomb(s) that were opened and caused the player to lose
the rest of the signs are used in load_grid to show the edge of the screen
'''

# Imports
import math
import pygame
import random
import time

# Constants
HAVE_FONTS = False     # set this to True if you have the .ttf files!

REFRESH_RATE    = 60
CELL_SIZE       = 34 # The size of each cell in pixels
TEXT_SPACE      = 100 # The space dedicated to the timer and the bombs left at the top
IMG_DICT = {'0':'images/open0.png','1':'images/open1.png','2':'images/open2.png','3':'images/open3.png',
            '4':'images/open4.png','5':'images/open5.png','6':'images/open6.png','7':'images/open7.png',
            '8':'images/open8.png','x':'images/mine.png','+':'images/flag.png','w':'images/wrongflag.png',
            'r':'images/red_mine.png','-':'images/unopened.png','eo':'images/edge_open.png',
            'eu':'images/edge_unopened.png','er':'images/edge_red_mine.png','bo':'images/bottom_open.png',
            'bu':'images/bottom_unopened.png', 'br':'images/bottom_red_mine.png'}

LEFT_CLICK      = 1
MIDDLE_CLICK    = 2
RIGHT_CLICK     = 3

WHITE       = (255, 255, 255)
BRIGHT_GREY = (100, 100, 100)
DARK_GREY   = (20 , 20 , 20 )
BLACK       = (0  , 0  , 0  )
RED         = (255, 0  , 0  )
GREEN       = (0  , 255, 0  )
DARK_GREEN  = (0  , 60 , 0  )
DARK_BLUE   = (20 , 50 , 120)

# Functions
def main():
    ''' The main function of Minesweeper.py. '''
    
    pygame.init()
    pygame.font.init()
    clock = pygame.time.Clock()

    if HAVE_FONTS:
        font1_16 = pygame.font.SysFont('MINE-SWEEPER Regular', 16)
        font2_50 = pygame.font.SysFont('Digital-7 Mono', 50)
    else:
        font1_16 = pygame.font.SysFont('Courier New', 16)
        font2_50 = pygame.font.SysFont('Consolas', 50)

    img_loaded = dict()
    for cell in IMG_DICT.keys():
        img_loaded[cell] = pygame.image.load(IMG_DICT[cell])
    
    # Screen setup - done with input form the console/shell.
    print '\nEnter difficulty:\n1 - beginner\n2 - intermediate\n3 - expert\n0 - custom\n'
    difficulty = input()
    while not type(difficulty) is int:
        difficulty = input('Difficulty must be an integer.\nPlease try again:\n')
    if difficulty == 1:
        grid_width = 9
        grid_height = 9
        bomb_amount = 10
    elif difficulty == 2:
        grid_width = 16
        grid_height = 16
        bomb_amount = 40
    elif difficulty == 3:
        grid_width = 30
        grid_height = 16
        bomb_amount = 99
    else:
        grid_width = input('Enter the board\'s width:\n')
        while not type(grid_width) is int:
            grid_width = input('The board\'s width must be an integer.\nPlease try again:\n')
        if grid_width < 9:
            grid_width = 9
        grid_height = input('Enter the board\'s height:\n')
        while not type(grid_height) is int:
            grid_height = input('The board\'s height must be an integer.\nPlease try again:\n')
        if grid_height <= 0:
            grid_height = 1
        bomb_amount = input('Enter the amount of bombs:\n')
        while not type(bomb_amount) is int:
            grid_height = input('The amount of bombs must be an integer.\nPlease try again:\n')
        if bomb_amount < 0:
            bomb_amount = 0
        elif bomb_amount > grid_width*grid_height - 9:
            bomb_amount = grid_width*grid_height - 9

    bombs_left = bomb_amount
    grid = [['-' for i in range(grid_width)] for j in range(grid_height)]

    # Game screen initialization
    screen = pygame.display.set_mode((CELL_SIZE*grid_width + 3, CELL_SIZE*grid_height + TEXT_SPACE + 3))
    pygame.display.set_caption('Minesweeper')
    load_grid(screen, grid, bombs_left, img_loaded, font1_16, font2_50)
    pygame.display.flip()
    
    # The main loop
    lost = False
    won = False
    first = True
    mils = 0
    screen.fill(BRIGHT_GREY)
    while True:
        # Timer
        clock.tick(REFRESH_RATE)
        if mils % 30 == 0:
            load_timer(screen, mils / 30, grid_width, font2_50)
        mils+=1

        # Event loop
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # 'x' button
                pygame.display.quit()
                pygame.quit()
                print '\nThe game was closed.'
                option = raw_input('Would you like to start a new game? (enter y/n):\n')
                if option[0] == 'y':
                    return True
                else:
                    print 'Have a nice day!'
                    return False

            elif event.type == pygame.MOUSEBUTTONUP and event.button == LEFT_CLICK:
                # left click
                mouse_pos = pygame.mouse.get_pos()
                if mouse_pos[1] > TEXT_SPACE:
                    # the user clicked on a cell
                    cell_x = mouse_pos[0] / CELL_SIZE
                    cell_y = (mouse_pos[1] - TEXT_SPACE) / CELL_SIZE

                    if grid[cell_y][cell_x] == '+': # the user clicked on a flag
                        (bombs_left, grid) = flag_cell(cell_x, cell_y, grid, bombs_left)

                    elif first: # the first cell opened must be 0: the bombs are generated after it's clicked
                        first = False
                        bombs = plant_bombs(cell_x, cell_y, len(grid[0]), len(grid), bomb_amount)
                        grid = open_cell(cell_x, cell_y, grid, bombs)

                    elif (cell_x, cell_y) in bombs:
                        lost = True
                        grid[cell_y][cell_x] = 'r'

                    elif grid[cell_y][cell_x] == '-':
                        grid = open_cell(cell_x, cell_y, grid, bombs)

            elif event.type == pygame.MOUSEBUTTONUP and event.button == RIGHT_CLICK:
                # right click
                mouse_pos = pygame.mouse.get_pos()
                if mouse_pos[1] > TEXT_SPACE:
                    # the user clicked on a cell
                    cell_x = mouse_pos[0] / CELL_SIZE
                    cell_y = (mouse_pos[1] - TEXT_SPACE) / CELL_SIZE
                    if not grid[cell_y][cell_x].isdigit():
                        bombs_left, grid = flag_cell(cell_x, cell_y, grid, bombs_left)

            elif event.type == pygame.MOUSEBUTTONUP and event.button == MIDDLE_CLICK:
                # middle click
                mouse_pos = pygame.mouse.get_pos()
                if mouse_pos[1] > TEXT_SPACE:
                    # the user clicked on a cell
                    cell_x = mouse_pos[0] / CELL_SIZE
                    cell_y = (mouse_pos[1] - TEXT_SPACE) / CELL_SIZE

                    if grid[cell_y][cell_x].isdigit():
                        if mid_click(cell_x, cell_y, grid, bombs): # the player has lost
                            lost = True

            if not first and lost:
                # the player has lost
                grid_lost(grid, bombs)
                load_grid(screen, grid, bombs_left, img_loaded, font1_16, font2_50)
                quit = False
                while not quit: # the player sees the changed grid until he chooses to exit
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            quit = True
                pygame.display.quit()
                pygame.quit()
                print 'You lost :('
                option = raw_input('Would you like to start a new game? (enter y/n):\n')
                if option[0] == 'y':
                    return True
                else:
                    print 'Have a nice day!'
                    return False

            if not first and has_won(grid, bombs):
                # the player has won
                grid = grid_won(grid, bombs)
                load_grid(screen, grid, bombs_left, img_loaded, font1_16, font2_50)
                pygame.display.flip()
                quit = False
                while not quit: # the player sees the changed grid until he chooses to exit
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            quit = True
                pygame.display.quit()
                pygame.quit()
                print '\nYou win!'
                option = raw_input('Would you like to start a new game? (enter y/n):\n')
                if option[0] == 'y':
                    return True
                else:
                    print 'Have a nice day!'
                    return False

            load_grid(screen, grid, bombs_left, img_loaded, font1_16, font2_50)


def flag_cell(cell_x, cell_y, grid, bombs_left):
    ''' Flags/un-flags a cell. '''

    if bombs_left == 0: # there are supposedly no bombs left for the user to find - nothing to flag
        return 0, grid
    if grid[cell_y][cell_x] == '+': # the cell's already flagged
        grid[cell_y][cell_x] = '-'
        bombs_left += 1
    else: # the cell isn't flagged yet
        grid[cell_y][cell_x] = '+'
        bombs_left -= 1
    return bombs_left, grid


def grid_lost(grid, bombs):
    ''' Changes the grid after the player lost. '''

    for y in range(len(grid)):
        for x in range(len(grid[0])):
            if (x, y) in bombs:
                if grid[y][x] == '-':
                    grid[y][x] = 'x' # open all the bombs that haven't been flagged
            else:
                if grid[y][x] == '+':
                    grid[y][x] = 'w' # show all the wrong flags
    return


def grid_won(grid, bombs):
    ''' Changes the grid after the player won. '''

    for (x, y) in bombs:
        if grid[y][x] == '-':
            grid[y][x] = '+' # flag all the bombs that aren't already flagged

    return grid


def has_won(grid, bombs):
    ''' Checks if the player has won - all the cells that aren't bombs have been opened. '''

    for y in range(len(grid)):
        for x in range(len(grid[0])):
            if (not (x,y) in bombs) and (not grid[y][x].isdigit()):
                return False # a cell that isn't a bomb hasn't been opened

    return True


def load_grid(screen, grid, bombs_left, img_loaded, font1_16, font2_50):
    ''' Loads the grid on screen. '''

    text_surface = font1_16.render('*', True, DARK_GREY) # bomb in the top middle
    text_box = text_surface.get_rect()
    text_box.center = ((len(grid[0]) * CELL_SIZE + 3) / 2 + 2, TEXT_SPACE / 2 + 2)
    screen.blit(text_surface, text_box)
    text_surface = font1_16.render('*', True, WHITE)
    text_box = text_surface.get_rect()
    text_box.center = ((len(grid[0]) * CELL_SIZE + 3) / 2, TEXT_SPACE / 2)
    screen.blit(text_surface, text_box)

    pygame.draw.rect(screen, BLACK, (5, TEXT_SPACE/2 - 25, 78, 50))
    text_surface = font2_50.render('888', True, DARK_GREEN)
    text_box = text_surface.get_rect()
    text_box.center = (45, TEXT_SPACE / 2)
    screen.blit(text_surface, text_box) # a backshadow for the counter
    if bombs_left == 0:
        text_surface = font2_50.render('0'*3, True, GREEN)
    else:
        text_surface = font2_50.render('0'*int(3-math.log(bombs_left+1,10)) + str(bombs_left), True, GREEN)
    screen.blit(text_surface, text_box) # the counter

    for y in range(len(grid) - 1):
        for x in range(len(grid[0])):
            screen.blit(img_loaded[grid[y][x]], (x*CELL_SIZE, TEXT_SPACE + y*CELL_SIZE)) # show the current cell
        # V the borders have to be printed at the right edge of the screen V
        if grid[y][len(grid[0])-1] == '-' or grid[y][len(grid[0])-1] == '+': # unopened or flag
            screen.blit(img_loaded['eu'], ((len(grid[0]))*CELL_SIZE, TEXT_SPACE + y*CELL_SIZE))
        if grid[y][len(grid[0])-1] == 'r': # red mine
            screen.blit(img_loaded['er'], ((len(grid[0]))*CELL_SIZE, TEXT_SPACE + y*CELL_SIZE))
        else: # anything else
            screen.blit(img_loaded['eo'], ((len(grid[0]))*CELL_SIZE, TEXT_SPACE + y*CELL_SIZE))

    for x in range(len(grid[0])):
        # V the borders have to be printed at the buttom of the screen
        screen.blit(img_loaded[grid[len(grid)-1][x]], (x*CELL_SIZE, TEXT_SPACE + (len(grid)-1)*CELL_SIZE))
        if grid[len(grid)-1][x] == '-' or grid[len(grid)-1][x] == '+':
            screen.blit(img_loaded['bu'], (x*CELL_SIZE, TEXT_SPACE + (len(grid))*CELL_SIZE))
        elif grid[len(grid)-1][x] == 'r':
            screen.blit(img_loaded['br'], (x*CELL_SIZE, TEXT_SPACE + (len(grid))*CELL_SIZE))
        else:
            screen.blit(img_loaded['bo'], (x*CELL_SIZE, TEXT_SPACE + (len(grid))*CELL_SIZE))

    pygame.display.flip()
    return


def load_timer(screen, secs, grid_width, font2_50):
    ''' Displays the timer on the screen. The maximal time that can be shown is 99:59. '''

    if secs > 5999:
        return
    time = ''
    if secs / 60 == 0: # minutes
        time += '00:'
    else:
        time += '0'*int(2-math.log(secs/60+1,10)) + str(secs/60) + ':'
    if secs % 60 == 0: # seconds
        time += '00'
    else:
        time += '0'*int(2-math.log(secs%60+1,10)) + str(secs%60)
    pygame.draw.rect(screen, BLACK, (grid_width*CELL_SIZE-135, TEXT_SPACE/2 - 25, 130, 50))
    text_surface = font2_50.render('88:88', True, DARK_GREEN)
    text_box = text_surface.get_rect()
    text_box.center = (grid_width*CELL_SIZE - 70, TEXT_SPACE / 2)
    screen.blit(text_surface, text_box) # backdrop for the clock
    text_surface = font2_50.render(time, True, GREEN)
    screen.blit(text_surface, text_box) # the clock
    pygame.display.flip()
    return


def mid_click(cell_x, cell_y, grid, bombs):
    ''' Checks if the correct amount of flags are around (cell_x,cell_y).
    If so, opens all the cells that aren't flagged around it. '''

    free_cells = set([]) # the cells that should be opened
    flag_amount = 0
    lost = False
    for (x,y) in surrounding_cells(cell_x, cell_y, len(grid[0]), len(grid)):
        if grid[y][x] == '-':
            free_cells.add((x,y))
        if grid[y][x] == '+':
            flag_amount += 1
    if flag_amount != near_bombs(cell_x, cell_y, len(grid[0]), len(grid), bombs):
        return lost # the correct amount of flags must be around (cell_x,cell_y)
    for (x,y) in free_cells:
        if (x,y) in bombs: # a bomb has been opened
            grid[y][x] = 'r' # the bomb that was clicked is red
            lost = True
        else:
            open_cell(x, y, grid, bombs)

    return lost


def near_bombs(cell_x, cell_y, grid_width, grid_height, bombs):
    ''' Returns the amount of bombs surrounding (cell_x,cell_y). '''

    count = 0
    for cell in surrounding_cells(cell_x, cell_y, grid_width, grid_height):
        if cell in bombs:
            count += 1

    return count


def open_cell(cell_x, cell_y, grid, bombs):
    ''' Opens (cell_x,cell_y), assumes it's valid & not a bomb. If the cell is 0:
    Automatically opens all the cells surrounding it until reaches a non-zero cell in all directions.'''

    grid[cell_y][cell_x] = str(near_bombs(cell_x, cell_y, len(grid[0]), len(grid), bombs)) # open the cell
    if grid[cell_y][cell_x] == '0': # the cell is 0 - open all the cells around it
        current_value = 0
        for (x,y) in surrounding_cells(cell_x, cell_y, len(grid[0]), len(grid)):
            if grid[y][x] == '-' or grid[y][x] == '+':
                current_value = near_bombs(x, y, len(grid[0]), len(grid), bombs)
                if current_value == 0: # the cell is 0 - it needs to be opened
                    grid = open_cell(x, y, grid, bombs)
                else:
                    grid[y][x] = str(current_value) # Open the (x,y). It can't be a bomb since (cell_x,cell_y)=0
    return grid


def plant_bombs(first_x, first_y, grid_width, grid_height, bomb_amount):
    ''' Plants bombs so that the first cell opened is 0. '''

    bombs_planted = set([]) # the bombs that have been planted so far
    bomb_x = random.randint(0, grid_width-1)
    bomb_y = random.randint(0, grid_height-1)
    for i in range(bomb_amount):
        while not valid_bomb(first_x, first_y, bomb_x, bomb_y, grid_width, grid_height, bombs_planted):
            # if the bomb is invalid, find another random bomb
            bomb_x = random.randint(0, grid_width-1)
            bomb_y = random.randint(0, grid_height-1)
        bombs_planted.add((bomb_x, bomb_y))
    return bombs_planted


def surrounding_cells(cell_x, cell_y, grid_width, grid_height):
    ''' Returns a set of all the cells that surround (cell_x,cell_y). '''

    cells = set([]) # the cells that surround (cell_x,cell_y)
    if cell_x-1 >= 0 and cell_y-1 >= 0:
        cells.add((cell_x-1,cell_y-1))
    if cell_x-1 >= 0:
        cells.add((cell_x-1,cell_y))
    if cell_x-1 >= 0 and cell_y+1 < grid_height:
        cells.add((cell_x-1,cell_y+1))
    if cell_y-1 >= 0:
        cells.add((cell_x,cell_y-1))
    if cell_y+1 < grid_height:
        cells.add((cell_x,cell_y+1))
    if cell_x+1 < grid_width and cell_y-1 >= 0:
        cells.add((cell_x+1,cell_y-1))
    if cell_x+1 < grid_width:
        cells.add((cell_x+1,cell_y))
    if cell_x+1 < grid_width and cell_y+1 < grid_height:
        cells.add((cell_x+1,cell_y+1))

    return cells


def valid_bomb(first_x, first_y, bomb_x, bomb_y, grid_width, grid_height, bombs):
    ''' Returns whether or not planting a bomb in (bomb_x, bomb_y) is valid. '''

    if bomb_x == first_x and bomb_y == first_y:
        return False #The first cell has to be 0
    if (bomb_x, bomb_y) in bombs:
        return False #There can't be 2 bombs in the same place
    if near_bombs(first_x, first_y, grid_width, grid_height, {(bomb_x,bomb_y)}) == 1:
        return False #The first cell has to be 0

    return True


# Main function check. This has to be at the end of the code
if __name__ == '__main__':
    while main(): # main() returns True if the player wants to play again
        pass
    exit() # main() returned False - the player wants to end the game
