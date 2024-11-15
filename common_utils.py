import os
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


def system_functions():
    clear_screen()
    print_location(1, 0, '*** SYSTEM FUNCTIONALITIES ***')
    print_location(3, 0, '1. Search for tweets')
    print_location(4, 0, '2. Search for users')
    print_location(5, 0, '3. Compose a tweet')
    print_location(6, 0, '4. List followers')
    print_location(7, 0, '5. Logout')
    user_input = input("")

    if user_input == '1' or user_input == '1.':
        # search for tweets function to be added by luke
        pass
    elif user_input == '2' or user_input == '2.':
        # search for users to be added by anant
        pass
    elif user_input == '3' or user_input == '3.':
        # compose a tweet function to be added by gurbaaz
        pass
    elif user_input == '4' or user_input == '4.':
        # list followers to be added by yuheng
        pass
    elif user_input == '5' or user_input == '5.':
        # logout function to be added
        pass

    return