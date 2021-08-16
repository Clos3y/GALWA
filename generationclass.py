import copy
import random
from individualclass import Individual
import operator
import numpy as np
import json
import os
from scipy.constants import e, mu_0 as mu0, epsilon_0 as eps0, m_e

def plasma_frequency(plasma_density):

    return e * np.sqrt(plasma_density / (m_e * eps0))


def skin_depth(plasma_density):

    return np.sqrt(m_e / (plasma_density * mu0)) / e


class Generation:
    """
    This class contains the code which performs the bulk of the genetic
    algorithm. For each generation, the class will populate the generation
    with a given number of individuals, where the parameters are chosen
    randomly, calculate the merit value for each individual, take the top
    50% of individuals, and repopulate the next generation.

    There are also methods which introduce mutations, which avoid the
    algorithm getting stuck in a local maximum/minumum, by introducing
    random parameters.

    Attributes:
        Generation = Stores the current generation number. Set to 0 by
                     default.

        MutationRate = Stores the mutation rate for each generation.
                       Set to 2 by default, which means each
                       individual has a 20% chance of mutating. This
                       rate increases for each generation and is capped
                       at 60%.

    Class Variables:
        ga_inputs = Opens a json file that contains all the variables
                    that can be changed.

        parameter1 = ================ Plasma Density ================
                     Stores a list of numbers that the plasma
                     density could be.
                     This is a discrete list, not a continuous range.
                     Normalised to 5E+17.

        parameter2 = ============ Laser Spot Size: w_0 =============
                     Stores a list of numbers that the laser
                     spot size could be.
                     This is a discrete list, not a continuous range.

        parameter3_range = Stores the minimum, maximum, and step size
                           for parameter 3 (Jitter Distance).
                           This is to be used in a numpy arange function,
                           where each element of this list is a condition
                           for the arange function.

        parameter3 = =============== Jitter Distance ================
                     Uses the parameter3_range variable to create a
                     list of numbers for the jitter distamce with the
                     correct range.

        parameter4_range = Stores the minimum, maximum, and step size
                           for parameter 4 (Laser Focus).
                           This is to be used in a range function,
                           where each element of this list is a condition
                           for the range function.

        parameter4 = ================= Laser Focus =================
                     Uses the parameter4_range variable to create a
                     list of numbers for the laser focus with the
                     correct range.

    Methods:
        __init__ = Defines the initial variables when a generation is
                   created.

        __str__ = Returns the generation number when called.

        populate = This method is used when populating the very first
                   generation.

        output_current_status = Prints the current progress of the
                                algorithm.

        repopulate = Populates the next generation based on the
                     previous generation.

        mating_stage = Takes the top 50% of individuals and puts
                       their parameters into a parameter mixing
                       list, which is then used to create new
                       individuals, either by basic crossover or
                       mutations.

        crossover_stage = When no mutation is triggered, the new set
                          of individuals is created by picking random
                          parameters from the parameter mixing list.

        mutation_stage = When a mutation is triggered, one of the
                         parameters for the individual is chosen from
                         the original parameter list, which introduces
                         a way of escaping a local minimum/maximum.
    """
    # Loads the parameters in from the json
    ga_inputs = json.load(open("ga_inputs.json"))

    parameter1 = ga_inputs['plasma_density']

    parameter2 = ga_inputs['laser_spot_size']

    parameter3 = ga_inputs['down_ramp']

    parameter4 = ga_inputs['up_ramp']

    parameter5 = ga_inputs['electron_beam_length']

    parameter6 = ga_inputs['electron_beam_radius']
    
    parameter7 = ga_inputs['focus_position']

    def __init__(self, GenerationNum=0):
        """
        This method defines all the intial variables when a generation is
        initialised.

        Variables:
            self.generation = Stores the current generation number.

            self.num_of_individuals = Stores the number of individuals
                                      in the generation.
                                      MAKE SURE THIS IS AN EVEN NUMBER!!!

            self.mutation_rate = Stores the mutation rate for the
                                 generation.

            self.population = List that stores all the individuals that
                              are created.

            self.parameter_mixing_list = List that stores all the
                                         parameters that can be used
                                         to create the individuals
                                         for the next generation.

            self.newborn = Stores a list of individuals that will be
                           used for the next generation.

            self.input_file_list = List that stores the name of all the
                                   input files.
        """
        self.generation = GenerationNum
        self.num_of_individuals = Generation.ga_inputs['num_of_individuals']
        self.mutation_rate = Generation.ga_inputs['mutation_rate']
        self.population = []
        self.parameter_mixing_list = []
        self.newborn = []
        self.input_file_list = [
            f"Generation{self.generation}/inputfile{i}.inp" for i in range(self.num_of_individuals)]

    def __str__(self):
        """
        Returns the generation number when called.
        """
        return f"Generation: {self.generation}"

    def populate(self, History):
        """
        Populates the generation by creating the individuals.
        This method is only ran for generation 0.

        Parameters:
            History = Passes a list which tracks all the previous
                      individuals. Any new individuals created
                      are appended to the list.
        """
        # Use for loop to create all the individuals.
        for indiv in range(self.num_of_individuals):
            os.system(f"mkdir Generation{self.generation}/Invididual{indiv}")
            self.population.append(
                Individual(
                    random.uniform(
                        *Generation.parameter1),
                    random.uniform(
                        *Generation.parameter2),
                    random.uniform(
                        *Generation.parameter3),
                    random.uniform(
                        *Generation.parameter4),
                    random.uniform(
                        *Generation.parameter5),
                    random.uniform(
                        *Generation.parameter6),
                    random.uniform(
                        *Generation.parameter7)),

            )
            
            os.system(
                f"python Specific\ Input\ File\ Maker.py -f Generation{self.generation}/Invididual{indiv}/Individual{self.generation*self.num_of_individuals + indiv}.inp --cores_per_node 128 -n0 {self.population[-1].parameter_list[0]} --downramp {self.population[-1].parameter_list[2]} --upramp {self.population[-1].parameter_list[3]} -E 31.3 -L {self.population[-1].parameter_list[4]} -R {self.population[-1].parameter_list[5]} -w0 {self.population[-1].parameter_list[1]} --focus_position {self.population[-1].parameter_list[6]}")
            
            os.system(f"cp jobscript.pbs Generation{self.generation}/Invididual{indiv}/jobscript{self.generation*self.num_of_individuals + indiv}.pbs")

            os.chdir(f"Generation{self.generation}/Invididual{indiv}")

            self.population[-1].merit_calc(self.generation*self.num_of_individuals + indiv,f"Individual{self.generation*self.num_of_individuals + indiv}.inp")

            os.chdir("..")
            os.chdir("..")

            History.append(copy.deepcopy(self.population[-1]))

    def repopulate(self, NewPop, History):
        """
        This method is used to populate generation 1 and above.
        Takes in a list of new individuals and checks to see if
        a merit value already exists. If merit does not exist,
        then the merit is calculated and the individual is stored
        into the History list.

        Parameters:
            NewPop = Passes in a list of individuals, which is
                     used to populate the generation.

            History = Passes in a list that stores all the
                      previous individuals and appends any new
                      individuals.
        """
        self.population = NewPop

        # Checks if there is a merit value already.
        # Calculates merit for new individuals.
        for i in range(len(self.population)):
            os.system(f"mkdir Generation{self.generation}/Invididual{i}")

            if self.population[i].merit is None:

                os.system(
                f"python Specific\ Input\ File\ Maker.py -f Generation{self.generation}/Invididual{i}/Individual{self.generation*self.num_of_individuals + i}.inp --cores_per_node 128 -n0 {self.population[-1].parameter_list[0]} --downramp {self.population[-1].parameter_list[2]} --upramp {self.population[-1].parameter_list[3]} -E 31.3 -L {self.population[-1].parameter_list[4]} -R {self.population[-1].parameter_list[5]} -w0 {self.population[-1].parameter_list[1]} --focus_position {self.population[-1].parameter_list[6]}")
            
                os.system(f"cp jobscript.pbs Generation{self.generation}/Invididual{i}/jobscript{self.generation*self.num_of_individuals + i}.pbs")

                os.chdir(f"Generation{self.generation}/Invididual{i}")

                self.population[i].merit_calc(self.generation*self.num_of_individuals + i,f"Individual{self.generation*self.num_of_individuals + i}.inp")

                os.chdir("..")
                os.chdir("..")

                History.append(copy.deepcopy(self.population[i]))

                continue
            
            os.system(
                f"python Specific\ Input\ File\ Maker.py -f Generation{self.generation}/Invididual{i}/Individual{self.generation*self.num_of_individuals + i}.inp --cores_per_node 128 -n0 {self.population[-1].parameter_list[0]} --downramp {self.population[-1].parameter_list[2]} --upramp {self.population[-1].parameter_list[3]} -E 31.3 -L {self.population[-1].parameter_list[4]} -R {self.population[-1].parameter_list[5]} -w0 {self.population[-1].parameter_list[1]} --focus_position {self.population[-1].parameter_list[6]}")

            os.system(f"cp jobscript.pbs Generation{self.generation}/Invididual{i}/jobscript{self.generation*self.num_of_individuals + i}.pbs")

            os.chdir(f"Generation{self.generation}/Invididual{i}")

            self.population[-1].create_jobscript(self.generation*self.num_of_individuals + i,f"Individual{self.generation*self.num_of_individuals + i}.inp")

            os.chdir("..")
            os.chdir("..")

    def mating_stage(self, History):
        """
        This method performs the mating stage of the algorithm.
        It takes the top 50% of individuals and places their parameters
        into the parameter mixing list. It adds the top 50% to the
        newborn list. Then creates the remaining 50% by either the
        crossover stage or mutation stage.

        Parameters:
            History = Passes in a list which stores all the individuals
                      that have already been created. Is used as an
                      argument for the crossover stage and mutation stage
                      methods.

        Variables:
            top50 = A list that stores the top 50% of individuals from this
                    generation, based on the merit value.

            chance_of_mutation = Stores a random number between 0 and 10.
                                 If the chance of mutation is less than
                                 the mutation rate, then the mutation stage
                                 method will be called.
        """
        top50 = []
        # List comprehension to make right sized list.
        self.parameter_mixing_list = [[] for i in range(
            len(self.population[0].parameter_list))]

        # Sorts the population list based on the merit value.
        # Key takes a function.
        # operator.attrgetter = '.' as in self.merit.
        # Reverse makes it highest to lowest.
        self.population.sort(key=operator.attrgetter('merit'), reverse=False)

        # Iterates through half of the population list and appends it to
        # the top50 and newborn lists.
        for i in range(int(len(self.population) / 2)):
            top50.append(self.population[i])
            self.newborn.append(self.population[i])

            # For each individual in the top50 list, append parameter1
            # to the first sublist in the mixing list.
            # Append parameter2 to the second sublist in the mixing
            # list, etc.
            for j in range(len(top50[0].parameter_list)):
                self.parameter_mixing_list[j].append(
                    top50[i].parameter_list[j])

        # Creates the other individuals for the new population, by drawing
        # characteristics from the gene pool, and mutating at random
        for i in range(len(top50)):
            self.mutation_stage(History)

    def mutation_stage(self, History):
        """
        If a mutation is triggered, then this method will be called.
        Picks a random parameter to be mutated (either 1, 2, 3, or 4).
        Depending on which parameter is picked, the mutation will be
        implemented. The rest of the parameters will be picked from
        the parameter mixing list.

        History list is used to check if the individual has been used
        before. If it has, then the individual from the History list
        will be used so that the merit value does not have to be
        recalculated.
        This saves computing power and time.

        Parameters:
            History = Passes a list that stores all the individuals
                      that have been used previously. Used to check
                      if the individual has already been created or
                      not.

        Variables:
            mutation_parameter = Stores which parameter will be
                                 mutated.

            new_individual = Stores the new individual that is created.
        """

        # Shuffle each sublist in the mixing list.
        for j in range(len(self.parameter_mixing_list)):
            random.shuffle(self.parameter_mixing_list[j])

        # Depending on which parameter was picked for mutation,
        # create a new individual.
        new_individual = Individual(
            random.choice(
                Generation.parameter1) if np.random.random() <= self.mutation_rate else self.parameter_mixing_list[0].pop(),
            random.choice(
                Generation.parameter2) if np.random.random() <= self.mutation_rate else self.parameter_mixing_list[1].pop(),
            random.uniform(
                *
                Generation.parameter3) if np.random.random() <= self.mutation_rate else self.parameter_mixing_list[2].pop(),
            random.uniform(
                    *
                    Generation.parameter4) if np.random.random() <= self.mutation_rate else self.parameter_mixing_list[3].pop(),
            random.uniform(
                    *
                    Generation.parameter5) if np.random.random() <= self.mutation_rate else self.parameter_mixing_list[4].pop(),
            random.uniform(
                    *
                    Generation.parameter6) if np.random.random() <= self.mutation_rate else self.parameter_mixing_list[5].pop(),
            random.uniform(
            *
            Generation.parameter7) if np.random.random() <= self.mutation_rate else self.parameter_mixing_list[6].pop())
        
        # Iterate over History list to see if the individual has been
        # used before.
        # If it has, reuse the individual.
        for j in range(len(History)):
            if new_individual.parameter_list == History[j].parameter_list:
                new_individual = copy.deepcopy(History[j])
                break

        self.newborn.append(copy.deepcopy(new_individual))