# Lab 2 : Nim Game
The goal of this lab is to create agents able to play efficiently the Nim Game, using both rule-based and evolutionary strategies.
## 1. Rule-based agent
This version is based on a demonstrated mathematic strategy, which is to always play moves with a nim-sum $\neq$ 0 in order to not be the last to pick up a stick. The nim-sum is the sum of an XOR applied on every line of the game, coded with 1 as sticks and 0 as nothing.
