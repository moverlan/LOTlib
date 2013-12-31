LOTlib
------

LOTlib is a python library for programming "language of thought" models. With it, you specify a set of primitives and can model learners who search over compositions of the primitives to express complex concepts. The examples provided all describe a grammar and a probablistic Bayesian model over the expressions generated by that grammar, and using sampling in order to determine likely hypotheses, given some observed data. There are several sampling methods provided, including tree-regeneration metropolis-hastings (from the Rational Rules model of Goodman et al. 2010), and variants that include tempering, tempered transitions, and Gibbs sampling. In general, the original algorithm seems to be fastest and most robust. NOTE: The bound-variable part of PCFGs is not heavily tested or debugged (yet).

This library provides basic support for MPI through SimpleMPI (using mpi4py), allowing sampling algorithms to run in parallel on a single computer, or an entire cluster. 

The best way to use this library is to read and modify the examples. 


RELEASE NOTES
-------------

As of December 2013, the code has been substantially updated to allow more powerful lambda abstraction. This has broken backward compatiblitiy (but allows a more intuitive specification of grammars and lambda terms). Updating to the newest version is recommended. 

The original vesion of LOTlib was based on scheme code (available upon request -- spiantado@gmail.com) and was ported to python 2.x in September 2011. 

REQUIREMENTS
------------

- lockfile
- numpy
- scipy
- mpi4py (if using MPI)
- multiprocessing
- pyparsing (for SimpleLambdaParser)

INSTALLATION
------------

Put this library somewhere--mine lives in /home/piantado/Libraries/LOTlib/
	
Set the PYTHONPATH environment variable to point to LOTlib/:
	
	export PYTHONPATH=$PYTHONPATH:/home/piantado/Desktop/Libraries/LOTlib
	
You can put this into your .bashrc file to make it loaded automatically when you open a terminal. On ubuntu and most linux, this is:
	
	echo 'export PYTHONPATH=$PYTHONPATH:/home/piantado/Desktop/Libraries/LOTlib' >> ~/.bashrc

And you should be ready to use the library via:
	
	import LOTlib
	
in python 2.x.

EXAMPLES
--------

A good starting place is the FOL folder, which contains a simple example to generate first-order logical expressions. These have simple boolean functions as well as lambda expressions. 

The best reference for learning how to create/modify grammars is FunctionNodeDemo in Examples. It contains all of the syntax for various parts of grammars. 

More examples are provided in the "Examples" folder. These include simple symbolic regression, the recursive number learning model, a quantifier learning model. The "tests" folder may also be useful, as this runs some simple models to check for, e.g., correct sampling and inference. The Number demo has syntax for a number of different sampling and inference schemes included in LOTlib.