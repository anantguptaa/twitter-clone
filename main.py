import os
import sys
import sqlite3

CONN = None
CURSOR = None

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

def connect(path):
    global connection, cursor

    connection = sqlite3.connect(path)
    cursor = connection.cursor()
    cursor.execute(' PRAGMA foreign_keys=ON; ')
    connection.commit()
    return

def main():
    global CURSOR, CONN
    
    path = "./" + sys.argv[1]
    connect(path)
    
    os.system("")  # Clear console

    clear_screen()  # Clear the screen
    print_location(1, 0,'*** MINI PROJECT 1 ***')    # Print game heading

if __name__ == "__main__":
    main()