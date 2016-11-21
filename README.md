# PathVision

A Python tool for visualising the Bellman-Ford algorithm in action over a variety of best-path algebras. At the moment it allows you to interactively edit graphs and then step backwards and forwards through time to track how the state changes at each iteration. It may well be buggy, feel free to open an issue if you encounter one.

![example image](/examples/screenshot.png)

## Requirements

- Matplotlib [http://matplotlib.org/]
- NetworkX [https://networkx.github.io/]

## Execution

To run, navigate to the main directory and execute the command `python3 PathVision.py`.

## Adding new algebras

In order to add a new algebra to PathVision it is necessary to make changes in two places:

#### *theory/algebra.py*

Here you need to add the core of the algebraic operations in the form of an instance of the "Algebra" class. In particular you will need to provide it:
- An addition function (takes in two routes and returns the preferred route)
- An extension operation (takes an edge value, a route and the edge's source node and returns a new route)
- An invalid route (represents no route being available)
- An identity route (represents the route between a node and itself)
- An invalid edge (an edge value representing no edge being present)

For example the shortest-path `Algebra` is formed by:

`minPlus = Algebra(min, lambda x,y,_ : x + y, float('inf'), 0, float('inf'))`


#### *theory/displayAlgebra.py*

Here you will need to provide PathVision the information necessary to integrate the new algebra into the user interface. In particular you will need to provide:
- the newly created algebra (from *theory/algebra.py*)
- the name of the algebra to displayed in the GUI
- a default value for newly created edges
- a validation function that takes in a string and determines whether it is a valid edge value
- a parsing function that takes in a string and returns the edge value
- a list of subalgebras (for most purposes simply use `[]`)
- a function that generates a random edge value

For example the shortest-path `DisplayAlgebra` is formed by:

`minPlusD = DisplayAlgebra(minPlus, "(N, min, +)", 1, isInt, int, [], intRandom)`

In order to add the new algebra to the GUI, append the newly created DisplayAlgebra to the `examples` list at the end of the file.
