from . import defs

NONE        =   0
UPPER       =   1
UPPER_LEFT  =   2
LEFT        =   4
LOWER_LEFT  =   8
LOWER       =  16
LOWER_RIGHT =  32
RIGHT       =  64
UPPER_RIGHT = 128

class Board(object):
    def __init__(self):
        self.__raw_board = [ [ 0 for i in range(defs.BOARD_SIZE + 2) ] for j in range(defs.BOARD_SIZE + 2) ]

        self.__turns = 0
        self.__current_color = defs.BLACK

        self.__update_log = []
        self.__movable_pos = [ [] for i in range(defs.MAX_TURNS + 1) ]
        self.__movable_dir = [ [ [ 0 for i in range(defs.BOARD_SIZE + 2) ] for j in range(defs.BOARD_SIZE + 2) ] for k in range(defs.MAX_TURNS + 1)]
        self.__liberty = [ [ 0 for i in range(defs.BOARD_SIZE + 2) ] for j in range(defs.BOARD_SIZE + 2) ]

        self.__discs = defs.ColorStorage(int)

        self.init()

    def init(self):
        for x in range(1, defs.BOARD_SIZE + 1):
            for y in range(1, defs.BOARD_SIZE + 1):
                self.__raw_board[x][y] = defs.EMPTY

        for y in range(0, defs.BOARD_SIZE + 2):
            self.__raw_board[0][y] = defs.WALL
            self.__raw_board[defs.BOARD_SIZE + 1][y] = defs.WALL

        for x in range(0, defs.BOARD_SIZE + 2):
            self.__raw_board[x][0] = defs.WALL
            self.__raw_board[x][defs.BOARD_SIZE + 1] = defs.WALL

        c = defs.BOARD_SIZE // 2
        self.__raw_board[c][c] = defs.WHITE
        self.__raw_board[c + 1][c + 1] = defs.WHITE
        self.__raw_board[c][c + 1] = defs.BLACK
        self.__raw_board[c + 1][c] = defs.BLACK

        for x in range(1, defs.BOARD_SIZE + 1):
            for y in range(1, defs.BOARD_SIZE + 1):
                liberty = 0
                if self.__raw_board[x + 1][y] == defs.EMPTY:
                    liberty += 1
                if self.__raw_board[x + 1][y - 1] == defs.EMPTY:
                    liberty += 1
                if self.__raw_board[x][y - 1] == defs.EMPTY:
                    liberty += 1
                if self.__raw_board[x - 1][y - 1] == defs.EMPTY:
                    liberty += 1
                if self.__raw_board[x - 1][y] == defs.EMPTY:
                    liberty += 1
                if self.__raw_board[x - 1][y + 1] == defs.EMPTY:
                    liberty += 1
                if self.__raw_board[x][y + 1] == defs.EMPTY:
                    liberty += 1
                if self.__raw_board[x + 1][y + 1] == defs.EMPTY:
                    liberty += 1

                self.__liberty[x][y] = liberty

        self.__discs[defs.BLACK] = 2
        self.__discs[defs.WHITE] = 2
        self.__discs[defs.EMPTY] = defs.BOARD_SIZE * defs.BOARD_SIZE - 4

        self.__turns = 0
        self.__current_color = defs.BLACK

        self.__update_log.clear()

        self.__init_movable()

    def exec_move(self, point):
        if point.x <= 0 or point.x > defs.BOARD_SIZE:
            return False
        if point.y <= 0 or point.y > defs.BOARD_SIZE:
            return False
        if self.__movable_dir[self.__turns][point.x][point.y] == NONE:
            return False

        self.__flip_discs(point)
        self.__turns += 1
        self.__current_color = -self.__current_color

        self.__init_movable()

        return True

    def pass_move(self):
        if len(self.__movable_pos[self.__turns]) != 0:
            return False
        if self.is_game_over():
            return False

        self.__current_color = -self.__current_color

        null_update = []
        self.__update_log.append(null_update)

        self.__init_movable()

        return True

    def undo_move(self):
        if self.__turns == 0:
            return False
        self.__current_color = -self.__current_color

        update = self.__update_log[-1]

        if len(update) == 0:
            self.__movable_pos[self.__turns].clear()
            for x in range(1, defs.BOARD_SIZE + 1):
                for y in range(1, defs.BOARD_SIZE + 1):
                    self.__movable_dir[self.__turns][x][y] = NONE
        else:
            self.__turns -= 1
            x = update[0].x
            y = update[0].y

            self.__raw_board[x][y] = defs.EMPTY
            for i in range(1, len(update)):
                self.__raw_board[update[i].x][update[i].y] = -update[i].color

            self.__liberty[x + 1][y] += 1
            self.__liberty[x + 1][y - 1] += 1
            self.__liberty[x][y - 1] += 1
            self.__liberty[x - 1][y - 1] += 1
            self.__liberty[x - 1][y] += 1
            self.__liberty[x - 1][y + 1] += 1
            self.__liberty[x][y + 1] += 1
            self.__liberty[x + 1][y + 1] += 1

            disc_diff = len(update)
            self.__discs[ self.__current_color] -= disc_diff
            self.__discs[-self.__current_color] += (disc_diff - 1)
            self.__discs[defs.EMPTY] += 1

        self.__update_log.pop()

        return True

    def is_game_over(self):
        if self.__turns == defs.MAX_TURNS:
            return True
        if len(self.__movable_pos[self.__turns]) != 0:
            return False

        disc = defs.Disc(0, 0, -self.__current_color)
        for x in range(1, defs.BOARD_SIZE + 1):
            disc.x = x
            for y in range(1, defs.BOARD_SIZE + 1):
                disc.y = y
                if self.__check_mobility(disc) != NONE:
                    return False
        return True

    def count_disc(self, color):
        return self.__discs[color]

    def get_color(self, p):
        return self.__raw_board[p.x][p.y]

    def get_movable_pos(self):
        return self.__movable_pos[self.__turns]

    def get_update(self):
        if len(self.__update_log) == 0:
            return []
        else:
            return self.__update_log[-1]

    def get_current_color(self):
        return self.__current_color

    def get_turns(self):
        return self.__turns

    def get_history(self):
        history = []
        for update in self.__update_log:
            if len(update) == 0:
                continue
            history.append(defs.Disc(update[0].x, update[0].y, update[0].color))

        return history

    def get_liberty(self, p):
        return self.__liberty[p.x][p.y]

    def __flip_discs(self, point):
        x = 0
        y = 0
        dire = self.__movable_dir[self.__turns][point.x][point.y]
        operation = defs.Disc(point.x, point.y, self.__current_color)

        update = []
        self.__raw_board[point.x][point.y] = self.__current_color
        update.append(defs.Disc(operation.x, operation.y, operation.color))

        if dire & UPPER:
            y = point.y
            operation.x = point.x
            y -= 1
            while self.__raw_board[point.x][y] == -self.__current_color:
                self.__raw_board[point.x][y] = self.__current_color
                operation.y = y
                update.append(defs.Disc(operation.x, operation.y, operation.color))
                y -= 1

        if dire & LOWER:
            y = point.y
            operation.x = point.x
            y += 1
            while self.__raw_board[point.x][y] == -self.__current_color:
                self.__raw_board[point.x][y] = self.__current_color
                operation.y = y
                update.append(defs.Disc(operation.x, operation.y, operation.color))
                y += 1

        if dire & LEFT:
            x = point.x
            operation.y = point.y
            x -= 1
            while self.__raw_board[x][point.y] == -self.__current_color:
                self.__raw_board[x][point.y] = self.__current_color
                operation.x = x
                update.append(defs.Disc(operation.x, operation.y, operation.color))
                x -= 1

        if dire & RIGHT:
            x = point.x
            operation.y = point.y
            x += 1
            while self.__raw_board[x][point.y] == -self.__current_color:
                self.__raw_board[x][point.y] = self.__current_color
                operation.x = x
                update.append(defs.Disc(operation.x, operation.y, operation.color))
                x += 1

        if dire & UPPER_RIGHT:
            x = point.x
            y = point.y
            x += 1
            y -= 1
            while self.__raw_board[x][y] == -self.__current_color:
                self.__raw_board[x][y] = self.__current_color
                operation.x = x
                operation.y = y
                update.append(defs.Disc(operation.x, operation.y, operation.color))
                x += 1
                y -= 1

        if dire & UPPER_LEFT:
            x = point.x
            y = point.y
            x -= 1
            y -= 1
            while self.__raw_board[x][y] == -self.__current_color:
                self.__raw_board[x][y] = self.__current_color
                operation.x = x
                operation.y = y
                update.append(defs.Disc(operation.x, operation.y, operation.color))
                x -= 1
                y -= 1

        if dire & LOWER_LEFT:
            x = point.x
            y = point.y
            x -= 1
            y += 1
            while self.__raw_board[x][y] == -self.__current_color:
                self.__raw_board[x][y] = self.__current_color
                operation.x = x
                operation.y = y
                update.append(defs.Disc(operation.x, operation.y, operation.color))
                x -= 1
                y += 1

        if dire & LOWER_RIGHT:
            x = point.x
            y = point.y
            x += 1
            y += 1
            while self.__raw_board[x][y] == -self.__current_color:
                self.__raw_board[x][y] = self.__current_color
                operation.x = x
                operation.y = y
                update.append(defs.Disc(operation.x, operation.y, operation.color))
                x += 1
                y += 1

        x = point.x
        y = point.y

        self.__liberty[x + 1][y] -= 1
        self.__liberty[x + 1][y - 1] -= 1
        self.__liberty[x][y - 1] -= 1
        self.__liberty[x - 1][y - 1] -= 1
        self.__liberty[x - 1][y] -= 1
        self.__liberty[x - 1][y + 1] -= 1
        self.__liberty[x][y + 1] -= 1
        self.__liberty[x + 1][y + 1] -= 1

        disc_diff = len(update)
        self.__discs[ self.__current_color] += disc_diff
        self.__discs[-self.__current_color] -= (disc_diff - 1)
        self.__discs[defs.EMPTY] -= 1

        self.__update_log.append(update)

    def __check_mobility(self, disc):
        if self.__raw_board[disc.x][disc.y] != defs.EMPTY:
            return NONE

        x = 0
        y = 0
        dire = NONE

        if self.__raw_board[disc.x][disc.y - 1] == -disc.color:
            x = disc.x
            y = disc.y - 2
            while self.__raw_board[x][y] == -disc.color:
                y -= 1
            if self.__raw_board[x][y] == disc.color:
                dire |= UPPER

        if self.__raw_board[disc.x][disc.y + 1] == -disc.color:
            x = disc.x
            y = disc.y + 2
            while self.__raw_board[x][y] == -disc.color:
                y += 1
            if self.__raw_board[x][y] == disc.color:
                dire |= LOWER

        if self.__raw_board[disc.x - 1][disc.y] == -disc.color:
            x = disc.x - 2
            y = disc.y
            while self.__raw_board[x][y] == -disc.color:
                x -= 1
            if self.__raw_board[x][y] == disc.color:
                dire |= LEFT

        if self.__raw_board[disc.x + 1][disc.y] == -disc.color:
            x = disc.x + 2
            y = disc.y
            while self.__raw_board[x][y] == -disc.color:
                x += 1
            if self.__raw_board[x][y] == disc.color:
                dire |= RIGHT


        if self.__raw_board[disc.x + 1][disc.y - 1] == -disc.color:
            x = disc.x + 2
            y = disc.y - 2
            while self.__raw_board[x][y] == -disc.color:
                x += 1
                y -= 1
            if self.__raw_board[x][y] == disc.color:
                dire |= UPPER_RIGHT

        if self.__raw_board[disc.x - 1][disc.y - 1] == -disc.color:
            x = disc.x - 2
            y = disc.y - 2
            while self.__raw_board[x][y] == -disc.color:
                x -= 1
                y -= 1
            if self.__raw_board[x][y] == disc.color:
                dire |= UPPER_LEFT

        if self.__raw_board[disc.x - 1][disc.y + 1] == -disc.color:
            x = disc.x - 2
            y = disc.y + 2
            while self.__raw_board[x][y] == -disc.color:
                x -= 1
                y += 1
            if self.__raw_board[x][y] == disc.color:
                dire |= LOWER_LEFT

        if self.__raw_board[disc.x + 1][disc.y + 1] == -disc.color:
            x = disc.x + 2
            y = disc.y + 2
            while self.__raw_board[x][y] == -disc.color:
                x += 1
                y += 1
            if self.__raw_board[x][y] == disc.color:
                dire |= LOWER_RIGHT

        return dire

    def __init_movable(self):
        disc = defs.Disc(0, 0, self.__current_color)
        dire = 0
        self.__movable_pos[self.__turns].clear()

        for x in range(1, defs.BOARD_SIZE + 1):
            disc.x = x
            for y in range(1, defs.BOARD_SIZE + 1):
                disc.y = y
                dire = self.__check_mobility(disc)
                if dire != NONE:
                    self.__movable_pos[self.__turns].append(defs.Disc(disc.x, disc.y, disc.color))
                self.__movable_dir[self.__turns][x][y] = dire
