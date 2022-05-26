# myTeam.py
# ---------
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


from captureAgents import CaptureAgent
import random, time, util
from game import Directions
import game
from keyboardAgents import KeyboardAgent

#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
               first = 'week12DefAgent', second = 'week12AtkAgent'):
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
  return [eval(first)(firstIndex), eval(second)(secondIndex)]

##########
# Agents #
##########

class week13DefAgent(CaptureAgent):
  def registerInitialState(self, gameState):
    CaptureAgent.registerInitialState(self, gameState)
    self.home = gameState.getInitialAgentPosition(self.index)
    self.fortress = self.getFortressPosition(gameState)

  def getFortressPosition(self, gameState):
    # standard = (15, 8)
    # myCapsules = self.getCapsulesYouAreDefending(gameState)
    # minDistance = 9999 
    # for myCapsule in myCapsules:
    #   toFortress = util.manhattanDistance(standard, myCapsule)
    #   if minDistance > toFortress:
    #     fortress = myCapsule
    #     minDistance = toFortress

    myFoods = self.getFoodYouAreDefending(gameState).asList()
    # oppHome = gameState.getInitialAgentPosition(self.getOpponents(gameState)[0])
    if self.red:
      oppHome = (32, 16)
    else:
      oppHome = (1, 1)
      
    minDistance = 9999
    for myFood in myFoods:
      DistanceToFood = self.getMazeDistance(oppHome, myFood)
      if DistanceToFood < minDistance:
        minDistance = DistanceToFood
        fortress = myFood

    return fortress

  def chooseAction(self, gameState):
    _, action = self.getActionViaGoal(gameState, self.fortress)
    minDistance = 9999
    for opp in self.getOpponents(gameState):
      oppPosition = self.getCurrentObservation().getAgentState(opp).getPosition()
      if oppPosition is not None:
        toOpp = self.getActionViaGoal(gameState, oppPosition)
        if toOpp[0] < minDistance:
          action = toOpp[1]
          minDistance = toOpp[0]

    return action
  
  def getActionViaGoal(self, gameState, goal):
    minDistance = 9999
    actions = gameState.getLegalActions(self.index) 
    for action in actions:
      successor = gameState.generateSuccessor(self.index, action)
      NextPos = successor.getAgentState(self.index).getPosition()

      if (self.red and NextPos[0] >= 17) or (not self.red and NextPos[0] <= 16):
        continue

      NextDistanceToGoal = self.getMazeDistance(NextPos, goal)
      if NextDistanceToGoal < minDistance: 
        minDistance = NextDistanceToGoal
        GoodAction = action

    return minDistance, GoodAction

  
class week13AtkAgent(CaptureAgent):
  def registerInitialState(self, gameState):
    CaptureAgent.registerInitialState(self, gameState)
    self.home = gameState.getInitialAgentPosition(self.index)

  def chooseAction(self, gameState):
    actions = gameState.getLegalActions(self.index) 
    if gameState.getAgentState(self.index).numCarrying >= 3:
      TargetPlace = self.home
    else: 
      TargetPlace = self.getTargetPelletPosition(gameState)
        
    minDistance = 9999
    for action in actions:
      successor = gameState.generateSuccessor(self.index, action)
      NextPos = successor.getAgentState(self.index).getPosition()

      NextDistanceToFood = self.getMazeDistance(NextPos, TargetPlace)
      if NextDistanceToFood < minDistance: 
        minDistance = NextDistanceToFood
        GoodAction = action

    return GoodAction
    
  def getTargetPelletPosition(self, gameState):
    foodList = self.getFood(gameState).asList()   
    myPos = gameState.getAgentState(self.index).getPosition()

    minDistance = 9999
    for food in foodList:
      DistanceToFood = self.getMazeDistance(myPos, food)
      if DistanceToFood < minDistance:
        minDistance = DistanceToFood
        FoodPosition = food

    return FoodPosition


class PowerAgent(CaptureAgent):
  def registerInitialState(self, gameState):
    CaptureAgent.registerInitialState(self, gameState)
    self.home = gameState.getInitialAgentPosition(self.index)

  def chooseAction(self, gameState):
    actions = gameState.getLegalActions(self.index) 
    if len(self.getCapsules(gameState)) > 0:
      TargetPlace = self.getCapsules(gameState)[0]
    else: 
      TargetPlace = self.home
        
    minDistance = 9999
    for action in actions:
      successor = gameState.generateSuccessor(self.index, action)
      NextPos = successor.getAgentState(self.index).getPosition()

      NextDistanceToFood = self.getMazeDistance(NextPos, TargetPlace)
      if NextDistanceToFood < minDistance: 
        minDistance = NextDistanceToFood
        GoodAction = action

    return GoodAction
    

class SmarterAgent(CaptureAgent):
  def registerInitialState(self, gameState):
    CaptureAgent.registerInitialState(self, gameState)
    self.home = gameState.getInitialAgentPosition(self.index)

  def chooseAction(self, gameState):
    actions = gameState.getLegalActions(self.index) 
    if gameState.getAgentState(self.index).numCarrying >= 5:
      TargetPlace = self.home
    else: 
      TargetPlace = self.getTargetPelletPosition(gameState)
        
    minDistance = 9999
    for action in actions:
      successor = gameState.generateSuccessor(self.index, action)
      NextPos = successor.getAgentState(self.index).getPosition()

      NextDistanceToFood = self.getMazeDistance(NextPos, TargetPlace)
      if NextDistanceToFood < minDistance: 
        minDistance = NextDistanceToFood
        GoodAction = action

    return GoodAction
    
  def getTargetPelletPosition(self, gameState):
    foodList = self.getFood(gameState).asList()   
    myPos = gameState.getAgentState(self.index).getPosition()

    minDistance = 9999
    for food in foodList:
      DistanceToFood = self.getMazeDistance(myPos, food)
      if DistanceToFood < minDistance:
        minDistance = DistanceToFood
        FoodPosition = food

    return FoodPosition

