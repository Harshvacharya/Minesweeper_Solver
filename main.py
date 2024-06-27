import random
from scipy.optimize import linprog
import numpy as np
import cvxpy as cp
import sys



class MinesweeperBoard:
    def __init__(self, rows, cols, num_mines, first_move=(0,0)):
        self.rows = rows
        self.cols = cols
        self.num_mines = num_mines
        self.board = np.array([[0] * cols for _ in range(rows)])
        self.revealed = [[False] * cols for _ in range(rows)]
        self.flags = [[False] * cols for _ in range(rows)]
        self.mine=[[False]* cols for _ in range(rows)]
        self.initialize_board(first_move)
        self.reveal_cell(first_move[0],first_move[1])

    def initialize_board(self, first_move):
        """
        Initialize the Minesweeper game board with mines randomly placed.
        """
        total_cells = self.rows * self.cols
        if self.num_mines > total_cells-1:
            raise ValueError(f"Number of mines exceeds the possible number of mines.\nGiven: {self.num_mines}, Possible: {total_cells-1}")

        # Place mines randomly
        weights=[]
        points=[]
        for i in range(self.rows):
            for j in range(self.cols):
                weights.append(min(abs(first_move[0]-i)+abs(first_move[1]-j),10))
                points.append((i,j))
        weights_sum=sum(weights)
        weights=[i/weights_sum for i in weights]
        indices=np.random.choice(len(points), p=weights, replace=False, size=self.num_mines)
        for i in indices:
            x,y=points[i]
            self.mine[x][y]=True
            self.board[x][y]=-1
            for dr in range(-1, 2):
                for dc in range(-1,2):
                    if not(0<=x+dr<self.rows and 0<=y+dc<self.cols) or (dr==0 and dc==0) or self.mine[x+dr][y+dc]:
                        continue
                    self.board[x+dr][y+dc]+=1

    def update_neighbors(self, row, col):
        """
        Update neighboring cells of a mine with appropriate counts.
        """
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)]
        for dr, dc in directions:
            nr, nc = row + dr, col + dc
            if 0 <= nr < self.rows and 0 <= nc < self.cols and self.board[nr][nc] != -1:
                self.board[nr][nc] += 1

    def reveal_cell(self, row, col):
        """
        Reveal a cell on the board and recursively reveal neighboring cells if empty.
        """
        if not (0 <= row < self.rows and 0 <= col < self.cols) or self.revealed[row][col]:
            return
        self.revealed[row][col] = True
        if self.board[row][col] == 0:
            for dr in range(-1, 2):
                for dc in range(-1, 2):
                    self.reveal_cell(row + dr, col + dc)
    
    def flat_index(self, r, c):
        """
        Convert board_index to flat_index
        """
        return c+self.cols*r
    
    def board_index(self, i):
        """
        Convert flat_index to board_index
        """
        return (i//self.cols, i%self.cols)
    
    def flag_cell(self, row, col):
        """
        Flag a cell on the board.
        """
        self.flags[row][col] = True

    def get_board(self):
        """
        Print the game board with revealed cells and flags.
        """
        gb=[['.'] * self.cols for i in range(self.rows)]
        for row in range(self.rows):
            for col in range(self.cols):
                
                if self.revealed[row][col]:
                    if self.mine[row][col]:
                        gb[row][col]='*'
                    else:
                        gb[row][col]=self.board[row][col]
                elif self.flags[row][col]:
                    gb[row][col]='F'
                else:
                    gb[row][col]='.'
        return gb

    def print_board(self):
        gb=self.get_board()
        for i in gb:
            for j in i:
                print(j, end=' ')
            print()
    
    def check_game_over(self):
        """
        Check if the game is over (all mines revealed or all non-mine cells revealed).
        """
        for row in range(self.rows):
            for col in range(self.cols):
                if self.mine[row][col] and self.revealed[row][col] and not self.mine[row][col]:
                    return True, False, "Game over! You stepped on a mine!"
                if not self.mine[row][col] and not self.revealed[row][col] and not self.flags[row][col]:
                    return False,False, ""
        return True,True, "Congratulations! You won the game!"

class Solver:
    def __init__(self, board):
        self.board=board
        self.obj_coeffs=np.array([-1]*self.board.rows*self.board.cols)
        self.bounds=np.array([(0,1)]*self.board.rows*self.board.cols)
        self.A_eq=np.array([[0]*self.board.rows*self.board.cols]*self.board.rows*self.board.cols*2)
        self.b_eq=np.array([0]*self.board.rows*self.board.cols*2)
        self.to_visit=[]
        self.visited=np.array([False]*self.board.rows*self.board.cols)
        # print(self.A_eq)
    
    def set_value(self, i, v):
        self.A_eq[self.board.rows*self.board.cols+i][i]=1
        self.b_eq[self.board.rows*self.board.cols+i]=v
    
    def get_value(self, i):
        return (self.A_eq[self.board.rows*self.board.cols+i][i]==1 , self.b_eq[i])
    
    def unset_value(self, i):
        self.A_eq[self.board.rows*self.board.cols+i][i]=0
        self.b_eq[self.board.rows*self.board.cols+i]=0
    

    def get_matrices(self):
        board=self.board.get_board()
        A=[[1]*self.board.rows*self.board.cols]
        b=[self.board.num_mines]
        for i in range(self.board.rows):
            for j in range(self.board.cols):
                if(board[i][j]=='.'):
                    continue
                if(board[i][j]!='.' and board[i][j]!='*' and board[i][j]!='F'):
                    l=[0]*self.board.rows*self.board.cols
                    l[i*self.board.cols+j]=1
                    A.append(l)
                    b.append(0)
                    l=[0]*self.board.rows*self.board.cols
                    mines=int(board[i][j])
                    for dx in range(-1, 2):
                        for dy in range(-1, 2):
                            if(dx==0 and dy==0):
                                continue
                            i2=i+dx
                            j2=j+dy
                            if(0<=i2<self.board.rows and 0<=j2<self.board.cols):
                                l[i2*self.board.cols+j2]=1
                    A.append(l)
                    b.append(mines)
        return A, b
    
    
    def solve(self):
        A, b=self.get_matrices()
        A=np.array(A)
        b=np.array(b)
        params=self.board.rows*self.board.cols
        iden=np.identity(params)
        z=np.zeros(params)
        o=np.ones(params)
        x=cp.Variable(params)
        prob = cp.Problem(cp.Minimize(cp.quad_form(x, iden)),
                 [A @ x == b,
                  iden@x>=z,
                  iden@x<=o])
        prob.solve()
        # print(A)
        # print(b)
        # print(x.value)
        board=self.board.get_board()
        locked=[]
        for i in range(self.board.rows):
            for j in range(self.board.cols):
                id=i*self.board.cols+j
                if board[i][j]=='.':
                    locked.append((x.value[id], i, j))
        locked=sorted(locked)
        elem=0
        
        while(elem<len(locked) and locked[elem][0]<1e-2):
            value, i, j=locked[elem]
            self.board.reveal_cell(i, j)
            elem+=1
        
        if elem==0:
            print("Taking a Guess.\nBest probability:", locked[0][0], f"at {locked[0][1]}, {locked[0][2]}")
            for i in range(self.board.rows):
                for j in range(self.board.cols):
                    id=i*self.board.cols+j
                    # print(f"{np.round(x.value[id], 2):4.2f}", end=' ')
                # print()
            value, i, j=locked[0]
            self.board.reveal_cell(i, j)
        return 1
        
        
    def update(self):
        print()
        self.board.print_board()
        print()
        go, win, message=self.board.check_game_over()
        if(go):
            print(message)
            return
        
        
        gb=self.board.get_board()
        for row in range(self.board.rows):
            for col in range(self.board.cols):
                if gb[row][col]=='*':
                    self.board.print_board()
                    print("Solver was not able to solve it!")
                    return
        if not self.solve():
            print("Could not solve the lpp")
            return
        self.update()
            
        
        
        
                
                                
# Example usage:
# np.random.seed(8)
if __name__=="__main__":
  rows=20
  cols=20
  sys.setrecursionlimit(rows*cols*8)
  board = MinesweeperBoard(rows, cols, 100
                           ,(np.random.randint(0, rows), np.random.randint(0, cols)))
  # board.flags=board.mine
  
  board.print_board()
  
  solver=Solver(board)
  solver.update()

