import os
import h5py
import numpy as np
from os import listdir
import re
import time


class Individual:
    """Defines the individual, meant quite literally as an individual, within a generation.

    Attributes
    ----------
    ParameterList : list
        A list of parameters for the individual to possess.
    """

    def __init__(self, *ParameterList):
        """
        Parameters
        ----------
        self.parameter_list : list
            Takes the argument that is passed from the method and converts the tuple into a list.
        """
        self.parameter_list = list(ParameterList)

        self.merit = None

    def __str__(self):

        # For loop used to cycle through all the parameters.
        dataList = [
            f"Parameter {i+1}: {self.parameter_list[i]}" for i in range(len(self.parameter_list))]

        return str(dataList)

    def merit_calc(self, number, inputFile):
        """Calculates the merit function for the individual, and assigns it to them.

        Parameters
        ----------
        number : int
            Universal identifier for the individual

        inputFile
            The individual's input file.
        """

        self.run_simulation(number, inputFile)

        self.merit = self.extract_merit(number)

    def create_jobscript(self, number, inputFile):
        """Creates the individual's jobscript file

        Parameters
        ----------
        number : int
            Universal identifier for the individual

        inputFile
            The individual's input file.
        """

        while not os.path.exists(f"jobscript{number}.pbs"):
            time.sleep(1)

        # These directories need altering depending on your specific usage, the same is true in the jobscript (i.e, your OSIRIS binary will not be in the same absolute path as mine)
        os.system(
            f"sed -i 's/-N q3d_no_beam/-N Individual{number}/g' jobscript{number}.pbs")
        os.system(
            f"sed -i 's+/work/dp152/dp152/dc-clos1/q3d_no_beam.inp+{os.getcwd()}/{inputFile}+g' jobscript{number}.pbs")
        os.system(
            f"sed -i 's+completionTest+{os.getcwd()}/completionTest+g' jobscript{number}.pbs")

    def run_simulation(self, number, inputFile):
        """
        Takes the individual, creates the input file, and runs the simulation.
        """
        self.create_jobscript(number, inputFile)

        os.system(f"qsub jobscript{number}.pbs")

        while not os.path.exists("completionTest"):
            time.sleep(1)

        os.system("rm completionTest")

    def list_files(self, directory):
        """
        Takes the data files that are returned from the
        simulation and places them into a tuple.

        Parameters
        ----------
        directory : str
            the working directory.
        """

        s0 = 'RAW-Beam'  # String target

        e0 = '.h5'  # File extension

        return (f for f in listdir(directory) if (s0 in f and e0 in f))

    def extract_merit(self, number):
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

        hf = h5py.File(myfile, 'r')  # Read in the file
        q = np.abs(hf['q'][:])  # Strip the charge data
        ene = hf['ene'][:]  # Strip the energy data

        qene = q * ene  # Calculates the charge-energy product
        tot_qene = np.sum(qene)  # The total charge energy product
        tot_charge = np.sum(q)  # The total charge
        ave = tot_qene / tot_charge  # Weighted average

        standard_deviation = np.sqrt(
            np.sum(q * (ene - ave)**2 / tot_charge))  # Weighted error
        self.merit = standard_deviation / ave  # Merit value

        os.system(f"echo 'Average: {ave}' >> Individual{number}.data")
        os.system(
            f"echo 'Std Dev: {standard_deviation}' >> Individual{number}.data")
