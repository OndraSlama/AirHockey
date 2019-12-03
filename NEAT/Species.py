import random

class Species():
    def __init__(self, p):
        self.players = []
        self.bestFitness = 0
        self.averageFitness = 0
        self.staleness = 0  # how many generations the species has gone without an improvement
        self.rep = None

        # coefficients for testing compatibility
        self.excessCoeff = 50
        self.weightDiffCoeff = 0.5
        self.compatibilityThreshold = 3
        if p:
            self.players.append(p)
            # since it is the only one in the species it is by default the best
            self.bestFitness = p.fitness
            self.rep = p.brain.Clone()
            self.color =  [random.randint(0,255), random.randint(0,255), random.randint(0,255)]
            p.color = self.color
            # self.champ = p.cloneForReplay()
    
    def SameSpecies(self, genome):        
        excessAndDisjoint = self.GetExcessDisjoint(genome, self.rep); # get the number of excess and disjoint genes between self player and the current species self.rep
        averageWeightDiff = self.AverageWeightDiff(genome, self.rep); # get the average weight difference between matching genes


        largeGenomeNormaliser = len(genome.connections)- 20
        if largeGenomeNormaliser < 1:
            largeGenomeNormaliser = 1
        

        compatibility = (self.excessCoeff * excessAndDisjoint / largeGenomeNormaliser) + (self.weightDiffCoeff * abs(averageWeightDiff)) # compatibility formula
        return self.compatibilityThreshold > compatibility

    def AddPlayer(self,p):
        p.color = self.color
        self.players.append(p)


    def GetExcessDisjoint(self,brain1, brain2):
        matching = 0
        for con in brain1.connections:
            for con2 in brain2.connections:
                if con.innovationNo == con2.innovationNo:
                    matching += 1
                    break
        return len(brain1.connections) + len(brain1.connections) - 2*matching

    def AverageWeightDiff(self, brain1, brain2):
        if len(brain1.connections) == 0 or len(brain1.connections) == 0:
            return 0

        matching = 0
        totalDiff = 0
        for con in brain1.connections:
            for con2 in brain2.connections:
                if con.innovationNo == con2.innovationNo:
                    matching += 1
                    totalDiff += con.weight - con2.weight
                    break

        if matching == 0: return 100        
        return totalDiff / matching

    def SortSpecies(self):
        self.players.sort(key=lambda x: x.fitness, reverse=True)

        if len(self.players) == 0:
            self.staleness = 200
            return

        if self.players[0].fitness > self.bestFitness:
            self.staleness = 0
            self.bestFitness = self.players[0].fitness
            self.rep = self.players[0].brain.Clone()
        else:
            self.staleness += 1

    def SetAverageFitness(self):
        suma = 0
        for player in self.players:
            suma += player.fitness
        self.averageFitness = suma/len(self.players)

    def GetChild(self,innovation):
        if random.random() < 0.25: #25% of the time there is no crossover and the child is simply a clone of a random(ish) player
            child = self.SelectPlayer().brain.Clone()
        else:
            parent1 = self.SelectPlayer()
            parent2 = self.SelectPlayer()

            if parent1.fitness < parent2.fitness:
                child = parent2.brain.Crossover(parent1.brain)
            else:
                child = parent1.brain.Crossover(parent2.brain)

        child.Mutate(innovation)
        return child

    def SelectPlayer(self):
        fitnessSum = sum(p.fitness for p in self.players)
        rand = random.random() * fitnessSum
        cumSum = 0

        for player in self.players:
            cumSum += player.fitness
            if cumSum > rand: return player
        return self.players[0]

    def Cull(self, portion = 0.51):
        if len(self.players) > 2:
            for i in range(round(len(self.players))-1, round(len(self.players)*(1-portion)) - 1, -1):
                self.players.pop(i)

    def FitnessSharing(self):
        for player in self.players:
            player.fitness /= len(self.players)
