from individualclass import Individual
from constitutive_relations import *
import random  # For selecting random parameters and mutation
import operator  # To sort individuals
import numpy as np
import json
import os  # To execute command line options


class Generation:
    """
    Defines the Generation Class.

    The majority of the code is executed by this class.

    Attributes
    ----------
    Generation : int, Default = 0
        The current generation number.
    """
    # Loads the parameters in from the json
    ga_inputs = json.load(open("ga_inputs.json"))

    # Creates the parameters. This will lead to 'errors' in the code, whereby
    # it won't acknowledge the parameters, but they do exist.

    changeable_parameters = []

    for i, item in enumerate(ga_inputs['variable_parameters']):
        exec(f"parameter{i+1} = ga_inputs['variable_parameters']['{item}']")
        changeable_parameters.append(ga_inputs['variable_parameters'][item])

    def __init__(self, GenerationNum=0):
        """
        This method defines all the intial variables when a generation is
        initialised.

        Parameters
        ----------
        GenerationNum : int, Default = 0
            The present generation number.
        """
        self.generation = GenerationNum
        self.num_of_individuals = Generation.ga_inputs['genetic_algorithm']['num_of_individuals']
        self.selection_fraction = Generation.ga_inputs['genetic_algorithm']['selection_fraction']
        self.mutation_rate = Generation.ga_inputs['mutation_parameters']['mutation_rate']
        self.mutation_method = Generation.ga_inputs['mutation_parameters']['method']
        self.population = []
        self.parameter_mixing_list = []
        self.newborn = []

    def __str__(self):
        """
        Returns the generation number when called.

        Returns
        -------
        Generation Number : str
            Generation: `self.generation`
        """
        return f"Generation: {self.generation}"

    def populate(self, History):
        """
        Populates the generation by creating the individuals.
        This method is only ran for generation 0.

        Parameters
        ----------
        History : list
            A list containing all unique individuals.
        """
        # Use for loop to create all the individuals.
        for indiv in range(self.num_of_individuals):

            # Creates a folder for each individual
            os.system(f"mkdir Generation{self.generation}/Invididual{indiv}")

            # Creates the initial generation
            self.population.append(Individual(
                *[random.uniform(*i) for i in self.changeable_parameters]))

            os.system(
                f"python inputfile_maker.py -f Generation{self.generation}/Invididual{indiv}/Individual{self.generation*self.num_of_individuals + indiv}.inp --cores_per_node 128 -n0 {self.population[-1].parameter_list[0]} -E 31.3  -R {self.population[-1].parameter_list[2]} -w0 {self.population[-1].parameter_list[1]}")

            # Creates a specific jobscript.
            os.system(
                f"cp jobscript.pbs Generation{self.generation}/Invididual{indiv}/jobscript{self.generation*self.num_of_individuals + indiv}.pbs")

            # Change directory to the specific individual
            os.chdir(f"Generation{self.generation}/Invididual{indiv}")

            with open(f"Individual{self.generation*self.num_of_individuals + indiv}.data", "x") as f:
                f.write(self.population[indiv].__str__())

            self.population[-1].merit_calc(self.generation * self.num_of_individuals +
                                           indiv, f"Individual{self.generation*self.num_of_individuals + indiv}.inp")

            os.chdir("..")

            os.chdir("..")  # Two chdirs are needed to return to root

            # Add each individual to the history list. These are guaranteed to
            # be unique, and all but guaranteed not to be the same.
            History.append(self.population[-1])

    def repopulate(self, NewPop, History):
        """
        Generate populations after the original generation.

        Parameters
        ----------
        NewPop : list
            A list of individuals used to create the next generation. They provide the 'genes'

        History : list
            A list containing all unique individuals.
        """

        self.population = NewPop

        # Checks if there is a merit value already.
        # Calculates merit for new individuals.
        for i in range(self.num_of_individuals):

            os.system(f"mkdir Generation{self.generation}/Invididual{i}")

            # If the individual does not have a merit value, run a the
            # simulation to determine its value
            if self.population[i].merit is None:

                os.system(
                    f"python inputfile_maker.py -f Generation{self.generation}/Invididual{i}/Individual{self.generation*self.num_of_individuals + i}.inp --cores_per_node 128 -n0 {self.population[-1].parameter_list[0]} -E 31.3  -R {self.population[-1].parameter_list[2]} -w0 {self.population[-1].parameter_list[1]}")

                os.system(
                    f"cp jobscript.pbs Generation{self.generation}/Invididual{i}/jobscript{self.generation*self.num_of_individuals + i}.pbs")

                os.chdir(f"Generation{self.generation}/Invididual{i}")

                with open(f"Individual{self.generation*self.num_of_individuals + i}.data", "x") as f:
                    f.write(self.population[i].__str__())

                self.population[i].merit_calc(
                    self.generation * self.num_of_individuals + i,
                    f"Individual{self.generation*self.num_of_individuals + i}.inp")

                os.chdir("..")

                os.chdir("..")

                History.append(self.population[i])

                continue

            os.system(
                f"python inputfile_maker.py -f Generation{self.generation}/Invididual{i}/Individual{self.generation*self.num_of_individuals + i}.inp --cores_per_node 128 -n0 {self.population[-1].parameter_list[0]} -E 31.3  -R {self.population[-1].parameter_list[2]} -w0 {self.population[-1].parameter_list[1]}")

            os.system(
                f"cp jobscript.pbs Generation{self.generation}/Invididual{i}/jobscript{self.generation*self.num_of_individuals + i}.pbs")

            os.chdir(f"Generation{self.generation}/Invididual{i}")

            with open(f"Individual{self.generation*self.num_of_individuals + i}.data", "x") as f:
                f.write(self.population[i].__str__())

            self.population[-1].create_jobscript(self.generation * self.num_of_individuals + i,
                                                 f"Individual{self.generation*self.num_of_individuals + i}.inp")

            os.chdir("..")

            os.chdir("..")

    def mating_stage(self, History):
        """Performs the creation of the next generation.

        Parameters
        ----------
        History : list
            A list containing all unique individuals.

        Notes
        -----
        The method takes the top 50% of performers, and clones them into the next generation. Then, the 'genes' of these individuals (i.e., their Individual attributes) are collected into a pool, randomised, and new individuals are made. During this process, `mutation_stage` is called.
        """

        top50 = []

        # Dummy list for mixing parameters. If you can figure out what makes
        # this different from [[] * len(self.changeable_parameters)], please
        # send a commit!
        self.parameter_mixing_list = [[]
                                      for _ in range(len(self.changeable_parameters))]

        # Sorts the population list based on the merit value. Key takes a
        # function. operator.attrgetter = '.' as in self merit. Reverse makes
        # it highest to lowest.
        self.population.sort(key=operator.attrgetter('merit'), reverse=False)

        if self.num_of_individuals % int(
                2 / (self.selection_fraction)) != 0:  # if odd
            raise ValueError("Error! Need parents!")

        # Iterates through half of the population list and appends it to the
        # top50 and newborn lists.
        for i in range(int(self.num_of_individuals * self.selection_fraction)):

            # Add the top 50% to the gene pool
            top50.append(self.population[i])

        random.shuffle(top50)

        # Creates the other individuals for the new population, by drawing
        # characteristics from the gene pool, and mutating at random
        for i in range(int(self.num_of_individuals *
                           self.selection_fraction) // 2):
            self.mutation_stage(History, top50)

    def mutation_stage(self, History, top50):
        """Creates new individuals based on a gene pool of prior individuals, and mutates occassional parameters.

        Parameters
        ----------
        History : list
            A list containing all unique individuals.
        """

        parent1 = top50.pop()
        parent2 = top50.pop()

        genes = self.parameter_mixing_list

        for i in range(len(self.changeable_parameters)):
            for j in range(int(2 / self.selection_fraction)):
                genes[i].append(parent1.parameter_list[i])
                genes[i].append(parent2.parameter_list[i])

        for i in range(len(self.changeable_parameters)):
            random.shuffle(genes[i])

        for i in range(int(2 / self.selection_fraction)):
            if self.mutation_method == "perturbative":
                geneList = [
                    self.parameter_mixing_list[i].pop() *
                    random.gauss(
                        1,
                        1 /
                        3) if np.random.random() <= self.mutation_rate else self.parameter_mixing_list[i].pop() for i in range(
                        len(
                            self.changeable_parameters))]
                geneList = [self.changeable_parameters[i][0] if geneList[i] < self.changeable_parameters[i]
                            [0] else geneList[i] for i in range(len(self.changeable_parameters))]
                geneList = [self.changeable_parameters[i][1] if geneList[i] > self.changeable_parameters[i]
                            [1] else geneList[i] for i in range(len(self.changeable_parameters))]
                new_individual = Individual(*geneList)
            elif self.mutation_method == "jumping":
                new_individual = Individual(
                    *
                    [
                        random.uniform(
                            *
                            val) if np.random.random() <= self.mutation_rate else self.parameter_mixing_list[i].pop() for i,
                        val in enumerate(
                            self.changeable_parameters)])  # Creates the new individual by mutation and breeding

            for j in History:  # Iterate over History list to see if the individual has been used before. If it has, reuse the individual.
                if new_individual.parameter_list == j.parameter_list:
                    new_individual = j
                    break

            self.newborn.append(new_individual)
