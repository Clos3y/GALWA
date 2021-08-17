![The GALWA logo, or de-facto logo](https://github.com/Clos3y/GALWA/blob/master/logo.png)

Genetic Algorithm used to minimise the energy spread of electrons for an electron beam injected laser wakefield accelerator (LWFA).

# Usage
After adjusting the relevant options in `ga_inputs.json` (see below), and then following through in the code, run

    $ python main.py

## Adding/Removing a Parameter
1. Edit `ga_inputs.json`. Add your parameter name and range. The range should be a list. The system presently supports continuous parameters only.
2. Edit `populate` and `mutation_stage` methods within `generationclass.py` to use your new parameters.
