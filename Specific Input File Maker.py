from scipy import optimize
from scipy.constants import e, c, mu_0 as mu0, epsilon_0 as eps0, m_e
import argparse
import numpy as np


def plasma_frequency(plasma_density):

    return e * np.sqrt(plasma_density / (m_e * eps0))


def skin_depth(plasma_density):

    return np.sqrt(m_e / (plasma_density * mu0)) / e


if __name__ == "__main__":

    # Specifies how one interacts with the cli options

    parser = argparse.ArgumentParser()

    # Filename
    parser.add_argument(
        "-f",
        "--filename",
        help="specify the file name. Default is output.inp",
        type=str,
        default="output.inp")

    # Cores per node

    parser.add_argument(
        "--cores_per_node",
        type=int,
        help="the number of cores per node the system will have to work with. Default is 128.",
        default=40)

    # Dimension

    parser.add_argument(
        "-d",
        "--dimension",
        type=int,
        help="the dimension for the simulation to be run in. Default is 2.",
        choices=[
            2,
            3],
        default=2)

    parser.add_argument(
        "--ndump",
        default=4800,
        help="specifies the number of iterations between any diagnostic or restart file dumps. Default is 4800",
        type=int)

    # simulation

    simulation = parser.add_argument_group(title="simulation")

    simulation.add_argument(
        "-a",
        "--algorithm",
        type=str,
        help="specifies the algorithm to be used in the simulation. Default is 'quasi_3d'",
        default="quasi-3D",
        choices=[
            "standard",
            "quasi-3D",
            "pgc",
            "hd_hybrid"])

    # Node number

    node_conf = parser.add_argument_group(title='node_conf')

    node_conf.add_argument(
        "--node_number",
        type=tuple,
        help="specifies the number of nodes to use in each direction for the simulation. The total number of nodes will be the product of the number of nodes for each direction. Default is 1.",
        default=(
            96,
            4))

    node_conf.add_argument(
        "--if_periodic",
        type=tuple,
        help="specifies if the boundary conditions for each direction will be periodic boundary conditions. Default is false.",
        default=(
            "false",
            "false"))

    # Window span

    space = parser.add_argument_group(title="space")

    space.add_argument(
        "--boundaries",
        nargs=2,
        help="specify the lower and upper boundaries of the global simulation space at the beggining of the simulation in [m]. Default is 0.",
        default=[(-3e-3, 0), (0, 50e-6)])

    space.add_argument(
        "--if_move",
        type=str,
        help="specifies a whether the code should use a moving window at the speed of light in the specified directions. Default is false.",
        default=(
            "true",
            "false"))

    # restart

    restart = parser.add_argument_group(title="restart")

    restart.add_argument(
        "--ndump_fac",
        default=10,
        type=int,
        help="specifies the frequency at which to write restart information. Default is 0.")

    restart.add_argument(
        "--if_restart",
        default="false",
        type=str,
        help="specifies whether the code should attempt to read information from restart files previously saved in order to restart the run exactly as it was at the time the restart information was saved. Default is false.")

    restart.add_argument(
        "--if_remold",
        default="false",
        type=str,
        help="specifies whether the code should remove older restart files after it has successfuly saved restart information on all the nodes. Default is false.")

    # time

    time = parser.add_argument_group(title="time")

    time.add_argument(
        "-t",
        "--time",
        default=[
            0,
            9.7e-17],
        type=list,
        help="specify the initial and final time of the simulation in [s]. Default is (0,9.7e-17).")

    # el_mag_fld

    el_mag_fld = parser.add_argument_group(title="el_mag_fld")

    el_mag_fld.add_argument(
        "--smooth_type",
        default="stand",
        type=str,
        help="controls the type of smoothing to be applied to the EM fields. Default is 'stand'",
        choices=[
            "none",
            "stand",
            "local"])

    # emf_bound

    emf_bound = parser.add_argument_group(title="emf_bound")

    emf_bound.add_argument(
        "--emf_type",
        default=[["open"] * 2, ["axial", "open"]],
        type=list,
        help="specifies the boundary conditions to use for the electro-magnetic fields. ### NOT YET FULLY IMPLEMENTED ### Default is [[vpml]*2]*2]")

    emf_bound.add_argument(
        "--emf_smooth_type",
        default=("5pass", "5pass"),
        type=tuple,
        help="specifies the type of smoothing to perform in each direction.")

    particles = parser.add_argument_group(title="particles")

    particles.add_argument(
        "--interpolation",
        default="quadratic",
        type=str,
        help="specifies the interpolation level to be used for all particles. Default is quadratic.")

    # plasma_electrons

    plasma = parser.add_argument_group(title="plasma")

    plasma.add_argument(
        "-n0",
        "--plasma_density",
        type=float,
        default=1.25e24,
        help="specifies the reference simulation plasma density for the simulation in units of [m^-3].Default is 0.0.")

    plasma.add_argument(
        "--num_par_x",
        default=(2,2),
        type=tuple,
        help="specifies the number of particles per cell to use in each direction. The total number of particles per cell will be the product of all the components of num_par_x. Default is (2,2).")

    plasma.add_argument(
        "--plasma_thermal_speed",
        default=0.0001,
        type=float,
        help="specifies the constant thermal spread in velocities for this particle species in each of the directions. Momenta specified are proper velocities i.e. gamma * v in units of c.")

    plasma.add_argument(
        "--upramp",
        default=1.5e-3,
        type=float,
        help="the length of the upramp to maximum plasma density, in [m]")

    plasma.add_argument(
        "--downramp",
        default=1.5e-3,
        type=float,
        help="the length of the downramp to minimum plasma density, in [m]")

    plasma.add_argument(
        "--plasma_length",
        default=6e-3,
        type=float,
        help="The length of the plasma in [m]")

    # beam

    beam = parser.add_argument_group(title="beam")

    beam.add_argument(
        "-q",
        "--beam_charge",
        default=20e-15,
        type=float,
        help="the overall beam charge in [C]. Default is 20fC.")

    beam.add_argument(
        "--num_par_x_beam",
        default=(2,2),
        type=tuple,
        help="specifies the number of particles per cell to use in each direction. The total number of particles per cell will be the product of all the components of num_par_x. Default is 0")

    beam.add_argument(
        "--beam_thermal_speed",
        default=0.0,
        type=float,
        help="specifies the constant thermal spread in velocities for this particle species in each of the directions. Momenta specified are proper velocities i.e. gamma * v in units of c. Default is 0.")

    beam.add_argument(
        "-E",
        "--beam_energy",
        type=float,
        default=50,
        help="specifies the energy of the injected beam, in [MeV]. Default is 50MeV")

    beam.add_argument(

        "-L",
        "--beam_length",
        type=float,
        default=4e-4,
        help="the length of the electron beam"
    )

    beam.add_argument(
        "-R",
        "--beam_radius",
        type=float,
        default=3e-5,
        help="beam radius"
    )

    beam.add_argument(
        "-se",
        "--beam_energy_spread",
        type=float,
        default=0.05,
        help="MeV"
    )

    # laser

    laser = parser.add_argument_group(title="laser")

    laser.add_argument(
        "-I",
        "--intensity",
        default=4e18,
        type=float,
        help="specify the peak laser intensity in [W * cm^-2]")

    laser.add_argument(
        "--laser_wavelength",
        type=float,
        help="the wavelength of the laser, in metres",
        default=8e-7)

    laser.add_argument(
        "-w0",
        "--laser_spot_size",
        type=float,
        default=20e-6
    )

    laser.add_argument(
        "-s",
        "--focus_position",
        type=float,
        default=1
    )

    # currents

    current = parser.add_argument_group(title="current")

    current.add_argument(
        "--current_smooth_type",
        default="none",
        type=tuple,
        help="specifies the type of smoothing to perform in each direction")

    # Only run this at the end
    args = parser.parse_args()

    with open(args.filename, "w+") as file:

        # simulation

        file.write("simulation\n{\n")

        file.write(f"algorithm = '{args.algorithm}',\n")

        file.write("}\n")

        # node_conf

        file.write("\nnode_conf\n{\n")

        file.write(
            f"node_number(1:{args.dimension}) = " + str(
                args.node_number).replace(
                "(", "").replace(
                ")", "") + ",\n")

        file.write(
            f"if_periodic(1:{args.dimension}) = " +
            f"{args.if_periodic}".replace(
                "('",
                ".").replace(
                "')",
                ".").replace(
                    "', '",
                    ".,.") +
            ",\n")

        file.write("}\n")
        # spatial grid
        file.write("\ngrid\n{\n")

        delta1 = args.laser_wavelength / (20 * skin_depth(args.plasma_density))  # x

        delta2 = 1 / 4  # y

        delta3 = 1 / 4  # z

        # Jesus that's a lot. Essentially, I want to take the user's two input
        # tuples (e.g. 0,0,0 1,2,3), and take their difference into a list or
        # tuple. Please submit a commit if you can fix this to be shorter.

        boundaries = [[]] * args.dimension

        for count, item in enumerate(args.boundaries):

            for subitem in item:
                boundaries[count] = list(item)

        window_lengths = [abs(boundaries[1][i] - boundaries[0][i])
                          for i in range(args.dimension)]

        window_lengths = [i / skin_depth(args.plasma_density)
                          for i in window_lengths]

        boundaries = [i / skin_depth(args.plasma_density)
                      for i in boundaries]

        # nx, ny, nz

        nx = int(np.ceil(

            np.ceil(
                window_lengths[0] / delta1

            ) / args.cores_per_node
        ) * args.cores_per_node)

        ny = int(np.ceil(

            np.ceil(
                window_lengths[1] / delta2

            ) / args.cores_per_node
        ) * args.cores_per_node)
        try:  # skips nz if it's only 2D
            nz = int(np.ceil(

                np.ceil(
                    window_lengths[2] / delta3

                ) / args.cores_per_node
            ) * args.cores_per_node)

            nlist = [nx, ny, nz]
        except BaseException:
            nlist = [nx, ny]
            pass

        file.write(
            f"nx_p(1:{args.dimension}) = " +
            str(nlist).replace(
                "[",
                "").replace(
                "]",
                "") +
            ",\n")

        file.write('coorindates = "cylindrical",\n')

        file.write("n_cyl_modes = 1,\n")

        file.write("}\n")

        # Time-step

        file.write("\ntime_step\n{\n")

        file.write(
            f"dt = {1 / np.sqrt(2*sum(map(lambda x: 1/(x*x),[delta1,delta2]))) if args.dimension == 2 else 1 / np.sqrt(2*sum(map(lambda x: 1/(x*x),[delta1,delta2,delta3])))}, ! courant condition /sqrt(2) \n")

        file.write(f"ndump = {args.ndump},\n")

        file.write("}\n")

        # Restart

        file.write("\nrestart\n{\n")

        file.write(f"ndump_fac = {args.ndump_fac},\n")
        file.write(f"if_restart = .{args.if_restart}.,\n")
        file.write(f"if_remold = .{args.if_remold}.,\n")

        file.write("}\n")

        # Space

        file.write("\nspace\n{\n")

        file.write(f"xmin(1:{args.dimension}) = ")

        for i in range(args.dimension):

            file.write(str(boundaries[0][i]) + ", ")

        file.write("\n")

        file.write(f"xmax(1:{args.dimension}) = ")

        for i in range(args.dimension):

            file.write(str(boundaries[1][i]) + ", ")

        file.write("\n")

        file.write(
            f"if_move(1:{args.dimension}) =  " +
            f"{args.if_move}".replace(
                "(",
                ".").replace(
                ")",
                ".").replace(
                ",",
                ".,.").replace(
                    "'",
                    "").replace(
                        " ",
                        "") +
            ",\n}\n")

        # time

        file.write("\ntime\n{\n")

        file.write(
            f"tmin = {args.time[0] * plasma_frequency(args.plasma_density)},\n")
        file.write(
            f"tmax = {args.time[1] * plasma_frequency(args.plasma_density)},\n")

        file.write("}\n")

        # el_mag_fld

        file.write("\nel_mag_fld\n{\n")

        file.write(f'smooth_type = "{args.smooth_type}",\n')

        file.write("}\n")

        # emf_bound

        file.write("\nemf_bound\n{\n")

        for i in range(args.dimension):
            file.write(
                f"type(1:{args.dimension},{i+1}) = {args.emf_type[i]}".replace(
                    "[", "").replace(
                    "]", "").replace(
                    "'", '"') + ",\n")

        file.write("}\n")

        file.write("\nsmooth\n{\n")

        file.write(
            f"type(1:{args.dimension}) =  {args.emf_smooth_type},\n".replace(
                "('", "'").replace(
                "')", "'"))

        file.write("}\n")

        # particles

        file.write("\nparticles\n{\n")

        file.write("num_species = 2,\n")

        file.write("num_cathode= 0,\n")

        file.write(f'interpolation = "{args.interpolation}",\n')

        file.write("}\n")

        # plasma electrons

        file.write("\nspecies\n{\n")

        file.write('name = "electrons",\n')

        file.write("num_par_max = 4000000,\n")

        file.write("num_par_theta = 16,\n")

        file.write("rqm = -1.0d0,\n")

        file.write(
            f"num_par_x(1:{args.dimension}) = " + str(
                args.num_par_x).replace(
                "(", "").replace(
                ")", "") + ",\n")

        file.write("}\n")

        file.write("\nudist\n{\n")

        file.write(
            f"uth(1:3) = {args.plasma_thermal_speed}, {args.plasma_thermal_speed}, {args.plasma_thermal_speed},\n")

        file.write("ufl(1:3) = 0.0, 0.0, 0.0,\n")

        file.write("}\n")

        file.write("\nprofile\n{\n")

        file.write("den_min = 1.0d-7,\n")

        file.write("density = 1.0,\n")

        file.write('profile_type = "math_func",\n')

        def up(x):
            return np.tanh((x - 4 * args.upramp) /
                           args.upramp, dtype=np.longdouble)

        def down(x):
            return np.tanh((4 *
                            (2 *
                             args.upramp -
                             args.downramp) +
                            args.plasma_length -
                            x) /
                           args.downramp, dtype=np.longdouble)

        def doubleSig(x, sign=-1):
            return np.longdouble(sign * (1 + up(x)) * (1 + down(x)) / 4)

        num = optimize.minimize_scalar(doubleSig)

        file.write(
            f'math_func_expr = "if(x1 < 0.0, 0.0, if(x1 <= {(args.plasma_length + 4*(args.downramp + args.upramp))/ skin_depth(args.plasma_density)}, (1 + tanh((x1 - {4*args.upramp / skin_depth(args.plasma_density)}) / {args.upramp / skin_depth(args.plasma_density)})) * (1 + tanh( ({(4*(2*args.upramp - args.downramp) + args.plasma_length) / skin_depth(args.plasma_density)} - x1) / {args.downramp / skin_depth(args.plasma_density)} ) / ({4 * doubleSig(num.x,sign=1)})),0.0))",\n')

        # file.write(f'math_func_expr = "if(x1 < 0.0, 0.0, if(x1 <= {args.plasma_length / 2}, 0.5*(tanh((x1-{4*args.upramp})/{args.upramp})+1),if(x1 <= {args.plasma_length}, -0.5*(tanh((x1- {4*(args.downramp - args.upramp)-args.plasma_length})/{args.downramp})-1), 0.0)))",\n')

        file.write("}\n")

        file.write("\nspe_bound ! placeholder, cannot yet be changed.\n{\n")

        file.write(
            'type(1:2,1) = "open", "open",\ntype(1:2,2) = "axial", "open",\n')

        file.write("}\n")

        # beam electrons, real s**t

        file.write("\nspecies\n{\n")

        file.write('name = "Beam",\n')

        file.write("num_par_theta = 16,\n")

        file.write("num_par_max = 4000000,\n")

        file.write("rqm = -1.0d0,\n")

        file.write(
            f"num_par_x(1:{args.dimension}) = " + str(
                args.num_par_x_beam).replace(
                "(", "").replace(
                ")", "") + ",\n")

        file.write("init_fields = .true.,\n")

        file.write("}\n")

        file.write("\nudist\n{\n")

        file.write("use_classical_uadd = .true.,\n")

        file.write(
            f"uth(1:3) = {args.beam_thermal_speed}, {args.beam_thermal_speed}, {args.beam_thermal_speed},\n")

        file.write(
            f"ufl(1:3) = {args.beam_energy * e * 1e6 / (m_e * c * c)}, {args.beam_energy_spread * e * 1e6 / (m_e * c * c)}, {args.beam_energy_spread * e * 1e6 / (m_e * c * c)},\n")

        file.write("}\n")

        file.write("\nprofile\n{\n")

        file.write("den_min = 1.0d-7,\n")

        file.write(
            f"density = {args.beam_charge / (e * (2*np.pi)**1.5 * args.beam_length * args.beam_radius**2 * args.plasma_density)},\n")

        file.write('profile_type = "gaussian", "gaussian",\n')

        file.write(f"gauss_center(1:{args.dimension}) = {-(80e-15 * c + (2 * np.pi * c)/plasma_frequency(args.plasma_density))/skin_depth(args.plasma_density)}, 0,\n")
        file.write(
            f"gauss_sigma(1:{args.dimension}) = {args.beam_length / skin_depth(args.plasma_density)}, {args.beam_radius/ skin_depth(args.plasma_density)},\n")

        file.write("}\n")

        file.write("\nspe_bound\n{\n")

        file.write("type(1:2,1) = 'open', 'open',\n")
        file.write("type(1:2,2) = 'axial', 'open',\n")

        file.write("}\n")

        file.write('\ndiag_species\n{\n')

        file.write('ndump_fac = 1,\n')
        file.write('ndump_fac_ave = 1,\n')
        file.write('ndump_fac_ene = 1,\n')
        file.write('ndump_fac_lineout = 1,\n')
        file.write('ndump_fac_pha = 1,\n')

        file.write('n_ave(1:2) = 128, 1,\n')

        file.write('reports = "charge",\n')

        file.write('ndump_fac_raw = 10,\n')
        file.write('raw_fraction = 1,\n')
        file.write("}\n")

        # zpulse

        file.write("\nzpulse\n{\n")

        file.write(
            f"a0 = { (e/(np.pi * m_e * np.sqrt(2*eps0 * c ** 5 ))) *  np.sqrt(args.intensity * 1e4) * args.laser_wavelength},\n")

        file.write(
            f"omega0 = {2 * np.pi * c * np.sqrt(eps0 * m_e / args.plasma_density) / (args.laser_wavelength * e)},\n")

        file.write("pol = 0.0,\n")

        file.write("pol_type = 0,\n")

        file.write('propagation = "forward",\n')

        file.write("lon_type = 'polynomial',\n")
        file.write(f"lon_rise = {(40e-15 * c)/skin_depth(args.plasma_density)},\n")
        file.write(f"lon_fall = {(40e-15 * c)/skin_depth(args.plasma_density)},\n")
        file.write(f"lon_start = {-1*(80e-15 * c)/skin_depth(args.plasma_density)},\n")
        file.write('per_type = "gaussian",\n')
        file.write("per_center = 0.0,\n")
        file.write(
            f"per_w0 = {args.laser_spot_size / skin_depth(args.plasma_density)},\n")
        file.write(f"per_focus = {-1 * args.focus_position / skin_depth(args.plasma_density)},\n") 

        file.write("}\n")

        # file.write("\nsmooth\n{\n")

        # file.write(f"type(1:{args.dimension}) = {args.current_smooth_type},\n")

        # file.write("}\n")
