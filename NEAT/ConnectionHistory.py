# ****************************************************************************** #
# Author: Ondrej Slama
# -------------------

# Zdrojovy kod vytvoreny v ramci projektu robotickeho vzdusneho hokeje - diplomova prace
#  na VUT FSI ustavu automatizace a informatiky v Brne.

# Source code created as a part of robotic air hockey table project - Diploma thesis
# at BUT FME institute of automation and computer sience.

# ****************************************************************************** #
class ConnectionHistory():
    def __init__(self, fromN, toN, inno, innos):
        self.fromNode = fromN
        self.toNode = toN
        self.innovationNumber = inno
        self.innovationNumbers = innos.copy()

    def matches(self, genome, fromN, toN):
        if len(genome.connections) != len(self.innovationNumbers): return False
        if fromN.number != self.fromNode or toN.number != self.toNode: return False

        for connection in genome.connections:
            if connection.innovationNo not in self.innovationNumbers:
                return False
        return True

class Innovation():
    def __init__(self):
        self.history = []
        self.nextInno = 1