import os
import h5py
import numpy as np
from os import listdir
import re
import time


class Individual:
    """
    A class that defines an 'Individual' object.
    The input parameters are the parameters that are being investigated
    in the genetic algorithm.
    This class has the ability to change the input file(s) for the
    simulation, run the simulation, extract the merit value, and restore
    the input files to their original state, so that they can be used
    for the next generation.

    Note: ====== !!! This needs to be changed !!! ======
          The current merit is just the sum of the items in the
          ParameterList tuple. This was used as dummy data to test
          if the genetic algorithm was working.
          See merit_calc function for more details.

    Attributes:
        *ParameterList = When an instance of this class is
                         initialised, it can take any number of
                         arguments, which are all then stored into a
                         tuple.
                         Later converted into a list for convenience.

    Methods:
        __init__ = Initialises an instance of the 'Individual'
                   object and assigns the variables.

        __str__ = Returns the parameters along with their corresponding
                  values. Also returns the merit value.

        merit_calc = Calls the methods to change the input file(s), run
                     the simulation, extract the merit, and restore the
                     changes made to the input file(s).
                     Currently the merit is the sum of the parameters,
                     and needs to be changed.
                     Check merit_calc method for more details.

        change_file = This method changes the text in the input file(s)
                      to the desired input parameters.

        run_simulation = This method should run the simulation.
                         The code needs to be implemented still.

        list_files = Puts the data files into a tuple.

        extract_merit = Extracts the merit value from the input file.

        reverse_change = Restores the input file(s) to the original state
                         so that they can be used for the next
                         generation.
    """

    def __init__(self, *ParameterList):
        """
        Initialises an instance of the 'Individual' class.
        The class can take any number of arguments, and they are placed
        into a tuple called ParameterList. This is then turned into a
        list.

        Parameters
        ----------
        self.parameter_list
            Takes the argument that is passed from the method and converts the tuple   into a list.

        self.merit
            Stores the merit value. Set to None as there is no merit calculated when the class in initialised.
        """
        self.parameter_list = list(ParameterList)
        self.merit = None

    def __str__(self):
        """
        Method returns the values of the parameters and the merit value.
        """
        # For loop used to cycle through all the parameters.
        dataList = [
            f"Parameter {i+1}: {self.parameter_list[i]}" for i in range(len(self.parameter_list))]

        return str(dataList)

    def merit_calc(self,number,inputFile):
        """
        Method calculates the merit value used by changing the
        input file(s) with the desired parameters, running the
        simulation, extracting the merit value from the data, and
        restoring the input file(s) so that they can be used for the
        next generation.

        The run_simulation and extract_merit methods are commented
        out as the run_simulation method still needs to be written.
        The extract_merit method can only be used once the run_simulation
        method has been implemented.
        The self.merit variable is currently set by summing all the
        parameters together, as this was used as dummy data to test how
        well the algorithm functioned.

        Parameters:
            input_file = Passes in the input file that is used
                         to run the simulation.
        """

        self.run_simulation(number,inputFile)
        
        # self.extract_merit()
        self.merit = np.prod(self.parameter_list)

    def create_jobscript(self,number,inputFile):
        """
        Creates the individual's jobscript file
        
        Parameters
        ----------
        number : int
            Universal identifier for the individual
        """
        while not os.path.exists(f"jobscript{number}.pbs"):
            time.sleep(1)
        os.system(f"sed -i 's/-N q3d_no_beam/-N Individual{number}/g' jobscript{number}.pbs")
        os.system(f"sed -i 's+/work/dp152/dp152/dc-clos1/q3d_no_beam.inp+{os.getcwd()}/{inputFile}+g' jobscript{number}.pbs")

    def run_simulation(self,number,inputFile):
        """
        Takes the individual, creates the input file, and runs the simulation.
        """
        self.create_jobscript(number,inputFile)
        os.system(f"qsub jobscript{number}.pbs")

    def list_files(self, directory):
        """
        Takes the data files that are returned from the
        simulation and places them into a tuple.

        Parameters
        ----------
        directory : str
            the working directory.
        """
        
        s0 = 'RAW-Beam' # String target
        
        e0 = '.h5' # File extension

        return (f for f in listdir(directory) if (s0 in f and e0 in f))

    def extract_merit(self,inputFile):
        """
        Extracts the merit value from the individual's RAW data
        """
        dirname = 'MS/RAW/Beam'
        files = self.list_files(dirname)
        it_old = 0

        for f in files:
            fullfilename = dirname + '/' + f
            try:
                it_new = int(
                    re.search(
                        'RAW-Beam-(.+?).h5',
                        fullfilename).group(1))
                if it_new > it_old:
                    it_old = it_new
                    myfile = fullfilename
            except BaseException:
                pass

        hf = h5py.File(myfile, 'r') # Read in the file
        q = np.abs(hf['q'][:]) # Strip the charge data
        ene = hf['ene'][:] # Strip the energy data

        qene = q * ene # Calculates the charge-energy product
        tot_qene = sum(qene) # The total charge energy product
        tot_charge = sum(q) # The total charge
        ave = tot_qene / tot_charge # Weighted average

        standard_deviation = np.sqrt(sum(q * (ene - ave)**2 / tot_charge)) # Weighted error
        self.merit = standard_deviation / ave # Merit value
