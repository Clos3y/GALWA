import os
import numpy as np
import matplotlib.pyplot as plt
from scipy import interpolate
from generationclass import Generation
import copy


class GeneticAlgorithm:
    """
    Class that defines a genetic algorithm object. This class is used to define the initial variables of the algorithm and run it.

    Attributes
    ----------
    MaxGenerationNumber : int
        The maximum number of generations to test. Numbering starts from the zeroeth generation, i.e., 10 generations would be 0-9.
    """

    def __init__(self, MaxGenerationNumber):
        """
        This method defines the initial variables that are used to
        run the genetic algorithm.

        Parameters
        ----------
        self.max_generation_number : int, Default = `MaxGenerationNumber`
            The maximum number of generations to test. Numbering starts from the zeroeth generation, i.e., 10 generations would be 0-9.
        """
        self.max_generation_number = MaxGenerationNumber  # The maximum number of generations to test
        self.generation_list = []  # A list of all generations that have been created
        self.current_generation = 0  # An iterator to store the present generation
        self.individuals_history = []  # A history of all unique individuals
        # Plotting parameters
        self.generation_x_axis = []
        self.merit_y_axis = []
        self.generation_smoothing = []
        self.merit_smoothing = []
        self.data = []
        self.curve_data = []

    def run(self):
        """
        Runs the genetic algorithm.
        """
        # Loops over for the number of generations specified.
        for i in range(self.max_generation_number):
            os.system(f"mkdir Generation{i}")
            # Create a generation object.
            if i == 0:
                # For the very first generation, use the populate
                # method.
                # Create the smoothing list.
                self.generation_list.append(Generation(
                    GenerationNum=i))
                self.generation_list[i].populate(
                    History=self.individuals_history)
                self.merit_smoothing = [[]
                                        for i in range(self.max_generation_number)]
            else:
                # For every other generation, use the repopulate method.
                self.generation_list.append(Generation(
                    GenerationNum=i))
                self.generation_list[i].repopulate(NewPop=self.generation_list[i - 1].newborn,
                                                   History=self.individuals_history)

            # Save and plot the data, output the current status, and
            # perform the mating stage.
            self.data_saver()
            self.data_plotter()
            self.generation_list[i].mating_stage(
                History=self.individuals_history)

        # Save the data into files and show final figure.
        np.save("GAData", self.data, allow_pickle=True)
        self.curve_data = [
            copy.deepcopy(
                self.generation_smoothing), copy.deepcopy(
                self.merit_smoothing)]
        np.save("SmoothingData", self.curve_data, allow_pickle=True)
        plt.show()

    def data_saver(self):
        """
        Saves the data from the algorithm into appropriate lists so that the data can then be saved into lists.
        """
        item_in_data = []

        # Append the generation number to both lists.
        item_in_data.append(self.generation_list[-1].generation)
        self.generation_smoothing.append(self.generation_list[-1].generation)

        # Loop over each individual and append to the lists.
        for i in range(len(self.generation_list[-1].population)):
            self.generation_x_axis.append(self.generation_list[-1].generation)
            item_in_data.append(self.generation_list[-1].population[i])
            self.merit_y_axis.append(
                self.generation_list[-1].population[i].merit)
            self.merit_smoothing[self.generation_list[-1].generation].append(
                self.generation_list[-1].population[i].merit)
        self.data.append(copy.deepcopy(item_in_data))

    def data_plotter(self):
        """
        Plots the merit function vs. generation data onto a new figure and saves it.
        """
        # Try to clear the figure.
        try:
            plt.clf()
        except BaseException:
            pass

        # Make the new plotting lists.
        x_axis = np.array(self.generation_x_axis)
        x_average = np.array(self.generation_smoothing)
        y_average = []

        # Populate the y_average list by calculating the average.
        for i in range(len(self.generation_smoothing)):
            y_average.append(np.average(self.merit_smoothing[i]))
        plt.xticks(list(range(0, len(x_axis), 3)))
        plt.semilogy(x_axis, self.merit_y_axis, 'o')

        # Plot the progression curve.
        if len(x_average) == 1:
            pass
        else:
            f = interpolate.interp1d(x_average, y_average)
            x_fit = np.linspace(0, x_average[-1], int((x_average[-1] + 1) / 2))
            y_fit = f(x_fit)
            plt.semilogy(x_fit, y_fit, '-')

        plt.xlabel("Generation Number")
        plt.ylabel("Merit")
        plt.title(
            f"Progression of the Merit as Generation Number Increases. R = {self.generation_list[-1].mutation_rate}")
        plt.savefig("MeritProgression.png")
