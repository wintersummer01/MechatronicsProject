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


from argparse import _get_action_name
from captureAgents import CaptureAgent
import random, time, util
from game import Directions
import numpy as np
import game
import distanceCalculator
from keyboardAgents import KeyboardAgent

#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
               first = 'team3AtkAgent', second = 'team3DefAgent'):
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

class minFinder:
  def __init__(self, fixed, gameState):
    self.distancer = distanceCalculator.Distancer(gameState.data.layout)
    self.distancer.getMazeDistances()
    self.fixed = fixed
    self.minDist = 9999
    self.minIdx = None
    self.alpha = None
  def pushItem(self, idx, alpha=None):
    dist = self.distancer.getDistance(self.fixed, idx)
    if self.minDist > dist:
      self.minDist = dist
      self.minIdx = idx
      if alpha is not None:
        self.alpha = alpha
  def popIdx(self):
    return self.minIdx
  def popDist(self):
    return self.minDist
  def popAlpha(self):
    return self.alpha


class team3Agents(CaptureAgent):
  def registerInitialState(self, gameState):
    CaptureAgent.registerInitialState(self, gameState)
    self.mode = None
    self.modeStep = 0
    self.modeCount = 0
    self.Walls = gameState.getWalls()
    self.foodHad = self.getFoodYouAreDefending(gameState).asList()

  def onOurArea(self, gameState, idx=None):
    if idx is None:
      idx = self.index
    pos = gameState.getAgentPosition(idx)
    if self.red and pos[0] <= 16:
      return True
    if not self.red and pos[0] >= 17:
      return True
    return False

  def getActionforGoal(self, goal, gameState):
    toGoal = minFinder(goal, gameState)
    actions = gameState.getLegalActions(self.index) 
    for action in actions:
      successor = gameState.generateSuccessor(self.index, action)
      NextPos = successor.getAgentState(self.index).getPosition()
      toGoal.pushItem(NextPos, alpha=action)
    return toGoal.popAlpha()

  def getActionforHome(self, gameState):
    if self.red:
      homeline = 16
    else:
      homeline = 17
    toHome = minFinder(gameState.getAgentPosition(self.index), gameState)
    for i in range(1, 17):
      if self.Walls[homeline][i]:
        continue
      toHome.pushItem((homeline, i))
    myHome = toHome.popIdx()
    return self.getActionforGoal(myHome, gameState)

  def getMyOppInfo(self, gameState):
    for opp in self.getOpponents(gameState):
      oppPos = gameState.getAgentPosition(opp)
      if oppPos is not None:
        closeTeam = minFinder(oppPos, gameState)
        for team in self.getTeam(gameState):
          closeTeam.pushItem(gameState.getAgentPosition(team), alpha=team)
        if closeTeam.popAlpha() == self.index:
          return opp, oppPos
    return None

  def pathWeight(self, idx, value):
    if value == 0:
      return 
    if idx[0] not in range(1, 33) or idx[1] not in range(1, 17):
      return
    if (self.Wmap[idx] != 0) or self.Walls[idx[0]][idx[1]]:
      return
    self.Wmap[idx] = value
    self.pathWeight((idx[0]+1, idx[1]), value-1)
    self.pathWeight((idx[0]-1, idx[1]), value-1)
    self.pathWeight((idx[0], idx[1]+1), value-1)
    self.pathWeight((idx[0], idx[1]-1), value-1)

  def setMode(self, mode, gameState, force=False):
    if self.mode == mode and not force:
      return

    self.mode = mode
    self.modeStep = 1

    if mode == 'collector':
      field = np.zeros((33, 17))
      for food in self.getFood(gameState).asList():
        self.Wmap = np.zeros((33, 17))
        self.pathWeight(food, 3)
        field += self.Wmap
      for capsule in self.getCapsules(gameState):
        self.Wmap = np.zeros((33, 17))
        self.pathWeight(capsule, 5)
        field += self.Wmap
      # print(np.rot90(self.field[17:,1:], k=1))
      self.goal = field.argmax()
      self.goal = (self.goal//17, self.goal%17)

    elif mode == 'killer':
      self.modeCount = 0

    elif mode == 'patrol':
      self.foodHad = self.getFoodYouAreDefending(gameState).asList()
      oppHome = gameState.getInitialAgentPosition(self.getOpponents(gameState)[0])
      oppFood = minFinder(oppHome, gameState)
      if self.foodHad is not None:
        for food in self.foodHad:
          oppFood.pushItem(food)
      capsules = self.getCapsulesYouAreDefending(gameState)
      oppCap = minFinder(oppHome, gameState)
      if capsules is not None:
        for capsule in capsules:
          oppCap.pushItem(capsule)
      self.goal = oppFood.popIdx()
      self.goal_ = oppCap.popIdx()

    elif mode == 'reaper':
      closeFood = minFinder(gameState.getAgentPosition(self.index), gameState)
      for food in self.getFood(gameState).asList():
        closeFood.pushItem(food)
      self.goal = closeFood.popIdx()
      self.modeCount = 0
      

  def getActionfromMode(self, gameState, extraMode=None):
    if extraMode is not None:
      mode = extraMode
    else:
      mode = self.mode
      
    if mode == 'collector':
      # modeStep control
      if gameState.getAgentPosition(self.index) == self.goal:
        self.modeStep = 2
      if gameState.getAgentState(self.index).numCarrying == 5:
        self.modeStep = 3
      if self.modeStep >= 2 and self.onOurArea(gameState):
        self.setMode('collector', gameState, force=True)
      # get Actions from modeStep
      if self.modeStep == 1:
        action = self.getActionforGoal(self.goal, gameState)
      elif self.modeStep == 2:
        closeFood = minFinder(gameState.getAgentPosition(self.index), gameState)
        for food in self.getFood(gameState).asList():
          closeFood.pushItem(food)
        if closeFood.popDist() <= 3:
          action = self.getActionforGoal(closeFood.popIdx(), gameState)
        else:
          action = self.getActionforHome(gameState)
      elif self.modeStep == 3:
        action = self.getActionforHome(gameState)

    elif mode == 'killer':
      myOpp = self.getMyOppInfo(gameState)
      if self.modeCount < 8:
        self.goal = myOpp[1]
        action = self.getActionforGoal(self.goal, gameState)
        self.modeCount += 1
      else:
        action = self.getActionfromMode(gameState, extraMode='collector')
    
    elif mode == 'runner':
      myOpp = self.getMyOppInfo(gameState)
      self.goal = None
      for capsule in self.getCapsules(gameState):
        if self.getMazeDistance(gameState.getAgentPosition(self.index), capsule) < self.getMazeDistance(myOpp[1], capsule):
          self.goal = capsule
          action = self.getActionforGoal(self.goal, gameState)
      if self.goal is None:
        action = self.getActionforHome(gameState) 
        successor = gameState.generateSuccessor(self.index, action)
        NextPos = successor.getAgentState(self.index).getPosition()
        if self.getMazeDistance(NextPos, myOpp[1]) < self.getMazeDistance(gameState.getAgentPosition(self.index), myOpp[1]):
          maxDist = 0
          for act in gameState.getLegalActions(self.index):
            act_successor = gameState.generateSuccessor(self.index, act)
            act_NextPos = act_successor.getAgentState(self.index).getPosition()
            dist = self.getMazeDistance(act_NextPos, myOpp[1])
            if dist > maxDist:
              maxDist = dist
              action = act   

    elif mode == 'patrol':
      if self.modeStep == 1 and gameState.getAgentPosition(self.index) == self.goal_:
        self.modeStep = 2
      elif self.modeStep == 2 and gameState.getAgentPosition(self.index) == self.goal:
        self.modeStep = 1
      if self.goal_ is None:
        self.modeStep = 2
      elif self.goal is None:
        self.modeStep = 1
      # Go when my food is disappeared
      currentDefFood = self.getFoodYouAreDefending(gameState).asList()
      if len(self.foodHad) > len(currentDefFood):
        self.modeStep = 3
        for food in self.foodHad:
          if food not in currentDefFood:
            self.goal = food
        self.foodHad = currentDefFood

      if self.modeStep == 1:
        action = self.getActionforGoal(self.goal_, gameState)
      elif self.modeStep == 2:
        action = self.getActionforGoal(self.goal, gameState)
      elif self.modeStep == 3:
        action = self.getActionforGoal(self.goal, gameState)
        if gameState.getAgentPosition(self.index) == self.goal:
          self.setMode('patrol', gameState, force=True)
        
    elif mode == 'reaper':
      # modeStep control
      if gameState.getAgentPosition(self.index) == self.goal:
        self.modeStep = 2
      if gameState.getAgentState(self.index).numCarrying == 3:
        self.modeStep = 3
      # get Actions from modeStep
      if self.modeStep == 1:
        action = self.getActionforGoal(self.goal, gameState)
        self.modeCount += 1
      elif self.modeStep == 2:
        closeFood = minFinder(gameState.getAgentPosition(self.index), gameState)
        for food in self.getFood(gameState).asList():
          closeFood.pushItem(food)
        if closeFood.popDist() <= 2:
          action = self.getActionforGoal(closeFood.popIdx(), gameState)
        else:
          self.modeStep = 3
        self.modeCount += 1
      if self.modeStep == 3 or self.modeCount > 15:
        self.setMode('patrol', gameState)
        action = self.getActionfromMode(gameState)

    return action

class team3AtkAgent(team3Agents):
  def registerInitialState(self, gameState):
    team3Agents.registerInitialState(self, gameState)
    self.setMode('collector', gameState)

  def chooseAction(self, gameState):
    myOpp = self.getMyOppInfo(gameState)
    if myOpp is not None: 
      if self.onOurArea(gameState, idx=myOpp[0]) or gameState.getAgentState(myOpp[0]).scaredTimer > 0:
        self.setMode('killer', gameState)
      else:
        self.setMode('runner', gameState)
    else:
      self.setMode('collector', gameState)
    
    if self.modeStep != 1 and self.onOurArea(gameState):
      self.setMode('collector', gameState, force=True)

    if gameState.getAgentState(self.index).scaredTimer > 0:
      self.setMode('collector', gameState)

    if len(self.getFood(gameState).asList()) == 0:
      self.setMode('patrol', gameState)
      self.goal_ = self.goal

    return self.getActionfromMode(gameState)

class team3DefAgent(team3Agents):
  def registerInitialState(self, gameState):
    team3Agents.registerInitialState(self, gameState)
    self.setMode('patrol', gameState)

  def chooseAction(self, gameState):
    if self.mode == 'killer':
      if gameState.getAgentPosition(self.index) == self.goal:
        self.setMode('reaper', gameState)
      if self.modeCount >= 8:
        self.setMode('patrol', gameState)

    myOpp = self.getMyOppInfo(gameState)
    if myOpp is not None:      
      if self.onOurArea(gameState, idx=myOpp[0]) or gameState.getAgentState(myOpp[0]).scaredTimer > 0:
        self.setMode('killer', gameState)
      elif not self.onOurArea(gameState):
        self.setMode('runner', gameState)
      else:
        self.setMode('patrol', gameState)
    elif self.mode != 'reaper':
      self.setMode('patrol', gameState)

    if gameState.getAgentState(self.index).scaredTimer > 0:
      self.setMode('reaper', gameState)

    if len(self.getCapsulesYouAreDefending(gameState)) == 0 and len(self.getFoodYouAreDefending(gameState).asList()) == 0:
      self.setMode('reaper')

    return self.getActionfromMode(gameState)