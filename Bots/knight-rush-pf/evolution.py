'''
population = list of chromosome
chromosomeData = [chromosome, fitness]
chromosome = list of paremeters
'''
import random
import os.path
import time
FLOAT_PRECISION = 5
CHROMOSOME_LEN = 69
NUM_GENE_TYPES = 3
IES = 100  #initial epoch size
#parems values
#Gene 1 represents mean distance in guassian distribution. 
#large map distance, will not need pf for larger distances
GENE1_MULT = 25 #halve of largest map width 
#Gene 2 represents standard deviation
GENE2_MULT = 10 #how thin the pf can be. 10 is pretty thin 
GENE3_MULT = 100 #peak strengh of pf. pf values range from [-GENE3_MULT, GENE3_MULT]

MUTATION_RATE = 0.1 #chance each gene mutates
MIN_SPATIAL_DIST = .1*CHROMOSOME_LEN #some of the difference of gene values between chromosomes must exceed this
EPOCHNUM_FILEPATH = "../../../knight-rush-pf/savedData/lattestEpochNum.txt"
POPULATION_FILEPATH = "../../../knight-rush-pf/savedData/populationData"
#EPOCHNUM_FILEPATH = "savedData/lattestEpochNum.txt"
#POPULATION_FILEPATH = "savedData/populationData"

'''
gene = int from min to max parem value
chromosome = list of genes
chromosomeData = [chromosome, fitness] //fitness = a float
populationData = {
    "population": list of chromosomeData
    "epochNum": 0 //iteration number
    "initialAveFitnessOfTopFourthIES": float 
}
'''


#===========================================================================================SAVE/LOAD
def readEpochNum():
    with open(EPOCHNUM_FILEPATH, 'r') as file:
        #first write iteration num
        return file.readline()

#input population is list of list. Saves to file in rows. one chromosome per line
def savePopulation(populationData):
    epochNumStr = str(populationData["epochNum"])
    pop_filename = POPULATION_FILEPATH + epochNumStr + ".txt"
    with open(pop_filename, 'w') as file:
        #first write iteration num
        file.write("epochNum: " + epochNumStr + "\n")
        #then write lastEpochBestAveFitness
        file.write("initialAveFitnessOfTopFourthIES: " +
                     str(populationData["initialAveFitnessOfTopFourthIES"]) + "\n")
        #write each chromosomeData in population line by line
        population = populationData["population"]
        for chromosomeData in population:
            chromosome = chromosomeData[0]
            file.write(" ".join(str(round(x, FLOAT_PRECISION)) for x in chromosome))
            file.write(", " + str(round(chromosomeData[1], FLOAT_PRECISION))) #write fitness after
            file.write("\n")

def loadLastestPopulation():
    lattestEpochNum = readEpochNum()
    POPULATION_FILEPATH
    return loadPopulationData(POPULATION_FILEPATH + lattestEpochNum + ".txt")

#load population from file into list of lists. Each inner list is a chromosome
def loadPopulationData(filename):
    with open(filename, 'r') as file:
        epochNum = int(file.readline().split(":")[1])
        initialAveFitnessOfTopFourthIES = float(file.readline().split(":")[1])
        pop = []
        for line in file:
            split_line = line.split(",")
            paremString = split_line[0]
            fitness = round(float(split_line[1][:-1]), FLOAT_PRECISION)
            chromosome = [round(float(x), FLOAT_PRECISION) for x in paremString.split(' ')]
            pop.append([chromosome, fitness])
        popData = {"population": pop,
                    "epochNum": epochNum,
                    "initialAveFitnessOfTopFourthIES": initialAveFitnessOfTopFourthIES
                    }
        #check for identical
        for cData1 in pop:
            counter = 0
            for cData2 in pop:
                if cData1[0] == cData2[0]:
                    counter += 1
            assert counter <= 1, "Identical chromosomes in population"
        return popData
#=========================================================================generations
def generateGene(geneIndex):
    '''returns new random value for gene base on which type of gene'''
    geneValue = random.random()
    if(geneIndex % 3) == 0:
        geneValue *= GENE1_MULT
    elif (geneIndex % 3) == 1:
        geneValue *= GENE2_MULT
    else:
        is_neg = random.random() < 0.5
        geneValue *= GENE3_MULT
        if(is_neg):
            geneValue *= -1
    return round(geneValue, FLOAT_PRECISION)

def intializePopulation():
    '''
    Generates new population
    #chromosomes = IES
    #parems per chromosome = CHROMOSOME_LEN
    Random integersfor each parem value.
    calulate initialAveFitnessOfTopFourthIES
    Returns generated populationData
    '''
    newPop = []
    random.seed(time.time())
    for x in range(IES):
        chromosome = []
        for geneIndex in range(CHROMOSOME_LEN):
            chromosome.append(generateGene(geneIndex))
        chromosomeData = [chromosome, -1] #-1 means fitness unassigned
        newPop.append(chromosomeData)

    newPopulationData = {"population": newPop,
                    "epochNum": 0,
                    "initialAveFitnessOfTopFourthIES": -1 #need to get fitness latter
                    }
    savePopulation(newPopulationData)
    #save iteration num
    with open(EPOCHNUM_FILEPATH, 'w') as file:
        file.write(str(0))
#mutate chromosome
#each gene have MUTATION_RATE chance of mutating to another random value
#returns mutated gene
def mutateChromosome(chromosome):
    copiedChromosome = chromosome[:]
    for geneIndex in range(len(copiedChromosome)):
        if random.random() <= MUTATION_RATE:
            #mutates gene
            copiedChromosome[geneIndex] = generateGene(geneIndex)
    return copiedChromosome

'''
uniform crossover with 50% chance to inherit geneTriplets from either parent
Will forcefully keep every set of 3 genes from the same parent
returns new chromosome
'''
def crossover(chromosome1, chromosome2):
    assert len(chromosome1) == CHROMOSOME_LEN, "chromosome not right len in crossover"
    assert len(chromosome2) == CHROMOSOME_LEN, "chromosome not right len in crossover"
    newChromosome = []
    numGeneTriplets = int(CHROMOSOME_LEN / 3)
    for tripletIndex in range(numGeneTriplets):
        if(random.randrange(2) == 0):
            newChromosome.append(chromosome1[tripletIndex*3])
            newChromosome.append(chromosome1[tripletIndex*3+1])
            newChromosome.append(chromosome1[tripletIndex*3+2])
        else:
            newChromosome.append(chromosome2[tripletIndex*3])
            newChromosome.append(chromosome2[tripletIndex*3+1])
            newChromosome.append(chromosome2[tripletIndex*3+2])
    assert len(newChromosome) == CHROMOSOME_LEN, "crossover new chromosome is wrong length"
    return newChromosome

'''
should be called after check end of epoch
creates the next epoch by selecting from current epoch.
Tries to select good fitness and spacially diverse chromosomes
ALSO returns newPopulationData
'''
def createNewEpoch(populationData):
    population = populationData["population"]
    #print len(population)
    initialAveFitnessOfTopFourthIES = populationData["initialAveFitnessOfTopFourthIES"]
    epochNum = populationData["epochNum"]
    #calc epochBestFitness
    aveFitnessOfTopFourth = calcAveFitness(IES/4, population)
    '''
    print "current ave top IES = " + str(calcAveFitness(IES, population))
    print "current ave top IES/4 = " + str(aveFitnessOfTopFourth)
    print "\nlast fitness ave = " + str(initialAveFitnessOfTopFourthIES)
    print "population size = " + str(len(population))
    print "creating new EPOCH==========================================================================="
    '''
    newPop = []
    population.sort(key = lambda chromosomeData: chromosomeData[1], reverse = True) #sort by fitness
    index = 0
    notSpaciallyDiverseBackups = []
    while(index < len(population)):
        if(len(newPop) == IES):
            break
        chromDataCandidate = population[index]
        normalizedChromCandidate = normalizeChromosome(chromDataCandidate[0])
        #check for MIN_SPATIAL_DIST criteria against all existing in newPop
        toAdd = True
        for chromInNewPop in newPop:
            normalizedChromInNewPop = normalizeChromosome(chromInNewPop[0])
            spacial_dist = 0
            for geneIndex in range(CHROMOSOME_LEN):
                spacial_dist += abs(normalizedChromInNewPop[geneIndex] - normalizedChromCandidate[geneIndex])
            if(spacial_dist > MIN_SPATIAL_DIST):
                toAdd = False
        
        if (toAdd):
            newPop.append(chromDataCandidate)
        else:
            notSpaciallyDiverseBackups.append(chromDataCandidate)
        index += 1
    #fill in remaining spots
    if(len(newPop) < IES):
        for x in range(IES - len(newPop)):
            newPop.append(notSpaciallyDiverseBackups[x])
    assert len(newPop) == IES, "createNewEpoch error. size of pop not right"
    newEpochNumStr = str(int(epochNum)+1)
    newPopulationData = {"population": newPop, "epochNum": newEpochNumStr,
            "initialAveFitnessOfTopFourthIES": aveFitnessOfTopFourth}
    savePopulation(newPopulationData)
    #save iteration num
    with open(EPOCHNUM_FILEPATH, 'w') as file:
        file.write(newEpochNumStr)
    return newPopulationData

#==========================================================================helper  functions
def normalizeChromosome(chromosome):
    '''
    divide chromosome value by approiate multplier to have normalized
    values between 0.0 and 1.0
    '''
    normalizedChromosome = []
    for geneIndex in range(len(chromosome)):
        divider = GENE1_MULT; #geneIndex % 3 == 0:
        if (geneIndex % 3) == 1:
            divider = GENE2_MULT
        elif (geneIndex % 3) == 2:
            divider = GENE3_MULT
        divider = abs(divider)
        assert divider != 0, "normalizeChromosome divided by zero"
        normalizedChromosome.append(chromosome[geneIndex] / divider)
    assert len(normalizedChromosome) == CHROMOSOME_LEN, "normalize chrom is wrong chromosome len"
    return normalizedChromosome

def calcAveFitness(numChromosome, population): #numChromosome should be IES or IES/4
    numChromosome = int(round(numChromosome))
    population.sort(key = lambda chromosomeData: chromosomeData[1], reverse = True) #sort by fitness
    sumFitness  = 0
    for x in range(numChromosome):
        sumFitness += population[x][1]
    aveFitness = float(sumFitness) / numChromosome
    return aveFitness

'''
Return fitness of chromosome by simulating a game using this chromosome
'''
def evaluateFitness(chromosome):
    return random.randrange(100)#random fitness for testing

def checkChromosomeData(chromosomeData, population):
    #check if better than average fitness of population
    if (chromosomeData[1] < calcAveFitness(IES, population)):
        #print ("chromosome failed fitness test\n ")
        return False
    #check if chromosomeData identical with any existing in population
    #print("Pop length in check chrom data = " + str(len(population)))
    #print("chromesome checking")
    #print(chromosomeData[0][:20])
    for cData in population:
        chromInPop = cData[0]
        '''
        if(chromInPop[0] == chromosomeData[0][0]):
            print("chromosome in pop")
            print(chromInPop[:20])'''
        if (chromInPop == chromosomeData[0]):
            cData[1] = chromosomeData[1] #replace fitness
            return False
    return True

'''
check if the current epoch(population) is ready to advance to next epoch
epoch is ready to advance if average fitness  of top IES chromosomes is greater than
the average fitness of top TES/4 that initialized it
'''
def checkEndOfEpoch(populationData):
    population = populationData["population"]
    initialAveFitnessOfTopFourthIES = populationData["initialAveFitnessOfTopFourthIES"]
    aveTopFitness = calcAveFitness(IES, population)
    return aveTopFitness > initialAveFitnessOfTopFourthIES



def continueInitializing(chromosomeCandidate, fitness):
    populationData = loadLastestPopulation()
    population = populationData["population"]
    assert len(population) == IES, "size of initial population not equal to IES"
    for chromosomeIndex in range(len(population)):
        chromosomeData = population[chromosomeIndex]
        if (chromosomeCandidate == chromosomeData[0]):
            #fill in fitness
            chromosomeData[1] = fitness
            if (chromosomeIndex == len(population)-1):
                #all fitness assigned
                populationData["initialAveFitnessOfTopFourthIES"] = calcAveFitness(
                                                                    IES/4, population)
            savePopulation(populationData)

#=========================================================================Evolution
'''
performs first part of  evolutionary step
1.)select one or two random chromosomeData from population
2.)performs mutation or crossover
return chromosome candidate
'''
def evolvePart1(populationData):
    population = populationData["population"]
    population.sort(key = lambda chromosomeData: chromosomeData[1], reverse = True) #sort by fitness
    newChromosome = None
    parent1Index = parent2Index = 0
    #roulette wheel selection of first parent
        #calc total
    sumFitness = float(0)
    for chromosomeData in population:
        sumFitness += chromosomeData[1]
    randRoulette1 = random.random()
    randCounterP1 = float(0)
        #selecting
    for chromosomeIndex in range(len(population)):
        chromosomeData = population[chromosomeIndex]
        prob = chromosomeData[1]/sumFitness
        randCounterP1 += prob
        if(randRoulette1 <= randCounterP1):
            parent1Index = chromosomeIndex
            break

    if(random.random() <= 0.5):
        print("Doing mutation")
        selectedChromosome = population[parent1Index][0]
        newChromosome = mutateChromosome(selectedChromosome)
    else:
        print ("Doing Crossover")
    #do crossover
    #parent 2 choice spacially diverse from parent 1
        #roulette selection based on distance from parent 1
            #calc total
        parent1Chromosome = population[parent1Index][0]
        sumDistFromP1 = 0
        for chromosomeIndex in range(len(population)):
            if chromosomeIndex == parent1Index:
                continue #identical to parent 1
            chromosome = population[chromosomeIndex][0]
            for geneIndex in range(len(chromosome)):
                sumDistFromP1 += abs(chromosome[geneIndex] - parent1Chromosome[geneIndex])
            #selecting
        randRoulette2 = random.random()
        randCounterP2 = float(0);
        for chromosomeIndex in range(len(population)):
            if chromosomeIndex == parent1Index:
                continue #identical to parent 1
            chromosome = population[chromosomeIndex][0]
            distFromP1 = 0
            for geneIndex in range(len(chromosome)):
                distFromP1 += abs(chromosome[geneIndex] - parent1Chromosome[geneIndex])
            prob = float(distFromP1)/sumDistFromP1
            #print "prob = " + str(prob) + "\n"
            randCounterP2 += prob
            if(randRoulette2 <= randCounterP2):
                parent2Index = chromosomeIndex
                break
        selectedChromosome1 = population[parent1Index][0]
        selectedChromosome2 = population[parent2Index][0]
        newChromosome = crossover(selectedChromosome1, selectedChromosome2)
       
        '''
    for chromosomeData in population:
        if(chromosomeData[0] == newChromosome ):
            print("generated identical chromosome")
            print("new chromo = \n")
            print(newChromosome)
            print("chrom in pop = \n")
            print (chromosomeData)
            '''
            
    return newChromosome
'''
performs second part of evolutionary step
3.)evaluates fitness of new chromosome
4.)tag new chromosome with new fitness
5.)check if new chromosomeData is appropiate
5.)append new chromosomeData to population
'''
def evolvePart2(populationData, chromosomeCandidate, fitness):
    #print("\nevolvepart2")
    #fitness = evaluateFitness(chromosomeCandidate)
    population = populationData["population"]
    newChromosomeData = [chromosomeCandidate, fitness]
    if(checkChromosomeData(newChromosomeData, population)):
        population.append(newChromosomeData)
        print("Added New ChromosomeData: ")
        print(newChromosomeData[0][:30])
        #print("population num = " + str(populationData["epochNum"]))
        print("pop len = " + str(len(population)) + "\n")
        savePopulation(populationData)
    else: #for testing
        print("Not added\n")
        #print(newChromosomeData)


#====================================================================MAIN CAlls
'''
Main Call the for evolution
funs until a new epoch is created
returns chromosome candidate
'''
def DPEA_Part1():
    random.seed(time.time())
    populationData = loadLastestPopulation()
    population = populationData["population"]
    #check if initialized
    if(populationData["initialAveFitnessOfTopFourthIES"] == -1):
        #not completely initilized
        for chromosomeData in population:
            if(chromosomeData[1] == -1): #no fitness
                return chromosomeData[0]
        #all filled
    if(checkEndOfEpoch(populationData)):
        populationData = createNewEpoch(populationData)
        #print "creating new epoch"
    return evolvePart1(populationData)

'''
check chromosomeCandidate and saves if good
'''
def DPEA_Part2(chromosomeCandidate, fitness):
    #print("DPEA_Part2")
    populationData = loadLastestPopulation()
    if(populationData["initialAveFitnessOfTopFourthIES"] == -1):
        continueInitializing(chromosomeCandidate, fitness)
    else:
        evolvePart2(populationData, chromosomeCandidate, fitness)



# testing


#import os.path
if not(os.path.exists(EPOCHNUM_FILEPATH)):
    intializePopulation()
'''
counter = 1
while(counter > 0):
    counter -= 1
    chromosome = DPEA_Part1()
    DPEA_Part2(chromosome, evaluateFitness(chromosome))
    DPEA_Part2(chromosome, evaluateFitness(chromosome))
    DPEA_Part2(chromosome, evaluateFitness(chromosome))
    DPEA_Part2(chromosome, evaluateFitness(chromosome))
    DPEA_Part2(chromosome, evaluateFitness(chromosome))

'''