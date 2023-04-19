import numpy as np
import time
import copy
import pickle

class Sudoku:
    def __init__(self, puzzle, fail=False):
        self.fail = fail
        self.puzzle = puzzle
        self.possibleValues = [[[i for i in range(1, 10)] for _ in range(1, 10)] for _ in range(1, 10)]
        self.finalValues = [ [-1] * 9 for i in range(9)]
        self.locations = [
                        ['TL','TL','TL','TM','TM','TM','TR','TR','TR'],
                        ['TL','TL','TL','TM','TM','TM','TR','TR','TR'],
                        ['TL','TL','TL','TM','TM','TM','TR','TR','TR'],
                        ['ML','ML','ML','M', 'M', 'M', 'MR','MR','MR'],
                        ['ML','ML','ML','M', 'M', 'M', 'MR','MR','MR'],
                        ['ML','ML','ML','M', 'M', 'M', 'MR','MR','MR'],
                        ['BL','BL','BL','BM','BM','BM','BR','BR','BR'],
                        ['BL','BL','BL','BM','BM','BM','BR','BR','BR'],
                        ['BL','BL','BL','BM','BM','BM','BR','BR','BR']]
    
    def isGoal(self):
        for i in range(0, len(self.finalValues)):
            if not all(value != -1 for value in self.finalValues[i]):
                return False
        return True
    
    def earlyFailure(self):
        return any(len(values) == 0 for values in self.possibleValues)

    def getPosVals(self, col, row):
        return self.possibleValues[col][row].copy()
    
    def getFinalState(self):
        if self.isGoal():
            return self.finalValues
        else:
            return -1
    
    def autoCompleteSingles(self):
        singleElements = []
        for i in range(0,len(self.possibleValues)):
            for j in range(0, len(self.possibleValues[i])):
                if len(self.possibleValues[i][j]) == 1 and self.finalValues[i][j] == -1:
                    singleElements.append((i,j))
        return singleElements
    
    def sendFail(self):
        puzzle = [[-1] * 9 for i in range(9)]
        state = Sudoku(puzzle=puzzle)
        state.finalValues = [[-1] * 9 for i in range(9)]
        state.fail = True
        return state
    
    def getArea(self, col, row):
        searchCol = []
        searchRow = []
        if col < 3:
            searchCol = [0,1,2]
        elif col < 6:
            searchCol = [3,4,5]
        else:
            searchCol = [6,7,8]
        
        if row < 3:
            searchRow = [0,1,2]
        elif row < 6:
            searchRow = [3,4,5]
        else:
            searchRow = [6,7,8]
            
        return searchCol, searchRow
        
    def setValue(self, col, row, value, enableSingles=True):
        if value not in self.possibleValues[col][row]:
            if value != 0:
                return self.sendFail()
        
        state = pickle.loads(pickle.dumps(self, -1))
        if value != 0:
            state.possibleValues[col][row] = [value]
            state.finalValues[col][row] = value
            index = (col, row)
            #update local area
            searchCol, searchRow = self.getArea(col, row)
            for i in searchCol:
                for j in searchRow:
                    check = (i, j)
                    #if area == self.locations[i][j]:
                    if (index != check) and value in state.possibleValues[i][j]:
                        if len(state.possibleValues[i][j]) == 1 and state.possibleValues[i][j][0] == value:
                            return state.sendFail()
                        state.possibleValues[i][j].remove(value)
                
            #update column
            for update in range(0, row):
                if value in state.possibleValues[col][update]:
                    if len(state.possibleValues[col][update]) == 1:
                        return state.sendFail()
                    state.possibleValues[col][update].remove(value)
            for update in range(row+1, len(state.possibleValues[col])):
                if value in state.possibleValues[col][update]:
                    if len(state.possibleValues[col][update]) == 1:
                        return state.sendFail()
                    state.possibleValues[col][update].remove(value)
            
            #update row
            for update in range(0, col):
                if value in state.possibleValues[update][row]:
                    if len(state.possibleValues[update][row]) == 1:
                        return state.sendFail()
                    state.possibleValues[update][row].remove(value)
            for update in range(col+1, len(state.possibleValues)):
                if value in state.possibleValues[update][row]:
                    if len(state.possibleValues[update][row]) == 1:
                        return state.sendFail()
                    state.possibleValues[update][row].remove(value)
            
            #finalise elements which have only a single possible value which can be assigned to them
            if enableSingles and not state.fail:
                singleElements = state.autoCompleteSingles()
                while len(singleElements) > 0:
                    if state.fail:
                        break
                    column = singleElements[0][0]
                    row = singleElements[0][1]
                    state = state.setValue(column, row, state.possibleValues[column][row][0])
                    singleElements = state.autoCompleteSingles()
        return state

def pickNextElement(sudoku):
    indices = []
    minPos = 9
    maxList = []
    for i in range(0, len(sudoku.possibleValues)):
        for j in range(0, len(sudoku.possibleValues[i])):
            minPosCol = len(sudoku.possibleValues[i][j])
            if minPosCol not in maxList:
                maxList.append(minPosCol)
    listAsc = sorted(maxList)
    if len(listAsc) > 1:
        minPos = listAsc[1]
    else:
        minPos = 1
    for j in range(0, len(sudoku.possibleValues)):
        for z in range(0, len(sudoku.possibleValues[j])):
            if len(sudoku.possibleValues[j][z]) == minPos:
                indices.append((j, z))
    
    return indices[0]

def orderValues(sudoku, col, row):
    values = sudoku.getPosVals(col, row)
    counts = []
    for value in values:
        count = 0
        for i in range(len(sudoku.possibleValues)):
            for j in range(len(sudoku.possibleValues[i])):
                if len(sudoku.possibleValues[i][j]) > 1:
                    if value in sudoku.possibleValues[i][j]:
                        count += 1
        counts.append(count)
        
    zipped = zip(values, counts)
    sortedZip = sorted(zipped, key = lambda x: x[1], reverse=False)
    finalValues = []
    for sortedValue in sortedZip:
        finalValues.append(sortedValue[0])
    return finalValues

def setup(sudoku):
    puzzle = sudoku
    sudoku = Sudoku(sudoku)
    for i in range(0, len(puzzle)):
        for j in range(0, len(puzzle[i])):
            sudoku = sudoku.setValue(i, j, puzzle[i][j], enableSingles=False)
            if sudoku.fail:
                return sudoku, False
    return sudoku, True

def recursiveSolve(sudoku, initial=True):
    if initial:
        sudoku, result = setup(sudoku)
        if not result:
            return sudoku
    
    indices = pickNextElement(sudoku)
    values = orderValues(sudoku, indices[0], indices[1])

    for value in values:
        newState = sudoku.setValue(indices[0], indices[1], value) 
        if newState.isGoal():
            return newState
        if not newState.earlyFailure():
            if not newState.fail:
                deepState = recursiveSolve(newState, initial=False)
                if deepState is not None and deepState.isGoal():
                    return deepState
    return sudoku.sendFail()

def sudoku_solver(sudoku):
    solutionState = recursiveSolve(sudoku)
    return np.asanyarray(solutionState.finalValues)

SKIP_TESTS = False

def tests():
    import time
    difficulties = ['very_easy', 'easy', 'medium', 'hard']
    total = 0
    start_timeFULL = time.process_time()
    for difficulty in difficulties:
        print(f"Testing {difficulty} sudokus")
        
        sudokus = np.load(f"data/{difficulty}_puzzle.npy")
        solutions = np.load(f"data/{difficulty}_solution.npy")
        
        count = 0
        for i in range(len(sudokus)):
            #i=14
            sudoku = sudokus[i].copy()
            print(f"This is {difficulty} sudoku number", i)
            print(sudoku)
            start_time = time.process_time()
            your_solution = sudoku_solver(sudoku)
            end_time = time.process_time()

            print(f"This is your solution for {difficulty} sudoku number", i)
            print(your_solution)
            
            print("Is your solution correct?")
            if np.array_equal(your_solution, solutions[i]):
                print("Yes! Correct solution.")
                count += 1
            else:
                print("No, the correct solution is:")
                print(solutions[i])
            
            print("This sudoku took", end_time-start_time, "seconds to solve.\n")

        print(f"{count}/{len(sudokus)} {difficulty} sudokus correct")
        end_timeFULL = time.process_time()
        print("This test took", end_timeFULL-start_timeFULL, "seconds to solve.\n")
        total += count
        if count < len(sudokus):
            break
        print(f"Total correct is {total}/60")
        
if not SKIP_TESTS:
    tests()