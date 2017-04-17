import numpy as np
import itertools
import operator
from operator import itemgetter
from itertools import repeat

assignments = []
diagonal_units=[]

def cross(a, b):
    "Cross product of elements in A and elements in B."
    return [s+t for s in a for t in b]

rows = 'ABCDEFGHI'
cols = '123456789'
boxes = cross(rows, cols)

row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')]
#Get the main diagonals ->Top left to bottom right
mainDiagonal=[r+c for rowIndex,r in enumerate(rows) for colIndex,c in enumerate(cols) if(rowIndex == colIndex)]
#Get the reverse diagonals -> Bottom left to top right
reverseDiagonal=[r+c for rowIndex,r in enumerate(rows) for colIndex,c in enumerate(cols[::-1]) if(rowIndex == colIndex)]
diagonal_units.append(mainDiagonal)
diagonal_units.append(reverseDiagonal)

unitlist = row_units + column_units + square_units+ diagonal_units #Add diagonal units thereby introducing new constraints into the environment
units = dict((s, [u for u in unitlist if s in u]) for s in boxes) #Diagonal units needs to be added to the appropriate boxes
peers = dict((s, set(sum(units[s],[]))-set([s])) for s in boxes) #Peers now include diagonal boxes too

def assign_value(values, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """
    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values

def grid_values(grid):
    """Convert grid string into {<box>: <value>} dict with '123456789' value for empties.

    Args:
        grid: Sudoku grid in string form, 81 characters long
    Returns:
        Sudoku grid in dictionary form:
        - keys: Box labels, e.g. 'A1'
        - values: Value in corresponding box, e.g. '8', or '123456789' if it is empty.
    """
    values = []
    all_digits = '123456789'
    for c in grid:
        if c == '.':
            values.append(all_digits)
        elif c in all_digits:
            values.append(c)
    assert len(values) == 81
    return dict(zip(boxes, values))

def display(values):
    """
    Display the values as a 2-D grid.
    Input: The sudoku in dictionary form
    Output: None
    """
    width = 1+max(len(values[s]) for s in boxes)
    line = '+'.join(['-'*(width*3)]*3)
    for r in rows:
        print(''.join(values[r+c].center(width)+('|' if c in '36' else '')
                      for c in cols))
        if r in 'CF': print(line)
    print

def eliminate(values):
    # Write a function that will take as an input, the sudoku in dictionary form,
    # run through all the boxes, applying the eliminate technique,
    # and return the resulting sudoku in dictionary form.
    #print(values)
    rowListIndexDict={'A':0,'B':1,'C':2,'D':3,'E':4,'F':5,'G':6,'H':7,'I':8}
    singlesDict={}
    for k, v in values.items():
        if(len(v) == 1): #Consider only boxes with a single value
            singlesDict[k] = v;
    for k, v in singlesDict.items():
            rowVal = k[0]
            colVal = int(k[1])-1
            #Eliminate the values from Square units
            squareListToEliminate =[]
            for subSquareLists in square_units:
                if(k in subSquareLists):
                    squareListToEliminate = subSquareLists
                    break
                
            for squareCell in squareListToEliminate:
                sqCellVal = values[squareCell]
                if(len(sqCellVal) !=1):
                    removedVal=sqCellVal.replace(v, "") 
                    assign_value(values, squareCell, removedVal)
                    
            #Eliminate the values from the Row units
            rowsToEliminate=row_units[rowListIndexDict[rowVal]]
            for rowCell in rowsToEliminate:
                rowCellVal = values[rowCell]
                if(len(rowCellVal) !=1):
                   removedVal=rowCellVal.replace(v, "") 
                   assign_value(values, rowCell, removedVal)
            
            #Eliminate the values from Column units 
            columnsToEliminate=column_units[colVal]
            for columnCell in columnsToEliminate:
                colCellVal = values[columnCell]
                if(len(colCellVal) !=1):
                   removedVal=colCellVal.replace(v, "") 
                   assign_value(values, columnCell, removedVal)
                   
    return values

def only_choice(values):
    # Write a function that will take as an input, the sudoku in dictionary form,
    # run through all the units, applying the only choice technique,
    # and return the resulting sudoku in dictionary form.

    for unit in unitlist:
        for digit in '123456789':
            dplaces = [box for box in unit if digit in values[box]]
            if len(dplaces) == 1:
                values = assign_value(values, dplaces[0], digit)
    return values

def naked_twins(values):
    """Eliminate values using the naked twins strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """
    #Consider boxes that have a 2 digit value and associate it with its units
    possibleTwinBox=[(box,units[box]) for box in boxes if len(values[box]) == 2]
    #Search for naked twins in all the units for the eligible box
    nakedTwinBoxes=[(box,uBox) for (box,unitBoxesList) in possibleTwinBox for unit in unitBoxesList for uBox in unit if(values[box] == values[uBox]) and (box !=uBox)]
    #Minimize the duplicates by removing exactly re-occuring tuples while the re-ordered copies of the tuple needs to be eliminted
    uniqueTwinsNonSorted=list(set(sorted(nakedTwinBoxes,key=operator.itemgetter(0,1))))
    for boxPairs in set(uniqueTwinsNonSorted):
        box1 = boxPairs[0]
        box2 = boxPairs[1]
        twinPairBoxList=[box1,box2]
        unitToRemoveTwin = [unit for unit in unitlist if set(twinPairBoxList) < set(unit)] #Find the units where both the twin boxes are co-located => determine the main set of  the subset of twin boxes
        flattenedUnitToRemoveTwin = list(itertools.chain.from_iterable(unitToRemoveTwin)) #Flatten the list
        for commonUnitBox in flattenedUnitToRemoveTwin:
            if len(values[commonUnitBox]) > 2 :
                for twinBoxVal in values[box1]:
                    assign_value(values,commonUnitBox,values[commonUnitBox].replace(twinBoxVal,''))
    return values

def reduce_puzzle(values):
    """
    Iterate eliminate() and only_choice(). If at some point, there is a box with no available values, return False.
    If the sudoku is solved, return the sudoku.
    If after an iteration of both functions, the sudoku remains the same, return the sudoku.
    Input: A sudoku in dictionary form.
    Output: The resulting sudoku in dictionary form.
    """
    #solved_values = [box for box in values.keys() if len(values[box]) == 1]
    stalled = False
    while not stalled:
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])
         # Your code here: Use the Eliminate Strategy
        eliminate(values)
         # Your code here: Use the Only Choice Strategy
        only_choice(values)
         # Your code here: Use the Naked Twins Strategy
        naked_twins(values)

        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
        stalled = solved_values_before == solved_values_after
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    return values

def search(values):
    "Using depth-first search and propagation, create a search tree and solve the sudoku."
    # First, reduce the puzzle using the previous function
    values = reduce_puzzle(values)
    if values == False:
        return False

    if all(len(values[s]) == 1 for s in boxes):
        return values ## Solved!
    
    unfilledSquares = dict([(box,len(values[box])) for box in boxes if  len(values[box]) > 1])
    sortedUnfilledSquares=sorted(unfilledSquares.items(),key=itemgetter(1))
    minPossibilitySquare= sortedUnfilledSquares[0][0]
    for value in values[minPossibilitySquare]:
        new_sudoku = values.copy()
        new_sudoku[minPossibilitySquare] = value
        attempt = search(new_sudoku)
        if attempt:
            return attempt

def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """
    values = grid_values(grid)
    values = search(values)

    return values

if __name__ == '__main__':

    #diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    diag_sudoku_grid = '8..........36......7..9.2...5...7.......457.....1...3...1....68..85...1..9....4..'
    #diag_sudoku_grid =  '...............9..97.3......1..6.5....47.8..2.....2..6.31..4......8..167.87......'
    solved_sudoku=solve(diag_sudoku_grid)
    display(solved_sudoku)

    try:
        from visualize import visualize_assignments
        visualize_assignments(assignments)
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
