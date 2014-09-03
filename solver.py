__author__ = 'Valerio'

import json


class LineSolver:
    def __init__(self, puzzle):
        self.puzzle = puzzle
        self.board = [[0 for y in range(len(puzzle['cols']))] for x in range(len(puzzle['rows']))]
        self.jobs = self.init_jobs()
        self.sort_jobs()
        self.jobcount = 0
        self._stack = []

    def get_row(self, index):
        return self.board[index]

    def set_row(self, index, line):
        self.board[index] = line

    def get_col(self, index):
        result = []
        for row in self.board:
            result.append(row[index])
        return result

    def set_col(self, index, line):
        i = 0
        for row in self.board:
            row[index] = line[i]
            i += 1

    def get_line(self, job):
        if job["type"] == 'col':
            return self.get_col(job["index"])
        else:
            return self.get_row(job["index"])

    def set_line(self, job, new_line):
        if job["type"] == 'row':
            self.set_row(job["index"], new_line)
        else:
            self.set_col(job["index"], new_line)

    def line_score(self, index, type):
        constraints = self.puzzle[type][index]
        l = len(self.puzzle[type])
        b = 0
        n = len(constraints)
        for c in constraints:
            b += c
        if b == l:
            return l
        else:
            return b * (n + 1) + n * (n - l - 1)

    def sort_jobs(self):
        self.jobs = sorted(self.jobs, key=lambda element: element['score'])

    def init_jobs(self):
        jobs = []
        for i in range(0, len(self.puzzle["rows"])):
            jobs.append({
                "type": 'row',
                "line": self.get_row(i),
                "index": i,
                "help": self.puzzle["rows"][i],
                "score": self.line_score(i, 'rows')
            })
        for i in range(0, len(puzzle["cols"])):
            jobs.append({
                "type": 'col',
                "line": self.get_col(i),
                "index": i,
                "help": self.puzzle["cols"][i],
                "score": self.line_score(i, 'cols')
            })
        return jobs

    def pick_a_cell(self):
        for i in range(len(self.board)):
            for j in range(len(self.board[0])):
                if self.board[i][j] == 0:
                    return i, j
        return None

    def guess_solve(self):
        result = self.logic_solve(True)
        if result != 0:  # we should start probing
            guesses = 0
            while True:
                cell = self.pick_a_cell()
                if not cell:
                    print "fuck"
                    print_board(self.board)
                    return
                self._stack.append(self.board[:])
                self.board[cell[0]][cell[1]] = 1
                self.jobs = []
                score = self.logic_solve()
                guesses += 1
                if not score:
                    print "contradiction found"
                    print_board(self.board)
                    # pop the stack, invert the choice and try again
                    self.board = self._stack.pop()
                    self.board[cell[0]][cell[1]] = 2
                    if guesses > 10:
                        print "stopping solver at", guesses, "guesses"
                        return
                elif score == 0:
                    print "solved after a guess"
                    print_board(self.board)
                    return
        return

    def logic_solve(self, verbose=False):
        if len(self.jobs) == 0:
            #self.jobcount = 0
            self.jobs = self.init_jobs()
        while len(self.jobs) > 0:
            job = self.jobs.pop()
            new_line = intersect(job["help"], self.get_line(job))
            if not new_line:
                return None
            elif new_line != job["line"]:
                self.jobcount += 1
                self.set_line(job, new_line)
                self.update_jobs(job, new_line)
                self.sort_jobs()
        if verbose:
            print_board(self.board)
            print "Jobs executed:", self.jobcount
            print "Solved" if self.empty_cells() == 0 else "Stall"

        return self.empty_cells()

    def update_jobs(self, old_job, new_line):
        count = 0
        for i in range(len(new_line)):
            if new_line[i] != old_job["line"][i]:
                count += 1
                found = False
                for job in self.jobs:
                    if job["type"] != old_job["type"] and job["index"] == i:
                        line_type = 'cols' if job['type'] == 'row' else 'rows'
                        job["score"] = self.line_score(i, line_type)
                        found = True
                        break
                if not found:
                    line_type = 'cols' if old_job['type'] == 'row' else 'rows'
                    self.jobs.append({
                        "type": 'col' if old_job["type"] == 'row' else 'row',
                        "line": self.get_col(i) if old_job["type"] == 'row' else self.get_row(i),
                        "index": i,
                        "help": self.puzzle["cols"][i] if old_job["type"] == 'row' else self.puzzle["rows"][i],
                        "score": self.line_score(i, line_type)
                    })

    def empty_cells(self):
        empty = len(self.board)*len(self.board[0])
        for line in self.board:
            for cell in line:
                if cell == 0:
                    empty -= 1
        return empty


def left_solve(constraints, line):
    j = 0
    pos = [0 for cell in range(len(constraints))]
    cov = [0 for cell in range(len(constraints))]
    b = 0
    backtracking = False

    state = 0

    while state != 6:
        continue_loop = False

        if state == 0:
            if b >= len(constraints):
                if b == 0:
                    j = 0
                b -= 1
                state = 3
                continue
            pos[b] = 0 if b == 0 else j + 1
            if pos[b] == len(line):
                return None
            state = 1

        elif state == 1:
            while line[pos[b]] == 2:
                pos[b] += 1
                if pos[b] >= len(line):
                    return None
            j = pos[b]
            cov[b] = -1 if line[j] != 1 else j
            j += 1
            while j - pos[b] < constraints[b]:
                if j > len(line):
                    return None
                if line[j] == 2:
                    if cov[b] == -1:
                        pos[b] = j
                        state = 1
                        continue_loop = True
                        break
                    else:
                        state = 4
                        continue_loop = True
                        break
                if cov[b] == -1 and line[j] == 1:
                    cov[b] = j
                j += 1
            if continue_loop:
                continue
            state = 2

        elif state == 2:
            if j < len(line):
                while j < len(line) and line[j] == 1:
                    if cov[b] == pos[b]:
                        state = 4
                        continue_loop = True
                        break
                    pos[b] += 1
                    if cov[b] == -1 and line[j] == 1:
                        cov[b] = j
                    j += 1
                if continue_loop:
                    continue
            if backtracking and cov[b] == -1:
                backtracking = False
                state = 5
                continue
            if j >= len(line) and b < len(constraints) - 1:
                return None
            b += 1
            backtracking = False
            state = 0

        elif state == 3:
            if j < len(line):
                while j < len(line):
                    if line[j] == 1:
                        j = pos[b] + constraints[b]
                        state = 5
                        continue_loop = True
                        break
                    j += 1
                if continue_loop:
                    continue
            state = 6

        elif state == 4:
            b -= 1
            if b < 0:
                return None
            j = pos[b] + constraints[b]
            state = 5

        elif state == 5:
            while cov[b] < 0 or pos[b] < cov[b]:
                if line[j] == 2:
                    if cov[b] > 0:
                        state = 4
                        continue_loop = True
                        break
                    else:
                        pos[b] = j + 1
                        backtracking = True
                        state = 1
                        continue_loop = True
                        break
                pos[b] += 1
                if line[j] == 1:
                    j += 1
                    if cov[b] == -1:
                        cov[b] = j - 1
                    state = 2
                    continue_loop = True
                    break
                j += 1
                if j >= len(line):
                    return None
            if continue_loop:
                continue
            state = 4
    return pos


def right_solve(constraints, line):
    j = 0
    pos = [0 for cell in range(len(constraints))]
    cov = [0 for cell in range(len(constraints))]
    b = len(constraints) - 1
    backtracking = False
    state = 0
    maxblock = len(constraints) - 1

    while state != 6:
        continue_loop = False

        if state == 0:
            if b < 0:
                if b == maxblock:
                    j = len(line) - 1
                b += 1
                state = 3
                continue
            pos[b] = len(line) - 1 if b == maxblock else j - 1
            if pos[b] - constraints[b] + 1 < 0:
                return None
            state = 1

        elif state == 1:
            while line[pos[b]] == 2:
                pos[b] -= 1
                if pos[b] < 0:
                    return None
            j = pos[b]
            cov[b] = -1 if line[j] != 1 else j
            j -= 1
            while pos[b] - j < constraints[b]:
                if j < 0:
                    return None
                if line[j] == 2:
                    if cov[b] == -1:
                        pos[b] = j
                        state = 1
                        continue_loop = True
                        break
                    else:
                        state = 4
                        continue_loop = True
                        break
                if cov[b] == -1 and line[j] == 1:
                    cov[b] = j
                j -= 1
            if continue_loop:
                continue
            state = 2

        elif state == 2:
            if j >= 0:
                while j >= 0 and line[j] == 1:
                    if cov[b] == pos[b]:
                        state = 4
                        continue_loop = True
                        break
                    pos[b] -= 1
                    if cov[b] == -1 and line[j] == 1:
                        cov[b] = j
                    j -= 1
                if continue_loop:
                    continue
            if backtracking and cov[b] == -1:
                backtracking = False
                state = 5
                continue
            if j < 0 < b:
                return None
            b -= 1
            backtracking = False
            state = 0

        elif state == 3:
            if j >= 0:
                while j >= 0:
                    if line[j] == 1:
                        j = pos[b] - constraints[b]
                        state = 5
                        continue_loop = True
                        break
                    j -= 1
                if continue_loop:
                    continue
            state = 6

        elif state == 4:
            b += 1
            if b > maxblock:
                return None
            j = pos[b] - constraints[b]
            state = 5

        elif state == 5:
            while cov[b] < 0 or pos[b] > cov[b]:
                if line[j] == 2:
                    if cov[b] > 0:
                        state = 4
                        continue_loop = True
                        break
                    else:
                        pos[b] = j - 1
                        backtracking = True
                        state = 1
                        continue_loop = True
                        break
                pos[b] -= 1
                if line[j] == 1:
                    j -= 1
                    if cov[b] == -1:
                        cov[b] = j + 1
                    state = 2
                    continue_loop = True
                    break
                j -= 1
                if j < 0:
                    return None
            if continue_loop:
                continue
            state = 4
    return pos


def intersect(constraints, line):
    if constraints[0] == 0:
        return [2 for x in line]
    elif constraints[0] == len(line):
        return [1 for x in line]

    new_line = list(line)
    changed = lb = rb = 0
    lgap = rgap = True
    left = left_solve(constraints, line)
    right = right_solve(constraints, line)

    if not left or not right:
        return None

    for i in range(len(line)):
        if not lgap and left[lb] + constraints[lb] == i:
            lgap = True
            lb += 1
        if lgap and lb < len(constraints) and left[lb] == i:
            lgap = False
        if not rgap and right[rb] + 1 == i:
            rgap = True
            rb += 1
        if rgap and (rb < len(constraints) and right[rb] - constraints[rb] + 1) == i:
            rgap = False
        if lgap == rgap and lb == rb:
            new_line[i] = 2 if lgap else 1
            changed += 1
    return new_line


def read_file():
    in_file = open("nonogram.txt", "r")
    puzzles = json.load(in_file)
    in_file.close()
    return puzzles


def print_board(board):
    for line in board:
        s = '|'
        for cell in line:
            s += '#, ' if cell == 1 else '-, ' if cell == 2 else ' , '
        print s[:-2] + '|'


def print_board_alt(board):
    lens = [max(map(len, str(col))) for col in zip(*board)]
    fmt = ' '.join('{{:{}}}'.format(x) for x in lens)
    table = [fmt.format(*row) for row in board]
    print '\n'.join(table)


puzzle_index = 7
name = "skiing"
puzzles = read_file()["puzzles"]
for p in puzzles:
    if p["name"] == name:
        puzzle = p
#puzzle = read_file()["puzzles"][puzzle_index]
if puzzle:
    print "Solving", puzzle["name"] if puzzle["name"] else " puzzle"
    solver = LineSolver(puzzle)
    #solver.logic_solve(True)
    solver.guess_solve()