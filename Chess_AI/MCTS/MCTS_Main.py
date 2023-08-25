import numpy as np
import copy
import chess

from Chess_AI.MCTS.self_play import start

"""
This file contains the implementation for the Monta Carlo Tree Search Algorithm, but modified for AlphaZero

Firstly, the UCB(Upper Confidence Bound) equation (V + C*sqrt( ln(N) / n) ) that is used to determine what node is choosen to traverse
to is replaced by the Q + U equation , where Q is the mean value of the next possible state and U is the function of P ( Prior Probability )
and N ( visits ) 

Secondly , instead of doing a rollout to decide the P and V values of a node, the deep neural network is called

"""

class MCTS(object):
    
    """
    This class is the structure of the MCTS algorithm
    """
    
    def __init__(self, Neural_Network):
        
        self.root = Node(None, 1.0)
        self.Network = Neural_Network
        
    def iteration_of_MCTS(self, state, last = 0):
        """
        The job of this function is to traverse down the tree to hit the leaf, get the value and backprapogate the value
        up the tree
        """
        while(1):
            last, answer = self.root.is_leaf(last)
            if answer or last:
                break
            # Greedily select the next move
            move, node = self.root.traverse_tree(5)
            move = chess.Move.from_uci(str(move))
            state.push(action)
        probability, leaf_value = self.Network(state)
        
        
        s = start(state)
        end, winner = s.results(state, state.result())
        
        
        if not end:
            self.root.leaf_expansion(probability)
        else :
            if winner == -1:
                leaf_value = 0.0
            else:
                leaf_value = 1.0
        
        self.root.backpropagation(-leaf_value)
        
    def move_probabilities(self, state, temperature = 1e-3):
        """
        The job of this function is to return available moves along with their probabilities
        """
        for n in range(10000):
            state_copy = copy.deepcopy(state)
            self.iteration_of_MCTS(state_copy)
        
        act_visits = [(act, node.N) for act, node in self.root.children.items()]
        moves, visits = zip(*act_visits)
        
        act_probs = softmax(1.0/temperature * np.log(np.array(visits) + 1e-10))
        return moves, act_probs
    
    def update_tree(self, last_move):
        """
        The job of this function is to update the tree keeping it up with the last action 
        taken by the MCTS algorithm
        """
        if last_move in self.root.children:
            self.root = self.root.children[last_move]
            self.root.parent = None
        else:
            self.root = Node(None, 1.0)

class agent_MCTS(object):
    """
    The job of this class is to run the MCTS algorithm and output the best move for the agent
    """
    def __init__(self, policy_value_function, training=0):
        self.mcts = MCTS(policy_value_function)
        self.training = training
    
    def choose_move(self, board, temperature = 1e-3, probability=0):
        
        legal_moves = list(board.legal_moves)
        probability_for_moves = np.zeros(len(legal_moves))
        moves, probs = self.mcts.move_probabilities(board, temperature)
        
        index = 0
        for i in list(moves):
            probability_for_moves[index] = probs[index]
            index += 1
            
        if self.training:
            move = np.random.choice(moves, p = 0.75 * probs + 0.25 * np.random.dirichlet(0.3 * np.ones( len(probs) )))
            self.mcts.update_tree(move)
        else:
            move = np.random.choice(moves, p=probs)
            self.mcts.update_tree(-1)
            
        if probability:
            return move, probability_for_moves
        else:
            return move
    
    def reset_player(self):
        self.mcts.update_tree(-1)
        
    def set_player(self, p1):
        self.player = p1

class Node(object):
    """
    This creates and stores the node in the tree. Each node stores the values Q, P and U
    """
    
    def __init__(self, parent, probability):
        self.parent = parent
        
        self.states = {}
        self.children = {}
        
        self.N = 0
        self.Q = 0
        self.P = probability 
        self.U = 0
    
    def traverse_tree(self, Cpunt):
        """
        The job of this function is to traverse down the tree
        """
        return max(self.children.items(), key = lambda act_node: act_node[1].node_value(Cpunt))
    
    def leaf_expansion(self, move_history):
        """
        The job of this function was to expand the current leaf node
        """
        for move, probability in move_history:
            if move not in self.children:
                self.children[move] = Node(self, probability)
    
    def node_value(self, Cpunt):
        
        """
        The job of this function is to output the value of the node
        """        
        
        self.U = (Cpunt*self.P*np.sqrt(self.parent.N)/(1+self.N))
        return self.Q + self.U
    
    def update_leaf_node(self, leaf_value):
        """
        The job of this function is to update the current value of the leaf node
        """
        
        #Count visit
        self.N += 1
        #Update Q, a running average of values of all the visits
        self.Q += 1.0*(leaf_value - self.Q) / self.N
        
    def backpropagation(self, leaf_value):
        """
        The job of this function is to backpropagate up the tree and update all the node
        values in it's path
        """
        # If the current node is not the root, the node's parent should be updated first
        if self.parent:
            self.parent.backpropagation(-leaf_value)
        
        self.update_leaf_node(leaf_value)
        
    def is_leaf(self, last):
        """
        The job of this function is to decide if the current node is a leaf or not
        It does this in two ways
            1. It checks to see if this node has children
                A. If it does, then it's not a leaf node
                B. If it doesn't, then it's a leaf node
            2. It checks to see if the last node has the exact same move
                A. If it does then it's a leaf node
                B. If it doesn't then it's not a lead node
                
        Step 2 is does so that the algorithm doesn't go into infinite loops
        """
        
        if last == self.children:
            return True, 0
        return self.children, self.children=={}
    
    def is_root(self):
        return self.parent is None
    
def softmax(x):
    """
    This is a custom softmax function for alphazero
    """
    probabilities = np.exp(x-np.max(x))
    probabilities /= np.sum(probabilities)
    return probabilities


            
        
        
            