import matplotlib.pyplot as plt
import numpy as np
import time

class PlotResults:
    """
    Class to plot the results. 
    """
    def plot_results(self, data1, data2, label1, label2, filename):
        """
        This method receives two lists of data point (data1 and data2) and plots
        a scatter plot with the information. The lists store statistics about individual search 
        problems such as the number of nodes a search algorithm needs to expand to solve the problem.

        The function assumes that data1 and data2 have the same size. 

        label1 and label2 are the labels of the axes of the scatter plot. 
        
        filename is the name of the file in which the plot will be saved.
        """
        _, ax = plt.subplots()
        ax.scatter(data1, data2, s=100, c="g", alpha=0.5, cmap=plt.cm.coolwarm, zorder=10)
    
        lims = [
        np.min([ax.get_xlim(), ax.get_ylim()]),  # min of both axes
        np.max([ax.get_xlim(), ax.get_ylim()]),  # max of both axes
        ]
    
        ax.plot(lims, lims, 'k-', alpha=0.75, zorder=0)
        ax.set_aspect('equal')
        ax.set_xlim(lims)
        ax.set_ylim(lims)
        plt.xlabel(label1)
        plt.ylabel(label2)
        plt.grid()
        plt.savefig(filename)

class Grid:
    """
    Class to represent an assignment of values to the 81 variables defining a Sudoku puzzle. 

    Variable _cells stores a matrix with 81 entries, one for each variable in the puzzle. 
    Each entry of the matrix stores the domain of a variable. Initially, the domains of variables
    that need to have their values assigned are 123456789; the other domains are limited to the value
    initially assigned on the grid. Backtracking search and AC3 reduce the the domain of the variables 
    as they proceed with search and inference.
    """
    def __init__(self):
        self._cells = []
        self._complete_domain = "123456789"
        self._width = 9

    def copy(self):
        """
        Returns a copy of the grid. 
        """
        copy_grid = Grid()
        copy_grid._cells = [row.copy() for row in self._cells]
        return copy_grid

    def get_cells(self):
        """
        Returns the matrix with the domains of all variables in the puzzle.
        """
        return self._cells

    def get_width(self):
        """
        Returns the width of the grid.
        """
        return self._width

    def read_file(self, string_puzzle):
        """
        Reads a Sudoku puzzle from string and initializes the matrix _cells. 

        This is a valid input string:

        4.....8.5.3..........7......2.....6.....8.4......1.......6.3.7.5..2.....1.4......

        This is translated into the following Sudoku grid:

        - - - - - - - - - - - - - 
        | 4 . . | . . . | 8 . 5 | 
        | . 3 . | . . . | . . . | 
        | . . . | 7 . . | . . . | 
        - - - - - - - - - - - - - 
        | . 2 . | . . . | . 6 . | 
        | . . . | . 8 . | 4 . . | 
        | . . . | . 1 . | . . . | 
        - - - - - - - - - - - - - 
        | . . . | 6 . 3 | . 7 . | 
        | 5 . . | 2 . . | . . . | 
        | 1 . 4 | . . . | . . . | 
        - - - - - - - - - - - - - 
        """
        i = 0
        row = []
        for p in string_puzzle:
            if p == '.':
                row.append(self._complete_domain)
            else:
                row.append(p)

            i += 1

            if i % self._width == 0:
                self._cells.append(row)
                row = []
            
    def print(self):
        """
        Prints the grid on the screen. Example:

        - - - - - - - - - - - - - 
        | 4 . . | . . . | 8 . 5 | 
        | . 3 . | . . . | . . . | 
        | . . . | 7 . . | . . . | 
        - - - - - - - - - - - - - 
        | . 2 . | . . . | . 6 . | 
        | . . . | . 8 . | 4 . . | 
        | . . . | . 1 . | . . . | 
        - - - - - - - - - - - - - 
        | . . . | 6 . 3 | . 7 . | 
        | 5 . . | 2 . . | . . . | 
        | 1 . 4 | . . . | . . . | 
        - - - - - - - - - - - - - 
        """
        for _ in range(self._width + 4):
            print('-', end=" ")
        print()

        for i in range(self._width):

            print('|', end=" ")

            for j in range(self._width):
                if len(self._cells[i][j]) == 1:
                    print(self._cells[i][j], end=" ")
                elif len(self._cells[i][j]) > 1:
                    print('.', end=" ")
                else:
                    print(';', end=" ")

                if (j + 1) % 3 == 0:
                    print('|', end=" ")
            print()

            if (i + 1) % 3 == 0:
                for _ in range(self._width + 4):
                    print('-', end=" ")
                print()
        print()

    def print_domains(self):
        """
        Print the domain of each variable for a given grid of the puzzle.
        """
        for row in self._cells:
            print(row)

    def is_solved(self):
        """
        Returns True if the puzzle is solved and False otherwise. 
        """
        for i in range(self._width):
            for j in range(self._width):
                if len(self._cells[i][j]) > 1 or not self.is_value_consistent(self._cells[i][j], i, j):
                    return False
        return True
    
    def is_value_consistent(self, value, row, column):
        for i in range(self.get_width()):
            if i == column: continue
            if self.get_cells()[row][i] == value:
                return False
        
        for i in range(self.get_width()):
            if i == row: continue
            if self.get_cells()[i][column] == value:
                return False

        row_init = (row // 3) * 3
        column_init = (column // 3) * 3

        for i in range(row_init, row_init + 3):
            for j in range(column_init, column_init + 3):
                if i == row and j == column:
                    continue
                if self.get_cells()[i][j] == value:
                    return False
        return True

class VarSelector:
    """
    Interface for selecting variables in a partial assignment. 

    Extend this class when implementing a new heuristic for variable selection.
    """
    def select_variable(self, grid):
        pass
    
class FirstAvailable(VarSelector):
    """
    Naïve method for selecting variables; simply returns the first variable encountered whose domain is larger than one.
    """
    def select_variable(self, grid):
        # Implement here the first available heuristic
        for i in range(grid.get_width()):
            for j in range(grid.get_width()):
                if len(grid.get_cells()[i][j]) > 1:
                    return (i, j)
        # If no variable with domain size greater than 1 is found
        return None

class MRV(VarSelector):
    """ Implements the MRV heuristic, which returns one of the variables with smallest domain. """
    def select_variable(self, grid):
        min_domain_size = float('inf')
        selected_var = None
        
        for i in range(grid.get_width()):
            for j in range(grid.get_width()):
                domain_size = len(grid.get_cells()[i][j])
                #find the one with the smallest domain size possible
                if domain_size > 1 and domain_size < min_domain_size:
                    min_domain_size = domain_size
                    selected_var = (i, j)
        return selected_var


class AC3:
    """
    This class implements the methods needed to run AC3 on Sudoku. 
    """
    def remove_domain_row(self, grid, row, column):
        """
        Given a matrix (grid) and a cell on the grid (row and column) whose domain is of size 1 (i.e., the variable has its
        value assigned), this method removes the value of (row, column) from all variables in the same row. 
        """
        variables_assigned = []

        for j in range(grid.get_width()):
            if j != column:
                new_domain = grid.get_cells()[row][j].replace(grid.get_cells()[row][column], '')

                if len(new_domain) == 0:
                    return None, True

                if len(new_domain) == 1 and len(grid.get_cells()[row][j]) > 1:
                    variables_assigned.append((row, j))

                grid.get_cells()[row][j] = new_domain
        
        return variables_assigned, False

    def remove_domain_column(self, grid, row, column):
        """
        Given a matrix (grid) and a cell on the grid (row and column) whose domain is of size 1 (i.e., the variable has its
        value assigned), this method removes the value of (row, column) from all variables in the same column. 
        """
        variables_assigned = []

        for j in range(grid.get_width()):
            if j != row:
                new_domain = grid.get_cells()[j][column].replace(grid.get_cells()[row][column], '')
                
                if len(new_domain) == 0:
                    return None, True

                if len(new_domain) == 1 and len(grid.get_cells()[j][column]) > 1:
                    variables_assigned.append((j, column))

                grid.get_cells()[j][column] = new_domain

        return variables_assigned, False

    def remove_domain_unit(self, grid, row, column):
        """
        Given a matrix (grid) and a cell on the grid (row and column) whose domain is of size 1 (i.e., the variable has its
        value assigned), this method removes the value of (row, column) from all variables in the same unit. 
        """
        variables_assigned = []

        row_init = (row // 3) * 3
        column_init = (column // 3) * 3

        for i in range(row_init, row_init + 3):
            for j in range(column_init, column_init + 3):
                if i == row and j == column:
                    continue

                new_domain = grid.get_cells()[i][j].replace(grid.get_cells()[row][column], '')

                if len(new_domain) == 0:
                    return None, True

                if len(new_domain) == 1 and len(grid.get_cells()[i][j]) > 1:
                    variables_assigned.append((i, j))

                grid.get_cells()[i][j] = new_domain
                
        return variables_assigned, False

    
    def pre_process_consistency(self, grid):
        """
        This method enforces arc consistency for the initial grid of the puzzle.

        The method runs AC3 for the arcs involving the variables whose values are 
        already assigned in the initial grid. 
        """
        Q = set()
        for i in range(grid.get_width()):
            for j in range(grid.get_width()):
                #If the domain is reduced to only 1 number, put it in the queue
                if len(grid.get_cells()[i][j]) == 1:
                    Q.add((i, j))
        
        return self.consistency(grid,Q)

   
    def consistency(self,grid, Q):
        """
        This is a domain-specific implementation of AC3 for Sudoku. 
        The method returns False if AC3 detected that the problem can't be solved with the current
        partial assignment; the method returns True otherwise. 
        """
        
        while Q:
            row, col = Q.pop()
            unit_list, failure1 = self.remove_domain_unit(grid, row, col)
            column_list, failure2 = self.remove_domain_column(grid, row, col)
            row_list, failure3 = self.remove_domain_row(grid, row, col)

            if failure1 or failure2 or failure3:
                return False  # Failure, domain size reduced to 0

            for i in unit_list:
                Q.add(i)
            for i in column_list:
                Q.add(i)
            for i in row_list:
                Q.add(i)

        return True  # Success


class Backtracking:
    """
    Class that implements backtracking search for solving CSPs. 
    """
    def search(self, grid, var_selector, ac3):
        """
        Implements backtracking search with inference. 
        """
        # Run pre-processing consistency check before starting the search
        ac3.pre_process_consistency(grid)
        #Then call backtracksearch on the remainng cells
        return self.backtrack_search(grid, var_selector, ac3)

    def backtrack_search(self, grid, var_selector, ac3):
        """
        Backtracks the search and checks new values when failure encountered with current values.
        """
        if grid.is_solved():
            return grid

        var = var_selector.select_variable(grid)   #Either MRV or FirstAvailable

        if var is None:
            return None

        row, col = var

        #Arbitrarly picks a domain value 
        for d in grid.get_cells()[row][col]:
            if grid.is_value_consistent(d, row, col):
                
                #Make copy of the current grid and copy the chosen value
                new_grid = grid.copy()
                new_grid.get_cells()[row][col] = d
                
                # Run consistency check for the assigned value
                if not ac3.consistency(new_grid,{(row,col)}):
                    continue  # Skip this value if consistency check fails
                
                #Backtrack and search for otehr values that might pass
                result = self.backtrack_search(new_grid, var_selector, ac3)
                if result is not None:
                    return result

        return None


with open('top95.txt', "r") as file:
    puzzles = file.read().splitlines()

# Create instances of the Backtracking class
backtracking_mrv = Backtracking()
backtracking_first_available = Backtracking()

# Create instances of the Variable Selectors
var_selector_MRV = MRV()
var_selector_first = FirstAvailable()

# Lists to store running times for each puzzle
running_time_mrv_all = []
running_time_first_available_all = []

count_MRV = 0
count_first_available = 0
start_MRV = time.time()
# Measure running time for MRV
for p in puzzles:
    grid = Grid()
    grid.read_file(p)

    ac3 = AC3()
    start_mrv = time.time()
    result_MRV = backtracking_mrv.search(grid, var_selector_MRV, ac3)
    end_mrv = time.time()
    
    if result_MRV.is_solved():
        count_MRV += 1

    running_time_mrv_all.append(end_mrv - start_mrv)
end_MRV = time.time()

# Measure running time for FirstAvailable
start_FA = time.time()
for p in puzzles:
    grid = Grid()
    grid.read_file(p)

    ac3 = AC3()
    start_first_available = time.time()
    result_first_available = backtracking_first_available.search(grid, var_selector_first, ac3)
    end_first_available = time.time()
    if result_first_available.is_solved():
        count_first_available += 1
    running_time_first_available_all.append(end_first_available - start_first_available)
end_FA = time.time()

# Print results
print("------------------------------------------------------------------------------------------------")
print("Total Success Count MRV:", count_MRV)
print("Total Success Count FirstAvailable:", count_first_available)
print("Total time taken for the MRV to run is : ", end_MRV - start_MRV, " seconds.") 
print("Total time taken for the FA to run is : ", end_FA - start_FA, " seconds.")
# Plot results
print("------------------------------------------------------------------------------------------------")
print("MRV RUN TIMES: ")
print(running_time_mrv_all)
print("This is the maximum it took for MRV to solve a puzzle : ", max(running_time_mrv_all))
print("------------------------------------------------------------------------------------------------")

print("FA RUN TIMES: ")
print(running_time_first_available_all)
print("This is the maximum it took for FirstAvailable to solve a puzzle : ",max(running_time_first_available_all))
print("------------------------------------------------------------------------------------------------")

#Plot results
plotter = PlotResults()
plotter.plot_results(
    running_time_mrv_all,
    running_time_first_available_all,
    "Running Time Backtracking (MRV)",
    "Running Time Backtracking (FA)",
    "running_time_plot"
)
