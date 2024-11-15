import os

ANSI = {
    "RESET": "\033[0m",     # Reset color
    "CLEARLINE": "\033[0K"  # Clear line
}

def print_location(x, y, text):
    '''
    ## Print text at specified location

    ### Args:
        - `x (int)`: x - coordinate
        - `y (_type_)`: y - coordinate
        - `text (_type_)`: The text to be printed
    '''
    print("\033[{1};{0}H{2}".format(y, x, text))


def clear_screen():
    '''
    ## Clear the terminal screen
    '''
    if os.name == "nt":  # for Windows
            os.system("cls")
    else:                # for Mac/Linux
        os.system("clear")


def move_cursor(x, y):
    '''
    ## Move cursor to specified location

    ### Args:
        - `x (int)`: x coordinate
        - `y (int)`: y coordinate
    '''
    print("\033[{1};{0}H".format(y, x), end='')

