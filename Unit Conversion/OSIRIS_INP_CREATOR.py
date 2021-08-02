from constitutive_rels import skin_depth
from scipy.constants import e, c, mu_0 as mu0, epsilon_0 as eps0
import math

if __name__ == "__main__":

    print("\nSam Close\n")

    with open("logo.txt", "r") as f:
        print(f.read())

    print("\nWelcome to the (unofficial) OSIRIS input config generator. You will be asked a series of questions to create a .inp file for OSIRIS. \n")

    # Filename
    while True:
        fileName = input(
            "\nPlease choose an output file name, i.e., 'output.inp', for example: \n")
        try:
            newFile = open(str(fileName), 'x')
            print(f"{fileName} successfully created!\n")
            break
        except FileExistsError:
            print("\nError! A file with this name already exists in this directory. Please choose another name or rename the existing file!\n")

    while True:
        try:
            dimension = int(input("\nPlease choose a dimension:\n"))
            if dimension not in [2, 3]:
                raise ValueError
            else:
                print(f"{dimension}D chosen!\n")
                break
        except BaseException:
            print(
                "\nDimension error! Illegal dimension, please choose a valid dimension\n")

    while True:
        try:
            cores_per_node = int(
                input("\nFinal preliminary question: how many cores per node are you using?\n"))
            print(f"{cores_per_node} cores per node, thank you!")
            break
        except BaseException:
            print("Not sure what you've done here :/")

    # Simulation

    newFile.write("simulation\n{\n")

    # algorithm
    while True:
        try:
            algorithm = input("\nChoose your simulation algorithm: \n")
            if algorithm not in ["standard", "quasi_3d"]:
                raise
            else:
                newFile.write(
                    "algorithm = " +
                    "'" +
                    str(algorithm) +
                    "'" +
                    ",\n")
                print(f"{algorithm} chosen!\n")
            break
        except BaseException:
            print("\nOops! Illegal algorithm, or unimplemented! Please choose another!")

    newFile.write("}\n")

    # Node_conf

    newFile.write("\nnode_conf\n{\n")

    # node_number

    while True:
        try:
            if dimension == 2:
                node_x, node_y = input(
                    "\nPlease input the number of axis-1 and axis-2 node numbers. The product of these should be the total number of nodes in use:\n").split()
                if int(node_x) < 0 or int(node_y) < 0:
                    raise
                else:
                    newFile.write(
                        "node_number(1:2) = " +
                        node_x.replace(
                            "e",
                            "d") +
                        ", " +
                        node_y.replace(
                            "e",
                            "d") +
                        ",\n")
                    break
            elif dimension == 3:
                node_x, node_y, node_z = input(
                    "\nPlease input the number of axis-1, axis-2, and axis-3 node numbers. The product of these should be the total number of nodes in use:\n").split()
                if int(node_x) < 0 or int(node_y) < 0 or int(node_z) < 0:
                    raise
                else:
                    newFile.write(
                        "node_number(1:3) = " +
                        node_x.replace(
                            "e",
                            "d") +
                        ", " +
                        node_y.replace(
                            "e",
                            "d") +
                        ", " +
                        node_z.replace(
                            "e",
                            "d") +
                        ",\n")
                    break
        except BaseException:
            print("\nInvalid node numbers! Please recalculate!")

    # if_periodic

    while True:
        try:
            if dimension == 2:
                xperiod, yperiod = input(
                    "\nPlease declare the truth of if the boundaries are periodic:\n").split()
                if xperiod not in [
                        "false",
                        "true"] or yperiod not in [
                        "false",
                        "true"]:
                    raise
                else:
                    newFile.write(
                        "if_periodic(1:2) = " +
                        "." +
                        xperiod +
                        "." +
                        ", " +
                        "." +
                        yperiod +
                        "." +
                        ",\n")
                    break
            elif dimension == 3:
                xperiod, yperiod, zperiod = input(
                    "\nPlease declare the truth of if the boundaries are periodic:\n").split()
                if xperiod not in [
                    "false",
                    "true"] or yperiod not in [
                    "false",
                    "true"] or zperiod not in [
                    "false",
                        "true"]:
                    raise
                else:
                    newFile.write(
                        "if_periodic(1:3) = " +
                        "." +
                        xperiod +
                        "." +
                        ", " +
                        "." +
                        yperiod +
                        "." +
                        ", " +
                        "." +
                        zperiod +
                        "." +
                        ",\n")
                    break
        except BaseException:
            print("\nInvalid truth statements! Please use 'false' or 'true'\n")

    newFile.write("}\n")

    # This gets a little more complex here. Because Fortran is backwards as is
    # OSIRIS, the order of the settings MUST be preserved. Therefore some of
    # the information collected here is a bit early but will be necessary.

    while True:
        try:
            print(
                "\nWe now need some key values in order to calculate OSIRIS complatible values.\n")
            plasma_density = float(
                input("\nPlease enter the plasma density:\n"))
            laser_wavelength = float(
                input("\nPlease enter the laser wavelength:\n"))
            break
        except BaseException:
            print("You've probably tried to outsmart the program. Just enter a number.")

    # This is the primary length scale of the system
    skinDepth = skin_depth(plasma_density)

    # These are rule of thumb. Worth calculating now.

    deltax = laser_wavelength / (20 * skinDepth)
    deltay = 1 / 4  # A consequence of naturalising the units.
    deltaz = 1 / 4  # A consequence of naturalising the units.

    # Calculates the window lengths and writes grid
    while True:
        try:
            if dimension == 2:
                xmin, ymin = input(
                    "\nPlease choose the minimum spatial limit of the simulation for the two axes.\n").split()
                xmax, ymax = input(
                    "\nSimilarly, please choose the maximum spatial limit of the simulation for the two axes.\n").split()
                windowlengths = [i /
                                 skinDepth for i in [abs(float(xmax) -
                                                         float(xmin)), abs(float(ymax) -
                                                                           float(ymin))]]
                break
            elif dimension == 3:
                xmin, ymin, zmin = input(
                    "\nPlease choose the minimum spatial limit of the simulation for the three axes.\n").split()
                xmax, ymax, zmax = input(
                    "\nSimilarly, please choose the maximum spatial limit of the simulation for the three axes.\n").split()
                windowlengths = [i /
                                 skinDepth for i in [abs(float(xmax) -
                                                         float(xmin)), abs(float(ymax) -
                                                                           float(ymin)), abs(float(zmax) -
                                                                                             float(zmin))]]
                break
        except BaseException:
            print("Wow, I'm surprised this is an issue.")

    nx = math.ceil(
        math.ceil(
            windowlengths[0] / deltax) / cores_per_node) * cores_per_node
    ny = math.ceil(
        math.ceil(
            windowlengths[1] / deltay) / cores_per_node) * cores_per_node
    if dimension == 3:
        nz = math.ceil(
            math.ceil(
                windowlengths[2] / deltaz) / cores_per_node) * cores_per_node

    newFile.write("\ngrid\n{\n")

    if dimension == 2:
        newFile.write(
            "nx_p(1:2) = " +
            str(nx).replace(
                "e",
                "d") +
            ", " +
            str(ny).replace(
                "e",
                "d") +
            ",\n")
    elif dimension == 3:
        newFile.write(
            "nx_p(1:3) = " +
            str(nx).replace(
                "e",
                "d") +
            ", " +
            str(ny).replace(
                "e",
                "d") +
            ", " +
            str(nz).replace(
                "e",
                "d") +
            ",\n")
    print("\nGrid dimensions written\n")

    newFile.write("}\n")

    # timestep and ndump

    newFile.write("\ntime_step\n{\n")

    if dimension == 2:
        newFile.write("dt = " +
                      str(0.99 /
                          (math.sqrt(2) *
                           (1 /
                            (deltax *
                             deltax) +
                              1 /
                              (deltay *
                               deltay)))).replace("e", "d") +
                      ",\n")
    elif dimension == 3:
        newFile.write("dt = " + str(0.99 / math.sqrt(2 * (1 / (deltax * deltax) +
                                                          1 / (deltay * deltay) + 1 / (deltaz * deltaz)))).replace("e", "d") + ",\n")

    while True:
        try:
            ndump = int(input(
                "Please choose how often you want to write out data: the so-called 'ndump' parameter.\n"))
            newFile.write("ndump = " + str(ndump).replace("e", "d") + ",\n")
            break
        except TypeError:
            print("Invalid ndump! Should be an integer!")

    newFile.write("}\n")

    # Restart

    newFile.write("\nrestart\n{\n")

    while True:
        try:
            ndump_fac = int(input("\nPlease enter the ndump_fac\n"))
            newFile.write(
                "ndump_fac = " +
                str(ndump_fac).replace(
                    "e",
                    "d") +
                ",\n")
        except BaseException:
            print("Invalid ndump_fac! Must be an integer.")

        try:
            if_restart = input(
                "\nPlease give the truth value for if_restart:\n")
            if_remold = input("\nPlease give the truth value for if_remold:\n")

            if if_restart not in [
                    "false",
                    "true"] or if_remold not in [
                    "false",
                    "true"]:
                raise
            else:
                newFile.write("if_restart = " + "." + if_restart + ".,\n")
                newFile.write("if_remold = " + "." + if_remold + ".,\n")
                break
        except BaseException:
            print("Invalid truth values")

    newFile.write("}\n")

    # Space

    newFile.write("\nspace\n{\n")

    while True:
        if dimension == 2:
            newFile.write("xmin(1:2) = " +
                          str(float(xmin) /
                              skinDepth).replace("e", "d") +
                          ", " +
                          str(float(ymin) /
                              skinDepth).replace("e", "d") +
                          ",\n")
            newFile.write("xmax(1:2) = " +
                          str(float(xmax) /
                              skinDepth).replace("e", "d") +
                          ", " +
                          str(float(ymax) /
                              skinDepth).replace("e", "d") +
                          ",\n")
            if_movex, if_movey = input(
                "\nPlease clarify in which dimension the windows will move with truth statements\n").split()
            newFile.write(
                "if_move(1:2) = " +
                "." +
                if_movex +
                "., " +
                "." +
                if_movey +
                ".,\n")
        elif dimension == 3:
            newFile.write("xmin(1:3) = " +
                          str(float(xmin) /
                              skinDepth).replace("e", "d") +
                          ", " +
                          str(float(ymin) /
                              skinDepth).replace("e", "d") +
                          ", " +
                          str(float(zmin) /
                              skinDepth).replace("e", "d") +
                          ",\n")
            newFile.write("xmax(1:3) = " +
                          str(float(xmax) /
                              skinDepth).replace("e", "d") +
                          ", " +
                          str(float(ymax) /
                              skinDepth).replace("e", "d") +
                          ", " +
                          str(float(zmax) /
                              skinDepth).replace("e", "d") +
                          ",\n")
            if_movex, if_movey, if_movez = input(
                "\nPlease clarify in which dimension the windows will move with truth statements\n").split()
            newFile.write(
                "if_move(1:3) = " +
                "." +
                if_movex +
                "., " +
                "." +
                if_movey +
                "." +
                if_movez +
                ".,\n")
        break

    newFile.write("}\n")

    # Time

    newFile.write("\ntime\n{\n")

    while True:
        try:
            tmin, tmax = input("Please enter the time limits:\n").split()
            newFile.write("tmin = " +
                          str(float(tmin)).replace("e", "d") +
                          ",\ntmax = " +
                          str(float(tmax)).replace("e", "d") +
                          ",\n")
            break
        except BaseException:
            print("Must be float or int!")

    newFile.write("}\n")

    # el_mag_fld
    newFile.write("\nel_mag_fld\n{\n")

    while True:
        try:
            smooth_type = input("Please choose the field smoothing type\n")
            if smooth_type not in ["none", "stand", "local"]:
                raise
            else:
                newFile.write(
                    "smooth_type = " +
                    "'" +
                    smooth_type +
                    "'" +
                    ",\n")
                break
        except BaseException:
            print("Invalid smoothing type!")

    newFile.write("}\n")

    # emf_bound
    newFile.write("\nemf_bound\n{\n")

    while True:
        try:
            if dimension == 2:
                boundx1, boundx2, boundy1, boundy2 = input(
                    "Please clarify the boundary conditions for em-fields:\n").split()
                newFile.write(
                    "type(1:2,1) = " +
                    "'" +
                    boundx1 +
                    "', " +
                    "'" +
                    boundx2 +
                    "',\n")
                newFile.write(
                    "type(1:2,2) = " +
                    "'" +
                    boundy1 +
                    "', " +
                    "'" +
                    boundy2 +
                    "',\n")
            elif dimension == 3:
                boundx1, boundx2, boundy1, boundy2, boundz1, boundz2 = input(
                    "Please clarify the boundary conditions for em-fields:\n").split()
                newFile.write(
                    "type(1:3,1) = " +
                    "'" +
                    boundx1 +
                    "', " +
                    "'" +
                    boundx2 +
                    "',\n")
                newFile.write(
                    "type(1:3,2) = " +
                    "'" +
                    boundy1 +
                    "', " +
                    "'" +
                    boundy2 +
                    "',\n")
                newFile.write(
                    "type(1:3,3) = " +
                    "'" +
                    boundz1 +
                    "', " +
                    "'" +
                    boundz2 +
                    "',\n")
            break
        except BaseException:
            print("Invalid boundary conditions!")

    # smooth
    newFile.write("\nsmooth\n{\n")
    while True:
        try:
            if dimension == 2:
                smoothx, smoothy = input(
                    "Please identify the type of smoothig you would like at the boundaries:\n").split()
                newFile.write(
                    "type(1:2) = " +
                    "'" +
                    smoothx +
                    "', " +
                    "'" +
                    smoothy +
                    "',\n")
            elif dimension == 3:
                smoothx, smoothy, smoothz = input(
                    "Please identify the type of smoothig you would like at the boundaries:\n").split()
                newFile.write(
                    "type(1:3) = " +
                    "'" +
                    smoothx +
                    "', " +
                    "'" +
                    smoothy +
                    "'" +
                    ", " +
                    "'" +
                    smoothz +
                    "',\n")
            break
        except BaseException:
            print("Invalid smoothing technique!")
    newFile.write("}\n")

    print(f"{fileName} created and filled! Thank you for using this tool!")

    newFile.close()
