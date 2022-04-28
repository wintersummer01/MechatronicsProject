# pacmanAgents.py
# ---------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


from pacman import Directions
from game import Agent
import random
import game
import util

def createTeam(firstIndex, secondIndex, isRed,
               first = 'LeftTurnAgent', second = 'GreedyAgent'):
  """
  This function should return a list of two agents that will form the
  team, initialized using firstIndex and secondIndex as their agent
  index numbers.  isRed is True if the red team is being created, and
  will be False if the blue team is being created.

  As a potentially helpful development aid, this function can take
  additional string-valued keyword arguments ("first" and "second" are
  such arguments in the case of this function), which will come from
  the --redOpts and --blueOpts command-line arguments to capture.py.
  For the nightly contest, however, your team will be created without
  any extra arguments, so you should make sure that the default
  behavior is what you want for the nightly contest.
  """

  # The following line is an example only; feel free to change it.
  return [firstIndex, secondIndex]

class LeftTurnAgent(game.Agent):
    "An agent that turns left at every opportunity"

    def registerInitialState(self, gameState):
        """
        This method handles the initial setup of the
        agent to populate useful fields (such as what team
        we're on).

        A distanceCalculator instance caches the maze distances
        between each pair of positions, so your agents can use:
        self.distancer.getDistance(p1, p2)

        IMPORTANT: This method may run for at most 15 seconds.
        """

        '''
        Make sure you do not delete the following line. If you would like to
        use Manhattan distances instead of maze distances in order to save
        on initialization time, please take a look at
        CaptureAgent.registerInitialState in captureAgents.py.
        '''
        CaptureAgent.registerInitialState(self, gameState)

        '''
        Your initialization code goes here, if you need any.
        '''

    def chooseAction(self, gameState):
        """
        Picks among actions randomly.
        """
        actions = gameState.getLegalActions(self.index)

        '''
        You should change this in your own agent.
        '''
        legal = state.getLegalPacmanActions()
        current = state.getPacmanState().configuration.direction
        if current == Directions.STOP: current = Directions.NORTH
        left = Directions.LEFT[current]
        if left in legal: return left
        if current in legal: return current
        if Directions.RIGHT[current] in legal: return Directions.RIGHT[current]
        if Directions.LEFT[left] in legal: return Directions.LEFT[left]
        return Directions.STOP

class GreedyAgent(Agent):
    def __init__(self, evalFn="scoreEvaluation"):
        self.evaluationFunction = util.lookup(evalFn, globals())
        assert self.evaluationFunction != None

        def registerInitialState(self, gameState):
            """
            This method handles the initial setup of the
            agent to populate useful fields (such as what team
            we're on).

            A distanceCalculator instance caches the maze distances
            between each pair of positions, so your agents can use:
            self.distancer.getDistance(p1, p2)

            IMPORTANT: This method may run for at most 15 seconds.
            """

            '''
            Make sure you do not delete the following line. If you would like to
            use Manhattan distances instead of maze distances in order to save
            on initialization time, please take a look at
            CaptureAgent.registerInitialState in captureAgents.py.
            '''
            CaptureAgent.registerInitialState(self, gameState)

            '''
            Your initialization code goes here, if you need any.
            '''

        def chooseAction(self, gameState):
            """
            Picks among actions randomly.
            """
            actions = gameState.getLegalActions(self.index)

            '''
            You should change this in your own agent.
            '''

        # Generate candidate actions
           legal = state.getLegalPacmanActions()
           if Directions.STOP in legal: legal.remove(Directions.STOP)

            successors = [(state.generateSuccessor(0, action), action) for action in legal]
            scored = [(self.evaluationFunction(state), action) for state, action in successors]
            bestScore = max(scored)[0]
            bestActions = [pair[1] for pair in scored if pair[0] == bestScore]
            return random.choice(bestActions)

def scoreEvaluation(state):
    return state.getScore()
