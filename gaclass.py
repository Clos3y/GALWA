import os
import numpy as np
import matplotlib.pyplot as plt
from scipy import interpolate
from scipy.optimize.minpack import curve_fit
from generationclass import Generation
import operator
import copy


class GeneticAlgorithm:
    """
    Class that defines a genetic algorithm object. This class is used
    to define the initial variables of the algorithm and run it.

    Attributes:
        MaxGenerationNumber = Stores the maximum number of generations
                              that we want to iterate through.

    Methods:
        __init__ = Defines all the initial variables that are needed
                   to run the genetic algorithm.

        run = Runs the genetic algorithm.

        data_saver = Saves the data into appropriate lists so that
                     the data can be saved into files.

        data_plotter = Plots the data onto a figure and then saves
                       the figure.
    """

    def __init__(self, MaxGenerationNumber):
        """
        This method defines the initial variables that are used to
        run the genetic algorithm.

        Variables:
            self.max_generation_number = Stores the maximum number
                                         of generations that we want
                                         to iterate through.

            self.generation_list = Stores all the generations that are
                                   created into a list.

            self.current_generation = Stores the current generation
                                      number.

            self.individuals_history = List that stores every 'individual'
                                       object that is created.

            self.generation_x_axis = Stores the generation numbers in a list
                                     to be used for plotting.
                                     Represents the x-axis.

            self.merit_y_axis = Stores the merit values in a list to be used
                                for plotting. Represents the y-axis.

            self.generation_smoothing = A list that is used to fit s smooth
                                        curve onto the data so that the
                                        overall trend can be seen.

            self.merit_smoothing = A list that is used to fit a smooth curve
                                   onto the data so that the overall trend
                                   can be seen.

            self.data = A list that stores all the data, which is saved
                        into a numpy file.

            self.curve_data = Saves the data that is used to create the
                              curve on the plot.
        """
        self.max_generation_number = MaxGenerationNumber
        self.generation_list = []
        self.current_generation = 0
        self.individuals_history = []
        self.generation_x_axis = []
        self.merit_y_axis = []
        self.generation_smoothing = []
        self.merit_smoothing = []
        self.data = []
        self.curve_data = []

    def run(self):
        """
        Runs the genetic algorithm by using a for loop.
        Iterates for the number specified by the maximum generation
        number variable.
        Saves the data at the end.
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
            # self.generation_list[i].output_current_status()
            self.data_plotter()
            self.generation_list[i].mating_stage(
                History=self.individuals_history)

        # Tells the user what the best simulation parameters were.
        self.generation_list[-1].population.sort(
            key=operator.attrgetter('merit'), reverse=False)
        # print("The best simulation parameters achieved were:")
        # print(self.generation_list[i].population[0])

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
        Saves the data from the algorithm into appropriate lists so
        that the data can then be saved into lists.

        Variables:
            item_in_data = Stores the data for each generation.
                           This is then appended to the self.data
                           list, which means each item in the
                           self.data list is data about a generation.
                           Structure of item_in_data:
                           [generation_num, individual_1, ... , individual_N]
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
        Clears the previous figure if it exists. Plots the data onto
        a new figure and saves it.
        To work out the progress of the algorithm, the average merit for
        each generation is calculated and a curve is plotted.

        Variables:
            x_axis = Stores the x-axis as a numpy array.

            x_average = Stores the x-axis that is used for the progression
                        curve.

            y_average = Stores the average merit per generation.

            f = Stores the function that is used to plot the progression
                curve.

            x_fit = Stores the x-coordinates for the progression curve.

            y_fit = Stores the y-coordinates for the progression curve.
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
        plt.axhline(4.725e-6)
        plt.title(f"Progression of the Merit as Generation Number Increases. R = {self.generation_list[-1].mutation_rate}")
        plt.savefig("MeritProgression.png")
