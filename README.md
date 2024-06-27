# Minesweeper Solver: A Quadratic Programming Approach

## Overview

Welcome to the Minesweeper Solver project! This project implements an innovative solution to solve the classic Minesweeper game using quadratic programming, achieving significantly better performance compared to traditional backtracking methods. Our solver approximates the expected number of mines in each cell and optimally distributes these expectations, providing a solution in weakly polynomial time.

## Why This Project is Special

### Traditional Approach: Backtracking

The most common method for solving Minesweeper is backtracking. This involves exploring all possible configurations of mines in a given grid, which is a highly computationally intensive process. The key shortcomings of the backtracking approach are:

1. **Exponential Time Complexity**: Backtracking can take an enormous amount of time to find a solution, especially for larger grids, as it explores all possible combinations.
2. **Inefficiency**: It often performs redundant calculations and doesn't leverage probabilistic insights, making it slow and resource-intensive.
3. **Scalability Issues**: As the grid size increases, the performance degrades rapidly, making it impractical for larger grids.

### Our Approach: Quadratic Programming

Our Minesweeper Solver overcomes these limitations by employing a quadratic programming (QP) approach. Here's how it works:

1. **Probability Estimation**: We use a variable for each square in the grid to represent the probability (or expected number) of having a mine.
2. **Constraints Formulation**: 
   - For a grid cell with a number \( n \), the sum of probabilities of mines in its neighboring cells is constrained to be \( n \).
   - The probability of a mine in any cell is between 0 and 1.
   - The total number of mines is fixed, so the sum of all probabilities equals the number of mines.
3. **Objective Function**: Instead of maximizing entropy (which is computationally challenging), we approximate by minimizing the sum of squares of probabilities (\( \sum p^2 \)). This objective helps in distributing the probabilities as uniformly as possible.
4. **Quadratic Programming Solution**: The resulting problem is a quadratic programming problem that can be solved in weakly polynomial time using any standard QP solver.

## Implementation Details

### Prerequisites

To run the Minesweeper Solver, you need the following:

- Python 3.x
- A quadratic programming solver library (e.g., `cvxopt`, `quadprog`, or similar)

### Installation

1. Clone this repository:
    ```sh
    git clone https://github.com/yourusername/minesweeper-solver.git
    cd minesweeper-solver
    ```

2. Install the required packages:
    ```sh
    pip install -r requirements.txt
    ```

### Usage

1. Prepare your Minesweeper grid input in a format where each cell's state (number or empty) is defined.
2. Run the solver:
    ```sh
    python solver.py input_grid.txt
    ```
3. The output will provide the expected number of mines for each cell, which can be interpreted as the solver's solution.

### Example

Consider a simple 5x5 Minesweeper grid. The solver will read the grid, set up the quadratic programming problem with the defined constraints and objective function, and output the expected number of mines for each cell.

## Advantages of Our Approach

- **Efficiency**: Solves the problem in weakly polynomial time, making it suitable for larger grids.
- **Optimality**: Provides a probabilistic distribution of mines that is close to the actual solution, reducing the need for exhaustive search.
- **Scalability**: Capable of handling larger grids without significant performance degradation.

## Conclusion

Our Minesweeper Solver demonstrates a novel application of quadratic programming to a classic problem, significantly improving efficiency and scalability. We invite you to explore, use, and contribute to this project. Your feedback and suggestions are highly valued!

## License

This project is licensed under the MIT License. See the LICENSE file for details.
