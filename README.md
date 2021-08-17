![The GALWA logo, or de-facto logo](https://github.com/Clos3y/GALWA/blob/master/logo.png)

Genetic Algorithm used to minimise the energy spread of electrons for an electron beam injected laser wakefield accelerator (LWFA).

# Usage
After adjusting the relevant options in `ga_inputs.json` (see below), and then following through in the code, run

    $ python main.py

## Adding/Removing a Parameter
Edit `ga_inputs.json`. Add your parameter name and range. The range should be a list. The system presently supports continuous parameters only.

## Headless run
Comment out all of the `data-plotter` method. You may also wish to then save computation by not saving files either, and so comment out `data-saver`.

Please submit any and all issues found.
