# MACH Tutorial
This repository contains a step-by-step tutorial for some of the tools in the MACH framework.
The MACH (MDO of Aircraft Configurations with High-fidelity) framework is developed by the [MDO Lab](http://mdolab.engin.umich.edu).
It facilitates the design, analysis, and optimization of large, multi-disciplinary systems.
The tutorial covers the basics needed to optimize the aerodynamic surface and internal wingbox structure of a basic wing.
It also includes an airfoil optimization example.

## Tutorial documentation
You can either view the [online tutorial](http://mdolab.engin.umich.edu/doc/packages/machtutorial/doc/index.html) or build the tutorial documentation locally.
To generate the tutorial locally, open a terminal and enter the following commands:

    $ cd MACHtutorial/doc
    $ make html

This generates html files in _build/html/. You can then open _build/html/index.html in your preferred browser to view the tutorial documentation.

## Required Packages to build
- Sphinx (1.6.6)
