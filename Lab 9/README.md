# Lab 9 : Minimum fitness call challenge with EA

The goal of the lab is to solve an abstract problem with a minimal number of calls to the fitness function.
Each following algorithm has been tested with a reduced individual size (around 30) as no test could be performed with 1000-gene individuals in reasonable time.

## Individual

An individual is represented by a genotype, which is a sequence of 0s or 1s, and a fitness, which is given by the fitness function of the problem.
If an individual reaches a fitness of 1, an exception is immediately raised, to prevent any further calls to the fitness functions for other individuals.

## Population

Basic implementation of a genetic algorithm. A population is a set of individuals that will evolve. Evolving is made by selecting a number of parents from the population, and using them to reate offspring individuals. Offsprings can either result from a mutation, which is a random inversion of an individual's gene, or from a recombination, which is done with a uniform crossover of two parents. The offspring is then mixed with initial population, and the most fitting individuals are selected to constitute the next generation's population, with the same size as the initial one.

## IslandPopulation

This class implements the island algorithm for promoting diversity. The population is split in n islands, in which evolution happens as usual. Once every given number of generations, each individual can randomly go to another island, which affects the evolution in this island.
This strategy seems to give worse results than the basic GA.

## ExtinctionPopulation

As partitioning the population doesn't seem to be effective, this population implements the extinction strategy. Every once in a while, a significant part of the population is killed (the most unfitting individuals are killed), and replaced by offsprings of the survivors. Extinction is then supposed to accelerate convergence towards max fitness. However, even if it works better than island population, the basic algorithm still seems to be slightly better than this one, in terms of fitness function calls.
