# MILP_IVLBC
MILP-Based Differential Characteristics Search Problem for Block Cipher IVLBC

## Source Code

There are two files in this source code:
- Ineq_Reduction.py
- IVLBC.py

## Generation and Reduction of Linear Inequalities

- First, Ineq_Reduction.py generates linear inequalities. Then, minimize the linear inequalities using GUROBI (to reduce the number of active S-boxes or to optimize the probability of differential characteristics).

- The command 'python Ineq_Reduction.py IVLBC sbox GUROBI -' gives the list of minimized linear inequalities to reduce the number of active S-boxes.

- The command 'python Ineq_Reduction.py IVLBC prob GUROBI -' provides the list of minimized linear inequalities to optimize the probability of differential characteristics.

## MILP model to minimize the number of active S-boxes and optimize the probability of differential characteristics

- Number of active S-boxes and high probability differential characteristic for 7-round IVLBC is searched using the following command:
```bash
    python IVLBC.py 64 7 5 4 no_fix 1 possible GUROBI
```
