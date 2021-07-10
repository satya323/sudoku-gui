import argparse
from tkinter import Tk, Canvas, Frame, Button, BOTH, TOP, BOTTOM

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

    # initialize the game_over flag and creates a copy of the board
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
