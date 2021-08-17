![The GALWA logo, or de-facto logo](https://github.com/Clos3y/GALWA/blob/master/logo.png)

Genetic Algorithm used to minimise the energy spread of electrons for an 
electron beam injected LWFA.

# Usage
After adjusting the relevant options in `ga_inputs.json` (see below), and then following through in the code, run
    $ python main.py

## Adding/Removing a Parameter
1. Edit `ga_inputs.json`. Add your parameter name and range. The range should be a list. If the range is continuous, enter the lower- and upper-bounds in that order; if the range is discrete, add a third element dictating the step size. If there are fixed values you want to test, that don't follow this pattern, you must enter each value in the list. Bear in mind that if there are two- or three-elements in your custom list, the system will read it as a continuous- or discrete-range respectively.
2. Edit `populate` and `mutation_stage` methods within `generationclass.py` to use your new parameters.
