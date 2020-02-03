import random

from hashlib import sha256
from itertools import zip_longest

def gen_sudoku_puzzle():
    puzzle = [
        0,0,0,0,0,0,6,8,0, \
        0,0,0,0,7,3,0,0,9, \
        3,0,9,0,0,0,0,4,5, \
        4,9,0,0,0,0,0,0,0, \
        8,0,3,0,5,0,9,0,2, \
        0,0,0,0,0,0,0,3,6, \
        9,6,0,0,0,0,3,0,8, \
        7,0,0,6,8,0,0,0,0, \
        0,2,8,0,0,0,0,0,0 
    ]
    # Indices of given values
    presets = [6,7,13,14,17,18,20,25,26,27,28,36,38,40,42,44,52,53,54,55,60,62,63,66,67,73,74]
    return puzzle, presets

def solve_sudoku_puzzle(puzzle):
    solution = [
        1,7,2,5,4,9,6,8,3, \
        6,4,5,8,7,3,2,1,9, \
        3,8,9,2,6,1,7,4,5, \
        4,9,6,3,2,7,8,5,1, \
        8,1,3,4,5,6,9,7,2, \
        2,5,7,1,9,8,4,3,6, \
        9,6,4,7,1,5,3,2,8, \
        7,3,1,6,8,2,5,9,4, \
        5,2,8,9,3,4,1,6,7
    ]
    return solution

def chunk(iterable, size):
    return [iterable[i:i+size] for i in range(0, len(iterable), size)]

def flatten(iterable):
    return [item for sublist in iterable for item in sublist]

def puzzle_rows(puzzle):
    return chunk(puzzle, 9)

def puzzle_columns(puzzle):
    return list(zip(*puzzle_rows(puzzle)))

def puzzle_subgrids(puzzle, size=3, n=9):
    subgrids = []
    rows = puzzle_rows(puzzle)
    for i in range(0,n,size):
        for j in range(0,n,size):
            subgrids.append(flatten([rows[j+k][i:i+size] for k in range(size)]))
    return subgrids

def create_permutations():
    permutations = list(range(1,10))
    random.shuffle(permutations)
    permutations = [0] + permutations
    return permutations

def puzzle_permute(puzzle, permutations):
    return [permutations[x] for x in puzzle]
    
def gen_nonces():
    nonces = [
        random.SystemRandom().getrandbits(256) for _ in range(9**2)
    ]
    return nonces

def puzzle_commitment(puzzle, nonces):
    return [sha256((str(nonce)+str(val)).encode('utf-8')).hexdigest() for nonce, val in zip(nonces, puzzle)]

def all_digits_exist_once(iterable):
    digit_mask = [0 for i in range(9)]
    for x in iterable:
        digit_mask[x-1]=1
    return all(digit_mask)

if __name__ == "__main__":
    # Alice: 
    puzzle, presets = gen_sudoku_puzzle()
    solution = solve_sudoku_puzzle(puzzle)
    # Alice sends: puzzle, presets, "Hey Bob! I found the solution!"
    # Bob: "I don't believe you!"
    # Alice: "Okay wait and see.." 

    permutations = create_permutations()
    permuted_solution = puzzle_permute(solution, permutations)
    nonces = gen_nonces()
    commitment = puzzle_commitment(permuted_solution, nonces)
    # Alice: <Commitment> "Here... pick a row, column, subgrid or presets"
    
    # Bob: "Hmmm.. Okay! I pick the 3rd row"
    # Alice:
    third_row = puzzle_rows(permuted_solution)[2]
    third_row_nonces = puzzle_rows(nonces)[2]
    # Alice sends: <third_row, third_row_nonces> "Hey Bob check them out!"

    # Bob: "Let me verify..."
    third_row_commitment = puzzle_rows(commitment)[2]
    sudoku_verification = all_digits_exist_once(third_row)
    assert sudoku_verification == True
    commitment_verification = puzzle_commitment(third_row, third_row_nonces)
    assert commitment_verification== third_row_commitment
    # Bob: "Okay seems like it is correct.. but I am only 1/28 confident..."
    # Alice: "If you still ahve doubts we can repeat this as many times as you want! :)"


    