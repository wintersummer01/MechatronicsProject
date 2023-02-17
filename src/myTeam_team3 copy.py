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