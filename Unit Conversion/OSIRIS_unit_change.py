import sys
from constitutive_rels import *
import json

"""
Takes an input file of system parameters, and converts them to usable relative numbers.
---------------------------------------------------------------------------------------
Example usage:

    > python OSIRIS_unit_change.py 3 input_file.json out_file.json

    This produces an output file out_file.json in the working directory, which will be for the three-dimensional OSIRIS.

    N.B.: Please ensure the input file is the same dimension as the output file you would like.

"""

# Choose a dimension (2 or 3)

dimension = int(sys.argv[1])

# Specify infile

inFile = sys.argv[2]

# Specify outfile

fileName = sys.argv[3]

# Bring data in

with open(str(inFile), "r") as read_file:
    data = json.load(read_file)


# Creates dictionaries from the data

for meta_config in data:

    # A reference data copy
    exec(str(meta_config) + " = " + str(data[str(meta_config)]))

    # A copy of the data to work on for the output
    exec(str(meta_config) + "OSI" + " = " + str(data[str(meta_config)]))

# Data manipulation. I can't think of a prettier way to do this honestly.
# Try not to touch it. All of the 'undefined' errors are to be ignored.
# The previous for loop creates and defines them, but isn't executed until
# runtime.

# System
SystemOSI['window_dimensions'] = [
    i / skin_depth(Plasma['density']) for i in System['window_dimensions']]
if dimension == 3:
    SystemOSI['dimension_steps'] = [
        x_step(
            Laser['wavelength']) /
        skin_depth(
            Plasma['density']),
        y_step(
            Plasma['density']) /
        skin_depth(
            Plasma['density']),
        z_step(
            Plasma['density']) /
        skin_depth(
            Plasma['density'])]  # These are the deltas
    SystemOSI['cores_per_dim'] = [
        nx(
            System['window_dimensions'][0], Laser['wavelength']), ny(
            System['window_dimensions'][1], Plasma['density']), nz(
                System['window_dimensions'][2], Plasma['density'])]
elif dimension == 2:
    SystemOSI['dimension_steps'] = [
        x_step(
            Laser['wavelength']) /
        skin_depth(
            Plasma['density']),
        y_step(
            Plasma['density']) /
        skin_depth(
            Plasma['density'])]  # These are the deltas
    SystemOSI['cores_per_dim'] = [nx(System['window_dimensions'][0], Laser['wavelength']), ny(
        System['window_dimensions'][1], Plasma['density'])]

SystemOSI['simulation_length'] = System['simulation_length'] / \
    skin_depth(Plasma['density'])
# Annoyingly, I can't use timestep() for this easily, so this is the
# alternative. It also has a discrepancy from the spreadsheet
SystemOSI['dt'] = 0.99 * \
    math.sqrt(sum(map(lambda x: x * x, SystemOSI['dimension_steps'])))
SystemOSI['timesteps'] = SystemOSI['simulation_length'] / SystemOSI['dt']
# Also annoyingly, can't use ndump() for this either
SystemOSI['ndump'] = SystemOSI['timesteps'] / 100

# Plasma

PlasmaOSI['density'] = 1  # Identically
PlasmaOSI['total_length'] = Plasma['total_length'] / \
    skin_depth(Plasma['density'])
PlasmaOSI['ramp_lengths'] = [
    i / skin_depth(Plasma['density']) for i in Plasma['ramp_lengths']]
PlasmaOSI['uniform_length'] = uniform_length(
    PlasmaOSI['total_length'], PlasmaOSI['ramp_lengths'])
PlasmaOSI['radius'] = Plasma['radius'] / skin_depth(Plasma['density'])

# Laser

# This is a guess, since it's not included in the excel doc
LaserOSI['wavelength'] = Laser['wavelength'] / wavelength(Plasma['density'])
LaserOSI['frequency'] = laser_frequency(
    Laser['wavelength']) / plasma_frequency(Plasma['density'])
LaserOSI['duration'] = plasma_frequency(Plasma['density']) * Laser['duration']
LaserOSI['focus_spot_radius'] = Laser['focus_spot_radius'] / \
    skin_depth(Plasma['density'])
LaserOSI['focus_position'] = Laser['focus_position'] / \
    skin_depth(Plasma['density'])

# Witness beam
Witness_BeamOSI['radius'] = Witness_Beam['radius'] / \
    skin_depth(Plasma['density'])
Witness_BeamOSI['duration'] = Witness_Beam['duration'] / \
    skin_depth(Plasma['density'])
Witness_BeamOSI['lorentz_factor'] = Witness_Beam['energy'] * \
    e / (c * c * m_e) + 1
Witness_BeamOSI['fwhm'] = (Witness_Beam['energy_spread']
                           * e / (c * c * m_e)) / (2 * math.sqrt(2 * math.log(2)))

if dimension == 3:
    Witness_BeamOSI['density'] = (num_electons(Witness_Beam['charge']) / (4 * math.pi * Witness_Beam['duration']
                                                                          * Witness_Beam['radius'] * Witness_Beam['radius'] / 3)) / Plasma['density']
elif dimension == 2:
    # This is whack. This cannot be correct.
    Witness_BeamOSI['density'] = (num_electons(Witness_Beam['charge']) / (
        2 * math.pi * Witness_Beam['duration'] * Witness_Beam['radius'])) / Plasma['density']

Witness_BeamOSI['focus_position'] = Witness_Beam['focus_position'] / \
    skin_depth(Plasma['density'])
Witness_BeamOSI['beam_centre'] = Witness_Beam['beam_centre'] / \
    skin_depth(Plasma['density'])
Witness_BeamOSI['separation'] = Witness_Beam['separation'] / \
    skin_depth(Plasma['density'])

# Write output file

newFile = {}

newFile['System'] = SystemOSI
newFile['Plasma'] = PlasmaOSI
newFile['Laser'] = LaserOSI
newFile['Witness_Beam'] = Witness_BeamOSI

with open(str(fileName), 'x') as f:
    json.dump(newFile, f, indent=1)
