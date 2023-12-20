# Lab 10 : Tic-Tac-Toe Player with Reinforcement Learning

*The work on this lab was highly inspired from the work done in class with Pr. Squillero.*

## Representation of a game

The game of Tic-Tac-Toe is played on a 3*3 grid. To avoid having to handle coordinates, the principle of the magical square was used : each position in the grid is encoded by a number such as the sum of each row, column and diagonal of the gris is always 15.
Here is the magical square used :

2 | 7 | 6 \
--------  \
9 | 5 | 1 \
--------  \
4 | 3 | 8

This way, each possible state of the game can be represented as a tuple of two sets : the first contains all the positions of the X, while the second contains all the positions of the O.
Because of this representation using a magical square, the method to verify if a state is final is to check whether there is any combination of 3 positions whose sum is equal to 15 in each set.

The first player is always the X player.

## Design of the agent

To create an agent able to play Tic-Tac-Toe, we first need to collect reward values for each possible state. In order to do that, we use the Monte-Carlo method, which consists in generating randomly a high number of games (which are sequences of states that end with either a winning state or a draw state), and for each of them, update all the involved states positively or negatively depending on the final reward. The final reward is either 1, if X player wins, -1 if O player wins, or 0 if there is a draw. The result of this is a dictionary of state-values where a higher value indicates that the state is more likely to support X player's victory, while a lower value tends to promote O player's victory.

Using this dictionary, we can infer the agent's strategy, which simply consists of looking all potential successor states of a given state (all possible moves for the agent), and pick the one who has the best value in the dictionary. The best value is the one closest to 1 if the agent plays X, or the one closest to -1 if the agent plays O.

## Performance of the agent

To test the performance of the agent's policy, we simulate 100 games versus a random playing agent, where each player is X half of the time and O the other half of the time. The performance of the agent can be evaluated using its win rate. To get more reliable results, we repeat this process as many times as it takes for the 95% confidence intervals on the average win rate to be completely disjoint, which means one strategy completely trumps the other.

Using a simulation of $10^5$ games for the learning process of the agent, going over more than 5200 different states, the evaluation shows that the RL agent is clearly much better than a random player, as it gets an average win rate between 90% and 95%. This means that despite using a completely random process for its creation, the algorithm was actually capable to learn the most valuable moves in almost every situation. This is even clearer when the RL agent only plays X, because it has a win rate of 100%, due to the fact that tic-tac-toe clearly advantages the first players given that their first move is to put an X in the center of the grid.
