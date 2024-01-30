import numpy as np 
from game import Game, Player, Move, Board
from copy import deepcopy
from tqdm.notebook import tqdm
from time import time
from queue import Queue
from collections import defaultdict
import random 
import pickle
import os 


'''
-------------------------------------------
|                 UTILS                   |
-------------------------------------------
'''

'''Returns the position corresponding to potentially playable cubes, on the periphery of the Quixo board'''
def get_periphery_board(board) :
    shape_y, shape_x = board.shape
    periphery_cubes = set()
    for i in range(shape_x) :
        periphery_cubes.add((0,i))
        periphery_cubes.add((shape_y-1,i))
    for j in range(shape_y) :
        periphery_cubes.add((j,0))
        periphery_cubes.add((j, shape_x-1))
    
    return periphery_cubes


'''For each playable cube, compute the possible successors, depending on the movement of slide, and returns the move and the associated board'''
def get_successors(player, board : Board) :
    '''Check which cube can be played'''
    playable_cubes = []
    for pos in get_periphery_board(board) :
        if board[pos] == -1 or board[pos] == player :
            playable_cubes.append(pos)
    
    successors = []
    for pos in playable_cubes :
        for slide_direction in board.acceptable_slides(pos) :
            new_board = deepcopy(board)
            new_board[pos] = player
            new_board.slide(pos, slide_direction)
            # Coordinates are inverted in the Game class, so they are returned inverted here for conversion
            successors.append([((pos[1], pos[0]), slide_direction), new_board.board])
        
    return successors


'''Class that represents a recursive tree, for application of MinMax algorithm'''
class Tree :
    def __init__(self, board = None, children : list = None) -> None:
        self.board = board
        self.children = children if children is not None else dict()
        # Moves are the plays corresponding one to one to the children boards
        self.score = -1        
    
    def get_leaves(self) :
        if self.children == dict() :
            return [self]
        leaves = []
        for move, node in self.children.items() :
            leaves.extend(node.get_leaves())
        
        return leaves


'''
-----------------------------------------------
|              MinMax Algorithm               |
-----------------------------------------------
'''

'''Scoring function that considers only the maximum number of cubes of the player aligned'''
def score(player, state : Board) :
    board = state.board
    score = 5
    for row in board :
        new_score = np.count_nonzero(row == player)
        score = min(score, 5 - new_score)
    
    for col in range(board.shape[1]) :
        new_score = np.count_nonzero(board[:,col] == player)
        score = min(score, 5 - new_score)
    
    diag1 = board.diagonal()
    new_score = np.count_nonzero(diag1 == player)
    score = min(score, 5 - new_score)

    diag2 = np.fliplr(board).diagonal()
    new_score = np.count_nonzero(diag2 == player)
    score = min(score, 5 - new_score)

    return score

'''Imrovement of naive score, that takes into account the score for the opponent --> The better the score of the opponent, the lesser the score of the state for the player'''
def score_consider_opponent(player, state : Board) :
    player_score = score(player, state)
    opponent_score = score(1 - player, state)
    score = player_score + (5 - opponent_score)

    return score
    

'''Computes all the next possible moves and boards until a given depth is reached, for further application of MinMax.
Because of the time limit, the tree is generated in breadth-first, to have in the end as much as possible a tree with all branches being the same size'''
def get_states_tree(player : int, board : Board, max_time, start_time = None) :
    if start_time is None :
        start_time = time()
    
    root = Tree(board)
    depth = 0
   
    # The Queue structure is not really fitting here, as we need to access elements in the middle of it to check for the time constraint
    queue = []
    queue.append((root, depth))

    explored_in_current_depth = 0
    while len(queue) != 0 :
        # We check if the execution time is above the limit, and if it is the case we accept to finish the current depth only if at least half of it has been explored
        # If that is not the case, the tree is returned as such, with branches of differnet lengths
        if (time() - start_time) > max_time :
            # remaining_in_current_depth = np.count_nonzero(np.array(queue)[:,1] == depth)
            # if remaining_in_current_depth > explored_in_current_depth :
                break
            
        old_depth = depth
        tree, depth = queue.pop(0)

        if tree.board.check_winner() != -1 :
            continue
        
        if depth != old_depth :
            player = 1 - player
            explored_in_current_depth = 1
        else :
            explored_in_current_depth += 1

        for move, succ in get_successors(player, tree.board) :
            child = Tree(Board(succ))
            tree.children[move] = child
            queue.append((child, depth + 1))
            
    return root


'''Computes the score of the leaves of the tree (furthest anticipated moves) for further application of MinMax'''
def valuate_tree(player : int, states_tree : Tree, score_function) :
    valuated_tree = deepcopy(states_tree)
    for leaf in valuated_tree.get_leaves() :
        leaf.score = score_function(player, leaf.board)
    
    return valuated_tree


'''MinMax Algorithm where the root node is always the player who tries to minimize the score --> Returns the Move as well as the score, as we want to know what to play'''
def min_max(valuated_tree : Tree, compute_max=False) :
    if valuated_tree.children == dict() :
        return None, valuated_tree.score
    
    options = []
    for move, child in valuated_tree.children.items() :
        options.append([move, min_max(child, compute_max=bool(1-compute_max))[1]])
    
    if compute_max :
        return max(options, key = lambda t : t[1])
    else : 
        return min(options, key = lambda t : t[1])
    

'''Player based on the precedently defined MinMax algorithm'''
class MinMaxPlayer(Player) :
    def __init__(self, score_function) -> None:
        super().__init__()
        self.score_function = score_function
    
    def make_move(self, game: Game) -> tuple[tuple[int, int], Move]:
        board = Board(game.get_board())
        player = game.get_current_player()
        tree = get_states_tree(player, board, 0.5)
        value_tree = valuate_tree(player, tree, self.score_function)
        move, score = min_max(value_tree)
        return move
    


'''
----------------------------------------------
|          Reinforcement Learning            |
----------------------------------------------
'''

'''Player that has to be trained to generate a Q-table. It uses a epsilon-greedy strategy'''
class QLearningPlayer(Player) :
    def __init__(self, q_table = None, learning_rate = 0.1, discount_rate = 0.5, exploration_rate = 0.1) -> None:
        super().__init__()
        self.q_table = q_table if q_table is not None else dict()
        self.learning_rate = learning_rate
        self.discount_rate = discount_rate
        self.exploration_rate = exploration_rate
        self.is_learning = False
    
    def train(self, save_file : str, num_iterations : int = 100, opponent : Player = None) :
        if os.path.exists(f'./{save_file}') :
            with open(save_file, 'rb') as f :
                self.q_table = pickle.load(f)
            return

        self.is_learning = True

        for i in tqdm(range(num_iterations // 2)) :
            if i % 50_000 == 0 :
                with open(save_file, 'wb') as f :
                    pickle.dump(self.q_table, f)
            g = Game()
            g.play(self, opponent)
        for i in tqdm(range(num_iterations // 2)) :
            if i % 50_000 == 0 :
                with open(save_file, 'wb') as f :
                    pickle.dump(self.q_table, f)
            g = Game()
            g.play(opponent, self)

        # Save table for later use
        with open(save_file, 'wb') as f :
            pickle.dump(self.q_table, f)

        self.exploration_rate /= 10 
        self.is_learning = False

    def make_move(self, game: Game) -> tuple[tuple[int, int], Move]:
        board = Board(game.get_board())
        player = game.get_current_player()
        state = frozenset((board, player))
        if self.is_learning :
            if state not in self.q_table :
                self.q_table[state] = defaultdict(lambda : 0)
            for action, next_board in get_successors(player, board) :
                next_board = Board(next_board)
                next_state = frozenset((next_board, player))
                # The immediate reward is the score used for MinMax (reverted as we want to maximize the reward) and a significant bonus if a winning state has been reached
                reward = 5 - score_consider_opponent(player, next_board) + 10 * (next_board.check_winner() == player)
                if next_state in self.q_table :
                    self.q_table[state][action] += self.learning_rate * (reward + self.discount_rate * max(self.q_table[next_state].values()) - self.q_table[state][action])
                else :
                    self.q_table[state][action] += self.learning_rate * (reward - self.q_table[state][action])
        
            # Exploration
            if np.random.random() < self.exploration_rate :
                return random.choice(list(self.q_table[state].keys()))

            # Exploitation
            return max(self.q_table[state], key=self.q_table[state].get)
        
        else :
            if state in self.q_table :
                # Exploration
                if np.random.random() < self.exploration_rate :
                    return random.choice(list(self.q_table[state].keys()))

                # Exploitation
                return max(self.q_table[state], key=self.q_table[state].get)
            else :
                # If the player didn't learn this state, do a random move
                possible_moves = np.array(get_successors(player, board), dtype=set)[:,0]
                
                return random.choice(possible_moves)


'''
-----------------------------------------
|            Utility Players            |
-----------------------------------------
'''

'''Completely random player, against which performance of other players are tested'''
class RandomPlayer(Player):
    def __init__(self) -> None:
        super().__init__()

    def make_move(self, game: 'Game') -> tuple[tuple[int, int], Move]:
        from_pos = (random.randint(0, 4), random.randint(0, 4))
        move = random.choice([Move.TOP, Move.BOTTOM, Move.LEFT, Move.RIGHT])
        return from_pos, move
    

'''Human Player adds the possibility to play directly against an algorithmic player'''
class HumanPlayer(Player) :
    def __init__(self) -> None:
        super().__init__()

    def make_move(self, game: Game) -> tuple[tuple[int, int], Move]:
        print(f"Turn : Player {game.get_current_player()}")
        print(game.get_board())
        x = int(input("X"))
        y = int(input("Y"))
        pos = (y,x)
        move = input('Move')
        if move == 't' :
            true_move = Move.TOP
        elif move == 'r' :
            true_move = Move.RIGHT
        elif move == 'b' :
            true_move = Move.BOTTOM
        elif move == 'l' :
            true_move = Move.LEFT

        return (pos, true_move)


'''
---------------------------------------------
|          Strategies evaluation            |
---------------------------------------------
'''

'''Simulates a certain number of games between two strategies, and displays the final performance of both strategies. To avoid potential edge associated to being the beginning player, player1 plays half the time first, half the time second.'''
def evaluate_strategies(player1 : Player, player2 : Player, deterministic_only = False) :
    # If at least one strategy includes randomness, we run 100 games to get reliable results
    if not deterministic_only :
        number_of_games = 100
    # If both strategies are deterministic, then running several games won't change anything in the results (we only need to play 2 games, one for each starting position)
    else :
        number_of_games = 2
    half_games = number_of_games // 2
    victories_1 = victories_2 = 0
    for _ in tqdm(range(half_games)) :
        g = Game()
        g.play(player1, player2)
        if g.check_winner() == 0 :
            victories_1 += 1
        else : 
            victories_2 += 1
    
    for _ in tqdm(range(half_games)) :
        g = Game()
        g.play(player2, player1)
        if g.check_winner() == 1 :
            victories_1 += 1
        else :
            victories_2 += 1
    
    return victories_1, victories_2


def main() :    
    # Win rate of MinMaxPlayer : 92%
    res_min_max = evaluate_strategies(MinMaxPlayer(score_consider_opponent), RandomPlayer())
    print(f"Win rate of MinMaxPlayer : {res_min_max}")

    
    # Win rate of QPlayer trained on 100 000 games : 51%
    q_player = QLearningPlayer()
    q_player.train('q_table.pkl', 100_000, RandomPlayer())
    res_q = evaluate_strategies(q_player, RandomPlayer())
    

if __name__ == '__main__':
    main()
