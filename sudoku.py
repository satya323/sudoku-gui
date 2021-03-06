import argparse
import time
from tkinter import BitmapImage, Tk, Canvas, Frame, Button, BOTH, TOP, BOTTOM
from typing import Mapping

BOARDS = ['debug', 'n00b', 'l33t', 'error'] # available sudoku boards
MARGIN = 20 # pixels around the board
SIDE = 50 # width of every board cell
WIDTH = HEIGHT = MARGIN * 2 + SIDE * 9 # width and height of whole board

class SudokuError(Exception):
    """
    An application specific error
    """
    pass

class SudokuBoard(object):
    """
    Sudoku Board representation
    """
    def __init__(self, board_file):
        self.board = self.__create_board(board_file)

    # initialized board matrix using board file
    def __create_board(self, board_file):
        # create an initial matrix, or a list of lists
        board = []

        # iterate over each line
        for line in board_file:
            line = line.strip()

            # raise error if line is longer or shorter than 9 characters
            if len(line) != 9:
                board = []
                raise SudokuError(
                    "Each line in the sudoku puzzle must be 9 chars long."
                )
            
            # create a list for the line
            board.append([])

            # then iterate over each character
            for c in line:
                # raise an error if the character is not an integer
                if not c.isdigit():
                    raise SudokuError(
                        "Valid characters for a sudoku puzzle must be in 0-9"
                    )
                # Add to the latest list for the line
                board[-1].append(int(c))
            
        # raise an error if there are not 9 lines
        if len(board) != 9:
            raise SudokuError(
                "Each sudoku puzzle must be 9 lines long"
            )
        
        # return the constructed board
        return board

class SudokuGame(object):
    """
    A Sudoku game, in charge of storing the state of the board and checking
    whether the puzzle is completed
    """

    def __init__(self, board_file):
        self.board_file = board_file
        self.start_puzzle = SudokuBoard(board_file).board

    # initializes the game_over flag and creates a copy of the board
    def start(self):
        self.game_over = False
        self.puzzle = []
        for i in range(9):
            self.puzzle.append([])
            for j in range(9):
                self.puzzle[i].append(self.start_puzzle[i][j])

    # checks board's rows, columns and 3X3 squares for win
    def check_win(self):
        for row in range(9):
            if not self.__check_row(row):
                return False
        for column in range(9):
            if not self.__check_column(column):
                return False
        for row in range(3):
            for column in range(3):
                if not self.__check_square(row, column):
                    return False

        self.game_over = True
        return True

    # checks if elements of block are in range 1-9
    def __check_block(self, block):
        return set(block) == set(range(1, 10));

    # checks if a row is valid
    def __check_row(self, row):
        return self.__check_block(self.puzzle[row])

    # checks if a column is valid
    def __check_column(self, column):
        return self.__check_block(
            [self.puzzle[row][column] for row in range(9)]
        )

    # checks if a 3X3 block is valid
    def __check_square(self, row, column):
        return self.__check_block(
            [
                self.puzzle[r][c]
                for r in range(row*3, (row+1)*3)
                for c in range(column*3, (column+1)*3)
            ]
        )

class SudokuUI(Frame):
    """
    The Tkinter UI, responsible for drawing the board and accepting user input.
    """

    def __init__(self, parent, game):
        self.game = game
        self.parent = parent
        Frame.__init__(self, parent)

        self.row, self.col = 0, 0
        self.__initUI()

    # sets up the UI
    def __initUI(self):
        self.parent.title("Sudoku")
        self.pack(fill=BOTH, expand=1)
        self.canvas = Canvas(self, width=WIDTH, height=HEIGHT)
        self.canvas.pack(fill=BOTH, side=TOP)
        clear_button = Button(self, text="Clear answers", highlightbackground='#3E4149', command=self.__clear_answers)
        clear_button.pack(fill=BOTH, side=TOP)
        solve_button = Button(self, text="Solve", highlightbackground='#3E4149', command=self.__solve)
        solve_button.pack(fill=BOTH, side=BOTTOM)

        self.__draw_grid()
        self.__draw_puzzle()

        self.canvas.bind("<Button-1>", self.__cell_clicked)
        self.canvas.bind("<Key>", self.__key_pressed)

    def __draw_grid(self):
        """
        Draws grid divided with blue lines into 3X3 squares
        """

        for i in range(10):
            color = "blue" if i%3 == 0 else "gray"

            x0 = MARGIN+i*SIDE
            y0 = MARGIN
            x1 = MARGIN+i*SIDE
            y1 = HEIGHT-MARGIN
            self.canvas.create_line(x0, y0, x1, y1, fill=color)

            x0 = MARGIN
            y0 = MARGIN+i*SIDE
            x1 = WIDTH-MARGIN
            y1 = MARGIN+i*SIDE
            self.canvas.create_line(x0, y0, x1, y1, fill=color)

    def __draw_puzzle(self):
        self.canvas.delete("numbers")
        for i in range(9):
            for j in range(9):
                answer = self.game.puzzle[i][j]
                if answer != 0:
                    x = MARGIN+j*SIDE + SIDE/2
                    y = MARGIN+i*SIDE + SIDE/2
                    original = self.game.start_puzzle[i][j]
                    color = "black" if answer == original else "sea green"
                    self.canvas.create_text(
                        x, y, text = answer, tags="numbers", fill=color
                    )

    def __clear_answers(self):
        self.game.start()
        self.canvas.delete("victory")
        self.__draw_puzzle()

    # uses backtracking to solve the puzzle from a given position
    def __solve(self):
        self.__draw_puzzle
        find = self.__find_empty()
        if not find:
            return True
        else:
            row, col = find

        for i in range(1, 10):
            if self.__valid(i, (row, col)):
                self.game.puzzle[row][col] = i
                self.__draw_puzzle()
                if self.__solve():
                    return True

                self.game.puzzle[row][col] = 0

        return False

    def __cell_clicked(self, event):
        if self.game.game_over:
            return
        
        x, y = event.x, event.y
        if (MARGIN < x < WIDTH-MARGIN and MARGIN < y < HEIGHT-MARGIN):
            self.canvas.focus_set()

            # get row and col numbers from x,y coordinates
            row, col = int((y-MARGIN)/SIDE), int((x-MARGIN)/SIDE)

            if (row, col) == (self.row, self.col):
                self.row, self.col = -1, -1
            elif self.game.puzzle[row][col] == 0:
                self.row, self.col = row, col
        else:
            self.row, self.col = -1, -1
        
        self.__draw_cursor()

    def __draw_cursor(self):
        self.canvas.delete("cursor")
        if self.row >= 0 and self.col >= 0:
            x0 = MARGIN + self.col*SIDE+1
            y0 = MARGIN + self.row*SIDE+1
            x1 = MARGIN + (self.col+1)*SIDE-1
            y1 = MARGIN + (self.row+1)*SIDE-1
            self.canvas.create_rectangle(
                x0, y0, x1, y1,
                outline="red", tags="cursor"
            )

    def __key_pressed(self, event):
        if self.game.game_over:
            return
        
        if self.row >= 0 and self.col >= 0 and event.char in "1234567890":
            self.game.puzzle[self.row][self.col] = int(event.char)
            self.col, self.row = -1, -1
            self.__draw_puzzle()
            self.__draw_cursor()
            if self.game.check_win():
                self.__draw_victory()

    def __draw_victory(self):
        x0 = y0 = MARGIN + SIDE*2
        x1 = y1 = MARGIN + SIDE*7
        self.canvas.create_oval(
            x0, y0, x1, y1,
            tags="victory", fill="dark orange", outline="orange"
        )

        x = y = MARGIN + 4*SIDE + SIDE/2
        self.canvas.create_text(
            x, y,
            text="You win!", tags="winner",
            fill="white", font=("Arial", 32)
        )

    def __find_empty(self):
        for i in range(9):
            for j in range(9):
                if self.game.puzzle[i][j] == 0:
                    return (i, j)

        return None

    def __valid(self, num, pos):
        for i in range(9):
            if self.game.puzzle[pos[0]][i] == num and pos[1] != i:
                return False

        for i in range(9):
            if self.game.puzzle[i][pos[1]] == num and pos[0] != i:
                return False

        box_x = pos[1] // 3
        box_y = pos[0] // 3

        for i in range(box_y*3, box_y*3+3):
            for j in range(box_x*3, box_x*3+3):
                if self.game.puzzle[i][j] == num and (i, j) != pos:
                    return False

        return True

def parse_arguments():
    """
    Parses arguments of the form:
        sudoku.py <board name>
    Where `board name` must be in the `BOARD` list
    """
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("--board",
                            help="Desired board name",
                            type=str,
                            choices=BOARDS,
                            required=True)
    
    args = vars(arg_parser.parse_args())
    return args['board']

if __name__ == '__main__':
    board_name = parse_arguments()

    with open('%s.sudoku' % board_name, 'r') as boards_file:
        game = SudokuGame(boards_file)
        game.start()

        root = Tk()
        SudokuUI(root, game)
        root.geometry("%dx%d" % (WIDTH, HEIGHT+60))
        root.mainloop()
