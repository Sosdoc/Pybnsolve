__author__ = 'Valerio'

import json
import copy
import tree
import argparse


class LineSolver:
    def __init__(self, puzzle):
        self.puzzle = puzzle
        self.board = [[0 for y in range(len(puzzle['cols']))] for x in range(len(puzzle['rows']))]
        self.jobs = self.init_jobs()
        self.sort_jobs()
        self.jobcount = 0
        self._stack = []
        self.guess_count = 0

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

    def line_score(self, index, line_type):
        constraints = self.puzzle[line_type][index]
        l = len(self.puzzle[line_type])
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

    def logic_solve(self, verbose=False):
        if len(self.jobs) == 0:
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
                        line_type = 'cols' if old_job['type'] == 'row' else 'rows'
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
        empty = 0
        for line in self.board:
            empty += line.count(0)
        return empty

    def cell_score(self, i, j):
        count = 4
        if i == 0 or self.board[i-1][j] == 1:
            count -= 1
        if i == len(self.puzzle['rows']) - 1 or self.board[i+1][j] == 1:
            count -= 1
        if j == 0 or self.board[i][j-1] == 1:
            count -= 1
        if j == len(self.puzzle['cols']) - 1 or self.board[i][j+1] == 1:
            count -= 1
        return count

    def get_best_cell(self):
        min_score = 5
        best_cell = None
        for i in range(len(self.board)):
            for j in range(len(self.board[0])):
                if self.board[i][j] == 0:
                    score = self.cell_score(i, j)
                    if score < min_score:
                        min_score = score
                        best_cell = (i, j)
        return best_cell

    def solve(self, node):
        self.board = node.content
        result = self.logic_solve()
        if result is None:
            return None
        elif result != 0:
            cell = self.get_best_cell()
            node.left = tree.Node(copy.deepcopy(self.board), node)
            node.left.content[cell[0]][cell[1]] = 1
            node.right = tree.Node(copy.deepcopy(self.board), node)
            node.right.content[cell[0]][cell[1]] = 2
            self.guess_count += 1
            result_left = self.solve(node.left)
            if result_left is None:
                result_right = self.solve(node.right)
                if result_right is None:
                    self.board = node.content
                    return None
                else:
                    return result_right
            else:
                return result_left
        else:
            return self.board


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
                if j >= len(line):
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


def read_file(filename):
    with open(filename) as f:
        res = json.load(f)
    return res


def print_board(b):
    for line in b:
        s = ['|']
        for cell in line:
            s.append(' # ' if cell == 1 else ' - ' if cell == 2 else '  ')
        s.pop()
        s.append('|')
        print "".join(s)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("name", nargs="?", default="edge", help="name of the puzzle to solve (looked up in the file)")
    parser.add_argument("--file", nargs="?", default="nonogram.txt", help="filename containing the puzzles")
    args = parser.parse_args()

    puzzles = read_file(args.file)["puzzles"]
    for p in puzzles:
        if p["name"] == args.name:
            puzzle = p

    if puzzle:
        print "Solving", puzzle["name"] if puzzle["name"] else " puzzle"
        solver = LineSolver(puzzle)
        root = tree.Node(solver.board)
        from datetime import datetime
        start = datetime.now()
        board = solver.solve(root)
        stop = datetime.now()
        diff = stop - start
        print_board(board)
        print "with", solver.guess_count, "guesses"
        print "in %ss %sms" % (diff.seconds, diff.microseconds/1000)


