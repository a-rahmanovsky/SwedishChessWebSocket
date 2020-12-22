bigfigs = ['l', 'k', 's', 'r', 'f']
dirD = {'l': [(1, 0, 8), (-1, 0, 8), (0, 1, 8), (0, -1, 8)],
        's': [(1, 1, 8), (-1, 1, 8), (-1, -1, 8), (1, -1, 8)],
        'k': [(2, 1, 1), (-2, 1, 1), (2, -1, 1), (-2, -1, 1),
              (1, 2, 1), (-1, 2, 1), (1, -2, 1), (-1, -2, 1)],
        'r': [(1, 0, 1), (-1, 0, 1), (0, 1, 1), (0, -1, 1),
              (1, 1, 1), (-1, 1, 1), (-1, -1, 1), (1, -1, 1)],
        'f': [(1, 0, 8), (-1, 0, 8), (0, 1, 8), (0, -1, 8),
              (1, 1, 8), (-1, 1, 8), (-1, -1, 8), (1, -1, 8)]}
D = {'w': 0, 'b': 1}


# ! - шах
# ? - инвалидный ход

class Cell:
    def __init__(self, figure='.', color='.'):
        self.figure = figure
        self.color = color


class Board:
    def __init__(self):
        self.field = [[Cell() for j in range(8)] for i in range(8)]
        self.r_moved = {'w': False, 'b': False}
        self.l_moved = {'w0': False, 'w7': False, 'b0': False, 'b7': False}
        self.turn = 'w'

    def __getitem__(self, i):
        return self.field[i]

    def __setitem__(self, i, a):
        self.field[i] = a

    def start(self):
        fig_set = ['l', 'k', 's', 'f', 'r', 's', 'k', 'l']
        self[0] = [Cell(fig_set[i], 'w') for i in range(8)]
        self[1] = [Cell('p', 'w') for i in range(8)]
        self[6] = [Cell('p', 'b') for i in range(8)]
        self[7] = [Cell(fig_set[i], 'b') for i in range(8)]

    def display(self):
        for i in range(7, -1, -1):
            for j in range(8):
                print(self[i][j].color, self[i][j].figure, sep='', end=' ')
            print()

    def moves(self, s_x, s_y):
        moves = []
        Cell = self[s_x][s_y]
        if Cell.figure in bigfigs:
            D = dirD[Cell.figure]
            for d in D:
                x, y = s_x, s_y
                dx, dy, r = d
                i, tag = 0, True
                while i < r and tag:
                    x, y = x + dx, y + dy
                    if x not in range(8) or y not in range(8):
                        tag = False
                    elif self[x][y].figure == '.':
                        moves.append((x, y))
                    elif self[x][y].color == Cell.color:
                        tag = False
                    elif self[x][y].figure == 'r':
                        tag = False
                    else:
                        moves.append((x, y))
                        tag = False
                    i += 1

        elif Cell.figure == 'p':
            dP = {'w': 1, 'b': -1}
            dx = dP[Cell.color]

            f_front = self[s_x + dx][s_y]
            if f_front.color == '.':
                moves.append((s_x + dx, s_y))

            if s_y < 7:
                right_front = self[s_x + dx][s_y + 1]
                if right_front.color not in ['.', Cell.color] and right_front.figure != 'r':
                    moves.append((s_x + dx, s_y + 1))
            if s_y > 0:
                left_front = self[s_x + dx][s_y - 1]
                if left_front.color not in ['.', Cell.color] and left_front.figure != 'r':
                    moves.append((s_x + dx, s_y - 1))

            sP = {'w': 1, 'b': 6}
            if s_x == sP[Cell.color]:
                ff_front = self[s_x + 2 * dx][s_y]
                if (f_front.color, ff_front.color) == ('.', '.'):
                    moves.append((s_x + 2 * dx, s_y))

        return moves

    def attacks_royal(self, s_x, s_y):
        Cell = self[s_x][s_y]
        if Cell.figure in bigfigs:
            D = dirD[Cell.figure]
            for d in D:
                x, y = s_x, s_y
                dx, dy, r = d
                i, tag = 0, True
                while i < r and tag:
                    x, y = x + dx, y + dy
                    if x not in range(8) or y not in range(8):
                        tag = False
                    elif self[x][y].color == Cell.color:
                        tag = False
                    elif self[x][y].figure == 'r':
                        return True
                    elif self[x][y].figure != '.':
                        tag = False
                    i += 1
            return False

        elif Cell.figure == 'p':
            dP = {'w': 1, 'b': -1}
            dx = dP[Cell.color]

            if s_y < 7:
                right_front = self[s_x + dx][s_y + 1]
                if right_front.color not in ['.', Cell.color] and right_front.figure == 'r':
                    return True
            if s_y > 0:
                left_front = self[s_x + dx][s_y - 1]
                if left_front.color not in ['.', Cell.color] and left_front.figure == 'r':
                    return True
            return False

    def attacks_cell(self, s_x, s_y, target_x, target_y):
        Cell = self[s_x][s_y]
        if Cell.figure in bigfigs:
            D = dirD[Cell.figure]
            for d in D:
                x, y = s_x, s_y
                dx, dy, r = d
                i, tag = 0, True
                while i < r and tag:
                    x, y = x + dx, y + dy
                    if x not in range(8) or y not in range(8):
                        tag = False
                    elif self[x][y].color == Cell.color:
                        tag = False
                    elif self[x][y].figure != '.':
                        tag = False
                    elif x == target_x and y == target_y:
                        return True
                    i += 1
            return False

        elif Cell.figure == 'p':
            dP = {'w': 1, 'b': -1}
            dx = dP[Cell.color]

            if s_y < 7:
                right_front = self[s_x + dx][s_y + 1]
                if right_front.color not in ['.', Cell.color] and right_front.figure == 'r':
                    return True
            if s_y > 0:
                left_front = self[s_x + dx][s_y - 1]
                if left_front.color not in ['.', Cell.color] and left_front.figure == 'r':
                    return True
            return False

    def check(self, color):
        for i in range(8):
            for j in range(8):
                if self[i][j].color not in ['.', color]:
                    if self.attacks_royal(i, j):
                        return True
        return False

    def checkmate(self, color):
        for start_x in range(8):
            for start_y in range(8):
                if self[start_x][start_y].color == color:
                    M = self.moves(start_x, start_y)
                    for m in M:
                        end_x, end_y = m
                        nextBoard = Board()
                        nextBoard.field = [[self[i][j] for j in range(8)] for i in range(8)]

                        nextBoard[end_x][end_y] = Cell(nextBoard[start_x][start_y].figure, color)
                        nextBoard[start_x][start_y] = Cell()
                        if not nextBoard.check(color):
                            del nextBoard
                            return False
                elif self[start_x][start_y].color == '.':
                    nextBoard = Board()
                    nextBoard.field = [[self[i][j] for j in range(8)] for i in range(8)]

                    nextBoard[start_x][start_y] = Cell('f', color)
                    if not nextBoard.check(color):
                        del nextBoard
                        return 'Must place a figure'
        return True

    def castling(self, color, direction):
        if color != self.turn:
            return 'Not Your Turn'
        castD = {'w': 0, 'b': 7}
        castF = {'l': (0, 5, 0), 'r': (4, 8, 7)}

        x = castD[color]
        a, b, rook = castF[direction]
        print(f'l_moved {self.l_moved}')
        if self.r_moved[color] or self.l_moved[color + str(rook)]:
            return '!'

        for y in range(a + 1, b - 1):
            if self[x][y].figure != '.':
                return '!'

        for i in range(8):
            for j in range(8):
                if self[i][j].color not in ['.', color]:
                    if self.attacks_royal(i, j):
                        return '!'
                    for y in range(a, b):
                        if self.attacks_cell(i, j, x, y):
                            return '!'

        self[x][4], self[x][rook] = Cell(), Cell()
        if direction == 'l':
            self[x][2] = Cell('r', color)
            self[x][3] = Cell('l', color)
        elif direction == 'r':
            self[x][6] = Cell('r', color)
            self[x][5] = Cell('l', color)

        self.r_moved[color] = True
        tempD = {'w': 'b', 'b': 'w'}
        self.turn = tempD[color]
        return '.'


class Game:
    def __init__(self, n=2):
        self.Boards = [Board() for i in range(n)]
        for i in range(n):
            self.Boards[i].start()

    def move(self, index, start, end):
        start_x, start_y = (int(start[1]) - 1, ord(start[0]) - ord('a'))
        end_x, end_y = (int(end[1]) - 1, ord(end[0]) - ord('a'))

        currBoard = self.Boards[index]
        if currBoard[start_x][start_y].color != currBoard.turn:
            return 'Not Your Turn'

        M = currBoard.moves(start_x, start_y)

        if (end_x, end_y) in M:
            temp_fig = currBoard[end_x][end_y].figure
            curr_fig = currBoard[start_x][start_y].figure
            curr_col = currBoard[start_x][start_y].color

            nextBoard = Board()
            nextBoard.field = [[currBoard[i][j] for j in range(8)] for i in range(8)]
            nextBoard.r_moved, nextBoard.l_moved = currBoard.r_moved, currBoard.l_moved

            nextBoard[end_x][end_y] = Cell(curr_fig, curr_col)
            nextBoard[start_x][start_y] = Cell()
            print('in (end_x, end_y)', curr_fig)
            if curr_fig == 'r':
                nextBoard.r_moved[curr_col] = True
            if curr_fig == 'l' and start_y in [0, 7]:
                print('in curr_fig')
                print(nextBoard.l_moved)
                nextBoard.l_moved[curr_col + str(start_y)] = True
            print('after if', currBoard.l_moved, nextBoard.l_moved)
            if nextBoard.check(curr_col):
                del nextBoard
                return '?'

            self.Boards[index] = nextBoard
            del currBoard

            tempD = {'w': 'b', 'b': 'w'}
            self.Boards[index].turn = tempD[curr_col]
            self.Boards[index].display()
            endD = {'w' : 7, 'b' : 0}
            print('pawn_wire', curr_fig, end_x, endD[curr_col])
            if curr_fig == 'p' and end_x == endD[curr_col]:
                return '+'
            return temp_fig
        return '!'

    def get_color(self, index):
        return self.Boards[index].turn

    def add_figure(self, index, position, asg_figure, color):
        Asgar = {'R': 'l',
                 'N': 'k',
                 'B': 's',
                 'Q': 'f',
                 'P': 'p'}

        currBoard = self.Boards[index]
        x, y = (int(position[1]) - 1, ord(position[0]) - ord('a'))
        if color != currBoard.turn:
            return 'Not Your Turn'
        figure = Asgar[asg_figure]

        if currBoard[x][y].color == '.' and (figure != 'p' or x not in [0, 7]):
            nextBoard = Board()
            nextBoard.field = [[currBoard[i][j] for j in range(8)] for i in range(8)]
            nextBoard[x][y] = Cell(figure, color)
            if nextBoard.check(color):
                del nextBoard
                return '!'

            self.Boards[index] = nextBoard
            del currBoard

            turnD = {'w': 'b', 'b': 'w'}
            self.Boards[index].turn = turnD[color]

            self.Boards[index].display()
            return figure
        return '!'

    def possible_placements(self, index, figure, color):
        currBoard = self.Boards[index]
        for x in range(7, -1, -1):
            for y in range(8):
                if currBoard[x][y].color == '.' and (figure != 'p' or x not in [0, 7]):
                    nextBoard = Board()
                    nextBoard.field = [[currBoard[i][j] for j in range(8)] for i in range(8)]
                    nextBoard[x][y] = Cell(figure, color)
                    if nextBoard.check(color):
                        print('!!', end=' ')
                    else:
                        print(color, figure.upper(), sep='', end=' ')
                    del nextBoard
                else:
                    print(currBoard[x][y].color, currBoard[x][y].figure, sep='', end=' ')
            print()

    def castling(self, index, color, direction):
        return self.Boards[index].castling(color, direction)
