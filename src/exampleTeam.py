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

#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
               first = 'RandomAgent', second = 'StupidAgent'):

  return [eval(first)(firstIndex), eval(second)(secondIndex)]

##########
# Agents #
##########

class RandomAgent(CaptureAgent):

    def registerInitialState(self, gameState):
        CaptureAgent.registerInitialState(self, gameState)

    def chooseAction(self, gameState):

        actions = gameState.getLegalActions(self.index)

        return random.choice(actions)

class StupidAgent(CaptureAgent):

    def registerInitialState(self, gameState):
        CaptureAgent.registerInitialState(self, gameState)

    def chooseAction(self, gameState):
        TargetPellet = self.getTargetPelletPosition(gameState) # 먹고자 하는 pellet 위치를 TargetPellet 변수에 저장
        actions = gameState.getLegalActions(self.index)
        
        minDistance = 9999
        for action in actions:
            successor = gameState.generateSuccessor(self.index, action)
            NextPos = successor.getAgentState(self.index).getPosition()

            NextDistanceToFood = self.getMazeDistance(NextPos, TargetPellet)
            if NextDistanceToFood < minDistance: # TargetPellet과 가까워지는 방향으로 이동
                minDistance = NextDistanceToFood
                GoodAction = action

        return GoodAction
    
    def getTargetPelletPosition(self, gameState):
        '''
        전체 pellet 중 maze distance를 계산했을 때 agent와 가장 가까이 있는 pellet의 위치를 반환하는 함수
        '''
        foodList = self.getFood(gameState).asList()   
        myPos = gameState.getAgentState(self.index).getPosition()

        minDistance = 9999
        for food in foodList:
            DistanceToFood = self.getMazeDistance(myPos, food)
            if DistanceToFood < minDistance:
                minDistance = DistanceToFood
                FoodPosition = food

        return FoodPosition