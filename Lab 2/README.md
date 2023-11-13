# Lab 2 : Nim Game

The goal of this lab is to create agents able to play efficiently the Nim Game, using both rule-based and evolutionary strategies.

## 1. Rule-based agent

This version is based on a demonstrated mathematic strategy, which is to always play moves with a nim-sum $\neq$ 0 in order to not be the last to pick up a stick. The nim-sum is the sum of an XOR applied on every line of the game, coded with 1 as sticks and 0 as nothing.

*Optimal :* The initial rule-based strategy, as proposed in the template. The idea is to see for each move possible the ones that have a nim-sum $\neq$ 0, and to choose randomly one of them.

*Optimal_rule_based1 :* The strategy mentioned above can be improved, because in the good moves a player can make, there are some better than others, especially if we consider that the opponent will try to make the best moves as well. This strategy takes the basis idea of the first one, but for each good move one can do, the analysis function is called once again to compute what good moves the opponent could do after. If there exists a good move that lets no good moves to the opponent, then it's considered to be the best one we can play.
When opposed to the optimal strategy, this strategy is usually 5 times more efficient than the first one.

*Optimal_rule_based2 :* This strategy takes the previous one as basis, except in this case, whether there exists a best move or not among the good ones, we always choose the move that lets to the opponent the smallest number of good moves. This improvement doesn't make this strategy better than the last one, but it is expected to be more efficient against agents playing randomly, as they are less likely to choose a good move if their number of possible good moves is low.

*Optimal_rule_based3 :* Here we start again from the previous strategy, but this time we always choose the move that lets the less good moves to the opponent, even if there are no moves with a nim-sum $\neq$ 0. Once again, this is to improve efficiency against random strategies.

This strategy is not absolutely optimal, because it would be even more efficient if it computed not only one move, but the whole game in advance. However, such a strategy would require exponential computation time, and couldn't be implemented in reasonable time. Hence, for practical reasons, the optimal_rule_based3 strategy will be considered as the best possible strategy in the next steps.

