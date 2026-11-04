#### Advanced Optimization for Process Systems Engineering
Based on the author’s 40 years of teaching experience, this unique textbook covers both
basic and modern advanced concepts of optimization theory and methods for process
systems engineers. Topics covered include continuous, discrete, and logic optimization
```
(linear, nonlinear, mixed-integer and generalized disjunctive programming), optimization
```
```
under uncertainty (stochastic programming and flexibility analysis), and decomposition
```
```
techniques (Lagrangean and Benders decomposition). Assuming only a basic background
```
in calculus and linear algebra, it enables easy understanding of mathematical reasoning, and
numerous examples throughout illustrate key concepts and algorithms. End-of-chapter
exercises involving theoretical derivations and small numerical problems, as well as in
modeling systems like GAMS, enhance understanding and help put knowledge into practice.
Accompanied by two appendices containing web links to modeling systems and models
related to applications in PSE, this is an essential text for single-semester, graduate courses in
process systems engineering in departments of chemical engineering.
Ignacio E. Grossmann is the R. R. Dean University Professor of Chemical Engineering at
Carnegie Mellon University, and Director of the Center for Advanced Process Decision-
making. He is a member of the National Academy of Engineering.
CAMBRIDGE SERIES IN CHEMICAL ENGINEERING
Series Editor
Arvind Varma, Purdue University
Editorial Board
Juan de Pablo, University of Chicago
Michael Doherty, University of California-Santa Barbara
Ignacio Grossmann, Carnegie Mellon University
Jim Yang Lee, National University of Singapore
Antonios Mikos, Rice University
Books in the Series
Daoutidis Baldea, Dynamics and Nonlinear Control of Integrated Process Systems
Chamberlin, Radioactive Aerosols
Chau, Process Control: A First Course with Matlab
Cussler, Diffusion: Mass Transfer in Fluid Systems, Third Edition
Moggridge Cussler, Chemical Product Design, Second Edition
Schieber De Pablo, Molecular Engineering Thermodynamics
Deen, Introduction to Chemical Engineering Fluid Mechanics
Denn, Chemical Engineering: An Introduction
Denn, Polymer Melt Processing: Foundations in Fluid Mechanics and Heat Transfer
Daoutidis Dorfman, Numerical Methods with Chemical Engineering Applications
Reimer Duncan, Chemical Engineering Design and Analysis: An Introduction 2E
Fan, Chemical Looping Partial Oxidation Gasification, Reforming, and Chemical Syntheses
Zhu Fan, Principles of Gas-Solid Flows
Fox, Computational Models for Turbulent Reacting Flows
Franses, Thermodynamics with Chemical Engineering Applications
Leal, Advanced Transport Phenomena: Fluid Mechanics and Convective Transport Processes
Shin Lim, Fed-Batch Cultures: Principles and Applications of Semi-Batch Bioreactors
Litster, Design and Processing of Particulate Products
Fox Marchisio, Computational Models for Polydisperse Particulate and Multiphase Systems
Wagner Mewis, Colloidal Suspension Rheology
Morbidelli, Gavriilidis, and Varma, Catalyst Design: Optimal Distribution of Catalyst in
Pellets, Reactors, and Membranes
Nicoud, Chromatographic Processes
Terry Noble, Principles of Chemical Separations with Environmental Applications
Sandler Orbey, Modeling Vapor-Liquid Equilibria: Cubic Equations of State and their Mixing
Rules
Petyluk, Distillation Theory and its Applications to Optimal Design of Separation Units
Pfister, Nicoud, and Morbidelli, Continuous Biopharmaceutical Processes: Chromatography,
Bioconjugation, and Protein Stability
Song Ramkrishna, Cybernetic Modeling for Bioreaction Engineering
Nott Rao, An Introduction to Granular Flow
Russell, Robinson, and Wagner, Mass and Heat Transfer: Analysis of Mass Contactors and
Heat Exchangers
Schobert, Chemistry of Fossil Fuels and Biofuels
Shell, Thermodynamics and Statistical Mechanics
Sirkar, Separation of Molecules, Macromolecules and Particles: Principles, Phenomena and
Processes
Slattery, Advanced Transport Phenomena
Varma, Morbidelli, and Wu, Parametric Sensitivity in Chemical Systems
Vassiliadis et al., Optimization for Chemical and Biochemical Engineering
Weatherley, Intensification of Liquid–Liquid Processes
Wolf, Bielser, and Morbidelli, Perfusion Cell Culture Processes for Biopharmaceuticals
Zhu, Fan, and Yu, Dynamics of Multiphase Flows
Advanced Optimization for Process
Systems Engineering
Ignacio E. Grossmann
Carnegie Mellon University, Pennsylvania
University Printing House, Cambridge CB2 8BS, United Kingdom
One Liberty Plaza, 20th Floor, New York, NY 10006, USA
477 Williamstown Road, Port Melbourne, VIC 3207, Australia
314–321, 3rd Floor, Plot 3, Splendor Forum, Jasola District Centre, New Delhi – 110025, India
79 Anson Road, #06–04/06, Singapore 079906
Cambridge University Press is part of the University of Cambridge.
It furthers the University’s mission by disseminating knowledge in the pursuit of
education, learning, and research at the highest international levels of excellence.
www.cambridge.org
Information on this title: www.cambridge.org/9781108831659
```
DOI: 10.1017/9781108917834
```
© Ignacio E. Grossmann 2021
This publication is in copyright. Subject to statutory exception
and to the provisions of relevant collective licensing agreements,
no reproduction of any part may take place without the written
permission of Cambridge University Press.
First published 2021
Printed in the United Kingdom by TJ Books Limited, Padstow Cornwall, 2021
A catalogue record for this publication is available from the British Library.
ISBN 978-1-108-83165-9 Hardback
Additional resources for this publication at www.cambridge.org/grossmann-resources.
Cambridge University Press has no responsibility for the persistence or accuracy of
URLs for external or third-party internet websites referred to in this publication
and does not guarantee that any content on such websites is, or will remain,
accurate or appropriate.
To the memory of my parents
To my wife Blanca and to my children, Claudia, Andrew, and Thomas
To my grandchildren, Oscar, Elena, Joaquin, Lucas, Jamie, and Alex
Contents
Preface page xiii
1 Optimization in Process Systems Engineering 1
1.1 Introduction 1
1.2 Classification of Optimization Models 3
1.3 Outline of the Book 7
2 Solving Nonlinear Equations 9
2.1 Process Modeling Approaches 9
2.2 Newton’s Method 9
2.3 Quasi-Newton Methods 11
Exercises 14
3 Basic Theoretical Concepts in Optimization 16
3.1 Basic Formulations 16
3.2 Nonlinear Programming Example 17
3.3 Basic Concepts 19
3.4 Optimality Conditions 21
3.4.1 Unconstrained Optimization 21
```
3.4.2 Constrained Optimization (Equalities) 22
```
```
3.4.3 Constrained Optimization (Inequalities) 24
```
3.4.4 Nonlinear Programming Problem 26
3.4.5 Active-Set Strategy Procedure for Determining
```
a Karush–Kuhn–Tucker Point (Sargent, 1975) 27
```
Exercises 30
4 Nonlinear Programming Algorithms 32
4.1 Successive-Quadratic Programming 32
4.2 Reduced-Gradient Method 35
4.3 Interior-Point Method 38
4.4 Comparison of NLP Algorithms 40
4.5 Guidelines for Formulating NLP Models 40
Exercises 42
ix
5 Linear Programming 44
5.1 Basic Theory 44
5.2 Simplex Algorithm 47
5.3 Numerical Example 51
Exercises 52
6 Mixed-Integer Programming Models 53
6.1 Modeling with 0-1 Variables 53
6.1.1 Motivating Examples 53
6.1.2 Modeling with Linear 0-1 Variables yj 55
6.1.3 Some Common IP Problems 57
Exercises 61
7 Systematic Modeling of Constraints with Logic 62
7.1 Modeling 0-1 Constraints with Propositional Logic 62
7.1.1 Example 1 of Logic Proposition 63
7.1.2 Example 2 of Logic Proposition 64
7.2 Modeling of Disjunctions 64
7.2.1 Big-M Reformulation 65
7.2.2 Convex-Hull Reformulation 65
7.2.3 Example 67
7.3 Generalized Disjunctive Programming 68
Exercises 69
8 Mixed-Integer Linear Programming 72
8.1 Introduction 72
8.2 MILP Methods 73
8.3 Gomory Cutting Planes 74
8.4 Branch and Cut Method 75
Exercises 79
9 Mixed-Integer Nonlinear Programming 81
9.1 Overview of Solution Methods 81
9.2 Derivation of Outer-Approximation and Generalized Benders
Decomposition Methods 82
9.3 Extended Cutting-Plane Method 86
9.4 Properties and Extensions 87
Exercises 91
x Contents
10 Generalized Disjunctive Programming 93
10.1 Logic-Based Formulation for Discrete/Continuous Optimization 93
10.2 Relaxations and Reformulations of GDP 94
10.3 Special Purpose Methods for GDP 97
10.3.1 Disjunctive Branch and Bound 97
10.3.2 Logic-Based Outer Approximation 100
Exercises 102
11 Constraint Programming 103
11.1 Logic-Based Modeling 103
11.2 Search in Constraint Programming 105
11.2.1 Domain Reduction and Constraint Propagation 105
11.2.2 Tree Search 106
Exercises 108
12 Nonconvex Optimization 109
12.1 Major Approaches to Global Optimization 109
12.2 Convexification 110
12.3 Global Optimization of Bilinear Programs 111
12.4 Global Optimization of More General Functions 117
Exercises 117
13 Lagrangean Decomposition 119
13.1 Overview of Decomposition for Large-Scale Problems 119
13.2 Lagrangean Relaxation 120
13.3 Lagrangean Dual 121
13.4 Lagrangean Decomposition 124
13.5 Update of Lagrange Multipliers 126
Exercises 128
14 Stochastic Programming 129
14.1 Strategies for Optimization under Uncertainty 129
14.2 Linear Stochastic Programming 132
14.3 L-Shaped Method 134
14.4 Multistage Stochastic Programming 138
14.5 Robust Optimization 139
Exercises 141
Contents xi
15 Flexibility Analysis 142
15.1 Introduction 142
15.2 Two-Stage Programming with Guaranteed Feasibility 142
15.3 Flexibility Analysis 144
15.4 Flexibility Test with No Control Variables 145
15.5 Flexibility Test with Control Variables 147
15.6 Parametric Region of Feasible Operation and Vertex Search 149
15.7 Flexibility Index and Vertex Search 151
15.8 Theoretical Conditions for Vertex Solutions 153
15.9 Active-Set Strategy 156
Exercises 161
Appendix A Modeling Systems and Optimization Software 163
Appendix B Optimization Models for Process Systems Engineering 171
References 180
Index 187
xii Contents
Preface
Process systems engineering has emerged as a major discipline in chemical engineering, and
is concerned with the systematic analysis and optimization of decision-making processes for
the discovery, design, manufacture, and distribution of chemical products. Optimization or,
more precisely, mathematical programming, has played a major role in the modeling of
decision making in problems related to conceptual design/process synthesis, process control,
```
and process operations. In fact, process systems engineering (PSE) has a rich history in the
```
area of optimization. For instance, some of the first applications of linear programming took
place at Gulf Oil in 1952, while the first branch and bound code for solving mixed-integer
linear programming was developed at British Petroleum in 1961. The areas of nonlinear and
mixed-integer nonlinear programming have been, and continue to be, very active in PSE, as
well as logic-based optimization, global optimization, optimization under uncertainty and
decomposition methods. In fact, PSE researchers have been making contributions in terms
of theory, algorithms, and software, which have had a major impact beyond PSE as they
represent fundamental contributions in the area of mathematical programming with appli-
cations in areas different than process systems.
The main goal of this book is to provide a unique overview of basic concepts of optimiza-
tion theory and methods that are relevant to chemical engineers, particularly process systems
engineers. The book is unique in that it covers continuous, discrete, and logic optimization,
as well as optimization under uncertainty and decomposition techniques. The book is also
unique in that it emphasizes several topics related to modeling. The book is the result of
having taught over 25 years the course “Advanced Process Systems Engineering” at
Carnegie Mellon in which the first part of the course is taught with the first 12 chapters of
the book, while the last 3 chapters are taught at the end of the course. The rest of the course
is devoted to applications of optimization in process synthesis, and in planning and schedul-
ing of batch and continuous processes.
The book consists of 15 chapters. After the introductory Chapter 1, the book addresses
the solution of nonlinear equations through Newton’s and quasi-Newton methods in
Chapter 2. Chapter 3 introduces basic theoretical optimization concepts, while Chapters 4
```
and 5 deal with continuous optimization (nonlinear and linear programming). Chapters
```
```
6–11 deal with discrete optimization (mixed-integer linear and mixed-integer nonlinear
```
```
programming, generalized disjunctive programming, and constraint programming).
```
Chapter 12 deals with global optimization, Chapter 13 with Lagrangean decomposition,
Chapter 14 with stochastic programming, and Chapter 15 with flexibility analysis. Only
knowledge of basic concepts of calculus and linear algebra is assumed. Fourteen of the
chapters contain exercises that involve derivations and simple proofs, as well as numerical
xiii
problems that require the use of the GAMS modeling system. Appendix A describes
software for modeling systems optimization algorithms, while Appendix B supplies links
to websites that address a variety of problems in PSE.
The author would like to acknowledge the many individuals who made this book possible.
I would like to thank the late Professor Sargent who provided me with the basic foundations
of optimization, especially through his brilliant course at Imperial College back in 1975.
I would like to thank the late Professor Egon Balas whose pioneering work in disjunctive
programming has been an inspiration to my students and me for the development of
generalized disjunctive programming. I am also most grateful to Professor John Hooker
for having introduced me to the area of logic-based optimization. Many thanks to Professor
Arthur Westerberg who made possible my hiring at Carnegie Mellon and taught me about
the importance of multidisciplinary research. I am also grateful to Professor John Anderson
who made possible the teaching of the material in this book through the establishment of the
graduate course “Advanced Process Systems Engineering.” I am also most grateful to my
colleagues from the Center of Advanced Process Decision-making, Larry Biegler,
Chrysanthos Gounaris, Nick Sahindis, Jeff Siirola, and Erik Ydstie, for their help and
support. Many thanks to my bright and dedicated former Ph.D. students and research
collaborators who have helped to advance the field of optimization. Special thanks to
Marco Duran, Gary Kocis, J. Viswanathan, Ramesh Raman, Metin Turkay, Aldo
Vecchietti, Sangbum Lee, Nicolas Sawaya, Juan Pablo Ruiz, Francisco Tresplacios,
Ignacio Quesada, Juan Zamora, Keshava Halemane, Ross Swaney, Chris Floudas,
Stratos Pistikopoulos, and Qi Zhang whose work has been the basis of the various chapters
in this book. Thanks also to GAMS Corporation, especially to Alexander Meeraus, for his
help in launching our MINLP code DICOPT. I am also indebted to my Ph.D. students
David Bernal, Can Li, Qi Chen, Markus Drouven, and Hector Perez, and to Professor
Diego Cafaro who helped me to proofread the manuscript and in creating many of the
figures. I would also like to acknowledge the Fulbright Award that allowed me a three-
month visit to the Universidad Nacional del Litoral/INTEC in Santa Fe, Argentina, that
was hosted by Professor Carlos Mendez, and that allowed me to write a large part of the
book. I am most indebted to Laura Shaheen and Barbara Carlson for their help and patience
in typing and correcting several versions of the manuscript. I am also indebted to Julia Ford,
Rachel Norridge and Steve Elliot of Cambridge University Press for their encouragement in
writing the book, and their help and advice in the preparation of the manuscript. I also very
much hope that this book will be of interest and useful to the Process Systems Engineering
community at large, and with whom I have had the privilege of interacting and collaborating
during my academic career.
This book is dedicated to my wife Blanca Grossmann, to whom I am most grateful for her
love, support, and patience in the writing of this book. The book is also dedicated to the
memory of my parents, to my children Claudia, Andrew, and Thomas, and to my grand-
children, Oscar, Elena, Joaquin, Lucas, Jamie, and Alex.
xiv Preface
1 Optimization in Process Systems Engineering
1.1 Introduction
This book deals with mathematical programming techniques for process systems engineer-
```
ing (PSE) (Sargent, 2004). The main focus is on the theory, model formulation, and
```
algorithms of mathematical optimization techniques. In this chapter, we provide a general
```
overview of how optimization problems arise in process systems engineering (Biegler et al.,
```
```
1997). A number of interesting and practical applications are increasingly being tackled in
```
the chemical industry through modern optimization models and methods. The major areas
that have been considered include the following:
– process design and synthesis
– planning and scheduling
– process control and operation.
Table 1.1 gives specific areas of application of optimization in process systems engineering
```
(Biegler and Grossmann, 2004; Grossmann and Biegler, 2004). Major optimization tech-
```
```
niques include linear programming (LP), nonlinear programming (NLP), mixed-integer
```
```
linear programming (MILP), mixed-integer nonlinear programming (MINLP), and quad-
```
```
ratic programming (QP) (Minoux, 1986).
```
Figure 1.1 provides the major steps that are involved in the formulation of optimization
problems listed in Table 1.1. Given is either a process flowsheet for producing a particular
chemical, or a production plan for manufacturing several different products. If we fix the
configuration and equipment sizes of a process flowsheet, or the timing of the operations for
the production plan, we resort to an analysis of the flowsheet or production plan in order to
```
evaluate the economics (e.g., operating cost), or its performance (e.g., completion time), or
```
```
its operability (e.g., flexibility or controllability). In order to improve the economics,
```
performance, or operability, we can select new values of parameters that represent degrees
```
of freedom (e.g., pressures, temperatures, reactor volumes, recycle ratios, production rates,
```
```
etc.). If our aim is to optimize the value of these parameters, mathematically this corres-
```
ponds to an optimization with continuous variables. We can go a step further and modify
the structure of the flowsheet or of the production plan, which can be interpreted as a
synthesis step since it gives rise to a new flowsheet structure or to a new production plan in
terms of production sequence. If our aim is to optimize these decisions, mathematically this
corresponds to an optimization problem with discrete variables.
1
In summary, from Fig. 1.1 we can conclude that the major steps involved in the design/
operation of a process flowsheet or production plan are:
```
(a) analysis
```
```
(b) evaluation
```
```
(c) synthesis.
```
The important point to realize is that the improved design/operation of a flowsheet or
production plan can be achieved through the optimization of continuous and discrete
Table 1.1 Applications of mathematical programming in process systems engineering
MILP MINLP LP QP NLP
Design and synthesis
HENS x x x x
MENS x x x x
Separations x x
Reactors x x x
Equipment design x x
Flowsheeting x x
Operations
Scheduling x x x
Supply chain x x x
Real-time optimization x x x
Linear MPC x x
Nonlinear MPC x
Hybrid x x
Flowsheet
production plan Synthesis
Sizes/timing
Structure
Optimizediscrete
variables
Optimizecontinuous
variablesAnalysis
Evaluation
economics/performance
/operability
Parameters
Systems design/operation
Figure 1.1 Major steps in the
formulation of optimization
problems in PSE.
2 1 Optimization in Process Systems Engineering
variables, which is the main topic of this textbook. Therefore, the outline of this textbook is
as follows.
Chapter 2 Solving Nonlinear Equations
Chapter 3 Basic Theoretical Concepts in Optimization
Chapter 4 Nonlinear Programming Algorithms
Chapter 5 Linear Programming
Chapter 6 Mixed-Integer Programming Models
Chapter 7 Systematic Modeling of Constraints with Logic
Chapter 8 Mixed-Integer Linear Programming
Chapter 9 Mixed-Integer Nonlinear Programming
Chapter 10 Generalized Disjunctive Programming
Chapter 11 Constraint Programming
Chapter 12 Nonconvex Optimization
Chapter 13 Lagrangean Decomposition
Chapter 14 Stochastic Programming
Chapter 15 Flexibility Analysis
Appendix A Modeling Systems and Optimization Software
Appendix B Optimization Models for Process Systems Engineering
1.2 Classification of Optimization Models
Optimization problems can generally be formulated with mathematical models that involve
```
continuous and discrete variables (Grossmann, 2002). These variables must be selected to
```
satisfy equations and inequality constraints, while optimizing a given objective function as
expressed with the model below:
```
min f x; yð Þ
```
```
s:t: h x; yð Þ ¼ 0
```
```
g x; yð Þ  0
```
x 2 X , y 2 Y :
```
(1.1)
```
The continuous variables are represented by x and the discrete variables by y, both with
arbitrary dimensionality. The feasible region for the variables x and y is defined by the
```
following constraints: h x; yð Þ ¼ 0, which are equations describing the performance of a
```
```
system (e.g., mass, energy balances, design equations); and g x; yð Þ  0, which are inequal-
```
```
ities that are related to specifications (e.g., minimum purity, maximum throughput). In
```
```
addition, the variables can be further confined to sets X (typically lower and upper bounds)
```
```
and Y (specific integers). The former typically specifies the ranges of values for the continu-
```
```
ous variables (e.g., positive flows, minimum/maximum pressures for a chemical reactor),
```
```
while the latter specifies the discrete choices (e.g., only 0-1 choices for the selection or not of
```
1.2 Classification of Optimization Models 3
```
a processing unit, or an integer number for number of plates in a distillation column). It
```
```
should be noted that the model in (1.1) can in practice also be posed as a maximization
```
```
problem, or with inequalities that must be greater than or equal to zero. The form in (1.1),
```
however, is used for presentation purposes. Also, any problem can be converted into that
form because maximizing a function is equivalent to minimizing its negative value.
Inequalities that are greater than or equal to zero can also easily be converted to less than
or equal to zero.
```
The mathematical model in (1.1) is technically known as a “mathematical program” and
```
```
an extensive body of literature exists on this subject (see Williams, 1985, for an introduction
```
```
to models; and Minoux, 1986, for a general review of methods). From a practical stand-
```
```
point, the important feature of model (1.1) is that it provides a powerful framework for
```
modeling many optimization problems, including design, scheduling, and control problems.
More recently, machine learning models are also being solved through formal optimization
```
methods (Bottou et al., 2018). Depending on the application at hand and the level of detail in
```
the equations, the objective function and constraints can be given in explicit or implicit form.
Explicit equations are given by mathematical expressions that are often used for simplified
models. In this case, the time to perform an evaluation of the model may be very fast even
though it may involve thousands of variables and constraints. Implicit equations arise when
detailed and complex calculations must be performed as procedures, as with, for instance,
process simulators or differential equation models. In these cases, the dimensionality of the
optimization model can be greatly reduced, although the time for performing an evaluation
of one trial point may require a significant length of time.
```
Formulating a given decision problem as a mathematical program in (1.1) requires three
```
```
major assumptions: (a) the criterion for optimal selection can be expressed through a single
```
```
objective function, (b) the constraints must be exactly satisfied, and (c) the parameters (input
```
```
data) are deterministic in nature. These, of course, represent oversimplifications of real-
```
```
world problems. However, it should be noted that extensions of the model in (1.1) are
```
available for addressing some of these issues. For instance, it is possible to relax the
```
assumptions in (a) and (b) through multiobjective optimization methods (Audet et al.,
```
```
2008), while the assumption in (c) can be addressed through stochastic optimization methods
```
```
(Sahinidis, 2004) or multiparametric optimization methods (Pistikopoulos et al., 2007).
```
```
If one assumes no special structure to the problem in (1.1) and to its various particular
```
```
cases (e.g., only discrete or only continuous variables), then direct search techniques are
```
```
often the easiest methods to apply but also the most time consuming (Rios and Sahinidis,
```
```
2013). Here, either a systematic or random selection of trial points is chosen to evaluate and
```
improve the objective function. Satisfaction of constraints can also be accomplished, but
```
frequently with some difficulty (e.g., using penalty functions in which a weighted violation of
```
```
constraints is added to the original objective function). Perhaps the most popular direct
```
search method that has emerged recently in process systems engineering is simulated
annealing. This method is based on analogies with free-energy minimization in statistical
mechanics. This method is, in principle, easy to apply to problems with simple constraints,
and is likely to find solutions that are close to the global optimum. However, aside from the
4 1 Optimization in Process Systems Engineering
fact that it often requires many thousands of function evaluations before the likely optimum
is found, its performance tends to be highly dependent on the selection of the parameters of
the algorithm.
On the other hand, the most prevalent approach that has been taken in optimization is to
```
consider particular problem classes of (1.1) depending on the form of the objective function
```
and constraints with which efficient solution methods can be derived to exploit
special structures.
```
The particular case of (1.1) that is best-known is the linear programming (LP) problem, in
```
which the objective function and all the constraints are linear, and all the variables are
```
continuous (Saigal, 1995; Vanderbei, 2020). As will be discussed in Chapter 5, LP problems
```
have the property that the optimum solution lies at a vertex of the feasible space. Also, any
local optimal solution corresponds to the global optimum. These problems have been
successfully solved for many years with computer codes that are based on the Simplex
algorithm, which is rooted in linear algebra methods. Major changes that have taken place
over the past ten years at the level of solution methods are the development of interior-point
algorithms that rely on nonlinear transformations and whose computational requirements
are theoretically bounded by a polynomial expressed in terms of the problem size
```
(Karmarkar, 1984; Marsten et al., 1990). Interestingly, this property is not shared by the
```
Simplex algorithm, which theoretically may require exponential time. Since this perform-
ance is rarely observed in practice, further significant advances have taken place for solving
large-scale problems with the Simplex algorithm. With this algorithm, problems with up to
50 000–100 000 constraints can be solved quite efficiently, while interior-point methods tend
to perform better in problems with up to 500 000–1000 000 constraints. It should also be
```
pointed out that the mathematical structure of very specialized cases of LP problems (e.g.,
```
```
network flows in assignment or transportation problems) has been greatly exploited, which
```
has made possible the development of codes that can be applied to problems involving
```
millions of variables (Bertsekas, 1998).
```
The extension of the LP model that involves discrete variables is known as a mixed-integer
```
linear program (MILP) (Nemhauser and Wolsey, 1988; Wolsey, 1998). As discussed in
```
Chapter 6, this model greatly expands the capabilities of formulating real-world problems
since one can include logical decisions with 0-1 variables, or account for discrete amounts.
As discussed in Chapter 8, the most common method for MILP is the branch and bound
search, which consists of solving a subset of LP subproblems while searching within a
decision tree of the discrete variables. The other common approach relies on the use of
cutting planes that attempt to make the MILP solvable as an LP with the addition of special
constraints. Owing to the combinatorial nature that is introduced by the discrete variables in
MILP problems, they have proven to be very hard to solve. In fact, theoretically, one can
```
show that this class of problems are NP-hard; that is, there is no known algorithm whose
```
computational requirements do not exceed a polynomial increase in terms of problem size.
Nevertheless, recent advances that are based on combining branch and bound methods with
cutting planes, and which have been coupled with advances in LP technology, are providing
rigorous optimal solutions to problems that were regarded as unsolvable ten years ago.
1.2 Classification of Optimization Models 5
For the case when all or at least some of the functions are nonlinear, and only continuous
```
variables are involved, problem (1.1) gives rise to nonlinear programming problems (NLP)
```
```
(Bazaraa et al., 2006; Biegler, 2010). For the case when the objective and constraint
```
functions are differentiable, local optima can be defined by optimality conditions known
```
as the Karush–Kuhn–Tucker (KKT) conditions, as discussed in Chapter 3. These are
```
perhaps the most common type of models that arise in process systems engineering. While
ten years ago, problems involving 1000 variables for NLP were regarded as being large,
nowadays the solution of problems with up to one million variables is quite common.
Reduced-gradient, successive-quadratic programming and interior-point methods, which
can be derived by applying Newton’s method to the Karush–Kuhn–Tucker conditions, have
emerged as the major algorithms for NLP, as will be discussed in Chapter 4. The reduced-
gradient method is, in general, better suited for problems with mostly linear constraints,
successive-quadratic programming tends to be the method of choice for highly nonlinear
problems, while the interior-point method is best suited for very large-scale NLP problems.
A limitation of these methods is that they are only guaranteed to converge to a local
optimum. For problems that involve a convex objective function and a convex feasible
region, this is not a difficulty since these exhibit only one local optimum, which therefore
corresponds to the global optimum. In practice, proving convexity in a nonlinear problem is
often not possible, and therefore finding any local optimum is often regarded as a satisfac-
tory solution, especially if this yields a significant improvement. On the other hand, there are
applications in which finding the global optimum to nonconvex problems is a major issue.
Over the past few years, significant progress has been made in developing rigorous methods
```
for globally optimizing problems with special structures (e.g., bilinear functions), as will be
```
```
discussed in Chapter 12 (Horst and Tuy, 1996; Tawarmalani and Sahinidis, 2004).
```
The extension of nonlinear programming for handling discrete variables yields a mixed-
```
integer nonlinear programming (MINLP) problem that in its general form is identical to
```
```
problem (1.1) (Grossmann, 2002; Trespalacios and Grossmann, 2014). MINLP problems
```
were regarded as essentially unsolvable twenty years ago. Algorithms such as the outer-
approximation method and extensions of the generalized Benders decomposition method,
which are discussed in Chapter 9, have emerged as major methods. These methods assume
differentiability in the functions, and consist of solving an alternating sequence of NLP
subproblems and MILP master problems. The former optimizes the continuous variables,
while the latter optimizes the discrete variables. As in the NLP case, global-optimum
solutions can be guaranteed only for convex problems. Solution of problems with typically
up to 1000 binary variables and 100 000 continuous variables and constraints has been
reported with these methods. Major difficulties encountered in MINLP include those
```
encountered in MILP (combinatorial nature requiring large computations) and in NLP
```
```
(nonconvexities yielding local solutions).
```
```
It should also be noted that all the above methods assume that the problem in (1.1) is
```
expressed through algebraic equations. Very often, however, these models may involve
differential equations as constraints. This gives rise to problems known as optimal control
problems or the optimization of differential algebraic systems of equations. The major
6 1 Optimization in Process Systems Engineering
approach that has emerged here is to approximate the differential equations by algebraic
```
equations that yield nonlinear programming problems (Biegler, 2010). The alternate
```
approach is to solve the differential model in a routine that is then treated by the optimizer
```
as a procedure (or implicit function) (Vassiliadis et al., 1994).
```
Finally, many optimization problems require anticipating the effect of uncertain
```
parameters (Sahinidis, 2004). The most general form of this problem is known as stochastic
```
```
programming (Birge and Louveaux, 2011), discussed in Chapter 14, in which the basic idea
```
is to optimize over a set of scenarios that arise from discretizing probability distribution
functions. Since these problems can give rise to very large-scale problems they are usually
solved with decomposition methods. In particular, Benders decomposition is usually used
```
for two-stage stochastic programming models (stage 1: here and now decisions; stage 2: wait
```
```
and see decisions), while Lagrangean decomposition, which is covered in Chapter 13, is used
```
for multistage stochastic programs by dualizing the so-called “nonanticipativity”
constraints. Robust optimization is the other major approach for optimization under
```
uncertainty (Bertsimas et al., 2011), but it is covered only briefly in Chapter 14 as a semi-
```
infinite programming problem. Finally, Chapter 15 examines flexibility analysis, which deals
with the problem of determining feasibility in the space of uncertain parameters, while
accounting for the fact that corrective action can be taken to regain feasibility.
1.3 Outline of the Book
Having given a general overview of optimization in this chapter, we now provide a general
outline of the book to explain the rationale of the order of the chapters, which in part is
somewhat nonconventional.
First, we cover Newton’s method for nonlinear equation solving in Chapter 2, as it is the
basis of deriving the different nonlinear programming algorithms. We also discuss in that
chapter quasi-Newton methods that approximate the Jacobian matrix. In Chapter 3 we
provide basic concepts on convexity and necessary and sufficient conditions for optimality
for unconstrained, equality constrained, and both equality and inequality constrained
```
problems, which give rise to the Karush–Kuhn–Tucker (KKT) conditions. In Chapter 4,
```
we discuss nonlinear programming algorithms to emphasize the fact that NLP algorithms
represent the application of Newton’s method to the Karush–Kuhn–Tucker conditions. In
Chapter 5, we provide some theoretical properties of LP models, and use them as a basis for
deriving the Simplex algorithms for which we view it as a special case of nonlinear program-
ming by making connections with the Karush–Kuhn–Tucker conditions and the reduced-
gradient method covered in Chapter 4.
Second, we introduce, in Chapter 6, modeling of mixed-integer linear programming
problems, stressing the importance of linear 0-1 inequalities. We also introduce several
classical combinatorial problems: assignment, facility location, knapsack, set covering,
and traveling salesman. Next, in Chapter 7, we introduce the use of propositional logic as
a higher-level modeling framework from which linear 0-1 inequalities can be systematically
1.3 Outline of the Book 7
derived. We also introduce disjunctions on continuous constraints, and its two major
reformulations as mixed-integer linear constraints big-M and hull reformulations.
Third, we cover in Chapter 8, the major methods for solving mixed-integer linear pro-
```
grams: branch and bound, and cutting planes. In Chapter 9 we describe methods for solving
```
mixed-integer nonlinear programming models, namely branch and bound, outer-
```
approximation (OA) and generalized Benders decomposition (GDB). Although GBD was
```
developed before outer approximation, we show it is easier to derive GDB from OA, and
hence the proposed order.
Fourth, we introduce, in Chapter 10, the concept of generalized disjunctive programming,
as a high-level representation of optimization problems in terms of continuous and Boolean
variables with algebraic, logic, and disjunctive constraints. Aside from showing that the
GDP can be used as a modeling framework to derive algebraic mixed-integer linear and
nonlinear problems, we also briefly describe disjunctive branch and bound and logic-based
outer-approximation algorithms.
Finally, the last five chapters deal with more specialized topics. Chapter 11 describes
constraint programming, an alternative logic-based optimization modeling and solution
approach based on concepts of logic inference. Chapter 12 discusses global optimization
of nonconvex NLP and MINLP models, stressing the use of convex envelopes within spatial
branch and bound methods. Chapter 13 describes Lagrangean relaxation and Lagrangean
decomposition methods, Chapter 14 describes methods aimed at solving mixed-integer
linear stochastic programming models, and Chapter 15 describes formulations and solution
methods for flexibility analysis which are relevant for establishing feasibility of constraints
under uncertainty with recourse actions.
Appendix A provides information and links to modeling systems such as GAMS,
AIMMS, AMPL, Pyomo, and Julia, and to optimization software for LP, NLP, MILP,
MINLP, and GDP problems. Appendix B provides links to libraries of problems that
contain many application problems in process systems engineering.
8 1 Optimization in Process Systems Engineering
2 Solving Nonlinear Equations
2.1 Process Modeling Approaches
In order to perform the analysis of a process system there are two major approaches: equation
```
oriented and sequential modular (Westerberg et al., 1979). Examples of computer software
```
implementing these approaches are gPROMS for the former, and Aspen Plus for the latter.
The basic idea in the equation-oriented approach is to define explicitly all the variables
x and assemble all the corresponding equations describing a process or system.
Mathematically, this is represented by the system of equations
```
f xð Þ ¼ 0, (2.1)
```
where f is the vector of equations and x is the vector of variables. Assuming that the
equations are independent, the dimensionality of both is the same, i.e. dim fð Þ ¼ dim xð Þ,
meaning there are no degrees of freedom. In contrast, in the sequential-modular approach
the equations are implemented in a set of modules like the ones presented in Fig. 2.1.
Given an input to module 1 and a guess of the recycle variables x, modules 1, 2, and 3 are
executed in sequence so that, given their inputs, the outputs are computed. The execution of
module 3 yields the calculated value in the recycle stream, which is denoted by the implicit function
g xð Þ. In order to converge to the solution, it is required that the following equation holds true:
```
x ¼ g xð Þ: (2.2)
```
```
This equation is also known as the fixed-point problem. The existence of the solution to (2.2)
```
```
is established through the contraction mapping theorem (Ortega and Rheinboldt, 1970). It
```
```
should be noted that (2.2) can be rearranged in the form of (2.1) by defining f xð Þ as follows:
```
```
f xð Þ ¼ x  g xð Þ: (2.3)
```
```
Thus, we will consider the solution of problem (2.1) as it represents both modeling
```
```
approaches. We should note that usually the existence of the solution of (2.1) is established
```
on physical grounds.
2.2 Newton’s Method
```
A general solution method for solving the system of equations in (2.1) is Newton’s method
```
```
(Ortega and Rheinboldt, 1970; Sargent, 1975). Below we present a brief derivation of
```
this method.
9
Consider the linear expansion of f xð Þ at x k
f x k þ p k
 
¼ f x k
 
```
þ J k p k, (2.4)
```
where the computed step p k is given by
```
pk ¼ xkþ1  x k (2.5)
```
and the Jacobian matrix J k ¼ J k x k
 
, by the matrix of partial derivatives, is
J k ¼ ∂f∂x
 
xk
¼
∂f 1
∂x1
∂f 1
∂x2  
∂f 1
∂x n
∂f 2
∂x1
∂f 2
∂x2  
∂f n
∂x1  
∂f n
∂x n
2
66
66
66
64
3
77
77
77
75
```
: (2.6)
```
Notice that each row of J k represents the gradient of the function f i xð Þ, i.e. the ith element
of the vector f xð Þ. Assuming the solution at f x k þ pk
 
```
¼ 0, this gives rise from (2.4) the
```
following system of linear equations,
J k pk ¼ f x k
 
```
, (2.7)
```
which in turn yields the predicted step
pk ¼  J k
 1
f xk
 
```
, (2.8)
```
and hence the new predicted points x kþ1 are given by
x kþ1 ¼ x k  J k
 1
f x k
 
```
k ¼ 0, 1, 2, . . . , (2.9)
```
where x0 is the initial guess. Note that, because the inverse of the Jacobian J k
 1
destroys
```
the sparsity of the Jacobian, it is preferable to solve the linear equations in (2.7) in the
```
computation of the step pk . Hence, the main steps of Newton’s algorithm are as follows.
Newton’s Algorithm
```
(1) Guess x0, set k ¼ 0, and select tolerances ε1 , ε2 .
```
```
(2) Calculate f xk
```
 
, J k ¼ J k x k
 
.
```
(3) Solve linear equations J k p k ¼ f x k
```
 
```
(sparse matrix).
```
1 2 3
```
x = g(x)Figure 2.1 Example of execution of
```
blocks in the sequential-modular
approach.
10 2 Solving Nonlinear Equations
```
(4) Set xkþ1 ¼ x k þ p k.
```
```
(5) Check convergence with both the error function φ and the error in the difference of the
```
predicted and current point, that is,
φ ¼ 12 f T x k
 
f xk
 
 ε1 , x kþ1  xk  ε2:
```
If any of the above inequalities is not satisfied, set k ¼ k þ 1, and return to step (2).
```
```
We should note that in step (2) the derivatives in the Jacobian matrix can be computed
```
```
analytically or by exact differentiation (Griewank, 2000; Griewank and Walther, 2008).
```
```
Some of the major properties of Newton’s method include the following (Sargent,
```
```
1975).
```
```
(1) Second-order convergence.
```
```
(2) Sufficient-conditions convergence:
```
```
(a) f xð Þ must be differentiable,
```
```
(b) det J k
```
 
6

¼ 0 8x, i.e. Jacobian must be nonsingular,
```
(c) initial guess x0 must be close to the solution (Kantorovich, 1948).
```
```
(3) Descent property
```
φ x k þ αp k
 
 φ x k
 
< 0 for α ! 0þ:
The descent property suggests that pk be used as a search direction so as to ensure the
decrease in the error function φ. The common procedure is as follows
```
(a) Set α ¼ 1.
```
```
(b) Calculate x kþ1 ¼ x k þ αp k.
```
```
(c) If φ x kþ1
```
 
< φ x k
 
```
go to step (5) of Newton’s method. Otherwise, set αnew ¼ θαold ,
```
```
where θ is a fractional value (e.g., θ ¼ 0:3), and return to (b).
```
As an example, let us assume the full predicted step with α ¼ 1 leads to an increase of φ
from 50 to 80. In that case the full step is not accepted and reduced to α ¼ 0:3. Assume this
leads to a decrease of φ from 50 down to 45, in which case the step that is taken is with
α ¼ 0:3.
2.3 Quasi-Newton Methods
```
The basic idea of quasi-Newton methods (Sargent, 1975; Nocedal, 1980) is to avoid the
```
explicit calculation of the Jacobian by approximating the Jacobian or its inverse, J k or
J k
 1
, with function values. An excellent review on quasi-Newton methods can be found in
```
(Nocedal, 1980). In this section we will focus on Broyden’s method (Broyden, 1965) as an
```
example of a quasi-Newton method.
2.3 Quasi-Newton Methods 11
The basic idea in Broyden’s method is to generate an explicit update for the Jacobian and
successively apply Newton’s method. To generate the update, assume that the new Jacobian
J kþ1 can be expressed in terms of the current Jacobian J k as follows:
J kþ1 ¼ J k þ yk z k
 T
```
, (2.10)
```
where yk , z k are vectors of dimensionality n. Note that yk zk
 T
```
yields a rank-1 matrix;
```
```
therefore, Broyden’s update formula in (2.10) is known as a rank-1 update formula. The
```
vectors yk, z k involve 2n unknown elements that can be determined as follows.
First, we consider a given Jacobian J k for which the step pkþ1 ¼ x kþ1  xk predicts the
```
function change
```
qkþ1 ¼ f xkþ1
 
 f x k
 
```
: (2.11)
```
Assuming a first-order expansion as in Newton’s method, f x kþ1
 
¼ f xk
 
þ J k pkþ1 , neg-
lecting the second-order terms, we can rearrange Newton’s equation as follows:
```
qkþ1 ¼ J k p kþ1: (2.12)
```
In order to obtain the new Jacobian, J kþ1 , we assume the two following conditions to
determine the vectors yk , z k.
```
(a) For the step pkþ1 , J kþ1pkþ1 predicts the same difference of functions qkþ1 as in (2.12), that is:
```
```
qkþ1 ¼ J kþ1pkþ1 , (2.13)
```
which defines n conditions.
```
(b) For an orthogonal direction r, i.e., pkþ1
```
 T
r ¼ 0, the Jacobians J k and J kþ1 predict the
same change in the function value, that is,
```
J kþ1r ¼ J k r, (2.14)
```
```
which defines n additional conditions. Using this along with (2.13) and (2.14) we can
```
calculate yk , z k.
```
We first postmultiply (2.10) by the orthogonal vector r,
```
J kþ1r ¼ J k r þ yk z k
 T
```
r: (2.15)
```
```
From (2.14), it follows that y k z k
```
 T
r ¼ 0. This can be accomplished if we select z k ¼ pkþ1 .
```
Next, we postmultiply (2.10) by pkþ1 ,
```
J kþ1pkþ1 ¼ J k p kþ1 þ yk pkþ1
 T
```
pkþ1: (2.16)
```
```
From (2.13), we can express (2.16) as
```
qkþ1 ¼ J k p kþ1 þ yk pkþ1
 T
```
pkþ1 , (2.17)
```
12 2 Solving Nonlinear Equations
from which we can solve for yk,
y k ¼ q
kþ1  J k pkþ1
pkþ1ð ÞT pkþ1
```
: (2.18)
```
Therefore, Broyden’s update for the Jacobian J k is given by
J kþ1 ¼ J k þ q
kþ1  J k pkþ1  pkþ1 T
pkþ1ð ÞT pkþ1
```
: (2.19)
```
To update the inverse of the Jacobian, J k
 1
, we make use of the Sherman–Morrison
```
formula (Sherman, 1949),
```
A þ xy T
 1
¼ A1  A
1xy T A1
1 þ yT A1x
```
, (2.20)
```
which leads to Broyden’s update of the inverse of the Jacobian J k
 1
J kþ1
 1
¼ J k
 1
þ
pkþ1  J k
 1
q kþ1
 
p kþ1
 T
J k
 1
pkþ1ð ÞT J k
 1
q kþ1
```
: (2.21)
```
```
The steps in Broyden’s algorithm using the update in (2.21) for the inverse of the Jacobian,
```
are as follows
```
(1) (a) Set k ¼ 0, guess x0 , ε1 , ε2 .
```
```
(b) Calculate q x0
```
 
, estimate J0 by finite differences.
```
Calculate: J0
```
 1
.
```
(2) Calculate p kþ1 ¼  J k
```
 1
f x k
 
.
Set xkþ1 ¼ x k þ p kþ1 .
```
(3) Calculate f x k
```
 
, qkþ1 ¼ f x kþ1
 
 f x k
 
.
```
(4) Check convergence as in Newton’s method with both the error function φ and the error
```
in the difference of the predicted and current point. If convergence is not achieved,
update J kþ1
 1
```
, set k ¼ k þ 1, and return to step (2).
```
```
We should note that, in (2.21), we need to store the matrix J k
```
 1
which destroys the sparsity
that might be present in the original Jacobian. Also, as in Newton’s method, we can
```
introduce and adjust the step size α in step (2). Finally, the initial Jacobian is usually
```
obtained by perturbation, in which the partial derivatives are estimated from the
approximation
∂f i
∂x jffi
f i x k þ he j
 
 f i xh
 
```
h , (2.22)
```
2.3 Quasi-Newton Methods 13
where h is the size of the perturbation and e j is the unit vector along the jth coordinate:
e j ¼
0
0
1
0
0
BB
@
1
CC
```
A: (2.23)
```
```
Note that (2.21) requires n þ 1 function evaluations. Also, we present in Fig. 2.2 a two-
```
dimensional example of a perturbation in the x1 and x2 direction for a given initial point x0 .
Notice that three function evaluations are required in this case.
EXERCISES
2.1 Specify three cases for which Newton’s method may fail to converge when solving the
square system of nonlinear equations f xð Þ ¼ 0.
2.2 Show that for a sufficiently small positive step size α, the step predicted by Newton’s
method exhibits the descent property as given by φ x k þ αpk
 
 φ xk
 
< 0,
where φ xð Þ ¼ 12 f T xð Þf xð Þ, and x k is any point for which f x k
 
6

¼ 0 and the Jacobian
J k exists.
2.3 The update formula for the Jacobian in Broyden’s method is given by:
J kþ1 ¼ J k þ q
kþ1  J k pkþ1  p kþ1 T
pkþ1ð ÞT pkþ1
,
```
where J k is the Jacobian matrix (n  n-matrix)
```
qkþ1 ¼ f x kþ1
 
 f xk
 
n-vectorð Þ
pkþ1 ¼ x kþ1  x k n-vectorð Þ:
Using the Sherman–Morrison formula
A þ xy T
 1
¼ A1  A
1xy T A1
1 þ yT A1x
,
derive the update formula for the inverse of the Jacobian in Broyden’s method.
x2
x1
x0
Figure 2.2 Perturbation in two
dimensions for given point x0 .
14 2 Solving Nonlinear Equations
2.4 Assume Broyden’s update formula is applied to the linear equations, Ax ¼ b, where A is
a square matrix:
J kþ1 ¼ J k þ q
kþ1  J k pkþ1  pkþ1 T
pkþ1ð ÞT pkþ1
:
If you start with the exact Jacobian for the initial guess, show that Broyden’s formula
predicts at the first iteration that same Jacobian. Does this result require the matrix A to
be nonsingular?
2.5 The system of equations
f 1 ¼ 2x21 þ x22  5 ¼ 0
f 2 ¼ x1 þ 2x2  3 ¼ 0
is to be solved with the starting point x1 ¼ 1:5, x2 ¼ 1:0, and with the criterion of
convergence 12 f T f  108 , using the two following methods:
```
(a) Newton’s method with unit step size α ¼ 1ð Þ,
```
```
(b) Broyden’s method with the update formula for the inverse of the Jacobian, using
```
unit step size α ¼ 1ð Þ and estimating the initial Jacobian J0 by using a perturbation
of h ¼ 104 in the variables.
Indicate in each case the number of iterations required to achieve the desired
convergence.
Exercises 15
3 Basic Theoretical Concepts in Optimization
3.1 Basic Formulations
In this section we introduce basic concepts of nonlinear constrained optimization as a
preamble of Section 3.4 on optimality conditions.
We first consider the model of a process given by the set of m equations h in n continuous
real-valued variables,
```
h xð Þ ¼ 0: (3.1)
```
```
The equations in (3.1) typically represent equations that describe the performance of a
```
system, say mass and energy balance equations and sizing equations. If n > m this implies
```
that there are degrees of freedom in the set of equations (3.1). If we define the number of
```
degrees of freedom to be df ¼ n  m, then, if df > 0, there is a finite number of degrees of
freedom, and therefore the model equations are amenable to optimization. Specifically, we
want to select the degree of freedom to optimize a given objective function. Say our goal is to
minimize the objective function represented by the scalar objective f xð Þ in n variables,
```
f : R n ! R1 . Aside from having to satisfy the equations in (3.1) the variables x may be
```
subject to a set of r inequalities that are represented by the constraints g xð Þ  0, g : R n ! R r.
Physically these may represent ranges of choices of the variables x, or simply nonnegativity
conditions on these variables.
If we gather the objective function, model equations, and inequalities, the continuous
```
optimization problem can be expressed mathematically as follows (Biegler, 2010):
```
min f xð Þ
```
s:t: h xð Þ ¼ 0
```
g xð Þ  0
x 2 Rn:
```
(3.2)
```
```
Assuming that at least some of the functions in (3.2) are nonlinear, problem (3.2) corres-
```
```
ponds to a nonlinear programming (NLP) problem. If all the functions are linear then the
```
```
problem corresponds to a linear programming (LP) problem. In both cases, they are
```
generally known as mathematical programming problems.
```
We can make a few remarks on problem (3.2).
```
```
(a) It can be easily proved that min f xð Þ is equivalent to max  f xð Þ. Figure 3.1 provides a
```
geometrical illustration of this property.
16
```
(b) Inequalities can always be rearranged in the form of g xð Þ  0. As a simple example
```
consider the inequality
```
x1 þ 2x2  3, (3.3)
```
which can be rearranged as follows:
```
x1  2x2 þ 3  0: (3.4)
```
```
(c) If a subset of the variables are discrete, y 2 Y q, say integer or 0-1, this then gives rise to
```
the following problem, which corresponds to a mixed-integer nonlinear programming
```
(MINLP) problem:
```
```
min f x; yð Þ
```
```
s:t: h x; yð Þ ¼ 0
```
```
g x; yð Þ  0
```
x 2 R n, y 2 Y q:
```
(3.5)
```
```
(d) Both problems (3.2) and (3.5) are declarative models, in the sense that in both the
```
```
formulations the conceptual problem is to find the optimum value of x∗ in (3.2) and
```
```
optimal values x∗, y∗ð Þ in problem (3.5) irrespective of how they are to be
```
solved numerically.
3.2 Nonlinear Programming Example
Consider the optimal design of the cooler shown in Fig. 3.2, in which a hot stream is to be
cooled from 550 K down to 320 K using cooling water that is available at 300 K. Its outlet
temperature t w is constrained not to be higher than 330 K.
Given the overall heat transfer coefficient U, the unit costs c A, c W for the area and
```
cooling water, respectively, the problem consists of finding the design of the cooler (area
```
```
A, heat load Q, outlet cooling water tw) that minimizes the total cost, namely area and
```
cooling water.
Without even writing the optimization model, we can qualitatively describe the problem
through Fig. 3.3, in which we plot the total cost versus the flowrate of cooling water W . As
```
f (x)
```
```
– f (x)
```
x
Figure 3.1 Illustration of the
relation between minimization
and maximization of objectives.
3.2 Nonlinear Programming Example 17
```
can be seen, the cost of cooling water (operating cost) increases linearly with the flowrate of
```
```
cooling water. On the other hand, the cost of the area (investment cost) decreases as we
```
increase the flowrate W . This follows from the fact that on the one hand at smaller flowrates
W , the outlet temperature increases, leading to smaller driving forces, and hence larger
areas. On the other hand, at larger flowrates, the driving force increases leading to smaller
areas. Adding both curves gives a total cost function whose minimum value is given at the
value W ∗. The solution to this optimization problem, which establishes an optimum trade-
off between investment and operating cost can be formulated as the following NLP problem.
In order to formulate the optimization model, let Q, A be the heat load and area, and let
W and t w be the water flowrate and its outlet temperature such that tw  330 K. The
corresponding nonlinear programming model can be formulated in the form of a general
```
NLP model in (3.5) as follows:
```
min C ¼ c A A þ c W W
```
s:t: Q  120 000 550  320ð Þ ¼ 0
```
Q  W tw  300ð Þ ¼ 0
Q  UA 550  twð Þ  320  300ð Þ
ln 550  tw320  300
¼ 0
tw  330  0
300  t w  0
 Q  0
 A  0
 W  0:
```
(3.6)
```
WW*
TotalCost
Operating cost
Area cost
Figure 3.3 Optimal trade-off
between area and cooling
water cost.
,Q A
tw
cp 
550 K
120 000 kg/hr
300 K
320 K
Figure 3.2 Optimal design of
a cooler.
18 3 Basic Theoretical Concepts in Optimization
```
Compared to (3.5) the variables x correspond to Q, A, W , tw. The three equations for the
```
heat balances and area sizing correspond to the equations h xð Þ ¼ 0, while the bounds on
tw, 300  t w  330, and Q, A, W  0, have been rearranged in the form of the inequalities
g xð Þ  0.
```
We should note that (3.6) corresponds to a declarative model, in which the objective
```
```
function and constraints as in (3.5) are explicitly declared without regard to how they will be
```
solved. Also note that the NLP has one degree of freedom as there are four variables,
Q, A, W , tw, and three equations. We should also note that, in software codes for NLP,
problem bounds can be specified separately from the inequalities g xð Þ  0.
3.3 Basic Concepts
```
This section introduces basic key theoretical concepts in optimization (Sargent, 1975;
```
```
Minoux, 1986).
```
Definition 3.1 Feasible region F ¼ xjx 2 R n, h xð Þ ¼ 0, g xð Þ  0f g.
Note that the feasible region F is given by the intersection of the constraints, and is
equivalent to applying the logic AND ^ð Þ operator to the set of equalities and inequalities
```
(e.g., see Fig. 3.4).
```
Definition 3.2 F is convex if and only if, for any x1 , x2 2 F,
x ¼ αx1 þ 1  αð Þx2 2 F, 8α 2 0, 1½ :
Figures 3.5 and 3.6 illustrate examples of convex and nonconvex feasible regions.
The following sufficient condition can be established for convexity of a feasible region.
Property 3.1 If h xð Þ ¼ 0 is linear and g xð Þ  0 involves convex functions, then F is a convex
feasible region.
Definition 3.3 f xð Þ is convex if and only if, for every x1 , x2 2 Rn
f αx1 þ 1  αð Þx2
 
 αf x1
 
þ 1  αð Þf x2
 
8α 2 0, 1½ :
```
h = 0
```
g1 ≤ 0g2 ≤ 0
x2
g3 ≤ 0
x1
Figure 3.4 Geometric
representation of feasible region
for three inequalities g xð Þ  0
and one equality h xð Þ ¼ 0.
Arrows point to
infeasible directions.
3.3 Basic Concepts 19
Figure 3.7 illustrates geometrically a convex function and a concave function that is
nonconvex.
Definition 3.4
```
(a) Local minimum. A point ^x 2 F corresponds to a local minimum if and only if,
```
f xð Þ  f ^xð Þ for 0 < x  ^xk k < δ, x 2 F, for δ arbitrarily small and positive.
```
(b) Global minimum. A point ^x 2 F corresponds to a global minimum if and only if,
```
f xð Þ  f ^xð Þ 8x 2 F :
The above are said to be strong local and global optima if the strict inequality applies >ð Þ
```
(see Fig. 3.8). If the equality applies, the above are said to be weak local and global optima.
```
x2
x1
x1
x2
Figure 3.5 Example of convex
feasible region.
x2
x2
x1
x1
Figure 3.6 Example of nonconvex
feasible region.
x1 x2 x
```
f (x) f (x)
```
x1 x2 x
```
(a) Convex (b) Concave
```
Figure 3.7 Examples of
convex and nonconvex
```
(concave) functions.
```
20 3 Basic Theoretical Concepts in Optimization
3.4 Optimality Conditions
3.4.1 Unconstrained Optimization
Consider the unconstrained optimization problem:
min f xð Þ
```
x 2 R n (3.7)
```
where we assume that f xð Þ is a continuous, differentiable function. A necessary condition for
```
the point ^x to be an extremum of problem (3.7) is given by the following theorem (Bazaraa
```
```
et al., 2006).
```
Theorem 3.1 If f xð Þ has an extremum in ^x, then ^x is a stationary point, which implies
rf ^xð Þ ¼ 0:
```
The first-order optimality condition of (3.7) (setting the gradient of f to zero rf ^xð Þ ¼ 0ð Þ
```
can be posed as the system of n equations in n unknowns,
∂f
∂x1
...
∂f
∂x n
2
66
66
66
64
3
77
77
77
75
¼
0
...
0
2
66
64
3
77
```
75: (3.8)
```
```
The system of equations in (3.8) can be solved with Newton’s method.
```
For the sufficient condition of point ^x to be an extremum, consider the second-order
expansion of f xð Þ at the point ^x,
```
f ^x þ Δxð Þ ¼ f ^xð Þ þ rf ^xð ÞT Δx þ 12 Δx T HΔx, (3.9)
```
```
where H is the Hessian matrix of second derivatives evaluated at ^x (e.g. x1 , x2 ),
```
H ¼
∂2f
∂x12
∂2f
∂x1∂x2
∂2f
∂x2∂x1
∂2f
∂x22
2
66
64
3
77
```
75: (3.10)
```
This matrix is symmetric since the order of differentiation is immaterial for Lipschitz
```
continuous functions. Since at the extremum rf ^xð Þ ¼ 0, this implies from (3.9) that
```
```
Δx T HΔx > 0 8Δx 6 ¼ 0: (3.11)
```
Strong min > Weak ≥
Figure 3.8 Examples of strong local
and weak local minima.
3.4 Optimality Conditions 21
```
A Hessian matrix H satisfying the above condition is said to be positive definite (strictly
```
```
positive definite for >0, and semipositive definite for 0). Since in general it is not trivial to
```
establish the positive definiteness of a Hessian matrix, we can exploit the following proper-
ties, which are based on the analysis of the signs of the eigenvalues or on the convexity of the
```
functions (Wilkinson, 1965):
```
```
(a) H is positive definite if and only if the eigenvalues λi > 0, i ¼ 1, 2, . . . , n,
```
```
(b) if f xð Þ is strictly convex, then H is positive definite.
```
We should also note that if f xð Þ is strictly convex and it has a stationary point ^x, then ^x is a
unique local minimum.
```
3.4.2 Constrained Optimization (Equalities)
```
We address in this section optimization problems with equality constraints, which can be
formulated as follows:
min f xð Þ
```
s:t: h xð Þ ¼ 0
```
x 2 R n,
```
(3.12)
```
where we assume that f xð Þ, h xð Þ are continuous, differentiable functions in the continuous
variables x.
```
The necessary conditions for an extremum at a point ^x in (3.6) are given by the following
```
theorem
Theorem 3.2 If f xð Þ has a constrained extremum at ^x such that hj ^xð Þ ¼ 0 j ¼ 1, . . . , m, then
the gradients rf ^xð Þ ¼ 0, rhj ^xð Þ are linearly dependent, that is,
λ0rf ^xð Þ þ
Xm
j¼1
```
λj rh j ^xð Þ ¼ 0 (3.13)
```
where λ0 , λj are scalars.
Proof Consider the m þ 1 equations, where y is the value of the function f xð Þ,
f xð Þ ¼ y
```
hj xð Þ ¼ 0 j ¼ 1 . . . m (3.14)
```
A sufficient condition for the existence of a solution around ^x for any y close to the assumed
```
extremum ^y, is that the Jacobian of (3.14),
```
J ^xð Þ ¼
rf T ^xð Þ
rhT1 ^xð Þ
. . .
rh Tm ^xð Þ
2
66
66
4
3
77
77
5
```
, (3.15)
```
22 3 Basic Theoretical Concepts in Optimization
has rank m þ 1. Since the rank of the Jacobian J ^xð Þ is m þ 1, this implies that we can find
solutions for y > ^y, which contradicts the assumption that ^y is an extremum. This then
implies that the rank of J ^xð Þ is strictly < m þ 1. This in turn implies that the rows in J ^xð Þ are
linearly independent, namely,
λ0rf ^xð Þ þ
Xm
j¼1
```
λj rhj ^xð Þ ¼ 0, (3.16)
```
```
which is identical to (3.13). ∎
```
```
We should note that if λ0 ¼ 1, then this means that a “constraint qualification” (Bazaraa
```
```
et al., 2006) holds and, hence,
```
rf ^xð Þ ¼ 
Xm
j¼1
```
λj rhj ^xð Þ, (3.17)
```
which means that at the extremum ^x, the gradient of the objective function can be expressed
as a linear combination of the gradients of the equalities. Figure 3.9 presents a geometrical
interpretation for the case of two dimensions and a quadratic objective function, where it
can be seen that rf , and rh are co-linear.
Figure 3.10 shows a case where the constraint qualification does not hold true since the
gradient of the objective rf , cannot be obtained by a finite linear combination of the
gradients of the equations rh1, rh2 .
x2
x1
h 0
ˆx
f
h
Figure 3.9 Minimum for a
constrained quadratic function
for which the constraint
qualification is satisfied.
x2
x1
h1 0
h2 0
fˆx
h1
h2
Figure 3.10 Minimum for a
constrained quadratic function
for which the constraint
qualification is not satisfied.
3.4 Optimality Conditions 23
```
Theorem 3.2 can also be interpreted as follows. If we set λ0 ¼ 1, it follows from (3.17) and
```
the condition of feasibility for the equations, that,
rf ^xð Þ ¼ 
Xm
j¼1
```
λj rh j ^xð Þ ¼ 0 (3.18)
```
```
hj ^xð Þ ¼ 0 j ¼ 1, . . . , m, (3.19)
```
which correspond to the stationary conditions of the Lagrangean function,
L ¼ f xð Þ þ
Xm
j¼h
```
λj hj xð Þ (3.20)
```
since
∂L
∂x ¼ rf xð Þ þ
Xm
j¼1
```
λj rh j ^xð Þ ¼ 0 (3.21)
```
∂L
```
∂λj¼ hj ^xð Þ ¼ 0 j ¼ 1, . . . , m, (3.22)
```
which gives rise to a system of n þ m nonlinear equations in the n þ m unknowns
```
x; λð Þ. The nonlinear equations in (3.21) and (3.22) are typically solved with Newton’s
```
method.
```
3.4.3 Constrained Optimization (Inequalities)
```
We consider the following nonlinear optimization problem with inequalities,
min f xð Þ
```
s:t: g xð Þ  0
```
x 2 R n,
```
(3.23)
```
where f xð Þ, g xð Þ are assumed to be continuous, differentiable functions. A necessary
```
condition for the point ^x to be a local minimum of (3.17) is given by the following theorem
```
```
by Fritz John (1948).
```
Theorem 3.3 If f xð Þ has a constrained minimum at ^x such that g j ^xð Þ  0 ^x, j ¼ 1, . . . , r, then
there exist nonnegative multipliers μj  0, j ¼ 0, 1, . . . , r  such that
μ0rf ^xð Þ þ
Xr
j¼1
```
μj rg j ^xð Þ ¼ 0 (3.24)
```
```
μj g j ^xð Þ ¼ 0 j ¼ 1, . . . , r: (3.25)
```
24 3 Basic Theoretical Concepts in Optimization
The first equation defines the condition of linear dependence of the gradients of the
objective function and inequality constraints, while the second equation establishes
complementary conditions between the multipliers μj and the corresponding inequalities
g j ^xð Þ  0 evaluated at the constrained minimizer ^x. These imply that if μj > 0, then
```
g j ^xð Þ ¼ 0, i.e. the inequality g j is active. If μj ¼ 0, then g j ^xð Þ  0; i.e. the inequality is
```
inactive if g j ^xð Þ < 0.
The proof of Theorem 3.3 can be obtained by applying Gordan’s Transposition Theorem
```
(Gordan, 1873). Rather than presenting the proof, we illustrate this theorem with the
```
example in Fig. 3.11 that involves two variables, x1 and x2 , and the three inequalities
g1 xð Þ  0, g2 xð Þ  0, g3 xð Þ  0. Notice that at the optimum solution, ^x, there are two active
constraints, g1 ^xð Þ ¼ 0, g2 ^xð Þ ¼ 0, and one inactive inequality g3 ^xð Þ < 0. Furthermore, we
can set μ0 ¼ 1, since a constraint qualification is assumed to hold true. Therefore, from
Theorem 3.3 the following conditions hold true at ^x, namely linear dependence of gradients
of the objective and active inequalities, and corresponding complementarity conditions
rf þ μ1rg1 þ μ2rg2 ¼ 0
g1 ¼ 0, g2 ¼ 0, μ1 , μ2  0
g3 < 0, μ3 ¼ 0
μ1g1 ¼ 0, μ2g2 ¼ 0, μ3g3 ¼ 0:
```
(3.26)
```
Referring to Fig. 3.11 it is interesting to note that the gradient of the objective rf can be
viewed as given by a linear combination of the gradients of the active constraints rg1 , rg2.
```
Also, note that the multipliers in (3.26) have an interesting interpretation. If we set μ0 ¼ 1,
```
```
then (3.21) reduces to
```
rf ^xð Þ þ
Xr
j¼1
```
μj rg j ^xð Þ ¼ 0 (3.27)
```
with μj  0. Let us consider the direction vector p shown in Fig. 3.11. We can project the
gradients of the objective and inequalities by considering the following scalar products,
which yield the changes δf in the objective, and δg j in the constraints,
```
p T rf ^xð Þ ¼ δf , pT rg j ^xð Þ ¼ δg j : (3.28)
```
x2
x1
g2
g1 f
g1 0
g3 0
g2 0
p
Figure 3.11 Two-dimensional
example with two
active inequalities.
3.4 Optimality Conditions 25
```
To relate these changes, we first premultiply (3.27) by the vector p,
```
p T rf ^xð Þ þ
Xm
j¼1
```
μj pT rg j ^xð Þ ¼ 0: (3.29)
```
```
By substituting (3.28) we obtain
```
δf þ
Xm
j¼1
```
μj δg j ¼ 0: (3.30)
```
```
If we now set δg j ¼ 0 8j 6 ¼ i, (3.30) reduces to
```
```
δf þ μiδg i ¼ 0, (3.31)
```
from which it follows that,
μi ¼  δfδg
i
 
δg j ¼ 0
j 6 ¼ i
```
: (3.32)
```
```
Equation (3.32) states that when δg i ! 0, the multiplier μi represents the rate of decrease of
```
the objective f ^xð Þwith a small perturbation of the inequality g i ^xð Þ, at the optimum solution
```
^x. Furthermore, we can interpret (3.32) in terms of the sign of the multipliers. Specifically,
```
consider an infeasible move δg i > 0 at the active inequality g j ^xð Þ ¼ 0.
```
(a) For μi > 0, (3.32) implies δf < 0; in other words a local decrease of the objective for an
```
```
infeasible perturbation of inequality constraint i;
```
```
(b) for μi < 0 (3.32) implies δf > 0; in other words, a local increase of the objective for an
```
infeasible perturbation of inequality constraint i.
As we will see in the next section, the sign of the multipliers can be used within an active
strategy for solving nonlinear programming problems.
3.4.4 Nonlinear Programming Problem
```
We consider the more general form of nonlinear programming (NLP) problems that involve
```
both equality and inequality constraints, h xð Þ ¼ 0, g xð Þ  0 h: m-vector, g: r-vectorð Þ:
min f xð Þ
```
s:t: h xð Þ ¼ 0
```
g xð Þ  0
x 2 R n:
```
(3.33)
```
```
The necessary conditions for a constrained minimum at the point ^x in the NLP in (3.33) are
```
```
given by the Karush–Kuhn–Tucker (KKT) conditions (Karush, 1939; Kuhn and Tucker,
```
```
1951), which result from combining the results for the NLP with only equalities and only
```
26 3 Basic Theoretical Concepts in Optimization
inequalities, and assuming a constraint qualification. The KKT conditions are given by the
three following conditions.
```
(1) Linear dependence of gradients
```
rf ^xð Þ þ
Xm
j¼1
λj rhj ^xð Þ þ
Xr
j¼1
```
μj rg j ^xð Þ ¼ 0: (3.34)
```
```
(2) Constraint feasibility
```
```
h j ^xð Þ ¼ 0, j ¼ 1, . . . , m g j ^xð Þ  0 j ¼ 1, . . . , r: (3.35)
```
```
(3) Complementarity conditions
```
μj g j ^xð Þ ¼ 0 j ¼ 1, . . . , r
```
μj  0 j ¼ 1, . . . , r: (3.36)
```
```
The following properties hold for the case of convex NLPs (convex objective and convex
```
```
feasible region):
```
Property 3.2 If f xð Þ is convex, the feasible region F is convex and nonempty, then if there
exists a local minimum at ^x, then:
```
(a) ^x corresponds to a global minimum,
```
```
(b) the constraint qualification is satisfied,
```
```
(c) the KKT conditions are necessary and sufficient for a global minimum.
```
The main implication of the above properties for convex NLPs is that there is no need to
```
analyze second-order information of the Hessian of the Lagrangean of (3.33), rxx L ^x, μ , λð Þ,
```
i.e. determine whether the Hessian is positive definite to define a local minimum.
```
In contrast to the unconstrained case (3.7) or the equality-constrained case (3.12), where
```
```
one can solve for the optimality conditions as a system of equations (e.g., with Newton’s
```
```
method), solving for the KKT conditions (3.34)–(3.36) is not straightforward due to the
```
```
complementarity conditions (3.36), which give rise to nonconvex equations.
```
The simplest method for finding a point that satisfies the KKT conditions is an iterative
active-strategy method in which a subset of inequalities are iteratively forced to become
active until they all satisfy the complementarity conditions and attain the correct sign of the
multipliers. The procedure outlined below provides the major steps involved in the active-
set strategy.
3.4.5 Active-Set Strategy Procedure for Determining a Karush–Kuhn–Tucker Point
```
(Sargent, 1975)
```
Let J1 ¼ jjg j xð Þ ¼ 0
 
be the index of active inequalities.
```
(1) Assume no active inequalities. Set j1 ¼ ∅, uj ¼ 0, j ¼ 1, 2, . . . , r.
```
```
(2) Formulate KKT equations (3.31)–(3.33) and solve for x, λj , j ¼ 1, 2, . . . , m, and μj , j 2 J1 ,
```
3.4 Optimality Conditions 27
rf xð Þ þ
Xm
j¼1
λj rhj xð Þ þ
X
j2J1
μj rg j xð Þ ¼ 0
h j xð Þ ¼ 0, j ¼ 1, . . . , m
g j xð Þ ¼ 0, j 2 J1:
```
(3) If at the solution ^x, g j ^xð Þ  0 and μj  0, j ¼ 1, 2, . . . , r, then STOP. Solution found.
```
```
(4) If any g j ^xð Þ > 0 (violated) and/or any μj < 0 (wrong sign), then do the following.
```
```
(a) Drop one active constraint with wrong sign for μj (largest magnitude).
```
```
(b) Add to J1 violated constraints g j xð Þ > 0 to make them active (maximum of n
```
```
constraints).
```
```
(c) Return to step (2).
```
We should note that the main goal in the active-set strategy is to identify the correct set of
```
active constraints. In step (1), we can start with the initial guess x0 and with a given set of active
```
constraints rather than assuming that they are all inactive. Also, the reason we drop only one
```
constraint in step (4a) is that the multiplier corresponds to the partial derivative; that is,
```
```
μj ¼ ∂f =∂g j if μj < 0 ) for ∂g j < 0, ∂f < 0:
```
We next present an example to illustrate the application of the active strategy for finding a
KKT point in the following NLP problem, which in fact corresponds to a quadratic
program since the objective is quadratic and the constraints are linear:
min f xð Þ ¼ 12 x21 þ x22
 
 3x1  x2
```
s:t: g1 ¼ x1 þ x2  0
```
g2 ¼ x1  12 x2  2  0
g3 ¼ x2  0:
```
(3.37)
```
Figure 3.12 shows the feasible region and contours of the objective function, where by
inspection we can see that the minimum solution lies at the point x1 ¼ 2:6, x2 ¼ 1:2, in
which the inequality g2 is active.
To apply the active-set strategy, we first determine the gradients of the objective function
and three inequalities:
rf ¼ x1  3x2  1
 
rg1 ¼ 11
 
rg2 ¼ 11=2
 
rg3 ¼ 01
 
:
We follow the steps of the active-set strategy.
First iteration
```
(1) Set J1 ¼ ∅, μ1 ¼ μ2 ¼ μ3 ¼ 0.
```
```
(2) Since there are no active inequalities, (3.34) reduces to the stationary condition of
```
f xð Þ:
rf xð Þ ¼ 0,
28 3 Basic Theoretical Concepts in Optimization
which in turn give rise to the equations:
x1  3 ¼ 0
x2  1 ¼ 0
whose solution yields x1 ¼ 3, x2 ¼ 1.
```
(3) Substituting these values in the three inequalities yields:
```
g1 ¼ 2 < 0 g2 ¼ 12 > 0 g3 ¼ 1 < 0:
```
(4) Make g2 active since it is violated; i.e., set J1 ¼ 2f g, meaning we treat it as the equation
```
g2 ¼ x1  12 x2  2 ¼ 0.
Second iteration
```
(2) Since g2 is active, the stationary conditions of the Lagrangean are as follows:
```
rf xð Þ þ μ2rg2 xð Þ ¼ 0
g2 xð Þ ¼ 0,
which in turn corresponds to a linear system of three equations in three unknowns
x1 , x2 , μ2 ,
x1  3
x2  1
" #
þ μ2
1
 12
" #
¼
0
0
" #
x1  12 x2  2 ¼ 0,
whose solution yields x1 ¼ 2:6, x2 ¼ 1:2 μ2 ¼ 0:4.
```
(3) Substituting these values in the three inequalities yields:
```
g1 ¼ 1:4 < 0 g2 ¼ 0 g3  1:2 < 0
μ ¼ 0 μ2 ¼ 0:4 μ3 ¼ 0:
ˆx
1 0g 
2 0g 
1x
2x
4
3
2
1
1 2 3 4
3 0g 
Figure 3.12 Feasible region and
contours of objective for
example problem.
3.4 Optimality Conditions 29
Since the three inequality constraints are satisfied and the multipliers have the correct
sign to satisfy the complementary conditions, we can stop and conclude that the point
x1 ¼ 2:6, x2 ¼ 1:2 with objective value f ¼ 4:9 corresponds to a KKT point of the
```
quadratic program (3.37).
```
It is interesting to note that, at the KKT point x1 ¼ 2:6, x2 ¼ 1:2, linear dependence of
gradients holds since for:
rf ¼
0:4
0:2
" #
, rg2 ¼
1
 12
" #
, μ2 ¼ 0:4:
We can easily verify the linear dependence of the gradients of the objective and active
inequality, that is:
0:4
0:2
" #
þ 0:4
1
0:5
" #
¼
0
0
" #
:
We can also establish that the KKT point found corresponds to a minimum that is unique
```
(i.e. global minimum). If we determine the Hessian matrix and substitute the corresponding
```
values this yields the identity matrix
H ¼
∂2f
∂x12
∂2f
∂x1∂x2
∂2f
∂x2∂x1
∂2f
∂x22
2
66
64
3
77
75 ¼
1 0
0 1
" #
:
The eigenvalues of the identity matrix can be computed by setting to zero the determinant of
the identity matrix minus the eigenvalues in the diagonal, that is,
1  λ 0
0 1  λ
¼ 1  λð Þ2 ¼ 0:
The solution of the quadratic polynomial yields λ1 ¼ λ2 ¼ 1. Since both eigenvalues are
strictly positive, it follows that the objective function f xð Þ is strictly convex. Furthermore,
since the inequality constraints are linear, the feasible region is convex. It then follows that
```
the quadratic programming problem (3.37) is convex. Hence it has a unique optimum, and
```
the KKT conditions are both necessary and sufficient.
EXERCISES
3.1 Show that if f xð Þ is a convex function on R n, then a local minimum of f xð Þ is also a
global minimum of f xð Þ on R n.
3.2 Determine whether or not the following quadratic function is convex:
f x1 , x2ð Þ ¼ 2x1 þ x2  x12 þ 2x1x2  x22:
30 3 Basic Theoretical Concepts in Optimization
3.3 Given is a set of linear equalities Ax ¼ b and a set of convex nonlinear inequalities
g xð Þ < 0, where A is an m  n matrix and x an n-vector m < nð Þ. Assuming that the
corresponding feasible region is nonempty, show that the region is convex.
3.4 Assume that you are given a quasiconvex function
```
g xð Þ: (3.38)
```
Show that its inequality in the form of g xð Þ  0 defines a convex feasible region.
3.5 Show that a Hessian matrix which is positive definite has positive eigenvalues.
3.6 Consider the nonlinear programming problem
min f xð Þ
```
s:t: g j xð Þ  0 j ¼ 1, . . . , r
```
x 2 Rn,
```
where the functions f and g are monotonic in each variable x i xi (i.e., ∂f =∂x i and
```
```
∂g j =∂x i are one-signed if the derivatives are nonzero).
```
```
Show that the following hold true (these are the so-called principles of monotonicity
```
```
analysis).
```
```
(a) If a variable x i is present in the objective and in some of the constraints, there is at
```
least one active constraint involving x i and whose derivative has an opposite sign
from the objective.
```
(b) If a variable x i is not present in the objective, it is either involved in at least two
```
active constraints with an opposite sign in the derivatives, or else it is not involved in
any active constraints.
3.7 Given the problem
min f xð Þ ¼ x1  3ð Þ2 þ x2  4ð Þ2
```
s:t: 2x1 þ x2  6  0
```
x1  x2  4  0
x1  1:8
x2  0
do the following.
```
(a) Plot the contours for f ¼ 0, 1, 2, 4, 6, 8, 10, and the feasible region. From inspection,
```
what is the optimal solution?
```
(b) Solve this problem using an active-constraint strategy. Plot the gradients of the
```
objective and active constraints at the optimum and verify geometrically the
Karush–Kuhn–Tucker conditions. Determine also whether the optimal solution
is unique.
Exercises 31
4 Nonlinear Programming Algorithms
We consider in this chapter algorithms for the solution of NLP problems of the following form:
min f xð Þ
```
s:t: h xð Þ ¼ 0
```
g xð Þ  0
x 2 R n:
```
(4.1)
```
The algorithms we will consider include the following.
```
(a) The successive-quadratic programming (SQP) algorithm that is implemented in the code
```
SNOPT in GAMS.
```
(b) Reduced-gradient algorithm that is implemented in the code CONOPT in GAMS.
```
```
(c) Interior-point method that is implemented in the code IPOPT, which is open
```
source software.
As we will show in the next few sections, the various algorithms apply Newton’s method to
the KKT conditions in a different way.
4.1 Successive-Quadratic Programming
The successive-quadratic programming algorithm, also known as the SQP algorithm, or the
```
Wilson–Han–Powell algorithm (Wilson, 1963; Han, 1976; Powell, 1978), is based on the idea
```
of applying Newton’s method to the KKT conditions of the NLP with equality constraints:
min f xð Þ
```
s:t: h xð Þ ¼ 0
```
x 2 R n:
```
(4.2)
```
```
Setting up the Lagrangean function of (4.2),
```
```
L x; λð Þ ¼ f xð Þ þ h xð ÞT λ, (4.3)
```
the necessary conditions for a stationary point of the Lagrangean, yield the following:
að Þ ∂L∂x ¼ rf xð Þ þ rh xð Þλ ¼ 0
bð Þ ∂L∂λ ¼ h xð Þ ¼ 0,
```
(4.4)
```
32
```
where rh ¼ rh1 , rh2; . . . , rhm½  is the transpose of the Jacobian. Note that (4.4a) and
```
```
(4.4b) define n þ m equations in n þ m unknowns for the variables x and λ. We now
```
```
represent (4.4a) and (4.4b) by the system of equations
```
```
ϕ uð Þ ¼ 0: (4.5)
```
```
Applying Newton’s method to (4.5) at a given point ui ¼ x i, λi
```
 
,
ϕ ui
 
þ rϕ ui
 T
u  u i
 
```
¼ 0, (4.6)
```
```
from (4.4a) this implies,
```
rf x i
 
þ rh x i
 
λi þ rxx f x i
 
x  xi
 
þ λi
 T
rxx h xi
 
x  xi
 
þ rh x i
 
λ  λi
 
```
¼ 0 (4.7)
```
which can be simplified as
rf x i
 
þ rh x i
 
λ þ rxx f x i
 
x  x i
 
þ λi
 T
rxx h x i
 
x  x i
 
```
¼ 0, (4.8)
```
```
where rxx h ¼ rxx h1; . . . , rxx hm½ . Note also that the term λi
```
 T
rxx h x ið Þ x  x ið Þ can be
written in expanded form as Pj λij∂
2hj
∂x2 x  x ið Þ.
Since the Hessian of the Lagrangean,rxx L x i, λi
 
¼ rxx f xið Þ þ λi
 T
```
rxx h x ið Þ, in (4.8)
```
together with the linearization of the equalities h xð Þ ¼ 0, this yields,
f x i
 
þ rh xi
 
λ þ rxx L x i, λi
 
x  x i
 
¼ 0
h x i
 
þ rh x i
 T
x  x i
 
¼ 0:
```
(4.9)
```
```
While (4.9) correspond to the equations for Newton’s method applied to (4.4a) and (4.4b),
```
the interesting observation is that they also correspond to the KKT conditions of the
quadratic program with the objective function
rf x i
 T
x  xi
 
þ 12 x  xið ÞT rxx L x i, λi
 
```
x  x ið Þ (4.10)
```
and constraints
h x i
 
þ rh xi
 T
x  x i
 
```
¼ 0: (4.11)
```
```
That is, we can compute the Newton step d ¼ x  x i for the system of equations in (4.9)
```
```
from the following quadratic program (QP):
```
min rf x i
 T
þ 12 d T rxx L xi, λi
 
d
```
s:t: h x i
```
 
þ rh x i
 T
x  x i
 
d ¼ 0,
```
(4.12)
```
```
where the Hessian of the QP is the Hessian of the Lagrangean. The solution of (4.12) yields
```
the Newton step d ¼ x  x i and the multipliers λiþ1. The new guess for the variables x can
then be set to x iþ1 ¼ x i þ d.
One may of course wonder what we gain by solving Newton’s method through the QP. Aside
from the fact that there are efficient methods for solving QP problems, the extension for
handling inequalities becomes trivial. That is, for given xi, λi, μi we can set up the QP:
4.1 Successive-Quadratic Programming 33
min rf x i
 T
þ 12 d T rxx L x i, λi, μi
 
d
```
s:t: h xi
```
 
þ rh x i
 T
d ¼ 0
g xi
 
þ rg x i
 T
d  0,
```
(4.13)
```
where the Lagrange function is given by
```
L x; λ; μð Þ ¼ f xð Þ þ
```
Xm
j¼1
λj hj xð Þ þ
Xr
j¼1
μj g j xð Þ:
In the implementation of the algorithm, the Hessian rxx L is often approximated with a
```
matrix B i using the quasi-Newton formula BFGS (Nocedal and Wright, 2006) to force
```
positive definiteness. Also, at each iteration a line search is performed to select the step size α
in xiþ1 ¼ xi þ αd to minimize the Lagrangean. We should also note that the SQP algorithm
is an infeasible path algorithm because it simultaneously optimizes the objective while
converging the constraints. Furthermore, being based on Newton’s method, it has quadratic
convergence close to optimum.
```
In summary, the major steps involved in the SQP algorithm (Wilson–Han–Powell) are as
```
follows.
```
(1) Set iteration counter i ¼ 0; set estimate Hessian of Lagrangean B0 ¼ I ; guess x0 :
```
```
(2) Evaluate the functions and the gradients.
```
f x i
 
, h x i
 
, g x i
 
, rf x i
 
, rh xi
 
, rg xi
 
:
```
(3) Solve the quadratic program QP to obtain step d, and multipliers λiþ1 , μiþ1
```
min rf x i
 T
d þ 12 d T B i d
```
s:t: h x i
```
 
þ rh x i
 T
```
d ¼ 0 ! d; λiþ1 , μiþ1
```
 
g x i
 
þ rg xi
 T
d  0:
```
(4) Check convergence:
```
If rL x i, λiþ1 , μiþ1
 
2 < ε, STOP,
where rL ¼ rf þ rhλ þ rgμ:
Else set x iþ1 ¼ x i þ αd α ¼ 1 : Newtonð Þ,
and go to step 5:
```
(5) Update the Hessian of the Lagrangean (BFGS).
```
```
(a) Determine s i ¼ x iþ1  xi
```
```
(b) Calculate yi ¼ rL x iþ1 , λiþ1 , μiþ1   rL x i, λi, μi  (rank-2 update).
```
```
(c) Set i ¼ i þ 1, B iþ1 ¼ B i  B
```
i si s iT B i
s iT B i s i þ
y i yiT
```
yiT si return to step (2).
```
34 4 Nonlinear Programming Algorithms
4.2 Reduced-Gradient Method
In this section we consider the reduced-gradient method as originally proposed by Murtagh
```
and Saunders (1978, 1982) with the code MINOS, and later extended by Drud (1994) with
```
the code CONOPT.
The basic ideas in the reduced-gradient method are to consider a linear approximation of
the constraints and to eliminate variables to reduce dimensionality, and then to apply
Newton’s method.
Consider the following NLP with linear equalities,
min f xð Þ
```
s:t: Ax ¼ b, (4.14)
```
where A is an m  n matrix, m < n, and for simplicity in the presentation we do not consider
nonnegativity conditions x  0. In order to eliminate variables from the linear constraints
we partition the variables x as follows:
x ¼ yu
 
```
, (4.15)
```
```
where y are the m dependent (i.e. calculated) variables, and u are the n  m independent or
```
```
superbasic variables (i.e., degrees of freedom). If we now partition the matrix as follows,
```
A ¼ BjC½ , where matrix B is an m  m square matrix, and C is an m  n  mð Þ matrix, we
can then rewrite the linear constraints as
Ax ¼ BjC½  yu
 
```
¼ b: (4.16)
```
Consider the step Δx, such that
Δx ¼ ΔyΔu
 
¼ y  y
k
u  uk
 
```
(4.17)
```
```
satisfies (4.16). We can then rewrite (4.16) at the predicted and current points as
```
By þ Cu ¼ b
```
Byk þ Cu k ¼ b: (4.18)
```
By subtracting both we obtain
```
BΔy þ CΔu ¼ 0, (4.19)
```
from which it follows that Δy ¼ B1CΔu, and hence the predicted step Δx is given by
Δx ¼ ΔyΔu
 
¼ B
1C
I
 
```
Δu: (4.20)
```
```
We can also rewrite (4.20) as
```
```
Δx ¼ ZΔu, (4.21)
```
4.2 Reduced-Gradient Method 35
where Z, the transformation matrix, is given by
Z ¼ B
1C
I
 
```
: (4.22)
```
```
To apply Newton’s method to problem (4.14), consider a second-order expansion of f xð Þ
```
at xi,
f xð Þ ¼ f x i
 
þ rf xi
 T
Δx þ 12 Δx T rxx f x i
 
```
Δx: (4.23)
```
```
If we substitute (4.21) in (4.23), it can be expressed in terms of the independent variables u,
```
f xð Þ ¼ f xi
 
þ rf x i
 T
ZΔu þ 12 ΔuT Z T rxx f x i
 
```
ZΔu: (4.24)
```
We define as the reduced gradient the term, g TR ¼ rf x ið ÞT Z, and as the reduced Hessian,
```
H R ¼ Z T rxx f x ið ÞZ. Hence (4.24) can then be expressed in terms of the reduced gradient
```
and reduced Hessian, namely
f uð Þ ¼ f xi
 
```
þ g TR Δu þ 12 ΔuT H RΔu: (4.25)
```
Since a necessary condition for a minimum of f xð Þ is given by the stationary condition
∂f
∂Δu ¼ 0, we can set
```
g R þ H RΔu ¼ 0: (4.26)
```
```
To determine the Newton step Δu, we rearrange (4.26) as follows,
```
```
H RΔu ¼ g R, (4.27)
```
which gives rise to a linear system of n  m equations in n  m variables to compute the
Newton step Δu.
We should note that, in the implementation of the reduced-gradient method, as in the SQP
method, the reduced Hessian matrix Z T ¼ rxx f x ið ÞZ is usually estimated with a quasi-
```
Newton formula (e.g., BFGS).
```
Also, to compute the reduced gradient g TR ¼ rf x ið ÞT Z, we can partition it into the
dependent yð Þ and independent uð Þ variables as follows:
g TR ¼ ry f ru f
 T B1C
I
 
```
¼ ry f T B1C þ ru f T : (4.28)
```
In order to avoid computing the inverse of the matrix B1 we solve the linear system for the
multipliers λ from the KKT equation,
```
B T λ ¼ ry f : (4.29)
```
Since B T λ
 T
¼ λT B ¼ ry f T , and by postmultiplying by B1, the reduced gradient can be
obtained from the following equation,
```
g TR ¼ λT C þ ru f T : (4.30)
```
36 4 Nonlinear Programming Algorithms
```
Finally, for handling nonlinear constraints, we reformulate the NLP in (4.1) in terms of
```
equalities r xð Þ ¼ 0 as follows,
min f xð Þ
```
s:t: r xð Þ ¼ 0
```
x  0:
```
(4.31)
```
This reformulation can be obtained by adding slack variables to the inequalities. As a
simple example consider the inequality x1 þ x2  1. By introducing a nonnegative slack
variable s, we can rewrite that constraint as the equality x1 þ x2 þ s ¼ 1, where the slack
variable s  0.
```
To handle the nonlinear inequalities r xð Þ ¼ 0 in (4.31), we define an augmented
```
Lagrangean in an “outer iteration” in which we add a dual term to the objective and where
we linearize the equations r xð Þ ¼ 0:
P i
 
: min f xð Þ þ λi
 T
r xð Þ  r x i
  
```
s:t: J xi
```
 
```
x ¼ b (4.32)
```
where J x ið Þ is the Jacobian matrix of r xð Þ, and λi are the multipliers computed at the
point x i.
The procedure then consists of formulating a sequence of P i
 
subproblems in an outer
iteration, each of which is solved in an “inner iteration” using the reduced-gradient method,
```
because (4.32) has the form of the linearly constrained problem (4.14). At each outer
```
iteration the new point is obtained by setting x iþ1 ¼ x i þ α x∗  x i½ , where x∗ is the solution
P i
 
and α is the step length, which is adjusted to ensure descent of the augmented Lagrange
```
function in (4.32).
```
In the procedure below, we summarize the main steps of the reduced-gradient method as
```
implemented in the original code MINOS (Murtagh and Saunders, 2003). Part I refers to the
```
inner iterations for the linearly constrained problem, while Part II refers to the outer iterations.
```
(I) Inner iterations
```
Linear constraints: min f xð Þs:t: Ax ¼ b
```
(1) (a) Select feasible starting point for Ax ¼ b;
```
A ¼ BjC½ , B-basis, y-basic variable, u-independent variable.
```
(b) Set reduced Hessian H0R ¼ I ; set k ¼ 0.
```
```
(2) Compute f x k
```
 
, rf x k
 
¼ ry fru f
 
.
```
(3) (a) Solve B T λ ¼ ry f
```
```
(b) Calculate reduced gradient, g TR ¼ λT C þ ru f T .
```
```
(c) Calculate steps Δu and Δy from H kRΔu ¼ g R and BΔy ¼ CΔu
```
and set Δx ¼ ΔyΔu
 
:
```
(4) Do line search for x kþ1 ¼ x k þ αΔx, where α = step size to min f xð Þ along Δu.
```
4.2 Reduced-Gradient Method 37
```
(5) Check convergence.
```
```
If g TR g R 2  ε, STOP. Else go to step (6).
```
```
(6) Update H kþ1R with the BFGS formula, set s k ¼ Δu, y k ¼ g R ukþ1
```
 
 g R u k
 
```
Set k ¼ k þ 1, return to step (2).
```
```
(II) Outer iterations for nonlinear constraints
```
```
(a) Linearize augmented Lagrangean (4.32).
```
```
(b) Apply algorithm I for inner optimization.
```
We should note that this algorithm is also an infeasible path method in the sense that the
```
optimization and convergence are carried out simultaneously. The code MINOS (Murtagh
```
```
and Saunders, 2003) essentially implements this algorithm.
```
```
In order to increase robustness codes like CONOPT (Drud, 1994) and GRG (Lasdon
```
```
et al., 1978) perform some Newton corrections to try to regain feasibility at each major
```
iteration as shown in Fig. 4.1 making the code look more like a feasible path method.
4.3 Interior-Point Method
```
We reformulate the NLP in (4.1) with only equality constraints,
```
min f xð Þ
```
s:t: c xð Þ ¼ 0
```
x  0,
```
(4.33)
```
which can be accomplished by replacing the inequalities by equalities and introducing slack
```
variables, similarly as we did in (4.31).
```
```
We then apply Newton’s method to the “barrier” problem (Fiacco and McCormick,
```
```
1968), in which the nonnegativity of the x i variables is handled by introducing the penalty
```
term α Pi ℓn x ið Þ
x1
Newton
correction
x2Figure 4.1 Newton correction to
regain feasibility.
38 4 Nonlinear Programming Algorithms
min f xð Þ  α
X
i
ℓn x ið Þ
```
s:t: c xð Þ ¼ 0
```
```
(4.34)
```
```
which then gives rise to the barrier term in the objective function shown in Fig. 4.2 (Fiacco
```
```
and McCormick, 1968). Notice that as α ! 0 the barrier function approaches the objective
```
```
function f xð Þ.
```
```
As shown in Marsten et al. (1990), (4.34) turns out to be equivalent to applying Newton’s
```
method to the KKT conditions with complementarity conditions, μi x i ¼ α, α > 0. More
specifically,
rf xð Þ þ A xð Þλ  v ¼ 0
Xv  μe ¼ 0
c xð Þ ¼ 0,
```
(4.35)
```
where
```
e T ¼ 1, 1, 1; . . .½ , X ¼ diag xð Þ
```
```
A ¼ rc xð Þ, W ¼ rxx L x; λ; νð Þ:
```
```
If we solve the systems of equations in (4.35) applying Newton’s method, this leads to:
```
W A I
A T 0 0
V 0 X
2
4
3
5
d x
dλ
dν
2
4
3
5 ¼ 
rf þ Aλ  ν
c
Xv  μ e
2
4
3
```
5: (4.36)
```
The step size α is selected to ensure a sufficient decrease of a merit function using a “step to
the boundary” rule with τe0:99, that is, for α 2 0, αð ,
x kþ1 ¼ xk þ α d x
xk þ α d x  1  τð Þx k > 0
vkþ1 ¼ v k þ α d v  1  τð Þv k > 0
λkþ1 ¼ λk þ α λþ  λkð Þ:
```
(4.37)
```
```
f (x) aln x
```
As a0
Optimal solution
x0
Figure 4.2 Barrier function for
the interior-point method.
4.3 Interior-Point Method 39
```
The above is essentially the basis of the codes IPOPT (Wächter and Biegler, 2006) and
```
```
KNITRO (Byrd et al., 2006), both of which implement the interior-point method for solving
```
NLP problems.
4.4 Comparison of NLP Algorithms
Based on the methods covered in this chapter, we briefly discuss the software available for
```
these methods (see Appendix A), and their relative advantages and limitations.
```
SNOPT is a representative code implementing the successive-quadratic programming
```
(SQP) algorithm. This method tends to be best for handling nonlinearities, and tends to
```
require relatively few iterations. We should note that special implementations that are based
```
on eliminating equations allow for solving large-scale problems (Biegler, 2010).
```
MINOS and CONOPT are representative codes for the reduced-gradient method. These
codes tend to perform best for mostly linear constraints. Although they tend to require more
iterations than the SQP method, the advantage is the implementation of the subproblems of the
inner iterations that apply “LP Simplex methodology” given the linearity of the constraints. In
```
fact, we should note that for the limiting case when problem (4.1) has linear objective function
```
and constraints, which leads to an LP, MINOS reduces to the Simplex algorithm.
CONOPT is slower than MINOS but it is more robust as it tries to recover feasibility at
each iteration.
IPOPT and KNITRO are representative codes of the interior-point method for NLP.
These codes require relatively few iterations, but computational benefits are only realized
with large-scale problems because in smaller problems the heavy overhead with the linear
algebra at each iteration makes the performance of these methods slower.
4.5 Guidelines for Formulating NLP Models
To close this chapter, we briefly review some general guidelines for formulations of “good”
```
NLP models as in the problem in (4.38) below, in which we assume that the objective and
```
constraints are written in equation form,
min f xð Þ
```
s:t: h xð Þ ¼ 0
```
g xð Þ  0
x 2 R n:
```
(4.38)
```
Some major guidelines are the following.
```
(1) It is important to try to specify lower, upper bounds on all variables
```
```
xL  x  x U (4.39)
```
as this leads to more constrained feasible regions, which in turn helps to obtain better
starting points and make the solution of the NLP more robust.
40 4 Nonlinear Programming Algorithms
```
(2) It is important to try to formulate whenever possible all the constraints as linear
```
constraints, as this obviously helps all the methods, especially reduced-gradient
methods. As a simple example, it is always better to reformulate the nonlinear inequality
x1
```
x2 2 (4.40)
```
as the linear equality
```
x1  2x2  0: (4.41)
```
```
(3) Elimination of variables only pays off if the nonlinearities do not increase much in
```
constraints, or even better if they can be transferred into the objective function.
Consider as an example the NLP:
min x1 þ 2x2
```
s:t: x1x2 ¼ 2
```
0  x1  2
0  x2  2:
```
(4.42)
```
If we eliminate from the equality constraint, x2 ¼ 2=x1 then from the lower bound
```
x2  2 ) 2x1  0 ) x1 < ∞, while from the upper bound x2  2 ) 2x1  2 ) x1  1.
```
This then leads to the reformulated NLP,
min x1 þ 4x
1
```
s:t: 1  x1  2,
```
```
(4.43)
```
```
which is smaller in size (reduced by one dimension), and with a convex nonlinearity only
```
```
in the objective function. Therefore, (4.43) is a desirable formulation.
```
Consider the second example:
min x1 þ 2x2 þ 3x3
```
s:t: e x1 x2 þ x3ð Þ ¼ 10
```
1  x1  2
0:5  x2  2
0:5  x3  2:
```
(4.44)
```
If we eliminate x1 , this leads to x1 ¼ ℓn 10x2þx3ð Þ2
h i
```
. If we then substitute x1 , in (4.44) this
```
```
leads to the reformulated NLP (4.45),
```
min ℓn 10
x2 þ x3ð Þ2
" #
þ 2x2 þ x3
```
s:t: e x2 þ x3ð Þ2  10
```
 e2 x2 þ x3ð Þ2  10
0:5  x2  2
0:5  x3  2,
```
(4.45)
```
4.5 Guidelines for Formulating NLP Models 41
```
which in fact introduces more nonlinearities than in (4.44) making the problem poten-
```
tially more difficult to solve. This clearly shows that variable elimination is not always
advisable in NLP models.
```
(4) It is important to try to scale the variables and constraints. For instance, if we have the
```
bounded variables,
0  x1  1 0  x2  10 000,
we can define a new variable z2 ¼ x210 000 so that the bounds become
0  x1  1 0  z2  1:
```
(5) The last guideline is given because Newton’s method requires an initial guess within a
```
neighborhood of the solution. This means one should try to supply “good” initial
guesses, which of course is often not trivial!
EXERCISES
```
4.1 Given the problem (3.5) in Chapter 3:
```
min f xð Þ ¼ x1  3ð Þ2 þ x2  4ð Þ2
```
s:t: 2x1 þ x2  6  0
```
x1  x2  4  0
x1  1:8
x2  0,
verify its solution with GAMS/MINOS, GAMS/CONOPT, GAMS/SNOPT,
GAMS/KNITRO, GAMS/IPOPT.
4.2 Assume we would like to solve the following NLP:
min maxj2J f j xð Þ
n o
```
s:t: g xð Þ  0
```
x 2 R n:
What difficulty will arise when trying to find a point that satisfies the Karush–Kuhn–
Tucker conditions in the above problem? Can you reformulate the problem to avoid this
difficulty?
```
4.3 (a) Show that for the linearly constrained NLP problem
```
min f xð Þ
```
s:t: Ax ¼ b A m  n matrix, m < n full rankð Þ
```
x 2 R n
the quadratic program in the SQP algorithm reduces to
42 4 Nonlinear Programming Algorithms
min rf x i
 T
d þ 12 d T rxx f xi
 
d
```
s:t: Ax i þ Ad  b ¼ 0:
```
```
(b) Assume that at a feasible point x i the above quadratic program is solved. Determine
```
if the predicted step above is identical to the one predicted by the reduced-
gradient method.
4.4 Assume you apply the SQP algorithm to the quadratic programming problem:
min Z ¼ c T x þ 12 x T B x
```
s:t: Ax  b
```
x  0,
where B is a positive definite matrix. Determine under what assumptions the SQP
algorithm will converge in one iteration and explain why.
4.5 Consider the design of a storage vessel that has the form of a cylinder. The required
volume is 25 m3 . The cost of the side of the cylinder is $150=m2 , while the top and
bottom cost $190=m 2 and $260=m2 , respectively. Formulate an NLP problem to deter-
mine the optimal dimensions of this vessel, and solve with GAMS/MINOS, GAMS/
CONOPT and GAMS/SNOPT.
4.6 Consider the nonlinear programming problem:
max Z ¼ f xð Þ
```
s:t: hj xð Þ  0 j ¼ 1, . . . , m
```
xL  x  x U :
Assuming that f xð Þ and h xð Þ are continuous and differentiable in the n-dimensional
vector x, derive the Karush–Kuhn–Tucker conditions for the above problem.
4.7 Given are the two following optimization problems:
```
P1 : min Z1 ¼ f xð Þ
```
```
s:t: g xð Þ  0
```
h xð Þ  0
x 2 R n
```
P2 : min Z2 ¼ f xð Þ
```
```
s:t: g xð Þ þ h xð Þ  0
```
x 2 R n:
```
(a) Show that the optimal objective function values of the above problems obey the
```
following inequality:
Z1
 ∗
 Z2
 ∗
:
```
(b) Does the above inequality rely on the assumption that the functions g xð Þ and h xð Þ
```
are convex?
Exercises 43
5 Linear Programming
5.1 Basic Theory
```
Linear programming (LP) models are among the most extensively used models in optimiza-
```
```
tion (Saigal, 1995; Vanderbei, 2020). These are defined by the optimization of a linear
```
objective function, subject to linear constraints and nonnegativity conditions on the continu-
ous variables x. Specifically, LP models are given by the following formulation, which
assumes minimization of the objective Z,
min Z ¼ c T x
```
s:t: Ax ¼ b
```
x  0,
```
(LP)
```
where x is an n-vector, A is an m  n matrix, c is the n-vector of cost coefficients, and the
right-hand side b is an m-vector. Notice that m < n, which means there are nonzero degrees
of freedom, assuming that the constraints are independent.
```
We should note the following about problem (LP).
```
```
(1) Inequality constraints can be transformed into equalities with slack variables. For
```
instance x1 þ x2  2 can be converted into an equality by adding the slack variable
x3  0, which leads to the equation x1 þ x2 þ x3 ¼ 2.
```
(2) Problem (LP) is a convex programming problem, and therefore it has a unique
```
optimum solution.
```
(3) Problem (LP) is solvable in polynomial time (Karmarkar, 1984).
```
```
The two major methods for solving problem (LP) are: (a) the Simplex algorithm
```
```
(Kantorovich, 1948; Dantzig, 1949, 1963) and (b) interior-point method (Karmarkar,
```
```
1984). Theoretically, the Simplex algorithm has exponential complexity, while the interior-
```
point method has polynomial complexity. As we will see, the Simplex algorithm is
closely related to the reduced-gradient method for NLP, while the interior-point method is
also closely related to the interior-point methods for NLP. The major software packages for
LP, CPLEX, XPRESS, and GUROBI implement both methods. Generally, the Simplex
algorithm is computationally more efficient for solving problems with several thousand
variables and constraints, while interior-point methods perform best in very large-scale
problems.
In order to describe the Simplex algorithm, we first present some basic definitions and
theoretical properties.
44
Definition 5.1 The feasible region F ¼ xjAx ¼ b, x  0f g is defined by a polyhedron that is a
closed convex region.
Since the objective function is linear and the feasible region is a polyhedron, the Simplex
algorithm exploits the fact that the optimum lies at a vertex or extreme point, as seen in
Fig. 5.1.
Definition 5.2 x 2 F is an extreme point if and only if for x such that,
x ¼ αx1 þ 1  αð Þx2 , α 2 0, 1ð Þ, x1 , x2 2 F , then x1 ¼ x2:
In other words, an extreme point cannot be obtained by a linear combination of different
points x1 6 ¼ x2 in F.
Consider partitioning the matrix of coefficients A ¼ BjN½ , where the m  m basis matrix
B is of full rank, and where N is the m  n  mð Þ matrix. Consider also partitioning the
vector of variables x
x ¼ xBxN
 
```
, (5.1)
```
where x B is an m-vector of basic variables, and xN is an n – m-vector of nonbasic variables.
```
We can then express the linear constraints of problem (LP) as:
```
```
Ax ¼ Bx B þ Nx N ¼ b: (5.2)
```
If we set the nonbasic variables x N ¼ 0, this then implies that the basic variables can be
computed as follows,
```
xB ¼ B1b, (5.3)
```
where B1 is assumed to exist as the basis B is assumed to be full rank.
```
As shown by the following theorem, the nonnegative basic variables computed from (5.3)
```
and zero nonbasic variables define an extreme point in the feasible region of the LP.
```
Theorem 5.1 A point x in (LP) is an extreme point of its corresponding feasible region F if and
```
only if x B ¼ B1b, x B  0, x N ¼ 0.
Proof Assume x is not an extreme point in F . This implies that x can be obtained as a linear
combination of two distinct points x1 , x2 , that is,
x2
x1
Optimum
Figure 5.1 Optimal solution of an
LP lies at a vertex point of the
feasible region.
5.1 Basic Theory 45
```
x ¼ αx1 þ 1  αð Þx2 , α 2 0, 1ð Þ, x1 , x2 2 F , x1 6 ¼ x2: (5.4)
```
This implies for xN ¼ 0 ¼ αx1N þ 1  αð Þx2N . However, since xN1 , x N2  0 and α 2 0, 1ð Þ, this
in turn implies x1N ¼ x2N ¼ 0, which contradicts the assumption that x N is not an extreme
point. Hence, x N ¼ 0 is an extreme point.
Consider now the basic variables, x B ¼ B1b ¼ αx1B þ 1  αð Þx2B . Since x B ¼ B1b  0, is a
unique solution and α 2 0, 1ð Þ, this implies x B ¼ x1B ¼ x2B, which contradicts the assumption
that xB is not an extreme point. Hence, x B ¼ B1b, x B  0 is an extreme point. ∎
Based on Theorem 5.1, we can prove the following theorem.
```
Theorem 5.2 The optimal solution x∗ of (LP) lies at an extreme point of F .
```
Proof Assume that x∗ is not an extreme point. It then follows that x∗ can be expressed as a
linear combination of extreme points, that is, x∗ ¼ Pi αi xi, where x i is an extreme point in F
and αi  0, Pi αi ¼ 1. If we multiply x∗ by c T , we obtain
c T x∗ ¼
X
i
```
αi cT x i: (5.5)
```
But since by assumption x∗ is the optimal solution, we have c T x∗ < c T xi, 8i. If we multiply
this inequality by αi and take the corresponding sum over αi  0, this leads to
c T x∗ < Pi αi c T x i, which contradicts the assumption that x∗ is not an extreme point.
```
Hence, the optimal solution x∗ of problem (LP) lies at an extreme point of F. ∎
```
```
We should note that the optimal solution of problem (LP) is a global optimum because the
```
objective function and the feasible region are convex. However, the global optimum may not be
unique, as shown in Fig. 5.2 in which we present two alternate optima that have the same
objective value.
The next important question that we need to address is to see how we can identify an
extreme point in F as being an optimal solution. For this let us eliminate x B from problem
```
(LP) for a feasible basis; that is, from Bx B þ Nx N ¼ b, we obtain
```
```
x B ¼ B1N, x N ¼ B1b  0: (5.6)
```
```
If we substitute x B in the objective function of the problem (LP) expressed in terms of basic
```
```
and nonbasic variables, Z ¼ c B T x B þ c N T x N , we can define a reduced (LP0) in terms of the
```
nonbasic variables x N ,
x2
Alternate optima
x1
Figure 5.2 Alternate optima in
an LP.
46 5 Linear Programming
min Z ¼ c TB B1N  c TN
 
x N þ c TB B1b
```
s:t:  x N  0:
```
```
(LP0 )
```
```
Comparing with Eq. (4.28) in Chapter 4 (the term ry f T B1C þ ru f T ), the coefficient for
```
xN can be interpreted as the reduced gradient g R T ¼  c TB B1N  c TN
 
. We can then estab-
lish the following theorem.
```
Theorem 5.3 A necessary and sufficient condition for x∗ to be an optimum of (LP0) is given by
```
the inequality c TB B1N  c TN  0T , which is equivalent to stating that g R T  0T .
```
Proof From the Karush–Kuhn–Tucker conditions (3.31)–(3.33) (see Chapter 3), and
```
defining ρ as the multiplier for the nonnegativity of x N , a necessary and sufficient condition
```
for (LP0) is given by,
```
c TB B1N þ c TN  ρT ¼ 0T
ρ  0,  x N  0, ρT xN ¼ 0:
```
(5.7)
```
This implies c TB B1N  c TN ¼ ρT . But because ρ  0 this implies c TB B1N  c TN  0T , which
proves the theorem. ∎
We should note that the multiplier ρ can be interpreted as the vector of reduced costs.
5.2 Simplex Algorithm
Given Theorems 5.1–5.3 in the previous section, we have all the elements required to derive
the Simplex algorithm. Qualitatively what we need to do is to select the “correct” basis that
defines the optimal extreme point. Since we cannot do this easily a-priori, we will develop an
iterative “exchange” algorithm for generating alternative bases. The exchanges are based on
the two following operations.
```
(a) Make one of the nonbasic variables a basic variable.
```
```
(b) Make one of the basic variables a nonbasic variable.
```
The generation of bases continues until the optimality condition given by Theorem 5.3 is
satisfied, namely, c TB B1N  c TN  0T , or equivalently until all the reduced costs ρ are
positive. The specific criteria that are used for the exchanges for deciding which nonbasic
variable should enter the basis and which basic variable should leave it are as follows.
```
(a) Which variable should enter the basis?
```
```
Assume x is a nonoptimal extreme point; then there exists at least one nonbasic
```
variable x N j such that
```
c TB B1nj  c N j > 0, (5.8)
```
where nj is the jth column of the submatrix N. Since there might be several nonbasic
```
variables that satisfy (5.8), as a heuristic we select those with the largest positive left-hand
```
5.2 Simplex Algorithm 47
```
side (LHS) in (5.8) to enter the basis. Geometrically this can be interpreted as selecting the
```
nonbasic variable with the steepest descent, as shown in Fig. 5.3.
```
(b) Which variable should leave the basis?
```
The main concern here is to ensure feasibility when making the choice on which variable
should leave the basis. For this, let us consider the current basis, which can be represented as
```
follows:
```
```
Bx B þ NxN ¼ b: (5.9)
```
Premultiplying by B1 leads to
```
Ix B þ B1Nx N ¼ B1b, (5.10)
```
which we rewrite as
```
Ix B þ Yx N ¼ b, (5.11)
```
```
where Y ¼ B1N and b ¼ B1b. From (5.10) for each basic variable xB i we have
```
x B i þ
X
k
```
yik x Nk ¼ bi i ¼ 1, . . . , m: (5.12)
```
Assume the nonbasic variable x N j enters the basis. Since we want xN j  0 and x B i  0 8i to
```
ensure feasibility, from (5.12) we obtain
```
```
xB i ¼ bi  yij x N j  0 8i (5.13)
```
from which it follows that
```
x N j  bi=yij 8i: (5.14)
```
```
To ensure that (5.14) is satisfied for all i, we pick the rth basic variable with the smallest
```
```
positive right-hand side (RHS), that is,
```
cT x
xN
Figure 5.3 Selection of nonbasic
variable with steepest descent.
48 5 Linear Programming
αrj ¼ minibi=yij
n o
```
for bi=yij > 0, (5.15)
```
which is known as the min test ratio.
```
With the two exchange rules given by the largest LHS in (5.8) and by (5.15), we have the
```
required criteria for generating a new basis when the current one is found not to be optimal,
that is, not satisfying the conditions in Theorem 5.3.
To derive the Simplex algorithm from the objective function and constraints expressed as
Z  c TB x B  c TN xN ¼ 0
Bx B þ Nx N ¼ b,
```
(5.16)
```
```
we represent (5.16) through the following Simplex tableau in which we explicitly display the
```
objective Z, the basic and nonbasic variables x B, x N , and the RHS,
Z xTB x TN RHS

1 c TB c TN 0
0 B N b
objectiveð Þ
constraint rowsð Þ:
```
(T)
```
In order to update the tableau we multiply the constraint rows by B1 , multiplied by c TB , and
we add them to the objective row, which is equivalent to a pivoting operation,
Z xTB xTN RHS

1 0 c TB B1N  c TN c TB b
0 1 B1N b:
```
(5.17)
```
```
From the tableau (5.17), because the nonbasic variables x N are zero at an extreme point, we can
```
```
directly read the value of the basic variables x B ¼ B1b as in (5.3). Furthermore, the coefficients
```
of the nonbasic variables in the objective function c TB B1N  c TN correspond to the negative of
the reduced gradient g R T . From Theorem 5.3 we can then check if c TB B1N  c TN  0T . If that
```
is the case, we have found the optimal solution of the LP with the current basis; otherwise, we
```
know that the current basis is not optimal, and we need to find a new one using the exchange
```
rules described above. In summary, starting from the tableau (T) we perform successive updates
```
```
through pivoting operations until the optimality conditions in (5.17) are satisfied.
```
To complete the description of the Simplex algorithm, we need to determine how we select
the initial basis. The simplest case is when the constraints of the LP are only inequalities,
A0x  b, with the RHS b  0. In this case, by introducing slack variables s  0, we can
rearrange the LP as follows:
min Z ¼ c T x
```
s:t: A0x þ Is ¼ b
```
x  0 s  0:
```
(5.18)
```
5.2 Simplex Algorithm 49
Because x ¼ 0 is a feasible point, the initial basis can simply be chosen as the identity matrix
corresponding to the slack variables s, which are the initial basic variables, while the x
variables are the initial nonbasic variables.
```
Because (5.18) is a special case, we need a more general procedure for problem (LP). We
```
assume that the constraints are rearranged as follows: A00x ¼ b, b  0. We then introduce
nonnegative artificial variables q and reformulate the LP as follows:
min Z ¼ c T x þ Mq
```
s:t: A00x þ Iq ¼ b
```
x  0 q  0,
```
(5.19)
```
where M > 0 is a large parameter. The initial basis can then be selected by choosing
the variables q to be basic variables with the corresponding identity matrix for the basis.
An alternative approach is to use a two-phase procedure where in phase I we solve for
```
Z ¼ min e T q (i.e., feasibility problem) until we find a feasible point q ¼ 0ð Þ; next in phase
```
II we optimize the original objective Z ¼ c T x.
```
In summary, the basic steps of the Simplex algorithm for solving the problem (LP) are
```
as follows.
```
Step 1 Select initial basis B ¼ I , set N ¼ A0 or A00(from (5.18) or (5.19)), and partition:
```
x ¼ xBxN
 
, c ¼ c Bc N
 
:
Step 2 Define Simplex tableau.
Z x TB x TN RHS
1 c B c TB B1N  c T 1ð ÞN c TB b 1ð Þ Objective row
I B1N 2ð Þ b Constraint rows
```
(1) At first iteration cB ¼ 0 for (5.18); (2) matrix N has columns nk and elements nij .
```
Step 3
```
(a) If c TB B1nk  c N k  0 for all nonbasic variables k STOP. Otherwise select variable x N j
```
with largest c TB B1nj  c N j > 0 to enter basis.
```
(b) To decide which basic variable leaves basis, compute b i=n ij , i ¼ 1, . . . , m and select row r
```
```
with smallest positive value (min test ratio).
```
Step 4
```
(a) Select element n and pivot on matrix I B1N b
```
 
to make their coefficient 1 and with
zero columns for n ij i 6 ¼ r, i ¼ 1, . . . , m.
```
(b) Add to objective row the new rth row multiplied by coefficient c j (cost coefficient of
```
```
variable j entering basis).
```
```
(c) Return to step 2 and continue until step 3a is satisfied.
```
50 5 Linear Programming
5.3 Numerical Example
Consider the following LP:
min Z ¼ x1  3x2
```
s:t: x1 þ x2  4
```
x1 þ 2x2  6
x1 , x2  0,
```
(5.20)
```
```
which has the simpler structure of only inequalities and a positive RHS (see (5.18)). To
```
convert the inequalities into equalities we introduce the slack variables, x3 , x4 , which then
yield the LP
min Z ¼ x1  3x2
```
s:t: x1 þ x2 þ x3 ¼ 4
```
x1 þ 2x2 þ x4 ¼ 6
x1 , x2  0 x3 , x4  0:
```
(5.21)
```
```
The feasible region of the LP in (5.20) is displayed in Fig. 5.4. Note that the slack variables x3 , x4
```
indicate the deviation from the boundary of the two corresponding inequalities.
The tableau at iteration 1 is shown below.
Z x1 x2 x3 x4 RHS
R1 basis 1 1 3 0 0 0
R2 x3 1 1 1 0 4
R3 x4 1 2 0 1 6
From this tableau we can infer that the objective Z ¼ 0, the basic variables x3 ¼ 4, x4 ¼ 6,
and the nonbasic variables x1 ¼ x2 ¼ 0. Because the coefficients of these variables are
positive 1, 3½  > 0, 0½  the corresponding extreme point is nonoptimal. Because 3 is the larger
value, we select x2 as the variable that enters the basis. We then perform the min test ratio.
For R2 we obtain 4=1 ¼ 4, while for R3 we obtain 6=2 ¼ 3. As the latter is smaller, we select
x4 as the variable that leaves the basis.
0 0Z 
1 9Z
x2
x1
 
4
4
Figure 5.4 Feasible region for
example problem.
5.3 Numerical Example 51
We next perform the pivoting operations shown in the left of the table below where they
are applied in the order R3/2, R2  R3/2, R1  3R3/2.
Z x1 x2 x3 x4 RHS
R1  3R3=2 basis 1  12 0 0  32 9
R2  R3=2 x3 12 0 1  12 1
```
R3=2 x2 12 1 0 12 3
```
Note that the basis is defined by x2 , x3 with its corresponding identity matrix for the basis.
From this table we can then determine that the basic variables x2 ¼ 3, x3 ¼ 1 and Z ¼ 9.
Since the coefficients of cB T B1N  c N T ¼ 1=2 ,  3
 =
2 < 0, 0½ , we can assert that the
extreme point x1 ¼ 0, x2 ¼ 3, x3 ¼ 1, x4 ¼ 0, corresponds to the optimal solution of the
```
LP in (5.20), and hence we can stop the search.
```
EXERCISES
5.1 Given is the linear programming problem
min Z ¼ c T x
```
s:t: Ax ¼ b
```
x  0,
where A is an m  n matrix with rank m. Show that, for a feasible selection of the basis
B, the Lagrange multipliers λ of the equations are given by
λ ¼  B T
 1
c B,
where c B is the cost coefficient of the basic variables.
5.2 Given is the following linear programming problem:
min Z ¼ 2x1  3x2
```
s:t: x1 þ x2  4
```
x1 þ 2x2  6
x1  0, x2  0:
```
(a) Plot the contours of the objective and the feasible region. Determine the optimum
```
by inspection.
```
(b) Solve the problem using the Simplex algorithm.
```
52 5 Linear Programming
6 Mixed-Integer Programming Models
```
The most general mixed-integer problems, a generalization of nonlinear programs (NLP),
```
```
are given by mixed-integer nonlinear programs (MINLP) (Lee and Leyffer, 2012;
```
```
Trespalacios and Grossmann, 2014) involving continuous and integer variables, x, y,
```
```
min Z ¼ f x; yð Þ
```
```
s:t: h x; yð Þ ¼ 0
```
```
g x; yð Þ  0
```
x 2 Rn y 2 0, 1f gm:
```
(MINLP)
```
The most general MINLP has in fact the y variables being specified as integer variables
y 2 Z mþ. However, we restrict ourselves to 0-1 variables for two reasons. First, the 0-1
variables tend to be the most common ones arising in applications. Second, an integer
variable or even an arbitrary discrete variable can always be expressed in terms of
0-1 variables.
```
A case of special interest is the mixed-integer linear program (MILP) (Nemhauser and
```
```
Wolsey, 1988; Wolsey, 1998) given by linear objective function and constraints,
```
min Z ¼ aT x þ bT y
```
s:t: Ax þ By  d
```
x  0 y 2 0, 1f gm:
```
(MILP)
```
If there are no y variables, the MILP reduces to an LP. If there are no x variables, the MILP
reduces to a pure integer program IP.
6.1 Modeling with 0-1 Variables
6.1.1 Motivating Examples
In this section we first introduce three motivating examples of constraints in terms of 0-1
variables to emphasize the point that while the constraints can intuitively be expressed as
```
nonlinear constraints, they can also be written as linear constraints (Williams, 1999).
```
Let
y j ¼ 1 if j true0 if j false:

```
(6.1)
```
53
```
First, consider the case where at most one yj is true (i.e., yj ¼ 1), for simplicity say y1 , y2 . If
```
```
we express this constraint in nonlinear form it is given by (6.2),
```
```
y1y2 ¼ 0: (6.2)
```
However, we can also express this constraint with a linear inequality
```
y1 þ y2  1: (6.3)
```
```
As shown in Fig. 6.1, the relaxation of constraint in (6.2) with y1  0, y2  0 defines a
```
```
nonconvex feasible region (a), while the relaxation of constraint (6.3) with y1  0, y2  0 gives
```
```
rise to a convex feasible region (b). Therefore, although constraint (6.2) is valid in the sense that
```
it represents the condition stated, its mathematical properties are less desirable than the linear
```
constraint in (6.3).
```
As a second case, consider the variable y ¼ 0, 1. A valid nonlinear constraint to represent
this binary variable as continuous, is the nonlinear inequality with the 0-1 bounds on y,
```
y 1  yð Þ  0 0  y  1: (6.4)
```
```
While (6.4) avoids the use of 0-1 variables, the drawback is that it is nonconvex. This can be
```
```
seen by rearranging (6.4) as
```
```
y  y2  0, (6.5)
```
where it is clear that y2 is a concave function.
```
Finally, as a third case, assume we want to represent the condition if y ¼ 1 ) h xð Þ ¼ 0.
```
A simple nonlinear constraint representing this condition, which is nonconvex, is given by
```
yh xð Þ ¼ 0, (6.6)
```
where it can clearly be seen that h xð Þ ¼ 0 if y ¼ 1, while the constraint holds for y ¼ 0 for
any h xð Þ.
```
One can also reformulate the constraint in (6.6) through the “big-M” inequalities which
```
are linear in the binary variable y, where M is a sufficiently large parameter,
10
1
y2
```
(a)
```
```
(b)
```
y1
```
Figure 6.1 Relaxations of (a)
```
```
constraint (6.2) and (b) constraint
```
```
(6.3).
```
54 6 Mixed-Integer Programming Models
```
M 1  yð Þ  h xð Þ  M 1  yð Þ: (6.7)
```
```
Notice that if y ¼ 1, (6.7) reduces to h xð Þ ¼ 0, because 0  h xð Þ  0, while for y ¼ 0 (6.7)
```
reduces to the inequality M  h xð Þ  M, which is redundant for sufficiently large M. In
practice, however, one should not select a very large value of M as it adversely affects the
continuous relaxation of the mixed-integer programming problem.
The three examples, then, show that while nonlinear inequalities may represent 0-1
conditions, they have the undesirable property of being nonconvex, which would necessitate
```
global-optimization methods (see Chapter 12). The main message from these examples is
```
that one should always try to model 0-1 variables y so that they appear linearly in the mixed-
integer programming model. Otherwise, expressing them in nonlinear form usually leads
to nonconvexities.
6.1.2 Modeling with Linear 0-1 Variables yj
In this section we present several major classes of constraints and functions that can be
```
expressed with linear 0-1 variables (Nemhauser and Wolsey, 1988; Williams, 1999).
```
```
(I) Multiple-choice constraints
```
As implied by the term characterizing these constraints, these deal with choices of
values for the binary variables.
```
(a) Select at least one
```
X
j2J
```
yj  1: (6.8)
```
```
(b) Select exactly one
```
X
j2J
```
yj ¼ 1: (6.9)
```
```
(c) Select not more than one
```
X
j2J
```
yj  1: (6.10)
```
```
As we will see later (Section 7.1 in Chapter 7), (a) can be interpreted as an
```
```
inclusive OR, (b) as an exclusive OR, and (c) is often denoted as a knapsack
```
constraint. We should also note that the logic operator AND defines imposing
```
several constraints. For instance, consider: (select 1 or 2) AND (select 3 or 4). This
```
```
logic statement can be translated as the two following inequalities (see Section 7.1
```
```
for more details):
```
y1 þ y2  1
```
y3 þ y4  1: (6.11)
```
6.1 Modeling with 0-1 Variables 55
```
(II) If then condition
```
```
Assume we state the condition “If select yk then select yj ” yk ) yj
```
 
, this condition can
be written as the linear inequality
```
y k  yj  0: (6.12)
```
This can be easily verified as follows:
```
if yk ¼ 1 ) yj ¼ 1; if yk ¼ 0 ) yj ¼ 0 or 1.
```
```
We should note that the condition iff (if and only if ) can be expressed as the equality
```
```
yk ¼ yj : (6.13)
```
```
(III) Disjunction
```
Consider the disjunctive constraint f 1 xð Þ  0 or f 2 xð Þ  0, meaning either f 1 or f 2 must
```
be satisfied (i.e., less than or equal to zero). This disjunction can be expressed with the two
```
following constraints that are linear in y and where M is a sufficiently large parameter:
f 1 xð Þ  M 1  y1ð Þ
f 2 xð Þ  M 1  y2ð Þ
y1 þ y2 ¼ 1:
```
(6.14)
```
```
We can easily verify from (6.14) that if y1 ¼ 1 then y2 ¼ 0 and we have f 1 xð Þ  0,
```
f 2 xð Þ  M, while if we have y1 ¼ 0 then y2 ¼ 1 and we have f 2 xð Þ  M, f 2 xð Þ  0.
Later in Section 7.2 in Chapter 7 we will study in more detail the topic of disjunctive
programming where more general forms of disjunctions are considered.
```
(IV) Discontinuous domains and functions
```
A prime example for this case is the fixed-charge cost model, which is widely used in
optimization planning models
C ¼ α þ βx L  x  U0 x ¼ 0,

```
(6.15)
```
and which is displayed in Fig. 6.2. The basic idea is that we have a discontinuous
domain given by x ¼ 0 and L  x  U. Furthermore, when x ¼ 0 the cost C ¼ 0,
while for L  x  U the cost is defined by the linear function α þ βx, where α repre-
sents the fixed cost while β is the variable-cost coefficient.
C
x
L U
a
Figure 6.2 Fixed-cost function.
56 6 Mixed-Integer Programming Models
```
The fixed-cost function in (6.15) can be represented with linear 0-1 variables by
```
C ¼ αy þ βx
Ly  x  Uy
x  0, y ¼ 0, 1:
```
(6.16)
```
We can verify that if y ¼ 0 then x ¼ 0 and C ¼ 0, while if y ¼ 1 then L  x  U and
C ¼ α þ βx. We should note that usually L ¼ 0 with which the domain of x becomes
continuous.
6.1.3 Some Common IP Problems
In this section we present some classic integer programming models to again illustrate the
```
use of linear 0-1 variables (Nemhauser and Wolsey, 1988; Conforti et al., 2014).
```
6.1.3.1 Assignment Problem
This problem can be stated as follows. Given is a set of n jobs i and given is a set of n
```
machines j (see Fig. 6.3). Also given is the cost c ij for assigning job i to machine j. The
```
problem then consists of finding the minimum cost assignment of the jobs to the machines.
To formulate the corresponding optimization problem we introduce the binary variables
yij such that y ij ¼ 1 if job i is assigned to machine j at cost c ij , and yij ¼ 0 otherwise. The
assignment problem can then be formulated as the following integer programming problem,
min Z ¼
Xn
i¼1
Xn
j¼1
c ij y ij
```
s:t:
```
Xn
j¼1
yij ¼ 1 i ¼ 1, . . . , n
Xn
i¼1
y ij ¼ 1 j ¼ 1, . . . , n
yij ¼ 0, 1:
```
(AP)
```
```
In (AP) we minimize the assignment cost subject to the constraints that for every job i only
```
one machine j can be assigned, and for every machine j only one job i can be assigned. These
assignment constraints represent exclusive OR statements.
```
An interesting property of problem (AP) is that it can be solved as an LP with continuous
```
variables yij , such that 0  yij  1. The reason is that all the extreme points of the polytope
jobs machines
0 0
0 0
0 0
n nFigure 6.3 Assignment of n jobs
to n machines.
6.1 Modeling with 0-1 Variables 57
defined by assignment constraints correspond to 0-1 values for the continuous variables y i.
In general, IPs that have this property are said to have a totally unimodular matrix
```
(Nemhauser and Wolsey, 1988).
```
6.1.3.2 Plant Location Problem
```
Consider n potential plants that are to serve m customers j with demands d j (see Fig. 6.4).
```
Each plant i has a fixed cost f i. Also, the combined transportation and manufacturing cost
from a plant i to customer j is given by the cost c ij . The problem then consists of selecting the
plants that serve the customers so as to satisfy the demands at minimum total cost.
If we denote by yi the 0-1 variables for selecting each plant i, and by x ij the amount of
material sent from plant i to customer j, the MILP problem can be formulated as follows:
min Z ¼
Xn
i¼1
f i yi þ
Xn
i¼1
Xm
j¼1
c ij xij
```
s:t:
```
Xn
i¼1
x ij ¼ d j j ¼ 1, . . . , m
Xn
j¼1
x ij  U i yi  0 i ¼ 1, . . . , n
yi ¼ 0, 1 x ij  0,
```
(PL)
```
```
where U i represents the maximum capacity of plant i. In problem (PL) the objective function
```
includes the fixed costs of the selected plants and their corresponding manufacturing/
transportation costs. The first equality states that for each customer j the amounts xij sent
by all the plants i have to satisfy the corresponding demands d j . The second inequality states
that the amount of material sent from each plant i to all the markets cannot exceed the
```
maximum capacity U i. In contrast to the assignment problem (AP), problem (PL) is known
```
```
to be NP-hard (Cornuéjols et al., 1990), meaning that in the worst case the computational
```
time scales exponentially with the problem size of the MILP.
6.1.3.3 Knapsack Problem
The knapsack is another classical combinatorial problem. It assumes that we are given n
objects i 2 Ið Þ of given weight w i and price pi. We are also given a knapsack that can hold a
```
maximum weight W of objects (see Fig. 6.5). The problem then consists of selecting those
```
objects that can be accommodated in the knapsack and that maximize their value.
yi x
ij
n plants
0
0
0 0
0
0
m customersFigure 6.4 Plant location
problem.
58 6 Mixed-Integer Programming Models
```
This problem can be formulated as the pure 0-1 integer programming problem (KP) by
```
defining the binary variable yi , where yi ¼ 1 if object i is selected and yi ¼ 0 otherwise:
max Z ¼
Xn
i¼1
pi yi
```
s:t:
```
Xn
i¼1
w i y i  W
y i ¼ 0, 1 i ¼ 1, . . . , n:
```
(KP)
```
```
In (KP) the objective corresponds to maximizing the value of the selected objects, while the
```
inequality limits the weights of the selected objects not to exceed the maximum weight W .
```
Despite its apparent simplicity, (KP) is NP-hard (Nemhauser and Wolsey, 1988).
```
6.1.3.4 Set-Covering Problem
The set covering is another classical combinatorial problem. We will state it here in terms of a
```
computer search problem (see Fig. 6.6) (Nemhauser and Wolsey, 1988). Assume that we are
```
given n computer files containing units of information i, which are represented by the set that
indicates the location of the unit of information i in file j, P i ¼ ijunit i is in file jf g.
```
Furthermore, assume that the size of each file j is given by c j (e.g., in megabytes) . The
```
problem then consists of deciding which files to open for reading so as to retrieve the required
units of information i 2 P j and so as to minimize the total size of the files that are searched.
```
If we define the binary variable yj ¼ 1 if file j is searched, the set-covering problem (SC)
```
can be formulated as follows:
min Z ¼
Xn
j¼1
c j yj
```
s:t:
```
Xn
j¼1
a ij yj  1 i ¼ 1, . . . , m
yj ¼ 0, 1,
```
(SC)
```
files 0 0 units info. searched
length file 0 0
one or several files
n m
y j
c j
each unit is inifile jFigure 6.6 Set-covering problemfor searching m units information
in n files.
Objects i
Weights w i
Price pi
yi Knapsack
Limit weight W0
0
0
Figure 6.5 Knapsack problem.
6.1 Modeling with 0-1 Variables 59
in which we minimize in the objective function the total length of the files, subject to the
constraints that the m units of information be retrieved. In order to represent such a
constraint we define the coefficients a ij ¼ 1 if i 2 P j0 otherwise

so that each information unit i is
accessed through a file j. As an example, consider that unit of information 1 is present in files
1 and 2 but not in file 3. This then means that we set the coefficients as a11 ¼ 1, a12 ¼ 1, and
a13 ¼ 0.
6.1.3.5 Traveling Salesman Problem
```
The traveling salesman problem (TSP) is perhaps the most extensively studied integer
```
```
programming problem (Laporte, 1992). The TSP considers n cities for which the distance
```
or cost c ij is given for every pair of cities i, j i 6 ¼ jð Þ. The problem then consists of finding the
shortest or cheapest tour so that every city is visited only once. This condition is equivalent
to finding a Hamiltonian path in the network defined by the n cities and their corresponding
```
pairwise arcs (see Fig. 6.7).
```
In order to formulate this problem, we define the binary variables yij such that:
yij ¼ 1 if go from city i to city j0 otherwise:

The TSP can then be formulated as follows:
min Z ¼
Xn
i¼1
Xn
j¼1
c ij yij
```
s:t:
```
Xn
j¼1
yij ¼ 1 i ¼ 1, . . . , n
Xn
i¼1
yij ¼ 1 j ¼ 1, . . . , n
X
i2Q
X
j2 Q
yij  1 8Q  V , Q 6 ¼ ∅
y ij  0 i ¼ 1, . . . , n, j ¼ 1, . . . , n:
```
(TSP)
```
A B
C D
yijFigure 6.7 Traveling salesman
problem network for four cities
A, B, C, and D.
60 6 Mixed-Integer Programming Models
The first two constraints correspond to assignment constraints. The first constraint states
that for every city i there must be exactly one outgoing link to city j. The second constraint
states that for every city j there must be exactly one incoming link from city i. These
constraints, however, are not sufficient to guarantee a closed Hamiltonian path. For
instance, for the case of six cities A, B, C, D, E, and F, one might obtain the two subtours
shown in Fig. 6.8, which satisfy the assignment constraints. To make these infeasible, it is
necessary to add the third set of constraints, which are known as the subtour elimination
```
constraints. These constraints ensure that for every subset Q of the set of cities V (or vertices)
```
there is at least one link with its complement Q. The difficulty with this set of constraints is
that there is an exponential number of them, which makes the TSP to be NP-hard.
```
We should also note that to avoid links from city i to the same city i (self loops) one can
```
specify an infinite cost or distance, that is c ij ¼ ∞. Finally, when c ij ¼ c ji the TSP problem is
symmetric, while if c ij 6 ¼ c ji the TSP is asymmetric. Generally, the symmetric TSP is more
difficult to solve as it will tend to give rise to a larger number of subtours. For more on the
```
TSP see Laporte (1992), Cook (2012).
```
EXERCISES
6.1 Assume that in an MILP model you have an integer variable n ¼ 1, 2, . . . , 8, and that
you want to express it in terms of 0-1 variables yi. Determine the constraints that are
needed to express n as:
```
(a) a linear combination of the binary variables; and
```
```
(b) a binary expansion in terms of binary variables. Discuss the relative advantages and
```
disadvantages of both formulations.
6.2 The following inequality for 0-1 variables y ¼ 0, 1, i ¼ 1, . . . , n, in which we partition
these variables into the subsets, B, N, is known as an integer cut,
X
i2B
yi 
X
i2N
yi  Bj j  1,
because its purpose is to make infeasible the choice of the following values of the binary
variables, yi ¼ 1, i 2 B, y i ¼ 0, i 2 N, and given that Bj j is the cardinality of the set B.
Explain why the constraint for the integer cut is correct.
A
B C
D
E F
Q A,B,C Q D,E,F
Figure 6.8 Two subtours for the
six-city problem.
Exercises 61
7 Systematic Modeling of Constraints with Logic
The major goal of this chapter is to show that constraints involving 0-1 variables or general
0-1 mixed-integer constraints can be modeled systematically by applying concepts of prop-
ositional logic and disjunctive programming. This is in contrast with the models presented in
Chapter 6 that were largely formulated by inspection or intuition.
7.1 Modeling 0-1 Constraints with Propositional Logic
In this section we will show that linear 0-1 constraints can be systematically derived using logic
```
expressions for the constraints in the form of propositional logic (Raman and Grossmann, 1994;
```
```
Williams, 1999; Hooker, 2002). In particular, propositional logic deals with symbolic expres-
```
```
sions that involve the operators: OR (inclusive OR), AND, NOT (negation), and
```
```
) (implication). The operators exclusive OR and , (if and only if ) are treated as special cases.
```
To express a logic proposition, let pj be a literal representing a selection or action. We can
associate to that literal a binary variable yj such that yj ¼ 1 means that the literal is true,
while yj ¼ 0 means that it is false. Applying the basic operators to the literals pj can be
represented in terms of the binary variables as follows:
```
NOT: ¬pj by 1  yj
```
```
OR: pi∨pj by yi þ yj  1
```
```
AND: pi ^ pj by yi ¼ 1, y j ¼ 1
```
```
): pi ) pj , ¬pi∨pj by 1  yi þ yj  1 or yi  yj :
```
```
Note that the implication pi ) p j makes use of the equivalent contraposition ¬p i∨pj to
```
derive the corresponding inequality y i  y j .
```
The special cases of exclusive OR (XOR) and equivalence ,ð Þ are represented as follows:
```
XOR pi∨ pj by yi þ yj ¼ 1
EQUIVALENCE pi , pj by yi ¼ yj :
We should also note that p i∨pj , which involves literals separated by inclusive OR
operators, is known as a logic clause. A clause is a basic building block for the conjunctive
```
normal form (CNF), which is given by a conjunction of clauses, as will be discussed below.
```
In order to convert logic expressions into the CNF, which is a convenient form that can be
readily transformed into linear 0-1 inequalities, we will make use of the two following
properties from Boolean algebra.
62
```
(1) De Morgan’s Theorem
```
```
(a) ¬ A∨Bð Þ , ¬A ^ ¬B
```
```
(b) ¬ A ^ Bð Þ , ¬A∨¬B
```
```
(2) Distribution of OR
```
A ^ Bð Þ∨C , A∨Cð Þ ^ B∨Cð Þ:
```
These equivalences can be easily proved by applying Truth Tables from logic (Williams, 1999).
```
As we can see, De Morgan’s Theorem applies the negation operator ¬ inwards of expres-
sions containing the OR ∨ð Þ or AND ^ð Þ operators, while the distribution applies the OR
operators on a conjunction of A and B.
```
The CNF is formally defined as a logic expression composed by the conjunction (AND) of
```
clauses, which are composed of literals separated by the OR operator. That is, the CNF can
be expressed as follows:
Ω ¼ ^j2J ∨i2I jpi
 
```
: (7.1)
```
An example is the logic expression, p1∨¬p2ð Þ ^ ¬p1∨p3ð Þ, which consists of two clauses.
Notice that the literals may or may not be negated. From the above representation for a
clause in terms of 0-1 variables, it readily follows that the two clauses can be represented by
the two following inequalities
```
y1 þ 1  y2  1, 1  y1 þ y3  1, (7.2)
```
which can be rearranged as follows:
```
y1  y2  0,  y1 þ y3  0: (7.3)
```
Therefore, it is clear that if the logic is given as a CNF, one can readily transform it into
linear 0-1 inequalities. The problem is that arbitrary logic is usually not expressed as a
CNF. However, it turns out that one can systematically convert logic expressions in
propositional logic by using a recursive procedure developed by Clocksin and Mellish
```
(1994), and which was used in the logic program Prolog. The procedure to convert propos-
```
itional logic into a CNF consists of applying the following steps in a recursive fashion until
the CNF is reached.
```
(1) Remove implication.
```
```
(2) Move negation inwards by applying De Morgan’s Theorem.
```
```
(3) Recursively distribute OR over the AND operator.
```
Once the CNF is obtained it is easy to translate it into inequalities as shown in the
examples below.
7.1.1 Example 1 of Logic Proposition
Consider the logic statement “If select flash, then select distillation and not membrane” in a
process-synthesis problem. The logic can be expressed in symbolic form as follows:
7.1 Modeling 0-1 Constraints with Propositional Logic 63
```
pF ) ∨ pD ^ ¬pMð Þ: (7.4)
```
We apply the three steps indicated above.
```
(1) Remove the implication leads to ¬pF ∨ p D ^ ¬pMð Þ.
```
```
(2) There is no need to apply De Morgan’s Theorem, so we proceed to distribute the OR
```
over the AND, which yields, ¬pF ∨pDð Þ ^ ¬pF ∨¬p Mð Þ. This corresponds to a conjunc-
tion of two clauses, that is it is a CNF, which in turn can then be translated into the
inequalities
```
1  yF þ yD  1, 1  yF þ 1  yM  1, (7.5)
```
which can be rearranged as follows:
```
y D  yF , yF þ yM  1: (7.6)
```
```
Notice that when y F ¼ 1 trueð Þ ) yD ¼ 1 trueð Þ, and yM ¼ 0 falseð Þ. On the other hand,
```
when y F ¼ 0 it implies yD ¼ 0, 1, and yM ¼ 0, 1.
7.1.2 Example 2 of Logic Proposition
Consider the following logic statement:
```
p1 ^ p2ð Þ ) p3 ^ p4ð Þ: (7.7)
```
```
Because it corresponds to an implication, A ) B, it is equivalent to ¬A∨B. Hence, substi-
```
tuting, we have from De Morgan’s Theorem and the distribution,
¬A ¼ ¬ p1 ^ p2ð Þ , ¬p1∨¬p2 ¼ C
```
¬A∨B ¼ C∨B ¼ C∨ p3 ^ p4ð Þ ) C∨p3ð Þ ^ C∨p4ð Þ:
```
And, finally, we obtain
```
¬p1∨¬p2∨p3ð Þ ^ ¬p1∨¬p2∨p4ð Þ, (7.8)
```
which is in CNF. Rewriting both clauses in terms of 0-1 variables yields the inequalities
1  y1 þ 1  y2 þ y3  1
```
1  y1 þ 1  y2 þ y4  1, (7.9)
```
which can be rearranged as
y3  y1 þ y2  1
```
y4  y1 þ y2  1: (7.10)
```
```
Notice that when y1 ¼ 1, y2 ¼ 1, the inequalities in (7.10) yield y3 ¼ 1, y4 ¼ 1, which
```
```
verifies the truth of the proposition in (7.7).
```
7.2 Modeling of Disjunctions
```
In this section we consider linear disjunctions of the following form (Balas, 1979; Balas,
```
```
2018):
```
64 7 Systematic Modeling of Constraints with Logic
∨j2D A j x  bj
 
```
, (7.11)
```
where j 2 D is the set of disjuncts or disjunctive terms, x is an n-vector of continuous
variables, A is an m  n matrix, and bj is an m-vector of right-hand sides.
An example of a disjunction is the following condition that arises in batch scheduling
problems in which it is stated that either A is manufactured before B, or B is manufactured before
A. If the start times of A and B are given by tA and t B, respectively, and the processing times of
A and B are given by pA and pB, respectively, the logic condition can be expressed as follows:
```
t A þ pA  tBð Þ∨ tB þ pB  t Að Þ: (7.12)
```
The disjunct on the left states that the start time of A and its processing time are less than or
```
equal to the start time of B (i.e., A is processed before B), while the disjunct on the right
```
states that the start time of B and its processing time are less than or equal to the start time of
```
A (i.e., B is processed before A). Clearly the OR operator, ∨, indicates that only one of the
```
conditions in the disjuncts can hold true. Note that although the notation implies an
inclusive OR, it is acting like an exclusive OR as only one disjunct can hold true.
7.2.1 Big-M Reformulation
Consider assigning to each disjunct a 0-1 variable yj , such that yj ¼ 1 if the linear inequality
holds true in the disjunct j, and such that yj ¼ 0 otherwise. The simplest way for reformu-
```
lating the disjunction in (7.11) in terms of the binary variables yj is with the big-M
```
```
formulation given by Raman and Grossmann (1994),
```
A j x  bj þ M j 1  y j
 
j 2 D
X
j2D
yj ¼ 1
yj ¼ 0, 1,
```
(7.13)
```
```
where M j is a sufficiently large parameter. The basic idea in the big-M constraints in (7.13) is
```
that, for y j ¼ 1, the inequality holds true, i.e., A j  bj . In contrast, when yj ¼ 0, the inequal-
ity becomes redundant for a sufficiently large parameter because then A j x  bj þ M j .
Clearly the value of M j has to be carefully chosen. A large value will help to render the
linear inequality to be redundant. On the other hand, a large value will cause the LP
```
relaxation to be weak (see Section 8.1 in Chapter 8).
```
7.2.2 Convex-Hull Reformulation
```
To avoid introducing the big-M parameter, we can replace each linear disjunction in (7.11)
```
```
by its convex hull (Balas, 1985; Raman and Grossmann, 1994). In this section, we present a
```
simple derivation based on exact linearization. Later in Chapter 10, Section 10.2, we will
present a formal derivation.
7.2 Modeling of Disjunctions 65
```
The disjunction in (7.11) is equivalent to the 0-1 nonlinear inequalities,
```
A j x yj  bj yj j 2 D
X
j2D
yj ¼ 1
yj ¼ 0, 1:
```
(7.14)
```
```
In order to linearize the constraints in (7.14), let z j ¼ xy j , which can be interpreted as a
```
disaggregated variable of x. The reason is that,
X
j2D
z j ¼
X
j2D
```
x yj (7.15)
```
and because Pj2D yj ¼ 1,
X
j2D
```
z j ¼ x, (7.16)
```
which means that the variables z j can be interpreted as disaggregated variables of the
continuous variable x. To ensure that z j ¼ 0 if yj ¼ 0, we need to add the upper-bound
constraints,
```
0  z j  U j yj : (7.17)
```
```
Rewriting constraints (7.14) in terms of the variables z j , and adding (7.16) and the upper-
```
```
bound constraints in (7.17) yields the following set of mixed-integer linear constraints,
```
x ¼
X
j2J
z j
Aj z j  bj yj j 2 D
X
j2J
yj ¼ 1
0  z j  U j yj j 2 D
yj ¼ 0, 1:
```
(7.18)
```
It can be shown that the above constraints correspond to the convex hull of the disjunction
```
in (7.11) (Balas, 1985) when the binary variables are treated as continuous, 0  yj  1.
```
We should note that the upper-bound constraint 0  z j  U j yj may not be needed if
A i z j  bj yj is such that z j ¼ 0 for yj ¼ 0. We should also note that the convex hull yields a
```
tighter relaxation than the big-M formulation in (7.13). A simple demonstration is
```
as follows.
```
Consider multiplying by yj the big-M inequality in (7.13):
```
```
A j x yj  b j yj þ M j 1  yið Þyj : (7.19)
```
```
Substituting for the variable z j ¼ xy j , and in analogy to (7.18), we obtain,
```
66 7 Systematic Modeling of Constraints with Logic
A j z j  bj yj þ M j 1  yj
 
yj
x ¼
X
j2D
z j
X
j2D
yj ¼ 1
0  zj  U j yj
yj ¼ 0, 1:
```
(7.20)
```
```
Comparing (7.20) with (7.18), since M j 1  y j
```
 
yj > 0 for 0 < yj < 1, it follows that the 0-1
```
relaxation of the convex hull in (7.18) is tighter. On the other hand it is clear that the number
```
```
of constraints and variables in the convex-hull constraints given by (7.18) is larger than those
```
```
in the big-M formulation (7.13).
```
7.2.3 Example
Consider the following disjunction,
x1  x2  1½ ∨ x1 þ x2  1½ 
0  x1 , x2  4:
```
(7.21)
```
```
Following (7.13), the big-M formulation is given by,
```
x1  x2  1 þ M 1  y1ð Þ
x1 þ x2  1 þ M 1  y2ð Þ
y1 þ y2 ¼ 1
y1 , y2 ¼ 0, 1
0  x1 , x2  4:
```
(7.22)
```
Since the continuous variables are bounded between 0 and 4 we do not need to select
an excessively large value of the parameter M. For instance, the relatively modest value
M ¼ 20 will suffice.
```
Following (7.18), and for simplicity defining the variables z and w for the disaggregation
```
of the variables x1 and x2 , the convex-hull formulation is given by
x1 ¼ z1 þ z2
x2 ¼ w1 þ w2
z1  w1  y1
z2 þ w2  y2
0  z1  4y1
0  z2  4y1
0  w1  4y2
0  w2  4y2
y1 þ y2 ¼ 1
0  x1 , x2  4:
```
(7.23)
```
7.2 Modeling of Disjunctions 67
```
Comparing (7.22) and (7.23) it is clear that the number of constraints and variables is larger
```
in the convex-hull formulation than in the big-M formulation.
```
Figure 7.1 shows the relaxed feasible regions defined by the big-M formulation (7.22)
```
```
0  x1 , x2  4ð Þ and the convex-hull formlation (7.23). It can be seen that the relaxed
```
feasible region of the convex hull is tighter than that of the big-M, with the difference being
the two black triangles in Fig. 7.1.
7.3 Generalized Disjunctive Programming
We close this chapter by introducing the concept of generalized disjunctive programming
```
(GDP) (Raman and Grossmann, 1994), which is a generalization of the concept of disjunct-
```
```
ive programming introduced by Balas (1979, 2018), which corresponds to linear program-
```
ming problems with linear disjunctive constraints.
The idea in GDP is to formulate optimization problems in terms of constraints in
algebraic form, and in the form of disjunctions and logic propositions. These are expressed
in terms of Boolean and continuous variables. Specifically, Boolean variables Y jk are
assigned to each term of the disjunctions, which are represented in terms of linear constraints
of continuous variables x, and continuous cost variables c k associated with the cost of
disjunction k. The GDP problem is then formulated as follows:
min Z ¼
X
k2K
c k þ f T x
```
s:t: Dx  d
```
∨j2J k
Y jk
B jk x  bjk
c k ¼ γjk
2
64
3
75k 2 K
∨
j2J k
Y jk , k 2 K
Ω Yð Þ ¼ True
```
Y jk ¼ True; Falsef g, x 2 X , c k 2 R1:
```
```
(7.24)
```
1
1
4
4 x1
```
x2Figure 7.1 Relaxations of (7.22)
```
```
and (7.23).
```
68 7 Systematic Modeling of Constraints with Logic
```
In (7.24) the inequalities Dx  d are denoted as global constraints in that they must always
```
be satisfied. The disjunctions k 2 K contain the linear inequalities B jk x  b jk and the cost
variables c k ¼ γjk must hold true when the Boolean variable Y jk ¼ True. Note that for each
disjunction k only one Boolean variable can be true due to the exclusive OR operator. The
constraints Ω Yð Þ ¼ True represent the logic propositions.
```
The GDP model in (7.24) can be used as a high-level framework for formulating discrete/
```
continuous linear problems. Furthermore, it can also be used as a basis for deriving MILP
```
problems (Raman and Grossmann, 1994).
```
One option is with big-M constraints. Here we introduce the yjk ¼ 0, 1 variables in place of
the Boolean variables Y jk. Furthermore, we replace the logic propositions Ω Yð Þ ¼ True by the
linear inequalities Ay  a, and substitute c k ¼ Pj2I k γk yjk . Finally, we replace the disjunctions
```
by the big-M constraints in (7.13). Thus, the GDP in (7.24) can be reformulated as the MILP:
```
min Z ¼
X
k2K
X
j2J k
γk yjk þ f T x
```
s:t: Dx  d
```
A j x  bj þ M j 1  yjk
 
j 2 J k , k 2 K
Ay  aX
j2D
yjk ¼ 1 k 2 K
y jk ¼ 0, 1, x 2 X :
```
(7.25)
```
```
Similarly, if we replace the disjunctions by the convex-hull formulation in (7.24) this yields
```
```
the following MILP, which is known as the hull reformulation (Balas, 1979, 2010, 2018;
```
```
Raman and Grossmann, 1994)
```
min Z ¼
X
k2K
X
j2J k
γk yjk þ f T x
```
s:t: Dx  d
```
x ¼
X
j2J k
z jk
A j z jk  bj yjk j 2 J k, k 2 K
0  z j  U j yjk j 2 J k, k 2 K
Ay  aX
j2D
yjk ¼ 1 k 2 K
y jk ¼ 0, 1 x 2 X :
```
(7.26)
```
We will examine generalized disjunctive programming in more detail in Chapter 10.
EXERCISES
7.1 Convert the logic expression below into a system of inequalities with 0-1 variables:
```
P1∨¬P2 ) P3∨P4:
```
Exercises 69
```
7.2 Show that y1 ) y2 is equivalent to ¬y1∨y2 .
```
7.3 Formulate linear constraints in terms of binary variables for the following cases.
```
(a) If A is true and B is true then C is true or D is true (inclusive OR).
```
```
(b) The choice of all 0-1 combinations for yj , j 2 J is feasible, except the one for which
```
yj ¼ 0, j 2 N, yj ¼ 1, j 2 B, where N and B are specified partitions of J.
```
(c) If power must be generated in any period 1, 2, or 3, then install a gas turbine.
```
7.4 It is proposed to model the condition,
if select item 1 and not item 2, then select item 3 and item 4
with the inequality:
y3 þ y4  2 y1  y2ð Þ,
where y i are binary variables that represent the selection of the corresponding items.
```
Using propositional logic, derive the inequality(ies) that model the above condition.
```
If you arrive at a different model, determine whether it is better or not, and in what
```
sense it is better (or not) than the inequality above.
```
7.5 Consider a scheduling problem involving two successive time slots k  1 and k and a set
of N products, i ¼ 1, 2, . . . , N. We would like to model integer constraints that reflect
the fact that if product i is assigned to slot k  1 yi, k1 ¼ 1

and product j to slot
```
k (y j, k ¼ 1), then there is a changeover from product i to product j z ijk ¼ 1
```

and vice
```
versa (see figure below).
```
```
(a) Using propositional logic, formulate linear constraints in terms of 0-1 variables to
```
model the above condition.
```
(b) Show that an alternative formulation with 0-1 linear inequalities is to consider the
```
```
logic fact that: (I) if there is a changeover from slot k  1 with a given product i to
```
```
any product j in slot k, then product i is assigned to slot k  1, and (II) if there is a
```
changeover from slot k  1 with any product i to a given product j in slot k, then
product j is assigned to slot k.
```
(c) Discuss the relative advantages of both formulations in terms of number of con-
```
straints and tightness of their relaxation.
i j
k – 1 k
7.6 Formulate mixed-integer linear constraints for the following disjunctions, using both
big-M and convex-hull formulations.
```
(a) Either 0  x  10 or 20  x  30.
```
```
(b) The temperature approach constraint for a heat exchanger
```
Tin  Tout  DT min ,
should hold only if the exchanger is actually selected.
7.7 Convert the following generalized disjunctive programming problem into an MILP
using a formulation that yields the tightest relaxation:
70 7 Systematic Modeling of Constraints with Logic
min Z ¼ c þ 2x1 þ 3x2
```
s:t:
```
Y 1
x1 þ x2 þ 2  0
c ¼ 5
2
66
4
3
77
5∨
Y 2
2  x2  0
c ¼ 7
2
66
4
3
77
5
Y 3
x1  x2  1
" #
∨
¬Y 3
x1 ¼ 0
" #
```
Y 1 ^ ¬Y 2 ) ¬Y 3
```
¬ Y 2 ^ Y 3ð Þ
0  x1  5, 0  x2  5, c  0
```
Y j 2 true; falsef g, j ¼ 1, 2, 3:
```
7.8 Consider the cost function shown in the graph below.
```
(a) Formulate the cost function C as a disjunction.
```
```
(b) Develop the mixed-integer constraints applying the convex hull to the disjunction.
```
C
L A U x
a1+b1x
a2+b2x
```
7.9 Given the nonlinear function shown below, derive (mixed-integer linear) constraints to
```
perform a piecewise linear approximation, for fixed points x i, i ¼ 0, 1, n, and by taking
linear combinations of the function values f x ið Þ at each interval i in terms of the weight
λ, where 0  λ  1.
```
f (x0 )
```
x0 x1 x2 xn–1
```
f (x1 )
```
```
f (x2)
```
```
f (xn–1)
```
```
f (xn)
```
xn
x
f
Exercises 71
8 Mixed-Integer Linear Programming
8.1 Introduction
```
We consider in this chapter the solution of mixed-integer linear programming (MILP)
```
```
models, which can be expressed as follows (Nemhauser and Wolsey, 1988; Wolsey, 1998):
```
min Z ¼ aT x þ bT y
```
s:t: Ax þ By  d
```
x  0, y 2 0, 1f gm,
```
(MILP)
```
```
in which x are the continuous variables (dimensionality n), and y are the discrete variables
```
```
(dimensionality m) assumed to be 0-1 values, a very common case. In fact, any bounded discrete
```
```
variable can always be reformulated in terms of 0-1 variables (see Exercise 6.1). Before we
```
consider formal solution methods, we first outline some simple-minded solution approaches.
```
The simplest approach for solving problem (MILP) is a “brute force approach” in which
```
```
linear programs (LP), are solved for all the 0-1 combination of the binary variables yj ,
```
j ¼ 1, . . . , m, in order to find the global minimum. The drawback, however, is that the
number of combinations increases exponentially with the number of 0-1 variables.
Specifically, the number of combinations is given by 2m. This means that for m ¼ 5 there
are 32 combinations, for m ¼ 10 there are 103 , while for m ¼ 50 there are 1015 combinations.
Clearly, this approach is only computationally feasible for a modest number of 0-1 variables.
Alternatively, we might consider a relaxation approach in which we relax each binary
variable yj as a continuous variable bounded between 0 and 1, that is, 0  y j  1,
j ¼ 1, . . . , m. We could then consider solving the MILP as a continuous LP. Problem is that
```
0-1 solutions are only obtained for special structures (e.g., assignment problem) in which the
```
```
matrix of coefficients is known to be totally unimodular (Nemhauser and Wolsey, 1988).
```
Although noninteger solutions are generally obtained with this approach, the relaxed MILP
yields a lower bound to the optimum solution, which will be useful in a search such as branch
and bound. We should note that simply rounding the solution of the relaxed MILP to the
```
nearest integer may yield solutions that are infeasible or suboptimal (see Fig. 8.1). Despite
```
these limitations, it might still provide a heuristic solution that corresponds to an upper bound.
Furthermore, if the rounding approach is applied to problems with integer variables that can
take relatively large values, useful near-optimal solutions might be obtained.
In contrast to nonlinear programming, there are no optimality conditions that characterize
the solution of the MILP. However, an elegant theory has been developed based on sequential
convexification of an MILP that yields an LP whose feasible space corresponds to the integer
```
convex hull; that is an LP where all vertices or extreme points yield 0-1 values. The sequential
```
72
```
convexification procedure is of course nontrivial (see Sherali and Adams, 1990; Lovasz and
```
```
Schrijver, 1991; Balas et al., 1993). It is beyond of the scope of this textbook to describe in
```
detail these convexification schemes. Suffice it to say that they roughly consist of successively
multiplying the constraints by a binary variable, then linearizing the variables to lift them to a
higher-dimensional space, and projecting them back to the original space. The latter step
causes this approach to have exponential complexity, making it impractical except for low-
dimensionality problems. However, it can be used as a framework for deriving cutting planes
that can help to strengthen the LP relaxation of the MILP.
8.2 MILP Methods
```
The major methods for solving problem (MILP) include the following.
```
```
(a) Cutting planes. This method consists of solving a sequence of LPs in which cutting planes
```
are successively generated to cut off the solution of the relaxed LP with previously accumu-
```
lated cutting planes. The first cutting-plane method was proposed by Gomory (1958).
```
```
(b) Benders decomposition. This method proposed by Benders (1962), partitions the prob-
```
```
lem (MILP) into y and x variables, and consists of solving a sequence of integer master
```
problems and LP subproblems. The latter generate cuts that are successively incorpor-
ated into the master problem that predicts lower bounds to the solution of the MILP.
```
(c) Branch and bound search. This method consists of representing the 0-1 combinations of
```
the MILP through a binary tree in which LP subproblems are solved to determine lower
and upper bounds in order to find the optimal solution by enumerating a subset of the
nodes of the tree. The first branch and bound method was proposed by Land and Doig
```
(1960), and subsequently formalized by Dakin (1965).
```
```
(d) Branch and cut methods. These methods combine the branch and bound method with
```
```
cutting planes with the goal of strengthening the lower bound in the tree search (mini-
```
```
mization case). Some of the initial branch and cut methods were described by Crowder
```
```
et al. (1983) and by Van Roy and Wolsey (1987) who relied on specialized cutting planes
```
for the knapsack and network-flow problems. The first general branch and cut method
```
was proposed by Balas et al. (1993), who generated disjunctive cuts derived for the
```
```
general (MILP) problem.
```
y2
y1
1
0 1
Relaxed
solution
Figure 8.1 Infeasible integer
rounding from LP relaxation.
8.2 MILP Methods 73
Below, we will describe in some detail the Gomory cutting planes and the branch and
cut methods.
8.3 Gomory Cutting Planes
We restrict the presentation to the pure integer program given by
min Z ¼ c T y
```
s:t: Ay ¼ b
```
y 2 Z nþ
```
(8.1)
```
in which the y variables correspond to nonnegative integer variables.
```
Assume that the LP relaxation of (8.1) is solved with y  0 using the Simplex algorithm.
```
Let the optimal basic variables be yB i 2 B, and the nonbasic variables be yj j 2 NB. Problem
```
(8.1) can then be rewritten as
```
min Z ¼ a00 þ
X
j2NB
a0j y j
```
s:t: yBi þ
```
X
j2NB
aij yj ¼ aio i ¼ 1, . . . , m
yj  0 j 2 NB:
```
(8.2)
```
```
From (8.2), if we round-down the right-hand side and the coefficients aij for a given
```
noninteger row i, this yields the following inequality
yBi þ
X
j2NB
a ij
 
```
yj  aiob c, (8.3)
```
```
which is known as the Gomory cut. The question that arises is: why is (8.3) a cut? Let us
```
```
substitute the equality constraint in (8.2) into (8.3). This then yields the following inequality
```
ai0  aiob c 
X
j2NB
a  aij
  
```
yj : (8.4)
```
```
Since yj ¼ 0, j 2 NB at the relaxed optimum, (8.4) then implies ai0  aiob c  0. But
```
```
ai0  aiob c > 0. This means that the inequality (8.3) is violated at yj ¼ 0, and therefore
```
```
(8.3) is a cutting plane as it makes the optimal solution of (8.2) to be infeasible. While one
```
can generate a sequence of cutting planes, by successively solving the relaxed LP and adding
the previous cutting planes, the convergence is slow. This is mainly due to the fact that the
```
cutting planes become nearly parallel (see Fig. 8.2), which in turn also induces near-
```
singularity in the matrix of the LP. Therefore, Gomory’s cutting plane is generally not a
practical method.
74 8 Mixed-Integer Linear Programming
8.4 Branch and Cut Method
As indicated above, the branch and cut method is a combination of the branch and bound
method with cutting planes. Major commercial codes such as CPLEX, GUROBI, and
```
XPRESS, implement these methods, as do some of the noncommercial codes (e.g., SCIP).
```
The major objective in the branch and cut method is to avoid the exhaustive enumeration
of a binary tree in which LP subproblems are solved at each node.
The branch and cut method consists of the two following major steps.
```
(a) The LP relaxation is solved at the root node of the binary tree which yields a lower
```
```
bound to the MILP in (8.1). In order to strengthen this lower bound, a sequence of
```
relaxed LPs are solved by adding cutting planes such as Gomory’s. The sequence of these
problems is solved until there is no improvement in the lower bound within a given
tolerance ε.
```
(b) The branch and bound enumeration of a binary tree (see Fig. 8.3) is performed in which
```
the problem is partitioned into a sequence of LPs, in which lower and upper bounds are
generated to eliminate combinations.
We should note that each node requires solution of a relaxed LP with constraints on the
binary variables. For example, in Fig. 8.3 the root node corresponds to the LP relaxation of
B
A
y2 1
y2 0
y2 1
y2 0
y3 0
y1 1
y1 0
Figure 8.3 Binary tree for branch
and bound search.
y2
y1
1
0 1
Figure 8.2 Generation of
Gomory cutting planes.
8.4 Branch and Cut Method 75
```
problem (MILP). Node A in the binary tree corresponds to the relaxed LP with the
```
constraint y1 ¼ 0. Node B corresponds to the relaxed LP with the constraints y1 ¼ 0,
y2 ¼ 1, y3 ¼ 0.
We should also note that the total number of nodes in the binary tree is 2mþ1  1, where m
is the number of binary variables. This means that with the three binary variables the tree
```
has 15 nodes although there are only eight binary combinations (i.e., 2m). The hope (or
```
```
gamble) is that when we enumerate the nodes in the tree, we will examine only a subset of the
```
total number of nodes. We should also note that the sequence of LPs can be updated very
efficiently with the dual Simplex algorithm with which one may require less computational
time even if we have to enumerate 2m nodes.
To appreciate why the binary tree can be interpreted as a partition consider node A in
Fig. 8.3 in which the relaxed LP is solved with the constraint y1 ¼ 0. As can be seen in
Fig. 8.4, that corresponds to a face of the unit cube. If we next consider node B, in which the
relaxed LP is fixed with y1 ¼ 0, y2 ¼ 1, y3 ¼ 0, that corresponds to the point in the
hypercube which is reached through the line y1 ¼ 0, y2 ¼ 1.
In order to derive criteria for rejecting or fathoming nodes in the enumeration of the
binary tree, consider the two corresponding LP subproblems in nodes k and i, in the binary
```
tree, where node k is a descendant of node i (e.g., k ¼ B, i ¼ A).
```
P i : min Z ¼ a T x þ bT y P k : min Z ¼ a T x þ bT y
```
s:t: Ax þ By  d s:t: Ax þ By  d
```
x  0, 0  yj  1 x  0, 0  yj  1
yj ¼ 0, 1, j 2 J ið Þ yj ¼ 0, 1, j 2 J kð Þ,
```
(8.5)
```
where J ið Þ, J kð Þ are index sets of those binary variables with fixed 0 or 1 values. Since node i
```
is a parent of node k, it follows that J ið Þ  J kð Þ; that is, J ið Þ is contained in the set J kð Þ. This
```
in turn means that problem P k is more constrained than problem P i . Hence, the following
properties hold.
```
(1) If P i is infeasible, then P k is infeasible. This trivially follows from the fact that if P i is
```
infeasible, adding more constraints leading to P k will also make this problem infeasible.
y2
y1
A
B
y3Figure 8.4 Hypercube for three
```
binary variables (see text).
```
76 8 Mixed-Integer Linear Programming
```
(2) If P k is feasible then P i is feasible and Z i∗ Z k∗. This means that Z i∗, the optimal
```
solution of P i, corresponds to a lower bound of the solution Z k∗of P k . This readily
follows from the fact that the optimal solution of P k must be at least as large as P i since
it is a more constrained problem.
```
(3) If a feasible integer solution is found for problem P k (i.e., yj ¼ 0 or 1, j ¼ 1, . . . , m) then
```
Z k∗ Z∗. This means that a feasible MILP solution at any node k, Z k corresponds to
an upper bound UB of the global optimum Z∗.
The three properties above can be used for fathoming nodes in the enumeration of the binary
tree search. In particular, if subproblem P i is infeasible then its corresponding node i can be
fathomed. Similarly, if Z i∗> UB, where UB is the current upper bound, then node i can
be fathomed.
In order to complete the branch and bound search, we need to decide how to enumerate
the nodes in the tree. Since there are various ways of doing this, we consider below the
common branching rules used in the branch and bound search.
The first rule addresses the question of which binary variable should be fixed to 0-1 at a
given node. Note that in Fig. 8.3 we decided to enumerate the nodes in the order y1 , y2 , and
y3. But, in general, we might consider the following three schemes.
```
(1) Priority rule, where we specify an order for the binary variables and branch on the first
```
```
noninteger binary variable; that is, we select the first yj 6 ¼ 0, 1. This order usually reflects
```
```
the hierarchical importance of decisions (e.g., investment vs. expansion of a plant).
```
Consider the case where we specify the order 1, 2, 3, and that the relaxation at the root
node yields y1 ¼ 1, y2 ¼ 0:8, y3 ¼ 0:5. We then select y2 as the variables on which we
generate the first branch.
```
(2) Rule: Select a noninteger binary closest to 0.5. The motivation here is first to resolve
```
those variables that are the furthest from integrality. In our example above, that would
mean branching first on y3 as it has a value of 0.5, which is further away from integrality
than y2 ¼ 0:8.
```
(3) Rule: Select a binary variable with the largest degradation (Beale, 1979). The basic idea
```
in this approach is to estimate the down and up penalties, Dj , Uj , when forcing each
noninteger binary variable yj , to be set to 0 or to 1 as shown in Fig. 8.5. These penalties
can be readily calculated with dual Simplex iterations. For each binary variable yj the
Z
0
Dj Uj
y *j yj1
Figure 8.5 Estimation of down
and up penalties, Dj, Uj.
8.4 Branch and Cut Method 77
degradation T j is set to its smallest value, T j ¼ min Dj , Uj
 
. The variable j to be
branched on is the one with the largest degradation, that is max j T j
 
.
The second rule addresses the question of which node to examine next. The two major
```
options for the tree enumeration (Morrison et al., 2016) are the following:
```
```
(a) Depth first (LIFO, newest bound rule), where the most recently created node is
```
expanded, and backtrack takes place at terminal nodes.
```
(b) Best bound rule (breadth first, priority rule), where the node with best lower bound is
```
expanded next.
For MILP, a combination of both depth first and breadth first is commonly used.
Specifically, depth first is used but two nodes are expanded at each step by forcing y j to
```
0 and to 1; the node with the smaller bound is selected next.
```
To illustrate with a small example the logic of the branch and bound search, we consider
the following IP problem:
min Z ¼ y1 þ 2y2 þ 4y3
```
s:t: y1 þ y2 þ y3  1
```
y1  y2  y3  0
y1  y2 þ 0:2
y1 , y2 , y3 ¼ 0, 1:
```
(8.6)
```
As can be seen in Fig. 8.6, at node 1 the relaxed LP is solved in which the binary
variables are treated as continuous. The relaxed LP yields a lower bound of Z ¼ 1:9,
with noninteger values for the binaries y1 ¼ 0:5, y2 ¼ 0:3, y3 ¼ 0:2. Since y1 is the value
closest to 0:5, we branch on y1 setting it to 0 and to 1, giving rise to nodes 2 and 3,
respectively. Although node 2 gives rise to an integer value y1 ¼ 0, y2 ¼ 0, y3 ¼ 1, it is
infeasible. Hence, node 2 is fathomed. Node 3 on the other hand, yields a solution that
is noninteger y1 ¼ 1, y2 ¼ 0:8, y3 ¼ 0:2 with an objective of Z ¼ 3:4, which represents a
lower bound on the solutions of the children nodes. In this case, we could either branch
1
2 3
4 5
Z 1.9
y1 y2 y3  
y1  y2  y3  
y1 y2 y3  
y1  y2 y3  y1  y2  y3 
Z 5.0 Z  infeasible
Z  infeasible
Z 3.4
y2 
y1 y1 
y2 
Figure 8.6 Branch and bound search for
example problem.
78 8 Mixed-Integer Linear Programming
on y2 or y3 . Say we branch on y2 . Setting it to y2 ¼ 0 yields a feasible integer solution
y1 ¼ 1, y2 ¼ 0, y3 ¼ 1 at node 4 with an objective value of Z ¼ 5:0. Since this solution is
```
integer feasible it becomes an upper bound to the optimum of problem (8.6). Setting
```
y2 ¼ 1 at node 5 yields an infeasible integer solution. Hence, node 5 is fathomed,
proving that the optimum integer solution is at node 4, namely Z ¼ 5:0, y1 ¼ 1,
y2 ¼ 0, y3 ¼ 1.
We should note that commercial MILP codes such as CPLEX, GUROBI, and XPRESS,
have become highly sophisticated in the implementation of branch and bound methods
```
(Bixby and Rothberg, 2007). First, they incorporate a variety of cutting planes, such as
```
Gomory’s cutting planes, in order to strengthen the lower bounds predicted at the nodes of
the branch and bound search. Typically, most of these cutting planes are added at the root
node until the improvement of the lower bound lies within a specified tolerance. The main
effect of the cutting planes is then to reduce the number of nodes in the branch and bound
search. Another major impact in MILP codes has been the use of preprocessing techniques
that allow a size reduction of models through the use of algebraic substitutions and logic
```
inference and constraint propagation based on constraint programming techniques (see
```
```
Chapter 11).
```
See Appendix A for further discussion on MILP codes.
EXERCISES
8.1 Given is the integer programming problem
max Z ¼ 1:2y1 þ y2
```
s:t: y1 þ y2  1
```
1:2y1 þ 0:5y2  1
y1 , y2 ¼ 0, 1:
```
(a) Plot the contours of the objective and the feasible region for the case when the binary
```
variables are relaxed as continuous variables y1 , y2 2 0, 1½ .
```
(b) Determine from inspection the solution of the relaxed problem.
```
```
(c) Enumerate the four 0-1 combinations in your plot to find the optimal solution.
```
```
(d) Solve the relaxed LP problem by hand and derive Gomory cuts based on the LP
```
relaxation and verify that they cut off the relaxed LP solution.
```
(e) Solve the above problem with the branch and bound method by enumerating the
```
nodes in the tree and solving the LP subproblems with GAMS.
```
8.2 (a) Show that the number of nodes in a tree where we represent all possible combinations
```
of m 0-1 binary variables is 2mþ1  1.
```
(b) If a complete enumeration of all the nodes in the tree were required, by what factor
```
would this enumeration increase with respect to the direct enumeration of all 0-1
combinations?
Exercises 79
8.3 It is desired to model a condition that states that if any of n items i are to be transported
```
(yi), then one must buy a container for them z ¼ 1ð Þ. Determine if an alternative
```
constraint can be formulated that is tighter than
X
i
y i  nz, y i ¼ 0, 1, i ¼ 1, 2, . . . , n, z ¼ 0, 1:
8.4 When solving an MILP problem you find that the relaxed LP has a finite optimum at the
root node, but that the descendants’ nodes produce infeasible LP subproblems. Explain
why this may be happening.
8.5 A company is considering the production of a chemical C, which can be manufactured
with either process II or process III, both of which use chemical B as a raw material.
Chemical B can be purchased from another company, or else manufactured with process
I, which uses A as a raw material. Given the specifications below, formulate an MILP
model and solve it with GAMS to reach a decision.
```
(a) Which process should be built (II and III are exclusive)?
```
```
(b) How should we obtain chemical B?
```
```
(c) How much of product C should be produced?
```
The objective is to maximize profit.
Consider the two following cases.
```
(1) The maximum demand of C is 10 tons/hr, with a selling price of $1800/ton.
```
```
(2) The maximum demand of C is 15 tons/hr; the selling price for the first 10 ton/hr is
```
$1800/ton, and $1500/ton for the excess.
Data
Investment and operating costs
```
Fixed ($/hr) Variable ($/ton raw mat.)
```
Process I 1000 250
Process II 1500 400
Process III 2000 550
Prices A $500/ton
B $950/ton
Conversions Process I 90% of A to B
Process II 82% of B to C
Process III 95% of B to C
The maximum supply of A is 16 tons/hr.
```
note: You may want to scale your cost coefficients (e.g., divide them by 100).
```
80 8 Mixed-Integer Linear Programming
9 Mixed-Integer Nonlinear Programming
9.1 Overview of Solution Methods
We consider next the case where the mixed-integer programming problem involves non-
linearities. In general, the MINLP problem with 0-1 discrete variables can be formulated as
```
follows (Floudas, 1995; Grossmann, 2002; Trespalacios and Grossmann, 2014):
```
```
min Z ¼ f x; yð Þ
```
```
s:t: h x; yð Þ ¼ 0
```
```
g x; yð Þ  0
```
x 2 R n, y 2 0, 1f gm:
```
(MINLP)
```
```
While problem (MINLP) is quite general, it is convenient to consider the special structure in
```
which the 0-1 variables appear in linear form in the objective function and constraints, while
the continuous variables are in general nonlinear. Furthermore, we specify the set X of
```
continuous variables as having linear constraints with lower and upper bounds, xL , xU ; that
```
is X ¼ xjCx  d, xL  x  xU
 
```
. In this way, problem (MINLP) is given by
```
min Z ¼ c T y þ f xð Þ
```
s:t: h x; yð Þ ¼ 0
```
g xð Þ þ By  0
Ay  a
x 2 X , y 2 0, 1f gm,
```
(MINLP0 )
```
in which the linear structure can be exploited as will be shown below. The two major
```
approaches for solving problem (MINLP0) are the following.
```
```
(1) Branch and bound. This method (Gupta and Ravindran, 1985) is similar to solving
```
```
problem mixed-integer linear programs (MILP) in the previous chapter. The major
```
difference, however, is that at each node, relaxed NLP subproblems are solved with
corresponding constraints for the fixed subset of 0-1 variables corresponding to that
node. This solution approach is reasonable when the number of 0-1 variables is not too
large, as otherwise one might face the solution of many NLP subproblems, which are
computationally more expensive than solving LP subproblems in the MILP case. If the
NLP relaxation of the MINLP is tight, larger problems can be solved with the NLP-
based branch and bound. Codes that implement this method for MINLP include SBB
and BONMIN.
81
```
(2) Decomposition. These methods consist of iterating between NLP subproblems with
```
fixed binary variables, and MILP master problems that predict new values for the binary
variables. The NLP subproblems provide upper bounds ZU if there are feasible solu-
tions, while the MILP subproblems predict lower bounds ZL . Iterations are continued
until the bounds lie within a given tolerance, as shown in Fig. 9.1.
Methods that use this solution approach include generalized Benders decomposition
```
(Geoffrion, 1972), outer approximation (Duran and Grossmann, 1986), LP/NLP-based
```
```
branch and bound (Quesada and Grossmann, 1992), and extended cutting plane
```
```
(Westerlund and Petersson, 1995). Codes that implement these methods for solving
```
MINLP problems are DICOPT, α-ECP, and BONMIN.
9.2 Derivation of Outer-Approximation and Generalized Benders
Decomposition Methods
For the derivation of decomposition methods we assume that there are no equations
h xð Þ ¼ 0 in the MINLP0 case, and that the functions f xð Þ, g xð Þ are convex. This leads to the
```
MINLP in (9.1), which is denoted as convex MINLP since its NLP relaxation is convex:
```
min Z ¼ c T y þ f xð Þ
```
s:t: g xð Þ þ By  0
```
Ay  a
x 2 X , y 2 0, 1f gm:
```
(9.1)
```
Select initial y
Solve NLP for fixed y
Solve MILP master problem
```
Determine lower bound (Z L )
```
```
Determine upper bound (Z U )
```
If ZL < ZU
stop
yes
no
Figure 9.1 Steps of
decomposition algorithms
for MINLP.
82 9 Mixed-Integer Nonlinear Programming
The subproblem at a fixed value y k of the binary variables is given by:
Z yk
 
¼ min c T yk þ f xð Þ
```
s:t: g xð Þ þ Byk  0
```
x 2 X :
ðSðykÞÞ
```
If the subproblem we have denoted (S(y k)) has a feasible solution, its optimal objective yields
```
```
an upper bound to MINLP in (9.1). If it has no feasible solution it is convenient to define the
```
feasibility problem:
min η
```
s:t: g xð Þ þ By k  eη
```
x 2 X , η 2 R1 ,
ðFðykÞÞ
where e is the unit vector.
For the master problem, develop an equivalent linear representation of the MINLP in
```
(9.1) and solve it by relaxation. Specifically, we assume f xð Þ, g xð Þ are convex differentiable
```
functions. Next, by transferring the objective as a constraint with the variable α, we
```
rearrange the MINLP in (9.1) as follows:
```
Z ¼ min α
```
s:t: α  c T y þ f xð Þ
```
g xð Þ þ By  0
Ay  a
x 2 X , α 2 R1 y 2 0, 1f gm:
```
(9.2)
```
Because f xð Þ, g xð Þ are convex, first-order linearizations at points x k yield supporting
hyperplanes at each of these points, namely,
f xð Þ  f x k
 
þ rf xk
 T
x  xk
 
g xð Þ  g xk
 
þ rg x k
 T
x  x k
 
```
)
```
```
8x k 2 X : (9.3)
```
Furthermore, the linearizations at the infinite set of points provides a valid representation
for the functions f xð Þ and g xð Þ. For a finite set of points the linearizations provide an
underestimation to the objective function and an overestimation to the feasible region as
shown in Figs. 9.2a and 9.2b.
```
If we substitute the linearizations (9.3) into (9.2) this yields the MILP master problem (MOA):
```
Z ¼ min α
```
s:t: α  cT y þ f x k
```
 
þ rf xk
 T
x  xk
 
g x k
 
þ rg xk
 T
x  xk
 
þ By  0
Ay  a
9
>>=
```
>>;8x
```
k 2 T
x 2 X , α 2 R1 y 2 0, 1f gm
T ¼ x k is solution of S yk
 
or F yk
 
, 8yk
 
:
```
(9.4)
```
9.2 Outer-Approximation, Generalized Benders 83
This master problem has the following property as stated in Theorem 9.1.
Theorem 9.1 Problems MINLP and MOA have the same optimal solution x∗, y∗ð Þ.
The proof trivially follows from the fact that the functions f xð Þ and g xð Þ can be replaced
```
by the infinite set of linearizations in (9.3). Because it is not practical to obtain linearizations
```
at an infinite number of points, we assume we are given the solution of K NLP subproblems
x k at yk , k ¼ 1, . . . , K. We can then define the relaxed MILP problem RMKOA for the outer-
```
approximation (OA) method:
```
Z KOA ¼ min αOA
αOA  c T y þ f x k
 
þ rf x k
 T
x  x k
 
```
s:t: g x k
```
 
þ rg x k
 T
x  x k
 
þ By  0
Ay  a
9
>>=
```
>>;k ¼ 1, . . . , K
```
x 2 X , αOA 2 R1 , y 2 0, 1f gm:
```
(9.5)
```
```
Generalized Benders decomposition (GBD) involves an MILP master problem that corres-
```
ponds to a projection in the space of the binary variables y. This is accomplished through a
dual representation in terms of the binary variables y that can be derived as follows.
Consider an outer approximation at yk in MOA
α  c T y þ f x k
 
þ rf x k
 T
x  x k
 
```
, (9.6)
```
g x k
 
þ rg x k
 T
x  xk
 
```
þ By  0: (9.7)
```
Let μk  0 be the optimal multiplier of the inequality of g xð Þ þ By  0 from subproblem
S y k
 
```
at the point yk . From (9.7), by premultiplying by μk we obtain
```
x1 x2 x
```
f (x)
```
```
(a)
```
```
(b)
```
x1
x2
x2
x1
```
Figure 9.2 (a) Linearizations of the convex function underestimate the objective function, and (b)
```
overestimate the feasible region.
84 9 Mixed-Integer Nonlinear Programming
μk
 T
g x k
 
þ By
 
  μk
 T
rg x k
 T
x  x k
 
```
: (9.8)
```
```
From the KKT conditions of subproblem (S(yk)) and, for simplicity, assuming we have no
```
active variable bounds, we have,
rf x k
 
þ rg x k
 
```
μk ¼ 0: (9.9)
```
```
If we postmultiply (9.9) by x  x k
```
 
, and rearranging the equality, we have,
rf x k
 T
x  x k
 
¼  μk
 T
rg x k
 T
x  x k
 
```
: (9.10)
```
```
Substituting (9.10) into (9.8) yields
```
μk
 T
g xk
 
þ By
 
 rf x k
 T
x  x k
 
```
: (9.11)
```
```
Finally, if we substitute into (9.6), we obtain the Benders cut,
```
α  c T y þ f xk
 
þ μk
 T
g x k
 
þ By
 
```
: (9.12)
```
```
This cut, which is a surrogate of the constraints (9.6) and (9.7), corresponds to a projection
```
```
of the outer approximations (9.6) and (9.7) into the space α; yð Þ. The cut can also be
```
interpreted as the Lagrangean function parametrized in the variables y,
ℒ yð Þ ¼ c T y þ f x k
 
þ μk
 
g x k
 
þ By
 
```
: (9.13)
```
```
For the case that the subproblem (S(yk)) has no feasible solution, the feasibility cut that can
```
```
be derived from the feasibility problem (F(yk)) is given by
```
μk
 T
g x k
 
þ By
 
```
 0: (9.14)
```
```
If we replace (9.6) and (9.7) by (9.12) and (9.14), and given the solution of K NLP
```
subproblems at yk , k ¼ 1, . . . , K with solution x k, μk, we can define the relaxed MILP
master problem RMKGB for GBD,
Z KGB ¼ min αGB
```
s:t: αGB  c T y þ f x k
```
 
þ μk
 T
g x k
 
þ By
 
k 2 K KF
μk
 T
g x k
 
þ By
 
 0 k 2 K KI
αGB 2 R1 y 2 0, 1f gm,
```
(9.15)
```
where k 2 K KF and k 2 K KI correspond to the optimality and feasibility cuts, respectively.
Based on the above, we can make the following remarks.
```
(1) RMKOA and RMKGB are MILP master problems that accumulate linearizations as iter-
```
ations k ¼ 1, . . . , K proceed.
```
(2) The optimal solutions to RMKOA and RMKGB correspond to lower bounds ZKOA , Z KGB in
```
```
(9.5) and (9.15), respectively. These lower bounds increase monotonically with the
```
```
iterations k, that is (see Fig. 9.3),
```
9.2 Outer-Approximation, Generalized Benders 85
Z1OA  Z2OA  . . .  Z KOA
Z1GB  Z2GB  . . .  Z KGB:
```
(3) The OA method predicts stronger lower bounds than GBD, Z KOA  Z KGB .
```
```
This follows from the fact that the Lagrangean cut in (9.12) is a linear combination or
```
```
surrogate of the linearization in (9.6) and (9.7) of the OA method. Furthermore, this implies
```
that the OA method generally requires fewer iterations than the GBD method. The trade-off
```
is that the OA involves a larger MILP master problem, (9.5) vs. (9.15), which is more
```
expensive to solve.
9.3 Extended Cutting-Plane Method
```
The extended cutting-plane (ECP) method of Westerlund and Petersson (1995) is similar to
```
the OA algorithm, except that it replaces the NLP step in OA by a simple function
evaluation, which is used to provide a new linearization to an MILP master problem of
```
the form of (9.5). In this way the ECP method resembles a successive MILP procedure. The
```
iterations continue until the nonlinear functions and constraints are converged within a
tolerance ε. The specific steps of the ECP are then as follows.
```
(1) Guess x0 , y0 set K ¼ 0.
```
```
(2) Find x Kþ1 , yKþ1 from the master problem of ECP, RMKECP .
```
min Z ¼ αECP
αECP  c T y þ f xk
 
þ rf x k
 T
x  x k
 
```
s:t: g x k
```
 
þ rg x k
 T
x  x k
 
þ By  0
Ay  a
9
>>=
```
>>;k ¼ 1, . . . , K
```
x 2 X , αECP 2 R1 , y 2 0, 1f gm:
.
Iteration
Upper bound
Z
Z*
Lower bound
Figure 9.3 Progression of lower
and upper bounds in OA and
GBD methods.
86 9 Mixed-Integer Nonlinear Programming
```
(3) If g xkþ1
```
 
þ By kþ1  ε, STOP.
Otherwise, set K ¼ K þ 1, linearize functions at x k, yk
 
```
, and return to step (2).
```
We should note that because the ECP method is expected to require a larger number of
iterations, a larger number of successive MILP master problems must be solved. Instead of
linearizing all the nonlinear constraint functions g xð Þ, usually only the functions corres-
ponding to the most violated inequalities are linearized.
```
A recent extension of the ECP method is the extended supporting-hyperplane (ESH)
```
```
method (Kronqvist et al., 2016). The main idea is not simply to linearize the functions at
```
```
the solution of the master problem of the ECP (step (2) above) to obtain supporting
```
hyperplanes at each iteration, and use these to construct a polyhedral outer approximation.
Specifically, a strict interior point xint , yint
 
is obtained from the NLP subproblem,
min μ
```
s:t: g j x; yð Þ  μ, j 2 J
```
x 2 X , y 2 0, 1f gm, μ 2 R1:
```
(9.16)
```
To construct the polyhedral outer approximation, a new function F is defined as the
pointwise maximum of the nonlinear constraints, according to
```
F x; yð Þ ¼ maxj2J g j x; yð Þ
```
 
```
: (9.17)
```
The new points x k, yk
 
are then determined by
x k ¼ λk xint þ 1  λk
 
xMIP
yk ¼ λk yint þ 1  λk
 
yMIP ,
```
(9.18)
```
```
where xMIP and yMIP are the solution of the master MILP in step (2), and λk is chosen such
```
```
that F x; yð Þ ¼ 0, i.e., at the boundary of the feasible region. The points x k, yk
```
 
are then
located at the boundary of the feasible region, so that linearizing the active constraints
results in supporting hyperplanes. Numerical experience has shown that these linearizations
significantly improve the convergence of the ECP method.
9.4 Properties and Extensions
The following properties can be established for the OA, GBD, and ECP methods presented
in the two previous sections.
```
(1) We should note that the OA and GBD methods have finite convergence, because either
```
they terminate by equality of the lower and upper bounds or, in the worst case, they
would end up enumerating all possible binary combinations, 2m.
```
(2) The branch and bound method converges in one iteration when the NLP relaxation in
```
```
(9.5), in which the binary variables are treated as continuous variables, 0  y i  1,
```
i ¼ 1, . . . , m, yields an integer solution. This effectively means that the MINLP problem
is solved at the root node of the tree.
9.4 Properties and Extensions 87
```
(3) The OA and ECP methods converge in one iteration for the case when the functions f xð Þ
```
```
and g xð Þ in the MINLP (9.1) are linear. This trivially follows from the fact that, in that
```
```
case problem (9.1), an MILP, becomes identical to the MILP master problems, RMKOA
```
and RMKECP .
```
(4) Sahinidis and Grossmann (1991) proved that the GBD method converges in one
```
```
iteration for optimal y∗ and if the problem (MINLP) in (9.5) has zero integrality gap.
```
This property points to the importance of developing tight MINLP models when
applying the GBD method.
A recent review of solvers for convex MINLP problems can be found in Kronqvist et al.
```
(2019).
```
```
In the previous sections we have addressed the case of when the MINLP problem in (9.5)
```
does not involve equations h xð Þ ¼ 0. The difficulty is that, generally, nonlinear equations
give rise to nonconvexities, unless they can be shown to relax as convex inequalities.
Specifically, we would require the relaxations of the equations to satisfy the following
conditions,
hi xð Þ ¼ h i xð Þ  0 convexh i xð Þ  0 concave:

```
(9.19)
```
Assuming we apply the algorithms without regard as to whether convexity applies or not,
```
the extensions for addressing problems of the form of (MINLP0) in Section 9.1 with non-
```
linear equations are as follows.
– In GBD it is easy if the NLP subproblems are feasible. The reason is that analyzing the
Lagrangean function ℒ ¼ c T y þ f x k
 
þ λk
 T
h x k
 
þ μk
 T
g x k
 
þ By
 
, it can be seen
that, if h x k
 
```
¼ 0, the Lagrangean reduces to the GBD cut given in (9.12).
```
– In the OA algorithm, because we cannot simply linearize the equations and add them to
the previous ones, as this would give rise to overspecifications and invalid cuts, we can
resort to relaxing the equations h xð Þ ¼ 0 by analyzing their KKT multipliers λi of the
```
corresponding NLP problem as follows (Kocis and Grossmann, 1987).
```
Relax as hi xð Þ  0 if λi > 0.
Relax as hi xð Þ  0 if λi < 0.
If λi ¼ 0, remove hi xð Þ ¼ 0.
Based on the above, we can define the relaxation matrix T k ¼ t kii
 
tkii ¼ 
1 if λi > 0
1 if λi < 0
0 if λi ¼ 0:
8
<
```
: (9.20)
```
In this way, for feasible points for which h x k
 
¼ 0, the linearizations can be expressed as
```
follows:
```
88 9 Mixed-Integer Nonlinear Programming
T k rh x k
 T
x  x k
 h i
```
 0: (9.21)
```
We should note that one can also add an integer cut to make integer points y k that have been
examined at previous iterations k ¼ 1, . . . , K to be infeasible. This can be accomplished with
```
the inequalities (see Exercise 6.2),
```
X
i2B k
yi 
X
i2N k
```
yi  B k  1 k ¼ 1, . . . , K, (9.22)
```
where Bki ¼ ijyki ¼ 1
 
, N ki ¼ ijyki ¼ 0
 
.
As for the issue of nonconvexity, we should note that convexity is a sufficient condition for
the OA, GBD, ECP, and branch and bound methods to converge to the global optimum.
Difficulties that may arise due to nonconvexities are that the NLP subproblems may have
multiple solutions. This implies that the upper bounds may not be valid. Furthermore, in the
OA, GBD, ECP methods nonconvex functions may cut off the optimum in the MILP master
problem since the linearizations may not underestimate the feasible region as is shown in the
simple example in Fig. 9.4.
Two options to overcome these problems include trying to convexify the MINLP problem,
or applying rigorous global-optimization methods, as will be discussed in Chapter 12 on
global optimization. The other option is to introduce slacks with an augmented penalty in the
```
spirit of SQP algorithms (Powell, 1978) in order to allow for the violation of
```
nonconvex constraints.
In the case of the MILP master problem of the OA method, we can modify it by
implementing equality relaxation, introducing slack variables for an augmented penalty,
and adding integer cuts. The modified MILP master problem is then as follows
```
(Viswanathan and Grossmann, 1990).
```
Let ρ be the penalty weight for the slack variables s k, pk , qk  0. The MILP master RM APOA
of equality relaxation with augmented penalty is given by
Local
optimum
x
Global
optimum
Cut off!
0 1 y
Figure 9.4 Cutting off global optimum with
linearization of nonconvex function.
9.4 Properties and Extensions 89
min Z KOA ¼ αOA þ ρ
X
k
s k þ e T pk þ e T qk
 
c T y þ f x k
 
þ rf xk
 T
x  x k
 
 αOA  sk
```
s:t: T k rh x k
```
 T
x  xk
 h i
 pk
g x k
 
þ rg x k
 T
x  xk
 
þ By  qk
Ay  a
9
>>>
>>>
=
>>>
>>>
```
;
```
k ¼ 1, . . . , K
X
i2B k
yi 
X
i2N k
y i  B k  1 k ¼ 1, . . . , K
x 2 X , αOA 2 R1 , s k, pk , qk  0 y 2 0, 1f gm:
```
(9.23)
```
```
We should note that if ρ is large ρ > γij jð Þ, then if the functions are convex (including relaxed
```
```
equations) the slack variables s k ¼ p k ¼ qk ¼ 0, which implies that the MILP master
```
```
problem in (9.23) reduces to the original MILP master problem (9.5) (except for the
```
```
integer cuts).
```
If the functions involved in the MINLP are nonconvex, the optimal value of the MILP
```
master problem in (9.23), Z KOA , will not correspond to a rigorous lower bound, among other
```
things, because the slacks will generally be nonzero. However, we can resort to a heuristic
termination criterion. Specifically, the termination rule is to stop until there is no improve-
ment in the NLP subproblems. Obviously, this will generally not provide the global-
optimum solution, although computational experience seems to indicate that in surprisingly
many cases one does find near-optimum solutions.
The computational strategy based on the augmented-penalty MILP master problem in
```
(9.23), and the termination criterion of nonimprovement, has been implemented in the
```
software code DICOPT, where the relaxed NLP is initially solved in order to generate a
```
point for the initial master problem (see Fig. 9.5). If that relaxed NLP yields an integer
```
solution, obviously no further search needs to be conducted.
```
MINLP optimization has been a very active area of research in the recent past (Bonami
```
```
et al., 2012). Appendix A describes some of the software for solving MINLP that has been
```
developed in the recent past.
yes – STOP
Solve relaxed NLP
Integer y?
MILP Aug.
NLP sub. Improve? NO
STOP
YES
Figure 9.5 Steps in DICOPT
solver for MINLP.
90 9 Mixed-Integer Nonlinear Programming
EXERCISES
9.1 Show that if f xð Þ is a convex differentiable function, then
f xð Þ  f x k
 
þ rf x k
 T
x  x k
 
for all x:
9.2 For what special class of MINLP problems will the branch and bound method for
solving MINLP problems outperform the OA, GBD, and ECP methods in terms of
number of NLP subproblems to be solved?
9.3 Using GAMS solve the following MINLP problem step by step with
```
(a) generalized Benders decomposition,
```
```
(b) outer-approximation method,
```
```
(c) extended cutting plane.
```
```
(d) Also verify your answer with GAMS/DICOPT:
```
min f ¼ y1 þ 1:5y2 þ 0:5y3 þ x21 þ x22
```
s:t: x1  2ð Þ2  x2  0
```
x1  2y1  0
x1  x2  4 1  y2ð Þ  0
x1  1  y1ð Þ  0
x2  y2  0
x1 þ x2  3y3
y1 þ y2 þ y3  1
0  x1  4, 0  x2  4
y1 , y2 , y3 ¼ 0, 1:
```
(e) Use the starting point y1 ¼ y2 ¼ y3 ¼ 1,
```
x1 ¼ x2 ¼ 0 for extended cutting plane.
9.4 Consider the “mostly linear” mixed-integer nonlinear programming problem of the
following form, where r vð Þ, t vð Þ are convex nonlinear functions in terms of “compli-
cating” nonlinear continuous variables v, while w are the linear variables:
min Z ¼ c T y þ aT w þ r vð Þ
```
s:t: Cy þ Dw þ t vð Þ  0
```
Ey þ Fw þ Gv  d
y 2 0, 1f g, w 2 W , v 2 V :
Show that the outer approximation of the above problem at fixed value of the binary
variable yk , and corresponding optimal solution xk , and optimal multipliers λk , μTk , can
be expressed by the following constraints in which only the nonlinear variables v are
projected out by Benders cuts:
α  c T y þ aT w þ r v k
 
þ λk T
 
Cy þ Dw þ t v k
  
 μkT
 
G v  v k
 
Ey þ Fw þ Gv  d
y 2 0, 1f g, w 2 W , v 2 V :
Exercises 91
9.5 It is proposed to manufacture a chemical C with a process I that uses raw material B. B
can be purchased or manufactured with either of two processes, II or III, which use
chemical A as a raw material. In order to decide the optimal selection of processes and
levels of production that maximize profit, formulate the MINLP problem and solve
with the augmented-penalty/outer-approximation/equality-relaxation algorithm in
DICOPT.
```
Data:
```
```
Conversion: Process I C ¼ 0:9B Process II B ¼ ln 1 þ Að Þ Maximum capacity: 5 ton
```
prod/hr
```
Process III B ¼ 1:2 ln 1 þ Að Þ (A, B, C, in ton/hr)
```
```
Prices: A$ 1800=ton
```
B$ 7000=ton
```
C$ 13 000=ton (maximum demand: 1 ton/hr)
```
Investment cost
Fixed 10 3 $=hr
 
Variable 10 3 $=ton product
 
Process I 3.5 2
Process II 1 1
Process III 1.5 1.2
```
Note: Minimize negative of profit.
```
92 9 Mixed-Integer Nonlinear Programming
10 Generalized Disjunctive Programming
10.1 Logic-Based Formulation for Discrete/Continuous Optimization
```
We now consider the case of generalized disjunctive programming (GDP) models, which are
```
discrete and continuous optimization models that involve equations, disjunctions, and logic
```
propositions (Raman and Grossmann, 1994; Grossmann and Trespalacios, 2013). We should
```
note that disjunctive programming refers to linear programming with disjunctions as per the
```
pioneering work by Balas (1979, 2018). Here we denote the model as GDP because it involves
```
nonlinear functions in the continuous variables and, in addition to disjunctions, it contains
logic propositions in terms of Boolean variables. These variables are specified in each term of
the disjunction and serve as indicators as, if they are true, a subset of equations must also hold
true. In Chapter 7 we introduced GDP models for linear constraints, and showed how they
can be reformulated as MILP models, either through the big-M reformulation or through the
hull reformulation. In this chapter we assume that the functions are generally nonlinear.
More specifically, the GDP problem is given as follows:
min Z ¼
X
k2K
c k þ f xð Þ
```
s:t: r xð Þ  0
```
∨j2J k
Y jk
g jk xð Þ  0
c k ¼ γjk
2
64
3
75k 2 K
∨
j2J k
Y jk
Ω Yð Þ ¼ True
```
0  x  U, c k 2 R1 , Y jk ¼ True; Falsef g,
```
```
(GDP)
```
where x 2 R n are the continuous variables, Y jk are the Boolean variables that take values of
True or False, r xð Þ  0 are global inequalities that must always hold true, and K is the set of
disjunctions in terms of the OR operator ∨, in which each term j 2 J k or disjunct contains the
Boolean variable Y jk, the inequalities g jk xð Þ  0, and the cost variable c k , which is equated to
a fixed cost γjk. If the Boolean variable is True both the inequalities and the cost equation are
```
enforced; if the Boolean variable is False they are both ignored. Thus, each disjunct is
```
equivalent to an IF THEN ELSE condition. Because only one term of a disjunction k can
be true, we enforce the exclusive OR on the Boolean variables. Next, we specify the logic
propositions through the symbolic logic relations Ω Yð Þ ¼ True. Finally, bounds are specified
on the continuous variables x and the Y jk are declared as Boolean variables.
93
We should note that a major motivation for formulating discrete/continuous problems in the
form of GDP problems is that they can help to facilitate the formulation of a model because the
disjunctions and logic provide a higher level of representation that does not require the user to
pose the problem in terms of only algebraic equations as is the case in mixed-integer program-
```
ming. See, for instance, Castro and Grossmann (2012) for the contrast of formulations between
```
mixed-integer and GDP models in the area of batch-scheduling optimization.
```
In order to address the solution of problem (GDP), we first assume, as we did for problem
```
```
(MINLP), that f xð Þ, r xð Þ, g jk xð Þ are convex differentiable functions. We consider next three
```
```
major solution approaches to solving problem (GDP) (Grossmann, 2002; Trespalacios and
```
```
Grossmann, 2014).
```
```
(a) Reformulation to an MINLP problem, which can be accomplished either by formulating
```
each disjunction through equations describing the convex hull, or through big-M constraints.
```
(b) Disjunctive branch and bound that uses at each node a relaxation based on taking the
```
convex hull of each disjunction or using big-M constraints.
```
(c) Decomposition approach that partitions the problem into continuous NLP optimization
```
problems and discrete MILP master problems. Two possible approaches include the
logic-based outer approximation and logic-based generalized Benders decomposition.
10.2 Relaxations and Reformulations of GDP
```
In order to obtain an NLP relaxation of problem (GDP), we consider first the convex hull of
```
```
a given disjunction k in (GDP) (Lee and Grossmann, 2000). This can be defined by
```
considering variable points ujk , j 2 J k for each disjunction k such that
g jk ujk
 
```
 0 j 2 J k: (10.1)
```
Taking a linear combination of these points for all λjk  0 leads to
x ¼
X
j2J k
λjk u jk
X
j2J k
```
λjk ¼ 1: (10.2)
```
Performing a similar linear combination for the cost variable leads to
c k ¼
X
j2J k
```
λjk γjk : (10.3)
```
A geometric interpretation of these linear combinations is shown in Fig. 10.1.
Note that the term λjk ujk is bilinear. In order to linearize it, let
```
v jk ¼ λjk ujk , (10.4)
```
```
which, from (10.2), then leads to the linear equality
```
x ¼
X
j2J k
```
v jk , (10.5)
```
94 10 Generalized Disjunctive Programming
where 0  ujk  Uλjk . Because g jk ujk
 
 0 and ujk ¼ ν jkλjk , λjk  0, the inequality constraint
```
in (10.1) can be set to
```
λjk g jkv
jk
λjk
 
```
 0, (10.6)
```
where we also multiply the inequality by λjk . This, at first sight, is counterintuitive, but it has
the justification that it gives rise to the perspective function λg vλ
 
, which has the following
```
desirable property (Hiriart-Urruty and Lemaréchal, 2001):
```
Property 10.1 The perspective function λg v=λð Þ is convex if g ð Þ convex and λg vλ
 
! 0 as λ ! 0.
Furthermore, note that for λ ¼ 1 the perspective function reduces to g vð Þ  0, and, for
λ ¼ 0, it reduces to 0  0.
```
In this way, substituting (10.5) and (10.6) for each disjunction k 2 K, substituting c k in the
```
```
objective function, and converting the logic Ω Yð Þ ¼ True into linear inequalities Aλ  a (see
```
```
Section 7.1), and by representing the Boolean variables Y jk with the variables λjk , the NLP
```
```
relaxation of problem (GDP) is given as the following continuous relaxation problem (CRP):
```
CRPð Þ : min ZL ¼
X
k2K
X
j2J k
λjkγjk þ f xð Þ
```
s:t: r xð Þ  0
```
x ¼
X
j2J k
v jk k 2 K
λjk g v jk =λjk
 
 0 j 2 J k, k 2 K
X
j2J k
λjk ¼ 1 k 2 K
0  v jk  λjk U j 2 J k , k 2 K
Aλ  a
0  x  U, v jk  0, λjk  0 j 2 J k, k 2 K
```
(10.7)
```
```
where problem (CRP) in (10.7), which is a convex NLP, has the following property.
```
x2
S1
S2
x1
Figure 10.1 Convex hull of
x 2 S1∨x 2 S2 .
10.2 Relaxations and Reformulations of GDP 95
Property 10.2 The solution ZL
 ∗
```
of problem (CRP) yields a lower bound to solutions of
```
```
GDP. This property readily follows from the fact that problem (CRP) in (10.7) is a continuous
```
```
relaxation of problem (GDP).
```
```
We note that an MINLP reformulation of problem (GDP) is simply given by specifying in
```
```
(CRP) the λjk variables to be binary, that is λjk ¼ 0, 1, that is
```
MINLP-HRð Þ min Z ¼
X
k2K j
X
j2J k
γjkλjk þ f xð Þ
```
s:t: r xð Þ  0
```
x ¼
X
j2J k
v jk k 2 K
λjk g v jk =λjk
 
 0 j 2 J k, k 2 K
X
j2J k
λjk ¼ 1 k 2 K
0  v jk  λjk U j 2 J k, k 2 K
Aλ  a
0  x  U, v jk  0 λjk ¼ 0, 1 j 2 J k, k 2 K:
```
(10.8)
```
```
This MINLP is denoted as the hull-relaxation formulation (MINLP-HR) since it consists of
```
```
intersecting the convex hull of each disjunction (Balas, 1985; Ceria and Soares, 1999).
```
An alternate formulation to MINLP-HR is the big-M reformulation, in which the inequal-
ities are replaced by big-M constraints, the c k variables are substituted in the objective function,
the logic Ω Yð Þ ¼ True is converted into linear inequalities Aλ  a, and the Boolean variables
Y jk are represented by the 0-1 variables λjk . The big-M formulation is then as follows:
MINLP-BMð Þ min Z ¼
X
k2K j
X
j2J k
γjk þ f xð Þ
```
s:t: r xð Þ  0
```
g jk xð Þ  M jk 1  λjk
 
j 2 J k, k 2 K
X
j2J k
λjk ¼ 1 k 2 K
Aλ  a
0  x  U, λjk ¼ 0, 1 j 2 J k , k 2 K:
```
(10.9)
```
```
The relaxation of MINLP-BM, also a convex NLP, yields a lower bound to problem (GDP)
```
that obeys the following property.
Property 10.3 The relaxation of MINLP-BM is weaker or equal to the relaxation of
MINLP-HR. That is, their corresponding optimal objectives yield the following inequality:
```
Z RBM  ZCRP: (10.10)
```
96 10 Generalized Disjunctive Programming
This means that generally we can expect the hull relaxation to provide stronger lower
bounds than the big-M formulation. However, we should note that the advantage of the
latter is its smaller size compared to the hull-relaxation formulation. Which formulation will
require less computational time depends on the relative strength of both bounds and their
```
corresponding sizes. For computational experience see Lee and Grossmann (2000).
```
A difficulty in applying model MINLP-HR is that the perspective function λg v=λð Þ is
nondifferentiable at λ ¼ 0, thus potentially causing failures in the solution of this problem.
To overcome this problem, we replace the perspective function by the approximation pro-
```
posed by Furman et al. (2020). In particular, we consider, for λg v=λð Þ  0, 0  v  Uλ, the
```
approximation inequality
```
1  εð Þλ þ ε½ g v= 1  εð Þλ þ ε½ ð Þ  εg 0ð Þ 1  λð Þ  0: (10.11)
```
We can verify that if we set λ ¼ 0, which implies 0  v  0, the inequality reduces to
εg 0ð Þ  εg 0ð Þ ¼ 0  0, and therefore it is exact.
On the other hand, if we set λ ¼ 1, the inequality reduces to g v=1ð Þ  εg 0ð Þ 0ð Þ ¼ g vð Þ  0,
which again is exact.
In addition to the desirable property that the approximation is exact at λ ¼ 0 and λ ¼ 1,
```
the approximation function in (10.11) is convex in v and λ if g ð Þ is convex (see Exercise
```
```
10.2). Thus, this approximation has been used when implementing the hull reformulation.
```
10.3 Special Purpose Methods for GDP
10.3.1 Disjunctive Branch and Bound
```
First, we consider the disjunctive branch and bound method for solving problem (GDP).
```
Rather than presenting detailed steps, we illustrate the main idea with Fig. 10.2, in which it
```
can be seen that we start at the root node by solving the relaxation problem (CRP) in (10.7)
```
```
(or alternatively the relaxation of the big-M formulation in (10.9)) in order to obtain the
```
initial lower bound. Assuming a noninteger solution is obtained for any of the variables λjk ,
we typically branch on the disjunction k, which has a term j whose variable λjk is closest to
one. We then create a new node by imposing the constraints of that corresponding term j of
disjunction k and add to it the hull relaxation of the remaining disjunctions. For the
complementary node, we take the convex hull of the remaining terms in the disjunction j
and also add to it the hull relaxation of the remaining disjunction. Both nodes yield new
```
lower bounds or an upper bound if a feasible solution is found to problem (GDP).
```
```
Relaxation CRP (or big-M)
```
Fix disjunction
```
(least violations)
```
Convex-hull remaining terms of
disjunction plus other disjunctions
Fix
ljk
Figure 10.2 General branching
rule for disjunctive branch
and bound.
10.3 Special Purpose Methods for GDP 97
```
To illustrate the disjunctive branch and bound consider the following GDP problem (Lee
```
```
and Grossmann, 2000):
```
min Z ¼ x1  3ð Þ2 þ x2  2ð Þ2 þ c
```
s:t:
```
Y 1
x1ð Þ2 þ x2ð Þ2  1  0
c ¼ 2
2
64
3
75
∨
Y 2
x1  4ð Þ2 þ x2  1ð Þ2  1  0
c ¼ 1
2
64
3
75
∨
Y 3
x1  2ð Þ2 þ x2  4ð Þ2  1  0
c ¼ 3
2
64
3
75
```
0  x1 , x2  8, c  0, Y j 2 True; Falsef g j ¼ 1, 2, 3:
```
```
(10.12)
```
Figure 10.3 shows the three subregions S1 , S2 , and S3 , corresponding to each term of the
disjunction. As it can also be seen, the global optimum of this GDP problem of Z∗ ¼ 1:172,
lies at the point x1 ¼ 3:293, x2 ¼ 1:707, which in turn lies inside the subregion S2 from the
second disjunctive term.
```
If we start the branch and bound search by solving the relaxed GDP problem (CRP) in
```
```
(10.7), we obtain a lower bound of ZL ¼ 1:154 at the point x1 ¼ 3:159, x2 ¼ 1:797, which is
```
infeasible for the GDP problem. However, as can be seen in Fig. 10.4 that point is closest to
subregion S2. That in fact is reflected by the values of the λj variables, namely λ1 ¼ 0:016,
λ2 ¼ 0:995, λ3 ¼ 0:029, where it can be clearly seen that λ2 is the closest to the value of one
because it is in fact closest to the subregion S2.
It is then logical to branch on subregion 2 by setting λ2 ¼ 1 on one node, while for the
other node we evaluate the hull relaxation of the intersection of subregions S1 and S3. As
can be seen in Fig. 10.5a, we obtain an upper bound ZU ¼ 1.172 for the first node. For
the second node where we take the hull relaxation of S1 and S3 , we obtain a lower bound
S3
Global optimum
```
(3.293,1.707)
```
1.172Z* 
Local solutions
S1
```
(0,0) x1
```
x2
S2
```
Contour of ( )f x
```
Figure 10.3 Geometric
interpretation of GDP in
```
(10.12).
```
98 10 Generalized Disjunctive Programming
```
ZL ¼ 3.327 (Fig. 10.5b) which is infeasible as it satifies neither of the constraints in
```
subregions S1 and S3 . Since that lower bound ZL ¼ 3.327 exceeds the value of the current
upper bound ZU ¼ 1.172, this proves that the optimal GDP solution is given at that node in
which x1 ¼ 3:293, x2 ¼ 1:707. The logic that has been used in this disjunctive branch and
bound is summarized in Fig. 10.5c.
x2
x1
x*
```
(0,0)
```
S1
S2
S3
```
xL = (3.159,1.797)
```
Infeasible to GDP
Convex-hull
optimum, ZL = 1.154
Figure 10.4 Fixing least
violated disjunction.
x2
S1
```
(0,0)
```
S3
S2
x1
```
(b)
```
Upper bound
1.172ZU 
```
Second node: conv(S 1 S3)Optimal solution: 3.327ZL 
```
Lower bound
3.327ZL 
x2
S1
```
(0,0)
```
S3
S2
```
Optimal solution(3.293,1.707)
```
1.172Z* 
x1
First node: S2Optimal solution: 1.172ZU 
```
(a)
```
Y2
First nodeFix 1, 1.172Z 
] [3.293,1.707][x1, x2 
[0,1,0] 
Root nodeConvex hull of all S
i1.154Z 
[0.016,0.955,0.029] 
1
Second node
Convex hull of andS1 S3
3.327Z 
[0.337,0,0.623]  0
Y2
3.327ZL ZU 
Stop
L 1.154Z 
Branch on Y2
1.172ZU 
Backtrack
```
(c) Summary of branch and bound tree
```
l2
```
Figure 10.5 Branch and bound search applied to GDP (10.12).
```
10.3 Special Purpose Methods for GDP 99
10.3.2 Logic-Based Outer Approximation
We describe in this section the logic-based outer-approximation algorithm by Türkay and
```
Grossmann (1996). For simplicity, in the derivation of this algorithm we consider a special
```
```
case of the problem (GDP), namely one that involves only two terms, and where the
```
negation involves setting to zero a subset of the continuous variables. The special case is
```
then given by the following GDP in (10.13):
```
GDP0ð Þ min Z ¼
X
k2K
c k þ f xð Þ
```
s:t: r xð Þ  0
```
Y k
g k xð Þ  0
c k ¼ γk
2
64
3
75∨
¬Y k
B k x ¼ 0
c k ¼ 0
2
64
3
75 k 2 K
Ω Yð Þ ¼ True
```
0  x  U, c k 2 R1 , Y k ¼ True; Falsef g,
```
```
(10.13)
```
where the B k matrix is introduced for setting to zero a subset of x when Y k ¼ False, namely,
B ii ¼
1 if x i set to zero
0 if x i not set to zero
```
(
```
B ij ¼ 0 i 6 ¼ j:
Note that this structure arises in process-synthesis problems where the Boolean variables Y k
indicate whether a given unit k is selected or not.
The basic idea in the logic-based outer-approximation algorithm is to solve a sequence of
NLP and GDP or MILP master problems in a similar manner to the original method. The big
difference, however, is that a reduced NLP is solved, in which only the equations describing
the selection of a given unit k are included as well as the definition of zero values for the units
```
that are not selected. The reduced NLP (r-NLP) for fixed Y k is then given as follows:
```
r-NLPð Þ min Z ¼
X
k2K
c k þ f xð Þ
```
s:t: r xð Þ  0
```
g k xð Þ  0
c k ¼ γk
```
)
```
for Y k ¼ True
B k x ¼ 0
c k ¼ 0
```
)
```
for Y k ¼ False
0  x  U:
```
(10.14)
```
In order to define the master problem, we assume we are given linearizations at iterations
ℓ ¼ 1, . . . , L and iterations L k ¼ ℓjY k ¼ True iteration ℓf g. Notice that this requires that a
```
number of reduced NLPs (r-NLP) are solved so as to cover all the disjunctive terms that are
```
true. For small or simple problems, these reduced NLP problems can be easily identified. As
an example, consider the simple superstructure in Fig. 10.6 consisting of four units arranged
100 10 Generalized Disjunctive Programming
in two processing stages, and where only one unit can be selected at each stage. A simple way
to generate two reduced NLPs is to consider one alternative with units 1 and 3, and the other
with units 2 and 4. Each of these alternatives gives rise to two reduced NLPs of the form
```
(r-NLP), whose solutions can then be used to obtain linearizations for the four units.
```
```
For more general problems, one can formulate a set-covering problem (see Section
```
```
6.1.3.4) to identify the fewest reduced NLPs that cover all the true terms of the disjunction.
```
The linear GDP master problem MOAGDP is then given as follows:
```
MOAGDP : min ZLOA ¼ α
```
```
s:t:
```
α 
X
k2K
c k þ f xℓ
 
þ rf xℓ
 
x  xℓ
 
r xℓ
 
þ rr xℓ
 T
x  xℓ
 
 0
9
>=
```
>;ℓ ¼ 1, . . . , L
```
Y k
g k xℓ
 
rg xℓ
 T
x  xℓ
 
 0 ℓ 2 L k
c k ¼ γk
2
66
4
3
77
5∨
¬Y k
B k x ¼ 0
c k ¼ 0
2
66
4
3
77
5 k 2 K
Ω Yð Þ ¼ True
```
0  x  U, c k 2 R1 Y k ¼ True; Falsef g:
```
```
(10.15)
```
This master problem can be reformulated as an MILP by using either the big-M formulation
or the hull-relaxation formulation described in Chapter 7. The master problem can also be
solved with a disjunctive branch and bound method as described in Section 10.3.1.
The steps of the logic-based OA algorithm are then as follows.
```
Step 0. Solve reduced NLPs (r-NLP) to cover all the disjunctions, i.e., L k 6 ¼ ∅ k 2 K.
```
Step 1. Solve MOAGDP with either of the two following solution approaches.
```
(a) Transform to MILP hull relaxation or big-M ! ZLOA .
```
```
(b) Use disjunctive branch and bound to determine Y new .
```
```
Step 2. Solve NLP (r-NLP) for Y new ! ZU upper bound.
```
Continue until ZLOA ’ ZU .
We should note that, for nonconvex GDP problems, one can add slack variables as in the
```
MILP master (9.23) in Chapter 9 for the OA algorithm with augmented penalty and
```
equality relaxation.
Superstructure
1
2
3
4
42NLP2NLP1 1 3
Figure 10.6 Example of superstructure optimization and two initial alternatives for generating
linearizations through NLP subproblems NLP1 and NLP2.
10.3 Special Purpose Methods for GDP 101
EXERCISES
10.1 Consider the case of disjunctions with linear constraints,
∨j2J kAjk x  bjk

:
```
Show that the nonlinear convex hull given by (10.5) and (10.6) reduces to
```
x ¼
X
j
v jk k 2 K
Ajk v jk  bjkλjk j 2 J k, k 2 K
X
λjk ¼ 1 k 2 K
0  v jk  Uλjk j 2 J k, k 2 K:
10.2 Prove that, for the perspective function λg v=λð Þ  0, and for which 0  v  Uλ, the
left-hand side in the approximation inequality is convex if g ð Þ is convex:
1  εð Þλ þ ε½ g v= 1  εð Þλ þ ε½ ð Þ  εg 0ð Þ 1  λð Þ  0:
10.3 Given the figure below, formulate the MINLP problem in which either x1 and x2 lie
within the area of the circle with a cost 2x1 + x2 , or else lie at the origin with zero cost.
```
(a) Formulate the problem first as a nonlinear GDP.
```
```
(b) Transform it into an MINLP without using big-M constraints and simplify it by
```
eliminating disaggregated variables.
1
1
2
2 x1
x2
10.4 For the generalized disjunctive program given below, do the following.
```
(a) Reformulate it as an MINLP using the convex-hull formulation for the disjunction.
```
```
(b) Reformulate it as a big-M MINLP (M = 50).
```
```
(c) Solve both reformulations and compare their relaxations.
```
minZ ¼ c þ ðx1  3Þ2 þ ðx2  2Þ2
st
Y 1
x21 þ x22  1
c ¼ 2
2
64
3
75∨
Y 2
ðx1  4Þ2 þ ðx2  1Þ2  1
c ¼ 1
2
64
3
75∨
Y 3
ðx1  2Þ2 þ ðx2  4Þ2  1
c ¼ 3
2
64
3
75
0  x1  8, 0  x2  8, Y j ¼ True, False, j ¼ 1, 2, 3
102 10 Generalized Disjunctive Programming
11 Constraint Programming
11.1 Logic-Based Modeling
```
Constraint programming (CP) is a logic-based approach to optimization that makes use of
```
```
implicit functions and logic inference (Van Hentenryck, 1989; Hooker, 2002; Hooker and van
```
```
Hoeve, 2018). There is no canonical form in constraint programming as it provides flexibility for
```
a variety of variables and constraints that can be handled. Specifically, we have the following.
```
(a) Variables: continuous, Boolean, discrete.
```
```
(b) Constraints:
```
```
– algebraic h xð Þ  0;
```
```
– disjunctions A1x  b1½ ∨ A2x  b2½ ;
```
– conditional constraints
```
if x ¼ y ) zy  w;
```
– global constraints, for example,
```
all different x i; i ¼ 1; . . . ; nð Þ x i-integer;
```
– cumulative constraint
```
Cum. t1 , t2; . . . , t nð Þ; D1 , D2; . . . , D nð Þ; c1 , c2; . . . , c nð Þ, C
```
```
ti start time, job D i consumes resource c i, C resource limit;
```
– meta constraints
x 6 ¼ yð Þ þ y 6 ¼ zð Þ þ z 6 ¼ xð Þ  2:
Constraint programming is largely aimed at finding feasible solutions to a set of constraints
such as those shown above, but it is also possible to optimize for a given objective function.
However, as we will see below, the search will consist of finding a sequence of feasible
solutions with a specified decrease in the objective function.
An example of a CP model is the following:
Find x, y, z
```
Continuous: x  5 y  0
```
```
Integer: z ¼ 0, 1, 2, 3, 4
```
x3 þ 10x ¼ yx  2z
zx þ 7:7y ¼ 2:4
z  1ð Þyþ1  10
ℓn y þ 2x þ 12ð Þ  z þ 5½ ∨ y  z2
 
```
) x  0 ^ y  1f g
```
 
```
x  0 ) z > 3:
```
```
(11.1)
```
103
```
The solution to the CP problem in (11.1) is x ¼ 1:28505, y ¼ 0:979, z ¼ 4.
```
```
It is interesting to note that the CP problem in (11.1) can be reformulated as a GDP
```
problem by reformulating the last two constraints by using the following equivalent logic
```
statements (see Chapter 7, Section 7.1).
```
```
For the second to last A∨B ) C ^ D is equivalent to ¬A ^ ¬B ∨ C ^ Dð Þ.
```
```
For the last constraint C ) E is equivalent to ¬C∨E.
```
```
By rewriting the last two logic expressions in (11.1) using these equivalent statements, the
```
```
CP in (11.1) can be rewritten as the following GDP problem in which we specify a zero value
```
for the objective as it is a feasibility problem:
min Z ¼ 0
```
s:t: x3 þ 10x ¼ yx  2z
```
zx þ 7:7y ¼ 2:4
z  1ð Þyþ1  1 0
Y 1
ℓn y þ 2x þ 12ð Þ  z  5  ε
y  z2  ε
2
66
4
3
77
5∨
Y 2
x  0
y  1
2
66
4
3
77
5
W 1
x  ε
" #
∨
W 2
z  4
" #
x  5, y  0, z ¼ 0, 1, 2, 3, 4, Y 1 , W 1 ¼ True, Y 2 , W 2 ¼ False:
```
(11.2)
```
As a second example, we consider the traveling salesman problem that we considered in
Chapter 6. First, assume we label all the cities with an integer n ¼ 1, 2, . . . , N. Let y k be an
integer variable that represents city n visited in kth position of the tour. For instance, if
y1 ¼ 3, city 3 is visited first. Furthermore, let c yk ykþ1 be the travel cost from city yk to y kþ1 .
Notice that we are defining a cost coefficient that has as indices the variables yk and y kþ1 . In
this way, the TSP problem can be formulated as the following CP problem
Select yk 1, . . . , N
min
XN
k¼1
c yk ykþ1
```
s:t: all different yk ; k ¼ 1; . . . ; Nð Þ,
```
```
(11.3)
```
where the all-different constraints ensure that different integer labels of the cities are
```
assigned to the variables y k. Notice that, with (11.3), we can write the traveling salesman
```
problem in a very compact form given the capability of handling indices as variables and
given the implicit constraint “all different.”
104 11 Constraint Programming
11.2 Search in Constraint Programming
11.2.1 Domain Reduction and Constraint Propagation
The search for a feasible and/or optimum solution in CP relies on an implicit enumeration of
a tree in which no LP relaxation is solved, but instead a domain reduction and constraint
propagation are performed at each node.
The first major element of the CP search is a depth-first search on the tree of
discrete or interval alternatives. Lower bounds are simply obtained by partial solutions
in the tree, while upper bounds correspond to feasible solutions found in the tree
enumeration.
The second major element of the CP search is domain reduction and constraint
propagation, which in many ways is unique to CP, and often a major reason for its successful
performance. Domain reduction and constraint propagation do not rely on general-purpose
algorithms, because they correspond to specific algorithms for different classes
of constraints.
An example is bounds tightening for linear constraints. Consider the constraints,
X
j
```
c j xj 2 L; U½ 
```
xj 2 ℓj , u j
 
,
```
(11.4)
```
where c j , L, U > 0.
```
Because Pj c j x j  L ) x i  L=c i  Pj6¼ i c j xj =c i, this in turn means that the smallest
```
lower bound occurs at the upper bound, x j ¼ uj , and hence, the tightest lower bound of x i
is given by the inequality,
x i  L=c i 
X
j6¼ i
```
c j uj =c j 8i: (11.5)
```
```
Similarly, because Pj c j x j  U ) x i  U=c i  Pj6¼ i c j x j =c i, this in turn means that the
```
largest upper bound occurs at the lower bound, x j ¼ l j , and hence the tightest upper bound
of xi is given by the inequality
x i  U=c i 
X
j6¼ i
```
c j l j =c i 8i: (11.6)
```
In summary, we can set as a result of the tightening of bounds the following:
```
Lower bound x i ¼ max l i; L=c i 
```
P
j6¼ i c j u j
c i
 
```
(11.7)
```
```
Upper bound x i ¼ min ui; U=c i 
```
P
j6¼ i c j l j
c i
 
```
: (11.8)
```
11.2 Search in Constraint Programming 105
```
(a) As a specific example, consider the linear equality with corresponding variable bounds,
```
2x þ 3y ¼ 11
```
x  0 y  0: (11.9)
```
For the case where the variables x, y are continuous, assume L ¼ 0, U ¼ 11.
```
Then it follows from (11.8) that the tightest upper bound is given by
```
```
x ¼ 11  3y2 , y ¼ 0 ) x ¼ 5:5
```
```
y ¼ 11  2x3 , x ¼ 0 ) y ¼ 3:66:
```
```
Hence, we can conclude that the tightest bounds for the linear inequality in (11.9) are
```
given by x 2 0, 5:5½  y 2 0, 3:66½ .
```
(b) Consider now the case where x, y are integer in the linear inequality in (11.9). If we
```
simply round down the fractional values obtained, the tightest bounds are given by
x 2 0, 5½ , y 2 0, 3½ .
We should note that, for nonlinear constraints, it is generally more difficult to infer tight
bounds unless the constraints have the property of monotonicity.
One additional example for domain reduction and constraint propagation is “edge-finding
conditions” for job-shop scheduling. Consider a pair of jobs with corresponding start times
and duration:
job i Ts i start time job i duration d i
job j Ts j start time job j duration d j
and for which the following disjunction holds:
Ts i þ d i  Ts j
 
∨ Ts j þ d j  Ts i
 
```
: (11.10)
```
That is, job i is executed before job j, or job j is executed before job i. The disjunction in
```
(11.10) can be expressed in terms of 0-1 and continuous variables as was shown in Chapter 7
```
```
(Section 7.2). Instead, in CP the disjunction is resolved by a procedure that is based on
```
analyzing earliest starts and latest ends. The procedure is known as “edge-finding condi-
```
tions” and was developed by Applegate and Cook (1991).
```
Let est ¼ earliest start, and lte ¼ latest end.
If ltei  esti  d j þ d i

and ltej  esti  d j

then job j must be executed before job i.
Consider the example in Fig. 11.1.
Applying the edge-finding conditions to the data in Fig. 11.1, this implies that job j must
take place before job i.
11.2.2 Tree Search
The search in CP consists of a depth-first enumeration of a tree with domain reduction at
```
each node (or logic inference; arc consistency).
```
106 11 Constraint Programming
To illustrate the tree enumeration in CP, consider the following example:
Find integer x, y, z
x 2 1, 3½  y 2 1, 3½  z 2 1, 3½ 
```
s:t: y < z
```
x  y ¼ 1
x 6 ¼ z:
```
(11.11)
```
Notice that the strict inequality y < z can be specified in CP, whereas in mathematical
programming no strict inequalities are allowed. But because the variables are integers one
would express that constraint in mathematical programming as y  z  1.
It can be shown that the maximum potential number of nodes in the tree search is 40. By
using the “generate and test” paradigm and by using domain reduction and constraint
```
propagation the search requires many fewer nodes and is as follows (see Fig. 11.2).
```
At the initial node 1, we can infer from x  y ¼ 1, that x 2 2, 3½  and y 2 1, 2½ , which in
turn means that, for x ¼ y þ 1 and y  z  1 or y þ 1  z, this implies z 2 2, 3½ .
```
If we start branching with x, we have x ¼ 2, from x  y ¼ 1, this implies y ¼ 1 (node 2).
```
On the other hand, if we set x ¼ 3, because x  y ¼ 1, this implies y ¼ 2. Furthermore,
y þ 1  z, which implies z ¼ 3. But this implies that the constraint x 6 ¼ z is violated. Hence,
node 3 is infeasible and can be fathomed.
If we now branch on node 4, by setting y ¼ 1, we have that because x 6 ¼ z must be
satisfied, z ¼ 1 or z ¼ 3. Since y þ 1  z, this implies we can set z ¼ 3 at node 4. As no
more nodes are open, this proves that x ¼ 2, y ¼ 1, z ¼ 3 is the feasible solution satisfying
```
the inequalities in (11.11).
```
job i
job j
est
est
lte
lte
15
0 10 20 30
10Figure 11.1 Jobs i and j with
corresponding earliest start times
```
(est) and latest end times (lte).
```
[2,3], [1, 2], [2,3]x y z   
3x 
1y  infeasible
2x 
1y 
3z 
1
2 3
4
Figure 11.2 Tree enumeration in
CP with constraint propagation.
11.2 Search in Constraint Programming 107
This simple example, then, illustrates the capability of inference and constraint
propagation of CP. Note that in “classical” branch and bound, the generate and test method
ends up typically enumerating a larger number of nodes because it usually does not perform
```
domain reduction and constraint propagation (except for recent versions of CPLEX,
```
```
GUROBI, and XPRESS).
```
In summary, CP problems are represented by a compact syntax in specialized modeling
```
software (e.g., OPL, Van Hentenryck et al., 1989). Although CP is aimed at feasibility/
```
discrete problems, optimization can be performed by solving a sequence of feasibility
problems, where we update the upper bound f xð Þ  UB  δ, where δ is the specified
decrease. The optimization in CP performs reasonably well on simple objective functions
```
(e.g., makespan in scheduling), but does not perform as well if there are many variables in
```
```
the objective function (e.g., total cost).
```
EXERCISES
11.1 The all-different constraints yi 6 ¼ y j i 6 ¼ j, where y i are integer variables n, can be
regarded as a disjunction
∨k¼1, Kz iky
i ¼ k
 
8i
in which, for z ik ¼ True, this implies that yi ¼ k.
Show that by using the convex full formulation of this disjunction, the “all-different
constraint” can be modeled through the following set of 0-1 linear constraints,
yi ¼
X
k
kz ik 8i
X
k
kz ik ¼ 1 8i
X
i
z ik  1 8k
z ik ¼ 0, 1:
11.2 Verify in Fig. 11.1 that job j must be executed before job i, both by inspection and by
applying the “edge-finding” conditions.
108 11 Constraint Programming
12 Nonconvex Optimization
12.1 Major Approaches to Global Optimization
```
When addressing the solution of NLP problems (12.1) or more generally MINLP problems
```
```
(12.2) these give rise to nonconvex optimization problems (Horst and Tuy, 1996;
```
```
Tawarlamani and Sahinidis, 2004). In the case of NLP problems, the nonlinear equations
```
h xð Þ ¼ 0 generally introduce nonconvexities unless they can be shown to relax as convex
inequalities. Furthermore, if either the objective function f xð Þ is nonconvex and/or the
inequalities g xð Þ  0 are nonconvex, the NLP will be nonconvex which means that there
is a distinct possibility that it may exhibit more than one local minima:
min f xð Þ
```
s:t: h xð Þ ¼ 0
```
g xð Þ  0
x 2 Rn:
```
(12.1)
```
In the case of MINLP problems, the nonconvexity first arises from the fact that the
discrete variables y define a nonconvex feasible region. This, in turn, implies that MILP
problems, despite having linear objective and constraints, are also nonconvex. Similarly, as
in NLP problems, nonconvexities may be due to the nonlinear equations and nonconvex
objective function and inequalities:
```
min f x; yð Þ
```
```
s:t: h x; yð Þ ¼ 0
```
```
g x; yð Þ  0
```
x 2 X , y 2 Y :
```
(12.2)
```
```
The three major approaches that are used in global optimization are: (a) convexification,
```
```
(b) heuristics, and (c) global optimization. The approach based on heuristics does not yield
```
rigorous global-optimum solutions and relies on computational strategies such as multistart
strategies from different initial points, typically generated at random. It can also rely on
modifying subproblems such as the MILP master problem of the OA algorithm in Section
9.4 of Chapter 9 in which slack variables and a penalty function are introduced to avoid
```
cutting off a feasible solution (see (9.23)), and modifying termination criteria (e.g., continue
```
```
search until no improvement is found). We should also note that, for the particular case of
```
concave separable objective and linear constraints, the problem can be approximated
```
through MILP using special ordered sets, as described in Beale and Forrest (1976).
```
109
We discuss in the next sections the approaches based on convexification and global
optimization.
12.2 Convexification
In a number of special cases it is possible to convexify an NLP problem or the NLP
relaxation of an MINLP problem so that the corresponding problems yield a unique local
optimum solution.
The presence of posynomials is a particular structure that can be exploited for convex-
ifications. A posynomial is formally defined as a function of the following form, consisting of
sums of products of variables raised to an arbitrary exponent,
f xð Þ ¼
X
i
c i
Y
j
```
xαijj , (12.3)
```
where c i > 0 and αij is an arbitrary exponent. These functions arise in a special class of NLP
```
problems known as geometric programs (Duffin et al., 1967), in which the objective function
```
and constraints correspond to posynomials.
Consider the transformation
```
xj ¼ e uj ; (12.4)
```
```
if we apply it to the posynomial in (12.3) this yields the transformed function,
```
f uð Þ ¼
X
i
c i
Y
j
eαij uj ¼
X
i
c i e
P
```
j αij uj , (12.5)
```
which can easily be shown to be convex as it consists of a sum of positive convex
functions.
```
As one specific example, consider the nonconvex inequality (linear fractional plus concave
```
```
separable)
```
x1
x2þ x
```
0:51  1: (12.6)
```
```
Substituting (12.4) yields
```
```
e u1 eu2 þ e0:5u1  1: (12.7)
```
This, in turn, can be rearranged as
```
e u1u2 þ e0:5u1  1, (12.8)
```
which corresponds to a convex inequality since both terms are convex.
Special cases are monomials, in which we have an inequality with a posynomial at each
side of the inequality. As an example, consider the monomial
110 12 Nonconvex Optimization
x1
x2 x
```
0:51 : (12.9)
```
```
This implies, by substituting (12.4),
```
```
e u1 eu2  e0:5u1 (12.10)
```
or
```
e u1u2  e0:5u1 : (12.11)
```
And finally, by taking natural logs on both sides, this yields
```
u1  u2  0:5u1 , (12.12)
```
which is a linear inequality. Thus, monomials can always be transformed into
linear inequalities.
12.3 Global Optimization of Bilinear Programs
Global-optimization methods can be classified first as deterministic methods in which global
solutions can be mathematically guaranteed for structured problems that include the
```
following types of functions (Tawarlamani and Sahinidis, 2004):
```
– concave functions
– bilinear, linear fractional
– difference of convex functions.
These methods can guarantee global optimality because they rely on valid convex
underestimators. As an example, Fig. 12.1 illustrates the use of a secant for underestimating
concave functions. The secant is denoted as a convex envelope since it is the
tightest underestimator.
Global-optimization methods can also be classified as stochastic methods that can handle
```
general types of functions. These methods include (Eiben and Smith, 2003):
```
```
g(x) = f (a)+ b − af (b) − f (a) (x − a)
```
a b x
```
f (x) secant g (x)Figure 12.1 Secant for
```
underestimating
concave functions.
12.3 Global Optimization of Bilinear Programs 111
– simulated annealing
– genetic algorithms.
These methods unfortunately have no mathematical guarantees of global optimality unless
they are evaluated at an infinite number of trial points.
In this section, we focus on deterministic global-optimization methods for bilinear pro-
```
grams (Sherali and Alameddine, 1992; Quesada and Grossmann, 1995) in order to illustrate
```
the main ideas behind deterministic global-optimization methods. The general form of a
bilinear NLP is as follows:
NLP-b : min Z ¼ f 0 xð Þ
```
s:t: f ℓ xð Þ  0 ℓ ¼ 1, 2, . . . , L
```
x 2 X , xL  x  xU ,
where X ¼ xjx 2 Rn, Ax  bf g and f ℓ ¼ Pi2IPj2J cℓij x i x j þ gℓx, ℓ ¼ 0, 1, . . . , L, where
gℓ xð Þ are convex functions.
The most common method for solving global-optimization problems such as the bilinear
```
NLP-b, is the spatial branch and bound method (Horst and Tuy, 1996). This method relies
```
on three basic elements:
– LP or NLP relaxation that yields lower bounds,
– upper bounds given by a local or feasible solution to nonconvex
NL-b,
– search in the space of continuous variables by generating subregions that are to be
analyzed by a branch and bound search.
```
The LP relaxation for bilinear terms is given by the McCormick (1976) convex
```
envelopes. These are derived as follows. Let x, y, be two continuous variables specified
within lower and upper bounds, xL  x  xU, yL  y  yU . We will use the principle
```
that for g1  0, g2  0 ) g1∗g2  0. Defining g1 ¼ xL  x  0, g2 ¼ yL  y  0, we then
```
have
```
xy  xyL þ xLy  xLyL: (12.13)
```
Similarly, let g1 ¼ xU  x  0, g2 ¼ yU  y  0, which implies g1∗g2 ¼ xUyU  xUy
xyU þ xy  0, or
```
xy  xUy þ xyU  xUyU: (12.14)
```
```
Notice that the right-hand side in the inequalities in (12.13) and (12.14) represent linear
```
underestimators of the bilinear term xy.
Also, from g1 ¼ x  xL  0, g2 ¼ yU  y  0, g1∗g2 ¼ xyU  xy  xLyU þ xLy  0,
which leads to
```
xy  xyU þ xLy  xLyU , (12.15)
```
and with g1 ¼ xU  x  0, g2 ¼ y  yL  0, g1∗g2 ¼ xUy  xUyL  xy þ xyL  0, or
112 12 Nonconvex Optimization
```
xy  xyL þ xUy  xUyL: (12.16)
```
```
Notice that (12.15) and (12.16) represent linear overestimators of the bilinear term x y. In
```
```
summary, the inequalities (12.13)–(12.16) represent the McCormick convex envelopes of the
```
bilinear term x y. These convex envelopes, which correspond to the tightest underestimators
and overestimators of the bilinear term x y, are displayed in Fig. 12.2.
The following property holds for the McCormick envelopes.
```
Property 12.1 The inequalities (12.13)–(12.16) are exact at the bounds of x y (boundary
```
```
of x y).
```
```
As an illustration, from (12.13) set x ¼ xL . This then leads to xLy 
```
xLyL þ xLy  xLyL ¼ xLyL , or xLy  xLyL , i.e., we obtain an exact approximation.
```
Making use of the convex envelopes in (12.13)–(12.16), we can define the relaxation
```
problem RP for the bilinear problem NLP-b by substituting the inequalities for the corres-
ponding bilinear terms u ij ¼ x i x j :
min Z R ¼
X
i2I
X
j2J
c0ij uij þ g0 xð Þ
```
s:t:
```
X
i2I
X
j2J
cℓij uij þ gℓ xð Þ  0 ℓ ¼ 1, . . . , L
uij  x i xLj þ xLi x j  xLi xLj
uij  x i xUj þ xUi x j  xUi xUj
uij  x i xUj þ xLi xj  xLi xUj
uij  x i xLj þ xUi xj  xUi xLj
9
>>>
>>=
>>>
```
>>;
```
i 2 I , j 2 J
xL  x  xU , uL  u  uU , x 2 X :
```
(RP)
```
We can establish the following properties.
Underestimators
Overestimators
x
yFigure 12.2 Geometrical
interpretation of McCormick
convex envelopes for bilinear
term xy.
12.3 Global Optimization of Bilinear Programs 113
```
Property 12.2 The relaxation problem (RP) is a convex NLP problem.
```
```
This simply follows from the fact that problem (RP) involves a convex objective function
```
```
and convex inequalities. Note that if gℓ xð Þ is linear, (RP) reduces to an LP problem.
```
```
Furthermore, being convex, problem (RP) has a unique optimum solution.
```
```
Property 12.3 The relaxation problem (RP) yields a lower bound Z R to problem (NLP-b);
```
i.e., Z R  Z∗.
```
This follows from the fact that we relaxed u ij ¼ x i y j by the inequalities in (RP).
```
We should also note that not all convex envelopes may be required. For example, assume
that a given bilinear term is only present in the objective function. In that case,
```
– if c0ij > 0 we only need the lower bounding inequalities uij     (12.13), (12.14);
```
```
– if c0ij < 0 we only need the upper bounding inequalities uij     (12.15), (12.16).
```
It is also important to note that tight bounds, xL , xU , are required to obtain a tight lower
```
bound from the relaxation problem (RP). This can be accomplished by a bound-tightening
```
procedure that involves successively minimizing and maximizing the value of each variable
```
x i (Zamora and Grossmann, 1999):
```
xL ! min x i xU ! max x i
```
s:t: constr: RPð Þ s:t: constr: RPð Þ:
```
```
(12.17)
```
The upper bound for the objective function can generally be obtained by finding a local
solution to NLP-b. For the special case that the nonlinear terms are convex in NLP-b, a
feasible point in that problem also yields an upper bound.
Finally, the branch and bound search is conducted in a similar way as for MILP and
MINLP problems, except that the branching is performed through region elimination. In
```
particular, if in a given subregion, when solving the corresponding relaxation problem (RP),
```
```
the lower bound lies below the upper bound, then we partition the subregion; otherwise we
```
reject the subregion. This partition is illustrated in Figs. 12.3 and 12.5 for one and two
variable problems. In Fig. 12.4 we show the corresponding tree search after performing two
partitions in the one variable problem of Fig. 12.3.
Multiple minima
Objective
Lower bound
```
UB = Upper bound
```
= LB
Multiple minima
Objective
Lower bound
= LB
= LB
```
(a) (b)
```
Figure 12.3 Successive partition of region in a one-dimensional problem.
114 12 Nonconvex Optimization
We should note that the variable bounds are updated in each subregion. Also, for the
general case, we need to decide on what bilinear terms x i xj to branch. A common branching
rule is as follows.
```
(a) Select term xi x j with largest difference from uij , d ij ¼ uij  x i x j .
```
```
(b) Determine for x i the sum difference Pk6¼ i d ij in all terms x i xk , k 6 ¼ i, and for xj the sum
```
difference Pk6¼ j d ij in all terms xk xj , k 6 ¼ j.
```
(c) Select x i or x j with largest sum differences.
```
Qualitatively, the idea behind this branching rule is to select the variable that leads to the
largest difference with respect to the variable u ij .
Finally, as an example, consider the following bilinear problem, P.
```
P : min f ¼ x  y
```
```
s:t: xy  4
```
0  x  6
0  y  4:
```
(12.18)
```
The plot of the feasible region of problem P is shown in Fig. 12.6.
```
The relaxation problem (RP) is given as follows:
```
```
RP : min f ¼ x  y
```
```
s:t: u  4
```
u  xyL þ xLy  xLyL
u  xyU þ xUy  xUyU
u  xyL þ xUy  xUyL
u  xyU þ xLy  xLyU
0  x  6 0  y  4:
```
(12.19)
```
LB < UB
LB < UBLB > UB
Figure 12.4 Branch and bound
tree from partitions in Fig. 12.3.
1 2
x1
x2
```
(a)
```
3
4
x2
x1
```
(b)
```
Figure 12.5 Successive elimination
of subregions in two dimensions.
12.3 Global Optimization of Bilinear Programs 115
Substituting the corresponding bounds yields the LP problem,
```
LP : min f ¼ x  y
```
```
s:t: u  4
```
u  0
u  4x þ 6y  24
u  6y
u  4x
0  x  6 0  y  4:
```
(12.20)
```
This yields the solution x ¼ 6, y ¼ 0:666, u ¼ 4, with objective value f ∗ ¼ 6:67, which
corresponds to the global-optimum solution. That is, the global optimum is obtained at the
initial relaxation of problem NLP-b shown in Fig. 12.7. This is due to the fact that, because
u ¼ 4, the inequality 4x þ 6y  24  4, which reduces to 4x þ 6y  28, corresponds to the
inequality shown in Fig. 12.7, which together with the bounds on the variables, defines the
linear convex hull of the feasible region, which has a minimum value of –6.66 at the extreme
```
point (6, 0.666).
```
0 1 2 3 4 5 6 7
0
1
2
3
4
5 5f *  
6.67f *  
y
x
44 6 24x y 
Figure 12.7 Plot of relaxation
```
(RP).
```
0 1 2 3 4 5 6 7
0
1
2
3
4
5 5f *  
6.67f *  
y
x
Figure 12.6 Plot of feasible region
for problem P.
116 12 Nonconvex Optimization
12.4 Global Optimization of More General Functions
We should note that the area of global optimization has expanded considerably beyond the
solution of bilinear NLP problems. The trend has been to accommodate a large class of
algebraic functions for which convex envelopes are developed for their use in spatial branch
```
and bound methods (e.g., Quesada and Grossmann, 1995; Adjiman et al., 1998; Tawarmalani
```
```
and Sahinidis, 2005). Global optimization has also been extended to MINLP problems (e.g.,
```
```
Kesavan et al., 2004; Misener and Floudas, 2013). Recent reviews on global-optimization
```
```
algorithms can be found in Floudas and Gounaris (2009) and Tawarmalani and Sahinidis
```
```
(2013). Appendix A summarizes the software such as BARON, Antigone, and SCIP, that is
```
currently available for solving nonconvex NLP and MINLP problems.
EXERCISES
12.1 Replace the following nonlinear inequality by a linear inequality that rigorously
bounds the feasible space defined by that inequality:
x1x2  8, where 0  x1  4, 0  x2  6.
12.2 Determine whether the following inequalities can be reformulated as convex inequalities:
x1x2  9
x1  2x2  0
x1 , x2  1:
12.3 Assume that the following MINLP problem is solved with both the NLP-based branch
and bound and the outer-approximation method:
min f 0 xð Þ þ aT0 y
```
s:t: f j xð Þ þ aTj y  b j ¼ 1, 2, . . . , n
```
xL  x  xU , x 2 R n, y ¼ 0, 1f gm,
where f j xð Þ ¼ Pi c iQk xαikk , c i  0, and αik is arbitrary. Determine if each of these
methods is guaranteed to find the global solution to this MINLP.
12.4 Consider the product y∗x in a constraint of an MINLP, where y ¼ 0, 1. In order to
linearize this term, it is proposed to use the Glover inequalities that involve a new
variable w ¼ y∗x:
x  1  yð ÞxU  w  0
w  x þ 1  yð ÞxL  0
yxL  w  0
w  yxU  0:
Develop alternative constraints using disjunctive programming as a basis.
Determine if your new constraints have a weaker, stronger or equivalent relaxation
to Glover’s inequalities.
Exercises 117
12.5 Given the bilinear NLP below, find the global-optimal solution using the McCormick
convex envelopes and a spatial branch and bound. To obtain good initial lower and
upper bounds solve LPs for the bounds of the four continuous variables:
min f ¼ x1  x2  y1  x1y1 þ x1y2 þ x2y1  x2y2
```
s:t: x1 þ 2x2  8
```
4x1 þ x2  12
3x1 þ 4x2  12
2y1 þ y2  8
y1 þ y2  5
0  x1 , x2 , y1 , y2  10:
Verify your answer with the software packages BARON and ANTIGONE in GAMS.
```
(Use OPTION NLP=BARON or ANTIGONE.)
```
118 12 Nonconvex Optimization
13 Lagrangean Decomposition
13.1 Overview of Decomposition for Large-Scale Problems
When addressing the solution of large-scale optimization problems, it becomes necessary at
some point to decompose them in order to avoid the solution of very large-scale problems,
and thereby achieve reasonable computational times. Two major structures that arise in
decomposition, and which we illustrate here for LP problems, are the following.
```
(a) LP problems with complicating variables:
```
max aT y þ
X
i¼1, ..., n
c Ti x i
```
s:t: Ay þ D i x i ¼ d i i ¼ 1, . . . , n
```
y  0, x i  0, i ¼ 1, . . . , n:
```
(13.1)
```
```
The general form is as presented in the LP in (13.1), where y are complicating variables
```
in the sense that if we fix values of the variables y, the problem decomposes into n
subproblems in terms of xi, i ¼ 1, . . . , n variables. See also Fig. 13.1. This structure
commonly arises in two-stage stochastic programming problems, and the corresponding
```
method that is used is Benders decomposition (see Chapter 14). The problem also arises
```
in multiperiod design problems where the y variables represent design decisions that
must be selected for the n different periods of operation.
```
(b) LP problems with complicating constraints:
```
max c T x
```
s:t: Ax ¼ b
```
D i x i ¼ d i i ¼ 1, . . . , n
```
x 2 X ¼ x xi; i ¼ 1; . . . ; nj j, x i  0f g:
```
```
(13.2)
```
```
The general form is as presented in the LP in (13.2), where there are complicating constraints
```
in the sense that if we remove the equations Ax ¼ b, the problem decomposes into n
subproblems in terms of the x i, i ¼ 1, . . . , n variables. See also Fig. 13.2. This structure
commonly arises in multistage stochastic programming problems, and the corresponding
method that is used is Lagrangean decomposition. The problem also arises in multiperiod
planning problems where the complicating constraints represent inventory equations that
interconnect successive time periods. We should note that it is possible to convert a problem
with complicating variables to one with complicating constraints by disaggregating the y
variables into the n variables yi, i ¼ 1, . . . , n, and imposing the following constraints:
119
```
yi ¼ yiþ1 i ¼ 1, 2, . . . , n  1: (13.3)
```
Hence, we concentrate only on Lagrangean decomposition because Benders
decomposition, which can be viewed as an extension of the generalized Benders
decomposition method that was presented in Chapter 9, will be covered in Chapter 14.
13.2 Lagrangean Relaxation
We start by introducing the concept of Lagrangean relaxation before we address
Lagrangean decomposition. Major references on Lagrangean relaxation are Geoffrion
```
(1974), Fisher (1981), Guignard and Kim (1987), Guignard (2003), and Frangioni (2005).
```
We will assume that we address the solution of MILP problems of the following form
Pð Þ : min c T x
```
s:t: Ax  b
```
Ex  d
```
x 2 X X ¼ x j ¼ 0, 1 j ¼ 1; . . . , p  n, x j  0 j ¼ p þ 1, . . . ; n
```
 
,
```
(13.4)
```
where the set X contains both 0-1 and continuous variables, and where Ax  b are regarded
as “complicating” constraints, while Ex  d are “easy” constraints. The basic idea is that, if
we remove the complicating constraints, the resulting MILP is relatively easy to solve. This
may arise in MILPs with the decomposable structure shown in Fig. 13.2 when complicating
constraints are removed, or in MILPs where the polyhedral structure of the “easy” con-
```
straints is favorable (e.g., the corresponding constraints have integer extreme points).
```
y x1 x2 x3
A
D 1
D 2
D 3
Figure 13.1 Problem with
complicating variables.
D 1
D 2
D 3
A
x1 x2 x3Figure 13.2 Problem with complicating
constraints.
120 13 Lagrangean Decomposition
The basic idea in Lagrangean relaxation is to create an “easy” MILP by removing the
“complicating” constraints. This can be accomplished by dualizing the objective function in
which the complicating constraints are transferred into the objective function multiplied by
the nonnegative Lagrange multipliers λ:
LRλð Þ : min c T x þ λT Ax  bð Þ
```
s:t: Ex  d
```
x 2 X ,
```
(13.5)
```
where λ  0 are nonnegative Lagrange multipliers.
Property 13.1 The optimal value of the objective functions, LRλð Þ  v Pð Þ, which implies that
```
LRλð Þ in (13.5) yields a lower bound to the original problem Pð Þ in (13.4).
```
This follows from the fact that the feasible space is being relaxed by the removal of the
complicating constraints Ax  b, and the fact that, as λT Ax  bð Þ  0 for λ  0, the object-
ive function is being underestimated.
13.3 Lagrangean Dual
In order to find the tightest Lagrangean lower bound we consider the following problem, the
Lagrangean dual, in which we determine the multipliers λ  0 that maximize the lower bound
```
LRð Þ : v LRð Þ ¼ maxλ0 v LRλð Þ: (13.6)
```
We should note that for MILP problems, the solution of the Lagrangean dual is such that
v LRð Þ  v Pð Þ, meaning that no equality may be achieved, which is an indication that there
```
might be a dual gap given the presence of integer variables in problem (P). Because there
```
might be a dual gap, what is done in practice is to iterate on λ for a maximum number of
iterations, which, strictly speaking, yields a heuristic solution if the gap is not reduced within
a small tolerance ε.
```
We should note that if there are no integer variables in problem (P), it reduces to an LP,
```
```
which we express in simplified form as the following primal problem (PP),
```
PPð Þ : min c T x
```
s:t: Ax  b
```
x  0:
```
(13.7)
```
```
If we consider the dual problem (DP) of the primal problem (PP), it is given by (Dantzig, 1963)
```
DPð Þ : max bT λ
```
s:t: Aλ  c
```
λ  0:
```
(13.8)
```
The following property holds for the primal and dual problems.
13.3 Lagrangean Dual 121
```
Property 13.2 At the optimum solution of problems (PP) and (DP), v PPð Þ ¼ v DPð Þ:
```
What this means is that if there are no discrete variables, there is no dual gap because
the optimum solution of the dual is then identical to the optimum solution of the
primal problem.
For the MILP case, however, we can establish an interesting relation between the
```
Lagrangean dual and the primal relaxation of problem (13.5). From MIP theory, Meyer’s
```
```
Theorem (Wolsey, 1998) establishes that there exists a set of inequalities,
```
```
Hx  h, (13.9)
```
that, when added to the inequalities Ex  d, yields the convex hull of these inequalities,
co x 2 X , Ex  dð Þ ¼ x 2 X R, Ex  d, Hx  h
 
```
: (13.10)
```
Let problem ~P
 
be defined as follows:
~P  min c T x
```
s:t: Ax  b
```
~Ex  ~d
x 2 X R,
```
(13.11)
```
where Ex  d, Hx  h are replaced by ~Ex  ~d , i.e., the convex hull of Ex  d and X R is the
```
continuous relaxation of the integer and continuous variables specified in (13.4).
```
We can then establish the following theorem:
Theorem 13.1 v LRð Þ ¼ v ~P
 
:
```
This is the optimal solution of the dual Lagrangean (LR) equal to the solution of problem
```
~P . This is a very interesting result because it states that solving the dual Lagrangean is
equivalent to having determined the convex hull of the noncomplicating constraints in
```
problem (13.4). We present here only the outline of the proof (see Frangioni (2005) for
```
```
rigorous proof ).
```
Let v ~P
 
¼ min x2X R c T x Ax  b, ~E T x  ~d
n o
. Consider its dual,
v ~P
 
¼ maxλ0, μ0 bT λ þ ~d T μ A T λ þ ~E T μ  c
n o
¼ maxλ0 bT λ þ maxμ0~d T μ : ~E T μ  c  A T λ
n o 
¼ maxλ0 bT λ þ minx2X R cT  λT A
 
```
x : ~Ex  ~d
```
 
¼ maxλ0 minx2X c T x  λT Ax  bð Þ : Ex  d
  
¼ v LRð Þ:
```
(13.12)
```
122 13 Lagrangean Decomposition
In this way we establish that the solution of the Lagrangean dual is equal to the primal
relaxation with convex hull for Ex  d. Furthermore, we can establish the following corollary:
Corollary 1 v LPð Þ  v LRð Þ:
```
This follows from the fact that the LP relaxation of (P), v LPð Þ is weaker than the
```
relaxation of problem ~P
 
with the convex hull for the noncomplicating variables,
v LPð Þ  v ~P
 
. Hence, it follows that v LPð Þ  v LRð Þ, i.e., the dual of the Lagrangean yields
```
lower bounds greater or equal to the LP relaxation (see Fig. 13.3). Note also that v LPð Þ ¼
```
v LRð Þ if Ex  d defines the convex hull of these constraints.
As an example of the application of Lagrangean relaxation consider the generalized
assignment problem for machines i ¼ 1, . . . , m and jobs j ¼ 1, . . . , n, where c ij are the
```
corresponding cost coefficients, and the coefficients aij (0 or 1) and bi determine the
```
feasibility of assignment:
min
X
i
X
j
c ij x ij
```
s:t:
```
X
j
aij x ij  bi 8i
Px
ij ¼ 1 8j
x ij ¼ 0, 1:
```
(13.13)
```
The first set of constraints can be interpreted as knapsack constraints, while the second set of
```
constraints are multiple-choice constraints (each job j can only be assigned to one machine
```
```
i). Say that we dualize these multiple-choice constraints as follows:
```
min
X
i
X
j
c ij x ij þ
X
j
λj 1 
X
i
xij
!
```
s:t:
```
X
j
a ij x ij  bi 8i
xij ¼ 0, 1:
```
(13.14)
```
```
v (LP)
```
```
v (LR)
```
```
v (P)
```
```
co( )Ex d
```
Ex d Ax b
x2
x1
ZFigure 13.3 Geometric
illustration of relation of bounds
of LP and dual of Lagrangean
relaxation.
13.3 Lagrangean Dual 123
```
Model (13.14) can be rearranged as follows, where (13.15a) and (13.15b) are equivalent:
```
min
X
i
X
j
c ij  λj
 
x ij þ
X
j
λj
```
s:t:
```
X
j
aij xij  bi 8i
```
(13.15a)
```
X
i
min
X
j
c ij  λj
!
x ij þ
X
j
λj
```
s:t:
```
X
j
aij x ij  b i 8i:
```
(13.15b)
```
```
Problem (13.15b) can then be solved independently for each machine i. Furthermore, this
```
means that for fixed λj , we have for each machine i a knapsack problem,
Z i ¼ min
X
j
c ij  λj
 
x ij
```
s:t:
```
X
j
aij x ij  bi
x ij ¼ 0, 1:
```
(13.16)
```
The lower bound is then given by
v LRλð Þ ¼
X
i
Z i þ
X
j
```
λj  v Pð Þ: (13.17)
```
Because the knapsack constraints do not yield the convex hull of the feasible region, this
then implies that the lower bound from the Lagrangean dual is stronger than the lower
bound of the LP relaxation, that is v LRð Þ > v LPð Þ. Before we address the issue of how to
readjust the λs to maximize v LDð Þ, we will consider Lagrangean decomposition.
13.4 Lagrangean Decomposition
```
Assume we reformulate problem (P) in (13.4) by copying the x variables into the y variables
```
```
(Guinard and Kim, 1987) so that we assign these variables to the two different types of
```
constraints, complicating and noncomplicating, that is,
P0ð Þ : min c T x
```
s:t: Ax  a
```
Ey  d
x ¼ y
x 2 X , y 2 Y :
```
(13.18)
```
124 13 Lagrangean Decomposition
We should note that this reformulation is especially useful for problems with staircase
matrices. In a similar way as we did in the previous section, we can define a dual Lagrangean
decomposition LDλð Þ:
LDλð Þ : min c T x þ λT x  yð Þ
```
s:t: Ax  a
```
Ey  d
x 2 x, y 2 Y :
```
(13.19)
```
```
For fixed value of λ (in this case they are unconstrained in sign due to the equality x ¼ y),
```
```
(13.19) decomposes into two subproblems: one in the space of x and the other in the
```
space of y,
min 12 c T x þ λT x
```
s:t: Ax  a
```
x 2 X
```
(13.20)
```
min 12 c T y  λT y
```
s:t: Ey  d
```
y 2 Y ,
```
(13.21)
```
where we have arbitrarily split the linear term c T y in equal parts between the two subpro-
blems. Similar to Theorem 13.1, we can prove that
ð~P0 Þ ¼ min c T x
```
s:t: x 2 co x 2 X , Ax  bð Þ \ co x 2 X , Ex  dð Þ,
```
```
(13.22)
```
which implies v ~P0
 
¼ v LDð Þ  v LRð Þ. Thus, the lower bound of Lagrangean decomposition
```
yields stronger lower bounds than the lower bound from Lagrangean relaxation (see Fig. 13.4).
```
Subproblem 1 Subproblem 2
Ax b
```
co( )Ex d
```
```
Ex d co( )Ax b
```
x1
x2 Z
```
v (LP)v (LR)
```
```
v (LD)v (P)
```
Figure 13.4 Geometric illustration of relation
of bounds of LP and dual of Lagrangean
decomposition.
13.4 Lagrangean Decomposition 125
13.5 Update of Lagrange Multipliers
In order to update the Lagrangean relaxation or Lagrangean decomposition, we would
ideally like to select the multipliers to maximize the corresponding dual functions. For
simplicity in the presentation, we consider the updates of the multipliers λ in the dual of
the Lagrangean relaxation LRλ
min c T x þ λT Ax  bð Þ
```
s:t: Ex  e
```
x 2 X :
```
(13.23)
```
Assume that the convex hull of the inequalities Ex  e, is a bounded polyhedron with
extreme points xk , k 2 V . We can then rewrite LRλ as follows:
mink2V c T xk þ λT Ax k  b
  
```
¼ Z λð Þ: (13.24)
```
```
The geometric interpretation of problem (13.24) is shown in Fig. 13.5, where it can be seen
```
that Z λð Þ is a concave function of λ.
Since we want to determine max λ v LRλð Þ, we can rewrite Z λð Þ as follows:
Z λð Þ ¼ max η
```
s:t: η  c T x k þ λT Ax k  b
```
 
```
8k 2 V : (13.25)
```
```
The drawback with the LP (13.25) is that it requires knowing all the extreme points, x k,
```
k 2 V , and hence it is impractical to set up such a problem. To circumvent this problem,
consider a relaxation in which we only consider a subset of known extreme points,
k 2 V  V . This LP is the basis of the cutting-plane method for updating the Lagrange
```
multipliers (Guignard, 2003).
```
Because the cutting-plane method is initially slow until it accumulates enough cutting
```
planes, an alternative method is the subgradient method (Fisher, 1981). In general, we have
```
Figure 13.5 Piecewise linear
approximation of Lagrangean dual.
126 13 Lagrangean Decomposition
that a subgradient γ is given by the following inequality, in which the right-hand side
overestimates the change in function value from x to x0 ,
f xð Þ  f x0
 
 γ x  x0
 
```
: (13.26)
```
```
From (13.24) we can define the subgradient as
```
```
s k ¼ Ax k  b: (13.27)
```
Let the new multiplier be given by this subgradient multiplied by the scalar μ, which can be
interpreted as a step size in analogy to the steepest-descent method,
```
λkþ1 ¼ λk þ μs k: (13.28)
```
Because we have
c T xk þ λk
 T
Ax k  b
 
```
¼ ηk, (13.29a)
```
and if we assume
c T x k þ λkþ1
 T
Ax k  b
 
```
¼ η∗, (13.29b)
```
```
from the definition of subgradient in (13.27) and from (13.29a) and (13.29b), we can set,
```
η∗  ηk ¼ s k
 T
λkþ1  λk
 
```
: (13.30)
```
```
Substituting (13.30) in (13.28), yields
```
η∗  ηk ¼ μ s k
 T
```
s k, (13.31)
```
or
μ ¼ η
∗  ηk
s kð ÞT s k
```
: (13.32)
```
```
From (13.28), and because η∗ is unknown, we replace it by the upper bound ZU
```
λkþ1 ¼ λk þ αk Z
U  ηk 
s kk k2
```
s k, (13.33)
```
where ηk ¼ c T x k þ λk
 T
Ax k  b
 
and the step size αk is typically chosen in the interval
[0,2], that is αk 2 0, 2½ .
In summary, the algorithm for Lagrangean relaxation consists of the following steps.
```
(1) Guess initial value of the multipliers λk (e.g., from the relaxed LP).
```
```
(2) Solve LRλð Þ to yield lower bound v LRλð Þ.
```
```
(3) Compute from (13.18) the upper bound ZU using rounding heuristics.
```
```
(4) If v LRλð Þ  ZU < ε, stop.
```
13.5 Update of Lagrange Multipliers 127
```
Otherwise update λkþ1 using (13.25) or (13.33) and go to step (2).
```
Notice that if we were to apply the above steps to the Lagrangean decomposition, then
```
step (2) decomposes into subproblems by solving the dual Lagrangaen LDλ.
```
Also, we can make the following remarks.
```
(1) Owing to the dual gap, the specified tolerance ε may not be satisfied. Therefore, we
```
specify a maximum number of iterations as a termination criterion. We can also use a
```
branch and bound method to close the gap (e.g., see Carøe and Schultz, 1999).
```
```
(2) We can also embed the LRλ or LDλ in a rigorous branch and bound search to compute
```
lower bounds that are stronger than the LP relaxation.
```
(3) If there are equalities in problem (13.4), the multipliers λ in the Lagrangean decom-
```
positions are unrestricted in sign.
```
(4) The Lagrangean relaxation or decomposition can be extended to the solution of NLP
```
and MINLP problems.
EXERCISES
13.1 Discuss the relative advantages and disadvantages of applying Lagrangean relaxation
```
versus Lagrangean decomposition to the solution of the MILP problem (13.4). Are
```
there any special cases for which both decompositions will yield the same computa-
tional performance?
13.2 Consider the following multiperiod LP problem:
min Z ¼ c T y þ
Xn
i¼1
aTi xi
```
s:t: Cy þ Ax i ¼ b, i ¼ 1, 2, . . . , n
```
y  0, x i  0, i ¼ 1, 2, . . . , n,
where n is the number of time periods.
```
(a) Reformulate the problem so that the LP can be solved by Lagrangean
```
decomposition.
```
(b) Show the explicit form of the Lagrangean decomposition problem.
```
128 13 Lagrangean Decomposition
14 Stochastic Programming
14.1 Strategies for Optimization under Uncertainty
In optimization models there is often the need to anticipate effects of uncertainty in the data
```
(e.g., demands in planning and scheduling applications) (Sahinidis, 2004). The problem of
```
```
optimization under uncertainty (assuming only inequalities) is generally given in initial form
```
as follows:
```
min f x; θð Þ
```
```
s:t: g x; θð Þ  0
```
x 2 X ,
```
(14.1)
```
```
where x are the decision variables and θ is the vector of uncertain parameters (e.g.,
```
```
demands). Problem (14.1) is not a well-defined problem, as we need to specify a strategy
```
for hedging against the uncertainty. One approach is to adopt a deterministic strategy where,
for instance, we assume that the uncertain parameters are specified in a given uncertainty set,
θ 2 T, e.g., T ¼ θL  θ  θu
 
. The idea is then to specify a given criterion on how to
anticipate the effect of the parameters θ. One possible criterion is to adopt a minimax
strategy in which we optimize the objective function for the worst outcome of θ, that is,
```
minx2X maxθ2T f x; θð Þjg x; θð Þ  0f g: (14.2)
```
```
The solution to problem (14.2) can then be interpreted as yielding the decision x that is
```
optimal for the “worst” condition for θ 2 T.
An alternative criterion is to use a robust optimization strategy in which the concern is to
```
select the variable x so as to ensure the feasibility of the inequalities g x; θð Þ  0 for all θ in T.
```
Mathematically that leads to the problem
min f xð Þ
```
s:t: g x; θð Þ  0 8θ 2 T
```
x 2 X ,
```
(14.3)
```
```
which is known as a semi-infinite programming problem (Hettich and Kortanek, 1993) since
```
```
an infinite number of inequalities g x; θð Þ  0 have to be satisfied for all points θ in T.
```
```
Problem (14.3) can be reformulated as a finite-dimensional optimization problem by maxi-
```
```
mizing each individual constraint g i x; θð Þ, i 2 I , with respect to θ. That is,
```
129
min f xð Þ
```
s:t: maxθ2T g i x; θð Þ  0 8i 2 I
```
x 2 X :
```
(14.4)
```
```
Finally, if we are given a probability distribution function (pdf ) ϕ θð Þ we can also formulate
```
```
the chance-constrained optimization problem (Prékopa, 1970)
```
min f xð Þ
```
s:t: prob g x; θð Þ  0ð Þ  1  α
```
x 2 X
```
(14.5)
```
in which we require the inequalities to be satisfied with a minimum probability 1  α. Notice
```
that the operator prob in (14.5) implies the integration of a multiple integral in θ over the
```
```
feasible region g x; θð Þ  0, a nontrivial problem. For this reason, problem (14.5) is often
```
replaced by individually imposing probability conditions on each constraint,
min f xð Þ
```
s:t: prob g i x; θð Þ  0ð Þ  1  αi, i 2 I
```
x 2 X ,
```
(14.6)
```
in which the probabilistic constraints are reformulated by taking the inverse of the cumula-
tive distribution function, ^F ,
min f xð Þ
```
s:t: g i x; θð Þ  ^F 1 1  αið Þ, i 2 I ,
```
```
(14.7)
```
which leads to a much more manageable problem.
An alternative approach to account for uncertainty in optimization is stochastic
```
programming (Birge and Louveaux, 2011). Here we also assume that the uncertain param-
```
eters θ are described by a pdf, ϕ θð Þ, which can be continuous or discrete. There are different
ways of defining the objective function and treatment of the variables, as follows.
```
(a) Minimization of expected cost
```
minx2X
ð
::
ð
```
f x; θð Þjg x; θð Þ  0½ ϕ θð Þdθ (14.8)
```
in which we select the variables x so as to minimize the average or expected cost, i.e.,
```
minx2X Eθ f x; θð Þjg x; θð Þ  0½ : (14.9)
```
If the pdf is continuous in θ, this involves selecting x to minimize the multiple integral in
```
(14.8). In contrast, if we have a discrete distribution function where the discrete uncer-
```
tainties θi, i ¼ 1, . . . , n, each have a probability given by pi ¼ ϕ θið Þ, the objective
involves a summation of the objective weighted by the probabilities,
130 14 Stochastic Programming
minx2X
Xn
i¼1
```
pi f x; θið Þ
```
```
s:t: g x; θið Þ  0, i ¼ 1, . . . , n
```
x 2 X :
```
(14.10)
```
```
(b) Two-stage programming
```
The basic idea here is to recognize that in many problems the decisions x can be split into
```
two: stage-1 decisions d that are “here and now” in the sense that once selected they
```
cannot be changed or adjusted, and stage-2 decisions z that are “wait and see” in that
these decisions can be adjusted according to the realization of the uncertain parameters θ.
These variables are also often denoted as design decisions for stage 1, and recourse
decisions for stage 2. The basic idea is illustrated in Fig. 14.1. As an example, consider a
supply-chain problem. We can regard the selection of the structure and process capacities
as stage-1 decisions, while stage-2 decisions could be levels of production that are adjusted
according to the uncertain demands.
```
If we partition the vector of variables x into design variables d (stage 1) and control or
```
recourse variables z,
x ¼
d
z
" #
,
we will assume that the recourse variable z can be adjusted for each realization of the
uncertain parameters θ, as shown in Fig. 14.2, which implies that one can measure the
```
realization of θ and make immediate adjustment of z (e.g., perfect control).
```
To formulate the two-stage programming problem, we consider first the stage-2
subproblem where for fixed stage-1 decision d, we optimize z for each parameter value θ:
```
minz f d; z; θð Þ
```
```
s:t: g d; z; θð Þ  0,
```
```
(14.11)
```
```
d (design) z (recourse)
```
Stage 1: here and now Stage 2: wait and see
Figure 14.1 Illustration for two-stage
stochastic programming.
d

```
)(zFigure 14.2 For fixed stage-1 d, recourse z can
```
be adjusted for each θ.
14.1 Strategies for Optimization under Uncertainty 131
```
if we take the average for all θ, the expected value, Eθ min z f d; z; θð Þjg d; z; θð Þ  0½ ,
```
then selecting the stage-1 variable d and stage-2 variable z θð Þ leads to the two-stage
programming problem, which can be formulated as:
```
mind Eθ minz f d; z; θð Þ g d; z; θð Þ  0
```
h i
```
: (14.12)
```
```
We should note that the formulation in (14.12) implicitly assumes feasibility 8θ for the
```
```
two-stage problem in (14.11), which is known as full recourse. To allow for the possibil-
```
ity of violation of constraints, a slack variable ui with a corresponding penalty cost c i can
be introduced for each inequality, with which the two-stage programming problem can
be formulated as follows:
```
mind Eθ minz f d; z; θð Þ þ
```
X
```
c i ui g i d; z; θð Þ  u i, ui  08i
```
z
2
4
3
5
2
4
3
```
5: (14.13)
```
```
(c) Multistage stochastic programming
```
The two-stage programming problem can be extended to multiple stages of decision as
shown in Fig. 14.3, in which the recourse variables z k in a given stage k, become stage-k
variables for stage k þ 1. The multistage stochastic programming problem can be
formulated with nested expectations as follows:
```
mind Eθ1minz1Eθ2minz2Eθ3minz3f d; z1 , z2 , z3 , θ1 , θ2 , θ3ð Þ
```
 
```
s:t: g d; z1 , z2 , z3 , θ1 , θ2 , θ3Þ  0½ 
```

:
```
(14.14)
```
14.2 Linear Stochastic Programming
Consider the two-stage LP stochastic programming problem
min c T x þ Q xð Þ
```
s:t: Ax ¼ b
```
x  0,
```
(14.15)
```
where x are the stage-1 variables, and Q xð Þ is the expected recourse function
```
Q xð Þ ¼ Eθ Q x; θð Þf g, (14.16)
```
Stage 1 Stage 2
d z1
q1 q2 q3 qn
z2 z3• • •Figure 14.3 Multistage stochastic
programming.
132 14 Stochastic Programming
where for every realization of the vector of uncertain parameter θ that obeys a given
```
probability distribution function, Q x; θð Þ is optimized in terms of the stage-2 variables y,
```
which are expressed as y θð Þ to denote the fact that these variables are adjusted for each value
of θ
```
Q x; θð Þ ¼ min q θð ÞT y θð Þ
```
```
s:t: W θð Þy θð Þ ¼ h θð Þ  T θð Þx
```
y θð Þ  0:
```
(14.17)
```
```
In (14.17) the uncertainties can arise in the cost coefficient q θð Þ, in the right-hand side h θð Þ,
```
```
in the matrix W θð Þ of the recourse (stage-2) variables, and in the matrix T θð Þ (sometimes
```
```
known as the “Technology Matrix”) of the stage-1 variables.
```
The following property can be established for the expected recourse function.
Property 14.1 The function Q xð Þ is convex and piecewise linear.
```
The above property follows from the fact that the subproblem in (14.15) is linear, and the
```
fact that changes in the basis of the LP give rise to breakpoints in the piecewise linear
```
function that is shown in Fig. 14.4.
```
```
From (14.16) and (14.17) the two-stage stochastic programming in (14.15) can be written
```
as follows:
min c T x þ Eθ miny q θð ÞT y θð Þ
 
```
s:t: Ax ¼ b
```
W θð Þy θð Þ ¼ h θð Þ  T θð Þx
x  0 y θð Þ  0:
```
(14.18)
```
If the uncertain parameters θ are described by a discrete probability distribution function, θj ,
```
j ¼ 1, . . . , n, with probabilities pj , j ¼ 1, . . . , n (see Fig. 14.5), (14.18) can be expressed as the
```
finite-dimensional linear programming problem
min c T x þ
X
j
pj qTj y j
```
s:t: Ax ¼ b
```
T j x þ W j yj ¼ h j j ¼ 1, . . . , n
x  0 y j  0,
```
(14.19)
```
x
```
( )Q xFigure 14.4 Expected recourse
```
```
function Q xð Þ.
```
14.2 Linear Stochastic Programming 133
where qj, hj, Wj, and Tj are evaluated at the discrete points θj , j ¼ 1, . . . , n. Each of these points
can be interpreted as a scenario that is realized in stage 2, as shown in the scenario tree in Fig. 14.6.
```
The LP in (14.19) is known as the deterministic equivalent problem of the two-stage
```
```
programming problem (14.18), and can simply be solved as an LP. If some of the stage-1 and
```
```
stage-2 variables are integers, the deterministic equivalent in (14.19) gives rise to an MILP
```
problem. In either case, the difficulty might be that the size of the deterministic equivalent is
too large if the number of scenarios is large. To address this problem either a sampling or a
```
decomposition method is required (Birge and Louveaux, 2011). We present below the
```
Benders decomposition method to address this problem.
14.3 L-Shaped Method
```
Benders decomposition (Benders, 1962) as applied to the two-stage LP problem in (14.18) is
```
```
also known as the L-shaped method (Van Slyke and Wets, 1969). The stage-1 variables x can
```
be regarded as complicating variables, so that if they are fixed at the value x k at iteration k,
the problem decomposes in the scenarios j ¼ 1, . . . , n that can be solved independently in
```
parallel (see Fig. 14.7). Specifically, the L-shaped method consists of solving a master
```
problem in terms of the stage-1 variables x, and the subproblems j ¼ 1, . . . , n for the
stage-2 variables y j for fixed variables x, as shown in Fig. 14.8.
q11
q21
q22
q23
q24
q2
q12 q13 q14 q1
Figure 14.5 Two-dimensional
discretization of two
uncertain parameters.
p1 p2 p3
q1 q2 q3
Figure 14.6 Scenario tree for
three parameter realizations.
134 14 Stochastic Programming
```
From (14.19) it follows that the subproblem S kj
```
 
of scenario j at iteration k is given by:
Z kj ¼ min qTj y j
```
s:t: W j yj ¼ hj  T j x k
```
yj  0:
```
(14.20)
```
```
Consider the Lagrangean function of the j subproblem (14.20) at iteration k,
```
L kj ¼ qTj yj þ λkj
 T
W j yj  hj þ T j x k
h i
```
, (14.21)
```
where λkj are the KKT multipliers of the equality constraints. The stationary conditions of
```
(14.21) yield
```
∂L kj
∂yj¼ qj þ W
```
Tj λkj ¼ 0: (14.22)
```
```
Given a total of K iterations, we can define the master problem for problem (14.19) as
```
```
follows:
```
min η
```
s:t: η  c T x þ
```
X
j
```
pj L kj x; yj ; λkj
```
 
, k ¼ 1, . . . , K
Ax ¼ b
x  0, η 2 R1:
```
(14.23)
```
x y1
y2
yn
T j
Figure 14.7 Block diagonal
structure for two-stage
programming.














x
y1
y2
yn
First stage Second stage
Master
problem
Scenario
subproblems
```
Figure 14.8 The L-shaped method (Benders
```
```
decomposition).
```
14.3 L-Shaped Method 135
```
Substituting (14.21) into (14.23) yields
```
min η
```
s:t: η  c T x þ
```
X
j
pj qTj yj þ
X
j
λkj
 T
W j yj þ T j x  hj
h i" #
k ¼ 1, . . . , K
Ax ¼ b
x  0, η 2 R1 ,
```
(14.24)
```
```
which can be simplified with (14.22) as follows,
```
min η
```
s:t: η  c T x þ
```
X
j
pj λkj
 T
T j x 
X
j
p j λkj
 T
hj k ¼ 1, . . . , K
Ax ¼ b
x  0, η 2 R1:
```
(14.25)
```
```
Note that the master problem in (14.25) is expressed in terms of the stage-1 variables x and
```
the objective η, and therefore it can be regarded as a projection that corresponds to an
approximation of the piecewise linear function in Fig. 14.4. Furthermore, its solution yields
```
a lower bound to the two-stage LP problem (14.19). Each inequality in (14.25) is denoted as
```
an optimality cut, where it is assumed that the subproblems S kj
 
are feasible. In case any
subproblem is infeasible one can derive a feasibility cut that results from minimizing the
```
violation in (14.20) (using 1-norm as discussed below). The feasibility cut for a given
```
iteration k is given by the inequality
X
j
μkj
 T
```
T j x  h j  0, (14.26)
```
where μkj are the multipliers of the feasibility problem.
In summary, by defining the set FEA as those iterations that yield feasible subproblems,
and the set INF as those iterations with infeasible subproblems, the master problem M k at
iteration k is given by the following LP,
LBk ¼ min η
```
s:t: η  c T x þ
```
X
j
p j λkj
 T
T j x 
X
j
pj λkj
 T
h j , k 2 FEA
X
j
μkj
 T
T j x  hj  0 k 2 INF
Ax ¼ b
x  0, η 2 R1 ,
```
(14.27)
```
where LBk corresponds to the lower bound predicted at each iteration k. The upper bound
UBk is then given by
136 14 Stochastic Programming
UBk ¼
X
j
```
pj Z kj þ c T x k, (14.28)
```
```
where Z kj is the solution to the subproblem in (14.20).
```
The L-shaped or Benders decomposition algorithm is then given by the following steps.
```
(1) Set k ¼ 0.
```
```
(2) Solve the master problem M k in (14.27) to obtain xk and the lower bound LBk.
```
```
(3) For a fixed value of the stage-1 variable x k, solve the subproblems S kj
```
 
j ¼ 1, . . . , n in
```
(14.20) to obtain the multipliers λkj for the optimality cuts. If the subproblems are
```
feasible, the upper bound is given by UBk ¼ Pj pj Z kj þ c T xk . If any of the subproblems
is infeasible, solve the feasibility problem,
min vþ  v
```
s:t: W j y þ Ivþ  Iv ¼ hj  T j x k
```
y, vþ, v  0,
to obtain the multipliers μkj . Set the upper bound to UBk ¼ ∞.
```
(4) Iterate until LBk ’ min k UBk
```
 
.
Figure 14.9 shows typical iterations with Benders decomposition, where, as it can be seen, the
lower bounds, LB, increase monotonically because cumulative Benders cuts are added to the
master problem at each iteration. In contrast, the upper bounds, UB, do not follow a decreasing
pattern as trial points for the UB are generated at each iteration, which may lead to improvements,
or not, of the upper bound.
We should note that the above algorithm can be extended to the multicuts version, where
```
cuts in the master problem are added for each scenario subproblem at each iteration (see
```
```
Exercise 14.1). It can be shown that this yields stronger lower bounds, but at the expense of
```
```
solving a large master problem (Birge and Louveaux, 2011).
```
We should also note that the above algorithm can be applied when the stage-1 variable x has
0-1 variables, in which case the master problem gives rise to an MILP while the subproblems are
still LPs. The extension to stage-2 variable y with 0-1variables is not trivial, as then one cannot
```
apply the dual conditions in (14.21), which then gives rise to a dual gap (Schultz, 2003). Finally,
```
for a computationally efficient implementation, the solution of the subproblems
S kj
 
```
j ¼ 1, . . . , n in (14.19) can be parallelized because they are independent of each other.
```
UB
LB
ZFigure 14.9 Progress of iterations
in Benders decomposition.
14.3 L-Shaped Method 137
14.4 Multistage Stochastic Programming
As indicated at the end of Section 14.1, two-stage programming problems can be extended to
multiple stages of decision as shown in Fig. 14.3, in which the recourse variables z k, in a
given stage k, become stage-k variables for stage k þ 1. Figure 14.10 shows the scenario tree
of a three-stage programming problem in which there are two realizations of the uncertain
parameters at each stage. As can be seen in Fig. 14.10, there are four terminal nodes,
meaning a total of four scenarios.
The mathematical formulation for the three-stage programming problem in Fig. 14.10 is
not trivial to develop, because one has to write the model in terms of parent and children nodes
in the scenario tree. However, one can replace the tree representation in Fig. 14.10 by the
```
alternative representation (Ruszczynski, 1997) shown in Fig. 14.11, in which each of the
```
scenarios Sc1, Sc2, Sc3, and Sc4 are represented by independent paths each with variables,
x, y, and z, associated to each scenario. In order to map this representation into the original
tree in Fig. 14.10, horizontal links between nodes are imposed to equate the variables involved
in the interconnected nodes. So, for instance, at stage 1, the links between the four nodes of the
scenarios represent the equality of the variables at those nodes, namely, x1 ¼ x2 ¼ x3 ¼ x4 ,
which correspond to the root node of the tree in Fig. 14.10. Similarly, at stage 2, the link
between the nodes of scenarios Sc1 and Sc2, represents the equality y1 ¼ y2 , which represents
the first node at stage 2 in Fig. 14.10. The equality constraints that are associated to the links in
```
Fig. 14.11 are known as nonanticipativity constraints (Ruszczynski, 1997).
```
Based then on the nonanticipativity constraints, x1 ¼ x2 , x2 ¼ x3 , x3 ¼ x4 , y1 ¼ y2 , and
y3 ¼ y4 , the multistage stochastic programming problem can be written as follows:
y22y1
x1
2
z13 z23 z33 z43
Figure 14.10 Scenario tree for a
three-stage problem.
Sc 1 Sc 2 Sc 3 Sc 4
x1 x2 x3 x4
y1 y2 y3 y4
z1 z2 z3 z4
Figure 14.11 Alternative
representation for multistage tree.
138 14 Stochastic Programming
min
X
s
ps c T x s þ qT1 y þ qT2 z s

```
s:t: Ax s ¼ b, 8s
```
T1x s þ W 1ys ¼ h s1 , 8s
T2ys þ W 2z s ¼ hs2 , 8s
x1 ¼ x2 ¼ x3 ¼ x4
y1 ¼ y2 , y3 ¼ y4
x s, ys, z s  0 8s:
```
(14.29)
```
```
Formulation (14.29) represents the deterministic equivalent to the three-stage stochastic
```
programming problem. Since this problem can become very large, it can be solved
```
with Lagrangean decomposition (see Chapter 13) by dualizing the nonanticipativity
```
```
constraints, as then problem (14.29) can be solved independently for each scenario
```
```
(Ruszczynski, 1997).
```
14.5 Robust Optimization
We should also note that, in terms of applications of optimization under uncertainty, the
```
alternative approach to stochastic programming is robust optimization (El Ghaoui, 1997;
```
```
Bertsimas et al., 2011) in which the major concern is to ensure feasibility over a specified
```
```
uncertainty set as formulated in (14.3).
```
For the specific case of linear programs, which is the most common model for robust
optimization, we consider the following model,
min
X
j
~c j x j
```
s:t:
```
X
j
~a ij x j  ~b i 8i 2 I
x  0,
```
(14.30)
```
which involves uncertainty in the cost coefficients ~c j , left-hand side coefficients ~a ij , and right-
```
hand sides ~b i. For convenience we rearrange (14.30) as follows:
```
min z
```
s:t: z 
```
X
j
~c j x j  0
~b i x0 þ X
j
~a ij x j  0 8i 2 I
x  0, x0 ¼ 1,
```
(14.31)
```
which in turn can be reduced to the compact form
14.5 Robust Optimization 139
min f T x
```
s:t: A ξð Þx  b 8ξ 2 Ξ
```
x  0,
```
(14.32)
```
```
where the inequalities A ξð Þx  b correspond to the two inequalities in (14.31), ξ are the
```
uncertain parameters, and the linear objective function generalizes the term z.
If we consider a polyhedral set for the P uncertain parameters,
Ξ ¼ ξ : V ξ  u, ξ 2 R Pþ
 
```
: (14.33)
```
```
we can express (14.32) as the semi-infinite programming problem:
```
min f T x
```
s:t: ai þ P iξð ÞT x  bi 8i 2 I , ξ 2 Ξ
```
x  0:
```
(14.34)
```
```
As will be shown in Chapter 15, the feasibility of the constraints in (14.33) can be established
```
by maximizing each constraint i,
```
aTi þ maxξ2Ξ P iξð ÞT x  bi: (14.35)
```
Taking the dual of the inner maximization problem,
maxξ2Ξ P Ti x
T
ξ
```
s:t: V ξ  u,
```
```
(14.36)
```
yields
minλ2R m
þ
u T λi
```
s:t: V T λi  P Ti x:
```
```
(14.37)
```
```
Substituting (14.36) in (14.34) and next in (14.33), and by omitting the min operation
```
```
(assuming weak duality), leads to the robust counterpart formulation that yields the LP
```
```
(Ben-Tal and Nemirovsky, 1999),
```
min f T x
```
s:t: aTi x þ uTi λi  b i 8i 2 I
```
V T λi  P Tj x 8i 2 I
λi 2 R mþ 8i 2 I , x  0:
```
(14.38)
```
```
Problem (14.38) can be solved efficiently as it is an LP. We should also note that it is possible
```
```
to consider other uncertainty sets (e.g., ellipsoidal, cone), and account for restricted classes
```
```
of recourse variables (e.g., adjustable linear functions) (Ben-Tal et al., 2004).
```
140 14 Stochastic Programming
Finally, as to whether stochastic programming or the robust approach is more suitable
depends on the problem at hand. For instance, in the area of process operations, stochastic
```
programming (two stages or multistage) is generally more meaningful for planning problems
```
due to their longer time horizons in which recourse decisions can be fully anticipated
```
(Alonso-Asuyo et al., 2003). On the other hand, for scheduling problems, robust
```
optimization is generally more meaningful since the major concern tends to be to satisfy
production demands over short-term horizons in which recourse actions may not be
```
readily applied (Lin et al., 2004).
```
EXERCISES
14.1 Rewrite the steps of the L-shaped algorithm for the case when optimality or feasibility
cuts for each scenario j are added to the master problem.
14.2 Consider the mixed-integer linear programming problem
min Z ¼ aT x þ bT y
```
s:t: Ax þ B y  d
```
x  0, y 2 0, 1f g:
Assume it is desired to solve this problem by Benders decomposition where the 0-1
variables are treated as “complicating” variables for the master problem. If the LP
subproblems for fixed y k, k ¼ 1, 2, . . . , K are feasible with an optimal solution x k and
multipliers λk , show that the master problem can be formulated as follows:
Z KL ¼ min α
```
s:t: α  bT y þ λTk By  d½ , k ¼ 1, 2, . . . , K
```
α 2 R1 , y 2 0, 1f g:
Exercises 141
15 Flexibility Analysis
15.1 Introduction
In this chapter, we address one of the important components in the operability of a process
```
system, namely, flexibility (see Grossmann et al., 2014, for a general review). By flexibility
```
we mean the capability of a system design to have feasible steady-state operation for a range
of uncertain conditions that may be encountered during plant operation. Clearly, there are
other aspects to the operability of a plant, such as controllability, safety, and reliability that
are equally important. However, flexibility is a general attribute as it provides a character-
ization for the capability of a design to ensure feasibility in the face of uncertainty while
anticipating that corrective actions can be taken to ensure feasibility. For an interesting
```
relationship between flexibility and robust optimization see Zhang et al. (2016).
```
In this chapter we will concentrate on two basic analysis problems for flexibility. The first
one will be the problem when we need to determine if a design is feasible for a fixed range of
uncertainty. In the second problem we will address the question of how to actually quantify
flexibility.
15.2 Two-Stage Programming with Guaranteed Feasibility
In Chapter 14 we considered the model
```
min f d; z; θð Þ
```
```
s:t: g d; z; θð Þ  0, (15.1)
```
```
where d is the vector of design variables (stage 1), z is the vector of control or recourse
```
```
variables (stage 2), and θ is the vector of uncertain parameters. To account for the uncer-
```
tainty of the parameters θ we considered the two-stage programming strategy. We indicated
that one way to ensure that the stage-2 problem is feasible is to assign a penalty for the
```
violation constraints as shown in (15.2),
```
```
mind Eθ2T minz C d; z; θð Þ þ
```
X
j
```
c j u j f j d; z; θð Þ  uj , u j  0, j 2 J
```
```
( )
```
```
: (15.2)
```
However, let us assume we would like to enforce feasible operation for a specified uncer-
tainty set T, for instance one that is given by lower and upper bounds of θ, that is for every
θ 2 T ¼ θjθL  θ  θU
 
.
142
```
We would then reformulate problem (15.2) as follows,
```
```
mind Eθ2T minz C d; z; θð Þ f d; z; θð Þ  0
```
n o
```
s:t: 8θ 2 T 9z 8j 2 J, f j d; z; θð Þ  0
```
 
,
```
(15.3)
```
in which we have added as a constraint the condition that ensures that, for the given design
```
d, by proper adjustment of the controls z the inequalities f j d; z; θð Þ  0, 8j 2 J are satisfied
```
for 8θ 2 T. Or, stated more precisely, for 8θ 2 T there exists a vector of control variables z
```
that can satisfy 8j 2 J the inequalities f j d; z; θð Þ  0. Needless to say the constraint in
```
```
problem (15.3) is nontrivial as it effectively involves an infinite number of constraints as
```
they have to hold for 8θ 2 T. This class of problems is denoted as semi-infinite
```
programming problems (Hettich and Kortanek, 1993).
```
Given the complexity of integrating the multiple integral for the expected value in
```
problem (15.3), let us consider a discrete approximation in which we consider N points,
```
```
θi, i ¼ 1, . . . , N, with probability w i for which z i is selected. Problem (15.3) can then be
```
reformulated as
mind, z1 , z2 , ..., zN
XN
i¼1
```
w i c d; z i, θi
```
 
```
s:t: 8θ 2 T 9z 8j 2 J, f j d; z; θð Þ  0
```
 
:
```
(15.4)
```
```
If we remove the semi-infinite feasibility constraint, we can reduce problem (15.4) to the
```
multiscenario problem,
mind, z1 , z2 , ..., zN
XN
i¼1
```
w i C d; z i, θi
```
 
```
s:t: f d; z i, θi
```
 
 0 i ¼ 1, . . . , N:
```
(15.5)
```
```
Figure 15.1 shows an interpretation of problem (15.5) as a multiscenario problem in which
```
the design variables d are selected over the four scenarios that each involve uncertain
parameters θi, i ¼ 1, . . . , 4, with probabilities w i, i ¼ 1, . . . , 4, and for which corresponding
control variables z i, i ¼ 1, . . . , 4, are selected. Here the probabilities w i can be interpreted as
lengths of time periods in the multiscenario problem.
z1
Variable
z2 z4z3
w1 w2 w3 w4
Time
```
(probability)
```
d
q1 q
2
q3
q4
Figure 15.1 Representation of the variables
```
involved in the formulation (15.5).
```
15.2 Two-Stage Programming/ Guaranteed Feasibility 143
```
An algorithm for solving the two-stage programming problem (15.4) with the flexibility
```
constraint is as follows.
```
(1) Set iteration counter k ¼ 0, and select an initial set of parameters T0 ¼
```
```
θi; i ¼ 1; 2; . . . , N0
```
 
:
```
(2) Solve the multiscenario problem (15.5) to determine the design variable d k for the
```
N k scenarios.
```
(3) Apply the flexibility test for d k .
```
```
Check if 8θ 2 T 9z 8j 2 J, f j d; z; θð Þ  0
```
 
.
```
(a) If the test is positive, stop.
```
```
(b) If it is negative, identify the point θc with worst constraint violation.
```
Define T kþ1 ¼ T k [ θcf g N kþ1 ¼ T kþ1j j.
```
Set k ¼ k þ 1, and return to step (2).
```
We should note that the above algorithm corresponds to an iterative multiscenario problem
in which the weights wi are selected to approximate expected values. Furthermore, the set T0
will normally contain the nominal value of the parameters, θN , that represents the expected
```
value of θ. The remaining challenge is how to apply in step (3) the flexibility test for the fixed
```
d k . The answer to that question is provided in the next section.
15.3 Flexibility Analysis
As shown in Fig. 15.2, let us consider a fixed design d that is subjected to a vector of
uncertain parameters θ, and for which there is a vector of control variables z that can be
adjusted to counteract the effect of the uncertainties. Or, more specifically, our goal in the
flexibility test is to determine if, for the given design d , 8θ 2 T a vector of control variables z
```
can be selected to satisfy the inequalities f j d; z; θð Þ  0 8j 2 J, where in the most common
```
case T ¼ θjθL  θ  θU
 
, where θL and θU are lower and upper bounds, respectively, for
the uncertain parameters. Note that we might consider more general uncertainty sets such as
T ¼ θjr θð Þ  0f g, where r θð Þ  0 is a set of linear or nonlinear inequalities. Also, simplicial
```
approximations might be used, as described in Goyal and Ierapetritou (2002).
```
As indicated above, the flexibility test can be symbolically expressed as follows:
```
8θ 2 T 9z 8j 2 J, f j d; z; θð Þ  0
```
 h i
```
: (15.6)
```
```
d  ( , , ) 0 |f d z T     
```
z
q L q Uqqqq q
Figure 15.2 Elements of flexibility test for a
fixed design d.
144 15 Flexibility Analysis
```
Equation (15.6) can, in turn, be shown to be equivalent to a constraint involving a max-min-
```
```
max optimization problem as shown below (Halemane and Grossmann, 1983),
```
```
8θ 2 T 9z 8j 2 J, f j d; z; θð Þ  0
```
 h i
```
, 8θ 2 T 9z maxj2J f j d; z; θð Þ
```
 
 0
```
( 8θ 2 T minz maxj2J f j d; z; θð Þ  0
```
```
, maxθ2T minz maxj2J f j d; z; θð Þ  0:
```
```
(15.7)
```
Thus, we have proved the following theorem.
```
Theorem 15.1 The flexibility test 8θ 2 T 9z 8j 2 J, f j d; z; θð Þ  0
```
 ih
is equivalent to the
```
inequality max θ2T min z max j2J f j d; z; θð Þ  0.
```
Given the max-min-max function, we can define the flexibility function χ dð Þ for a fixed
design d, as follows:
```
χ dð Þ ¼ maxθ2T minz maxj2J f j d; z; θð Þ: (15.8)
```
In this way by calculating the function χ dð Þ, we can arrive at either of the two following
conclusions.
```
(a) If χ dð Þ  0 it implies that the design d is feasible 8θ 2 T.
```
```
(b) If χ dð Þ > 0 it implies that the design d is infeasible for some θ 2 T.
```
```
These, then, provide an answer to the steps (3a) and (3b) in the iterative multiscenario
```
optimization algorithm presented in the previous section.
15.4 Flexibility Test with No Control Variables
To gain some insight into the geometric interpretation of the flexibility function, χ dð Þ,
consider the particular case when there are no control variables z, that is dim zð Þ ¼ 0. For
```
this, problem (15.8) reduces to the following maximization problem:
```
```
χ dð Þ ¼ maxθ2T maxj2J f j d; θð Þ: (15.9)
```
```
Since the order of the max operators can be reversed, (15.9) is also equivalent to
```
χ dð Þ ¼ maxj2J max
θj 2T
```
f j d; θj
```
 
```
, (15.10)
```
in which we select the inequality j 2 J that leads to the largest value of the maximization of
```
each constraint f j d; θj
```
 
```
. Formulation (15.10) then suggests the following algorithm.
```
```
(1) Solve uj ¼ max θj 2T f j d; θj
```
 
8j 2 J.
```
(2) Set χ dð Þ ¼ max j2J ujf g.
```
15.4 Flexibility Test with No Control Variables 145
```
(3) If χ dð Þ  0 ) feasible 8θ 2 T
```
```
χ dð Þ > 0 ) infeasible for some θ 2 T:
```
As an example, consider the case of the three inequalities f1 , f2, and f3 in Fig.15.3 that
involve one single uncertain parameter θ.
By maximizing each inequality with respect to the parameter θ, the algorithm yields the
following results:
u1 ¼ maxθ f 1 < 0 at θL
u2 ¼ maxθ f 2 < 0 at θU
u3 ¼ maxθ f 3 > 0 at θU:
From the above it is clear that the critical point θc is given by the upper bound, that is
θc ¼ θU , since it is the point at which the maximum constraint violation takes place, namely
```
f 3 d; θcð Þ > 0.
```
For the general case in which we have p uncertain parameters, θi, i ¼ 1, . . . , p, we should
```
note that the full numerical maximization of each inequality f j d; z; θð Þ, j 2 J corresponds to
```
an NLP with respect to each parameter θi, i ¼ 1, . . . , p. These optimizations can be avoided
```
if each inequality f j d; z; θð Þ is quasiconvex, as then either θci ¼ θLi or θci ¼ θUi , meaning we
```
```
need only to analyze the vertices (combinations of lower and upper bounds) in the parameter
```
set T ¼ θjθL  θ  θU
 
.
```
Furthermore, if f j d; θð Þ is monotone in each θi, only the sign of the gradients need to be
```
analyzed, that is,
∂f j
```
∂θi> 0 ) θ
```
ci ¼ θUi , ∂f j
```
∂θi< 0 ) θ
```
```
ci ¼ θLi : (15.11)
```
This can easily be verified with the example in Fig. 15.3.
```
As a final point, we should note that if, instead of the inequalities f j d; z; θð Þ, j 2 J, we are
```
given the model in the form of equation and inequalities in terms of the state variables x and
uncertain parameters θ, that is,
```
h d; xi; θð Þ ¼ 0
```
```
g d; x; θð Þ  0, (15.12)
```
```
then step (1) in the above algorithm involves solving the following LP or NLP:
```
uj ¼ max
θj 2T
```
g j d; x; θj
```
 
```
s:t: h d; x; θj
```
 
¼ 0:
```
(15.13)
```
0
f1
f2f3
qL qU
Figure 15.3 Example of three
inequalities in terms of a single
uncertain parameter θ.
146 15 Flexibility Analysis
15.5 Flexibility Test with Control Variables
For the general case when there are control variables z, that is dim zð Þ > 0, consider the
```
flexibility test in (15.8), that is,
```
```
χ dð Þ ¼ maxθ2T minz maxj2J f j d; z; θð Þ: (15.14)
```
```
To analyze (15.14) we define the inner minimax problem as the feasibility function ψ d; θð Þ for
```
fixed design d and fixed uncertain parameter θ,
```
ψ d; θð Þ ¼ minz maxj2J f j d; z; θð Þ: (15.15)
```
This feasibility function, which corresponds to a nondifferentiable optimization problem due
to the max operator, is equivalent to the following optimization problem,
```
ψ d; θð Þ ¼ min u
```
```
s:t: u  f j d; z; θð Þ j 2 J
```
u 2 R1 , z 2 R nz ,
```
(15.16)
```
```
which corresponds to an LP or NLP depending on whether the functions f j d; z; θð Þ are linear
```
or nonlinear, and where u is a scalar variable that represents the maximum constraint
```
violation that is being minimized. We should note that the function ψ d; θð Þ represents a
```
```
projection from the d; z; θð Þ space into the d; θð Þ space. With problem (15.16) the flexibility
```
```
test (15.14) can be formulated as the following maximization problem:
```
```
χ dð Þ ¼ maxθ2T ψ d; θð Þ: (15.17)
```
```
To provide a geometric interpretation of problems (15.16) and (15.17), consider the two
```
following linear inequalities:
f 1 ¼ z þ θ  0
```
f 2 ¼ z  2θ þ 2  d  0: (15.18)
```
Let us assume that we set d ¼ 0:5 and that we would like to determine whether the inequal-
```
ities in (15.18) can be satisfied for all θ in the interval, 1  θ  2.
```
By plotting these inequalities in Fig. 15.4, it is clear that they are infeasible for the interval
1  θ  1:5, while they are feasible for the interval 1:5  θ  2, if z is adjusted for each θ.
Furthermore, the critical point θc with largest violation of constraints corresponds to the
lower bound θL ¼ 1.
These observations can in fact be verified from the formulations presented above.
```
Consider the feasibility function in (15.16) applied to the inequalities in (15.18),
```
```
ψ d; θð Þ ¼ minu, z u
```
```
s:t u  z þ θ
```
u  z  2θ þ 1:5:
```
(15.19)
```
```
To solve problem (15.19), consider the Lagrange function, where λ1 , λ2 are the nonnegative
```
```
Lagrange multipliers of the two inequalities in (15.19),
```
15.5 Flexibility Test with Control Variables 147
```
ℒ ¼ u þ λ1 z þ θ  uð Þ þ λ2 z  2θ þ 1:5  uð Þ: (15.20)
```
From the stationary conditions of the Lagrange function, we can conclude the following:
∂ℒ
```
∂u ¼ 1  λ1  λ2 ¼ 0 ) at least λ1 or λ2 > 0
```
∂ℒ
```
∂z ¼ λ1 þ λ2 ¼ 0 ) λ1 ¼ λ2 two active constraints
```
```
) λ1 ¼ λ2 ¼ 0:5:
```
```
(15.21)
```
```
From (15.21) it follows that, since λ1 ¼ λ2 ¼ 0:5, the two inequalities are active.
```
```
Furthermore, the Lagrange function in (15.20) at the optimum can be equated to the
```
```
feasibility function ψ d; θð Þ,
```
```
ℒ ¼ ψ d; θð Þ ¼ 0:5θ  θ þ 0:75 ¼ 0:75  0:5θ: (15.22)
```
Figure 15.5 shows the plot of this function, indicating infeasibility for the interval 1 
θ < 1:5 because ψ > 0, and feasibility for the interval 1:5  θ  2 because ψ  0.
Furthermore, the critical point θc with largest value of ψ ¼ 0:25 corresponds to the lower
bound θL ¼ 1.
If we change the design variable d from 0.5 to 1, then, as can be seen in Fig. 15.6a,
feasibility is achieved for all θ in the interval 1  θ  2, and ψ  0 as seen in the Fig. 15.6b,
with the critical point θc corresponding to the lower bound θL ¼ 1 with ψ ¼ 0.
Consider that we now add constraint f 3 ¼ z þ 6θ  9d  0. In that case the feasible
region is shown in Fig. 15.7a, where it can be seen that feasibility is also achieved for all θ in
the interval 1  θ  2, but in this case ψ is a nondifferentiable piecewise linear function as
f2
f1
1 21.5
z

Figure 15.4 Plot of feasible region
```
for the inequalities in (15.18).
```
0.25
0.25
1 1.5 2
Figure 15.5 Plot of the function
```
ψ d; θð Þ in (15.22).
```
148 15 Flexibility Analysis
the left portion is given by the active constraints f 1 , f 2 , while the right portion is given by the
active constraints f 2 , f 3 . Also, note that the critical points lie at both the lower and upper
bounds, θ ¼ 1 and θ ¼ 2, because at these two points the feasibility function ψ attains its
maximum value of ψ ¼ 0. Thus, this simple example gives some insights into the nature of
the feasibility function.
15.6 Parametric Region of Feasible Operation and Vertex Search
```
Having defined the feasibility function ψ d; θð Þ, we consider its projected feasible region R in
```
the space of the uncertain parameters θ, namely,
```
R ¼ θj9z 8j 2 J, f j d; z; θð Þ  0
```
 n o
```
, R ¼ θj minz maxj2J f j d; z; θð Þ
```
 
```
¼ θjψ d; θð Þ  0f g:
```
```
(15.23)
```
For the case of two uncertain parameters, θ1 , θ2 , we show in Fig. 15.8 the feasible region
```
R in which it can be seen that the boundary is defined by the feasibility function ψ d; θð Þ.
```
```
This means that the boundary is expressed in terms of the optimization problem in (15.16).
```
We can then also visualize the flexibility test, as shown in Figs. 15.9a and 15.9b.
As can be seen in Fig. 15.9a, feasibility is achieved for the specified uncertainty set T
```
because ψ d; θð Þ  0 for all θ 2 T, χ dð Þ  0. Also the critical point θc lies at the boundary
```
1
1 2 q
2
```
d =1
```
z
```
d =1
```
f2 f
3
f1
```
(a)
```
1
1 2
```
( f1 , f2) ( f2 , f3)
```
```
y (d,q)
```
q
```
(b)
```
```
Figure 15.7 (a) Feasible region, (b) feasibility function for additional inequality f 3 for d ¼ 1.
```
z
1 1.5 2
f1
f2
1 2
2
1
```
(a) (b)
```
```
Figure 15.6 (a) Feasible region, (b) feasibility
```
```
function ψ for d = 1.
```
15.6 Parametric Region of Feasible Operation 149
```
ψ d; θcð Þ ¼ 0 of the region R and corresponds to the vertex θL1 ; θL2
```
 
of the uncertainty set T.
In contrast, Fig. 15.9b shows a region R that is infeasible for a subset of points in the set T.
```
Furthermore, the maximum value of the feasibility function ψ d; θcð Þ > 0 is also attained at
```
```
the vertex θL1 ; θL2
```
 
, and hence χ dð Þ > 0.
We next describe an algorithm for solving the flexibility test problem for a fixed design d
and a specified uncertainty set T,
```
χ dð Þ ¼ maxθ2T minz maxj2J f j d; z; θð Þ: (15.24)
```
Assuming that critical points θc correspond to vertices of the uncertainty set
T ¼ θjθc  θ  θU
 
```
, the max-min-max problem in (15.24) can be solved as follows.
```
```
(1) Define the vertices θk , k 2 V , where V ¼ 1, 2; . . . ; 2pf g and p ¼ dim θð Þ.
```
```
(2) Solve, for each parameter vertex θk k 2 V , the following optimization problem,
```
```
ψ d; θk
```
 
¼ min u
```
s:t: u  f j d; z; θk
```
 
, j 2 J
u 2 R1 , z 2 Rn z ,
```
(15.25)
```
where the scalar u represents the largest violation of the inequalities
```
f j d; z; θk
```
 
 0, j 2 J.
```
(3) Set χ dð Þ ¼ max k2V ψ d; θk
```
  
.
```
(4) If χ dð Þ  0 the design d is guaranteed to be feasible for all points in the set T; if χ dð Þ > 0
```
the design d is infeasible over the uncertainty set T.
```
The above algorithm requires, in step (2), the solution of 2p optimization problems where
```
p ¼ dim θð Þ. It is clear that if the number of parameters is large, this algorithm can be
Boundary defined
```
by ( , ) 0d 
```
q2
q1
q
Figure 15.8 Parametric region R
of feasible operation.
20
T R
0, c 1
L 1U
2L
2U
20
T R
1L 1U
2L
2U
```
(a) (b)0, c
```
```
1design d 2design dFigure 15.9 (a) Feasibility achieved
```
```
for all θ 2 T, (b) infeasibility for some
```
θ 2 T.
150 15 Flexibility Analysis
computationally expensive. Furthermore, we should note that if the region R is nonconvex,
```
the critical points θc may not necessarily correspond to vertices (see Fig.15.13).
```
15.7 Flexibility Index and Vertex Search
The flexibility test only provides a yes or no answer to the capability of a given design to
achieve feasible operation over a specified parameter set T. Next we consider instead the
problem of determining a measure of the size of the feasible region Rð Þ that, in turn,
provides a guaranteed range for the uncertain parameters θ for which feasibility can be
guaranteed by proper adjustment of the control variables z.
```
The measure of the region Rð Þ, which we will denote as the flexibility index (Swaney and
```
```
Grossmann, 1985a, b), is given with respect to a nominal parameter point θN , and expected
```
parameter deviations Δθþ, Δθ. If we then consider as a target for flexibility the set T defined
by the nominal point and expected deviations,
T∗ ¼ θjθN  Δθ  θ  θN þ Δθþ
 
```
, (15.26)
```
```
we can define, for the parametric set T(F) in (15.27),
```
T Fð Þ ¼ θjθN  F Δθ  θ  θN þ F Δθþ
 
```
, (15.27)
```
```
the largest scalar F such that T(F) is inscribed within the region R, as shown in Fig. 15.10.
```
We denote the scalar F as the flexibility index. Once we obtain its value, we can conclude the
following for a given design d depending on the value of the index:
```
F ¼ 1 ) design meets the flexibility target,
```
```
F > 1 ) design exceeds the target,
```
```
F < 1 ) design does not meet the target.
```
```
To develop a mathematical formulation for finding the largest rectangle T(F) within the
```
region R centered at θN , and with sides proportional to Δθþ, Δθ, we define the following
parametric set T δð Þ in terms of the nonnegative variable δ:
Δq1– Δq1+
Δq2+
Δq2–
q1 q1
q c
q2
```
T (F)
```
N
q2N
Figure 15.10 Geometric
```
interpretation of set T(F) with
```
flexibility index F.
15.7 Flexibility Index and Vertex Search 151
T δð Þ ¼ θjθN  δΔθ  θ  θN þ δΔθþ
 
```
, δ  0: (15.28)
```
The flexibility index can then be determined by selecting the largest value of δ such that the
feasibility test holds true for all the parameter points θ in the set T δð Þ, that is,
F ¼ max δ
```
s:t: maxθ2T δð Þminz maxj2J f j d; z; θð Þ  0
```
T δð Þ ¼ θjθN  δ Δθ  θ  θN þ δ Δθþ
 
, δ  0:
```
(15.29)
```
```
Note from Fig. 15.10 that, at the optimum solution, ψ d; θcð Þ ¼ 0, meaning that the critical
```
point θc lies at the boundary of the region R, and limits the size of the largest rectangle.
```
The solution of problem (15.29) can be simplified if it is assumed critical points θc
```
correspond to vertices of the parametric set T δð Þ. The basic idea could then be to find the
```
largest deviation δk along each vertex direction ~θk , k 2 V ¼ 1, 2; . . . ; 2pf g, and pick among
```
these the smallest one to define the flexibility index. As an example, the vertex direction ~θ1
defined by positive directions is given by
~θ1 ¼ Δθ
þ1
Δθþ2
" #
```
: (15.30)
```
The algorithm for vertex search is then as follows.
```
(1) For each k 2 V ¼ 1, 2; . . . ; 2pf g, solve the following problem,
```
δk ¼ max δ
```
s:t: f d; z; θð Þ  0 Pk
```
 
θ ¼ θN þ δ Δ ~θk, δ  0:
```
(2) Set F ¼ min k2V δk
```
 
.
We should note that having obtained the flexibility index we can determine the actual feasible
range given by θN  F Δθ  θ  θN þ F Δθk. Furthermore, the critical point θc, corresponds
to the vertex direction with smallest δk. As in the case of the feasibility test, the major
limitation of the vertex search is that it requires the solution of 2p optimization problems in
```
step (2). The next section (Section 15.8) will show how to overcome this problem.
```
An interesting additional point is that, from the results of the above algorithm, we can
perform a sensitivity analysis of the flexibility index with respect to changes in a given design
variable d i. For this, consider the variation of the flexibility index F with respect to the
design variable d i,
∂F
∂d i¼
X
j2J
∂F
∂f j
∂f j
```
∂d i, (15.31)
```
```
where ∂f j∂d i can be obtained analytically or by finite differences from the inequalities f j d; z; θð Þ.
```
152 15 Flexibility Analysis
Say k ¼ c corresponds to the closest vertex direction with deviation δc. Then,
∂F
∂f j¼
∂δc
∂f j¼ λ
```
cj , (15.32)
```
```
where λcj corresponds to the Lagrange multiplier of the jth inequality in problem (Pk).
```
```
Substituting in (15.31), one can then obtain an explicit equation to predict the sensitivity
```
of the flexibility index with respect to a change in the design variable d i.
∂F
∂d i¼ 
X
j2J
λcj∂f j∂d
i
```
: (15.33)
```
```
This sensitivity could be very useful for retrofit design problems (e.g., to determine in a heat-
```
exchanger network that exchanger where adding area leads to the largest increase in the flexibility
```
index). This analysis can also be extended to multiobjective optimization problems in which cost
```
```
is minimized and flexibility is maximized (see Pistikopoulos and Grossmann, 1988).
```
15.8 Theoretical Conditions for Vertex Solutions
As was shown in Sections 15.6 and 15.7, the flexibility test and calculation of the flexibility
index can be greatly simplified if it is assumed that critical points correspond to vertices in
the sets T and T δð Þ. An important theoretical question is to determine the sufficient
conditions that need to hold for a critical point θc to be a vertex in these parameter sets.
For simplicity, we restrict the presentation to the parameter set T ¼ θ θL  θ  θU
 
.
```
A region R ¼ θjψ d; θð Þ  0f g is defined as being one-dimensional (1-d) convex if and
```
only if, for θ1 , θ2 2 R, where θ2 ¼ θ1 þ βe j , β 6 ¼ 0, e j coordinate direction
 
, the point
θ ¼ αθ1 þ 1  αð Þθ2 2 R 8α 2 0, 1½ . In short, 1-d convexity requires that the convexity
condition holds true only along the coordinate directions.
Figure 15.11 shows examples of three regions. Figure15.11a corresponds to a convex
region, which is shown to be also 1-d convex. Figure 15.11b corresponds to a nonconvex
region, which, however, is 1-d convex. Finally, Fig. 15.11c corresponds to a nonconvex
q 1
q 1q 1
q 2q 2
q 2
q 2 q 2 q 2
q 1 q 1 q 1Convex
```
(a) (b) (c)
```
Nonconvex, 1-d convex Nonconvex, not 1-d convex
```
Figure 15.11 (a) Convex region, (b) 1-d convex region, (c) nonconvex region.
```
15.8 Theoretical Conditions for Vertex Solutions 153
region, which is not 1-d convex. In summary, 1-d convexity can be viewed as a less restrictive
condition than convexity.
```
The following theorems can be established for 1-dimensional convexity (Swaney and
```
```
Grossmann, 1985a, b).
```
```
Theorem 15.2 If ψ d; θð Þ is a 1-d quasiconvex function in θ, then R ¼ θjψ d; θð Þ  0f g is a 1-d
```
convex region.
```
Theorem 15.3 If ψ d; θð Þ is 1-d quasiconvex, then the critical point θc lies at a vertex of the set
```
T.
The above theorems rely on the following definition.
```
Definition 15.1 ψ d; θð Þ is 1-d quasiconvex in θ if and only if
```
```
ψ d; αθ1
```

```
þ 1  αð Þθ2Þ  max ψ d; θ1
```
 
```
, ψ d; θ2
```
  
8α 2 0, 1½ , where θ1 , θ2 2 R,
θ2 ¼ θ1 þ βe j .
```
Figure 15.12 illustrates an example of a function ψ d; θð Þ which is quasiconvex, while being
```
a nonconvex concave function.
```
The following theorem provides a sufficient condition for the feasibility function ψ d; θð Þ
```
to be 1-d quasiconvex in θ.
```
Theorem 15.4 If the constraint functions f j d; z; θð Þ  0, j 2 J are quasiconvex in z and 1-d
```
```
quasiconvex in θ, then ψ d; θð Þ is 1-d quasiconvex in θ.
```
In summary, from the above theorems, the following are sufficient conditions for a critical
point θc to lie at the vertex of the parameter set T.
```
(1) The functions f j d; z; θð Þ  0, j 2 J are quasiconvex in z and 1-d quasiconvex in θ.
```
```
(2) ψ d; θð Þ is 1-d quasiconvex in θ.
```
```
(3) R is 1-d convex.
```
```
An example of a problem where the critical point does not correspond to a vertex (Biegler
```
```
et al., 1997) is the heat-exchanger network shown in Fig. 15.13 where the heat capacity
```
flowrate FH1 is an uncertain parameter. We would like to determine whether this network is
feasible for the range 1  F H1  1:8 kW=Kð Þ.
The following inequalities are considered for feasible operation of this network:
```
( ),d
```
```
( , )d
```
q2q1
q1
q2Figure 15.12 Concave function
```
ψ d; θð Þ which is quasiconvex.
```
154 15 Flexibility Analysis
Feasibility in exchanger 2: T 2  T 1  0
Feasibility in exchanger 3: T 2  393  0
Feasibility in exchanger 3: T 3  313  0
Specification in outlet temperature: T 3  323:
```
(15.34)
```
By considering the corresponding heat balances, we can solve for the above temperatures in
terms of the cooling load Q c, the control variable, and in terms of FH1 , the uncertain
```
parameter. The reduced inequalities in (15.34) are then as follows:
```
f 1 ¼ 25 þ Q c 1=F H1ð Þ  0:5½  þ 10=F H1  0
f 2 ¼ 190 þ 10=F H1ð Þ þ Q c=F H1ð Þ  0
f 3 ¼ 270 þ 250=F H1ð Þ þ Q c=F H1ð Þ  0
f 4 ¼ 260  250=F H1ð Þ  Q c=F H1ð Þ  0:
```
(15.35)
```
```
If we now examine the two extreme points, for FH1 , by solving the NLP in (15.16) for the
```
above inequalities we obtain the following.
```
(a) For F H1 ¼ 1 kW/K, ψ1 1ð Þ ¼ 5, Qc ¼ 15 kW.
```
```
(b) For F H1 ¼ 1.8 kW/K, ψ2 1:8ð Þ ¼ 5, Qc ¼ 227 kW.
```
Because ψ1 < 0 and ψ2 < 0, we may be tempted to conclude that the network is feasible to
operate for the range 1  F H1  1:8 kW=K. However, let us consider an intermediate value,
```
say F H1 ¼ 1.2 kW/K, for problem (15.16). We then obtain:
```
```
F H1 ¼ 1:2 kW=K, ψ 1:2ð Þ ¼ 2:85; Qc ¼ 58:57 kW:
```
In other words, the network is infeasible at the nonvertex point F H1 ¼ 1.5 kW/K. If we
```
plot the constraints in (15.34) as shown in Fig. 15.14 we can clearly see that we have a
```
nonconvex region where for 1:118  F H1  1:65 we have infeasible operation. In fact, at
T12 kW/K
388 K
2 kW/K
723 K
Q c
553 K
F HI
583 K
563 K
T2
3 kW/K
313 K 393 K
323 KT3 
Figure 15.13 Heat-exchanger
network with uncertain heat
capacity flowrate, FH1 .
15.8 Theoretical Conditions for Vertex Solutions 155
F H1 ¼ 1.37 kW/K we have the greatest violation of constraints since at that point ψ 1:37ð Þ ¼
þ5:108 attains its maximum value. Hence, FH1 ¼ 1.37 corresponds to the critical point.
The above example then shows that it is possible to have nonvertex critical points and,
consequently, we need an appropriate method that will be able to predict such points, as we
will show in the next section.
15.9 Active-Set Strategy
In this section we present mixed-integer programming formulations for the flexibility test
```
(15.24) and flexibility index (15.29) that do not rely on the assumption that a critical point θc
```
corresponds to a vertex. The basic idea in these formulations relies on performing the search
```
in the space of active inequality constraints (Grossmann and Floudas, 1987).
```
```
The flexibility-test problem, χ d; θð Þ ¼ max θ min z max j2J f j d; z; θð Þ in (15.24), can be
```
reformulated as the two-level optimization problem
```
χ dð Þ ¼ maxθ2T ψ d; θð Þ
```
```
s:t: ψ d; θð Þ ¼ minz maxj2J f j d; z; θð Þ: (15.36)
```
In order to replace the lower level optimization problem with a set of constraints, we
```
consider the KKT conditions (Bazaraa et al., 2006) of the feasibility-test function ψ d; θð Þ,
```
```
ψ d; θð Þ ¼ minz u
```
```
s:t: f j d; z; θð Þ  u  0, j 2 J
```
u 2 R1 ,
```
(15.37)
```
Q c
1 1.5 2
1.37
F HI
300
200
100
f2
f3
f4
f1Figure 15.14 Feasible region for
```
constraints in (15.34).
```
156 15 Flexibility Analysis
```
where we assume that the functions f j d; z; θð Þ include the bounds for the control variables z.
```
Therefore, n ¼ dim zð Þ < m ¼ Jj j.
```
In order to derive the KKT conditions for problem (15.36), we define the Lagrangean
```
function
ℒ ¼ u þ
X
j2J
```
λj f j d; z; θð Þ  u
```
h i
```
: (15.38)
```
The stationary conditions with respect to the scalar variable u and the control variables z are
```
given by (15.39a) and (15.39b), while the complementarity conditions are given by (15.39c),
```
where λj  0 are the Lagrange multipliers,
∂ℒ
∂u ¼ 1 
X
j2J
λj ¼ 0 að Þ
∂ℒ
∂z ¼
X
j2J
λj∂f j∂z ¼ 0 bð Þ
```
λj f j d; z; θð Þ  u
```
h i
¼ 0
```
λj  0 f j d; z; θð Þ  u  0
```
9
=
```
;j 2 J cð Þ:
```
```
(15.39)
```
```
From (15.39a) we can conclude that at least one multiplier is strictly positive λj > 0 (i.e., one
```
```
f j is active). From (15.39b), if the transpose of the Jacobian, J Tz ¼ ∂f 1∂z∂f 2∂z    ∂f m∂z
```
h i
is full
```
rank, then at least n þ 1 multipliers must be strictly positive λj > 0. But from (15.39c),
```
```
to have a solution f j d; z; θð Þ  u  0, at most n þ 1 constraints are active
```
```
n ¼ dim zð Þ, dim uð Þ ¼ 1ð Þ. This property, known as the Haar condition (Haar, 1918),
```
```
holds for the minimax problem in (15.37). We can then establish the following
```
useful property.
```
Property 15.1 If ψ d; θð Þ has n þ 1 active constraints, then the KKT are necessary and
```
```
sufficient for a local min of ψ d; θð Þ.
```
```
The implication of this property is that we can use the KKT conditions to replace ψ d; θð Þ
```
```
as a constraint in problem (15.36), and then in turn identify the sets of active constraints as
```
shown in the example in Fig. 15.15.
```
By replacing the KKT conditions for ψ d; θð Þ in problem (15.36), the active-set formula-
```
tion for the feasibility-test problem is as follows:
15.9 Active-Set Strategy 157
```
χ dð Þ ¼ maxθ2T ψ d; θð Þ
```
```
s:t: 1 
```
X
j2J
λj ¼ 0
X
j2J
λj∂f j∂z ¼ 0
```
λj f j d; z; θð Þ  u
```
h i
¼ 0, j 2 J
```
λj  0, f j d; z; θð Þ  u  0, j 2 J:
```
```
(15.40)
```
```
The difficulty, however, in problem (15.40) lies in the complementarity conditions as they
```
involve bilinearities that, aside from introducing nonconvexities, give rise to discontinuities
in the derivatives. To circumvent these difficulties, we explicitly model the discrete choice of
active constraints involved in the complementarity conditions. First, we define the slack
variables, s j  0, such that the inequalities are expressed as follows:
```
sj ¼ u  f j d; z; θð Þ 8j 2 J: (15.41)
```
Next, we introduce the binary variables yj to indicate which constraints are active or not, namely,
yj ¼ 1 if constraint j is active s j ¼ 0
 
0 otherwise s j  0
 
:

```
(15.42)
```
The complementarity conditions, together with the Haar condition, can then be expressed as
```
follows:
```
s j  U 1  yj
 
 0, j 2 J
λj  yj  0 j 2 J
```
)
```
X
j2J
yj  n þ 1
sj , λj  0 j 2 J:
```
(15.43)
```
```
dim( z ) =1
```
f2
f1
f1, f2 f2, f3
f3
n+1 = z active sets
Active set 1 Active set 2
z
Nondifferentiable
maximum at bounds
y
q
q
Figure 15.15 Example of active sets for
three inequalities.
158 15 Flexibility Analysis
```
By substituting (15.41) and (15.43) into (15.40) the flexibility test can then be formulated as
```
```
the following mixed-integer programming problem (PFT),
```
χ dð Þ ¼ maxθ, u, z, λj , sj , y
j
u
```
s:t: 1 
```
X
j2J
λj ¼ 0
X
j2J
λj∂f j∂z ¼ 0
```
s j þ f j d; z; θð Þ ¼ u j 2 J
```
s j  U 1  y j
 
 0, j 2 J
λj  yj  0, j 2 J
X
j2J
yj  n þ 1
y j 2 0, 1f g, λj , s j  0, u 2 R1 , z 2 Rn, θL  θ  θU:
```
(PFT)
```
```
Depending on the nature of the inequalities problem, (PFT) corresponds to an MILP or an
```
```
MINLP problem. In particular, if the functions f j d; z; θð Þ are linear in z and θ then the
```
```
gradients ∂f j∂z are constants with which (PFT) reduces to an MILP problem. Furthermore, the
```
KKT conditions are necessary and sufficient, and the maximum number of active con-
```
straints is given by Pj2J yj  n þ 1. In the case that the functions f j d; z; θð Þ are nonlinear in
```
```
z, θ, problem (PFT) gives rise to an MINLP problem. For the particular case that the
```
```
constraints f j d; z; θð Þ are quasiconvex in z and quasiconcave in θ, the relaxation of the
```
MINLP will have a unique solution with which convex MINLP solvers can be used.
Interestingly, that is the case of the heat-exchanger network problem in Fig. 15.13 where
```
(PFT) can predict the nonvertex critical point FH1 ¼ 1.37 (Biegler et al., 1997). For the case
```
```
that the constraints f j d; z; θð Þ are quasiconvex in z and 1-d quasiconvex in θ, (PFT) will
```
correspond to a nonconvex MINLP that yields vertex solutions but without requiring the
solution of 2p subproblems, as is the case with vertex search methods. The computational
effort of the mixed-integer programming problem will be proportional to the number of
```
constraints, Jj j. Finally, we should also note that in problem (PFT) the bounds on the
```
uncertain parameters, θL  θ  θU , can easily be replaced by more general parameter sets
r θð Þ  0.
```
Another important point about problem (PFT) is that it can easily be extended for the
```
```
case where the original model is given by equations and inequalities as in (15.12). By
```
```
assigning multipliers to these constraints as in (15.44),
```
```
hi d; x; z; θð Þ ¼ 0, i 2 I ! μi
```
```
g j d; x; z; θð Þ  0, j 2 J ! λi, (15.44)
```
and defining the feasibility-test problem as follows,
15.9 Active-Set Strategy 159
```
ψ d; θð Þ ¼ minz u
```
```
h i d; x; z; θð Þ ¼ 0, i 2 I
```
```
g j d; x; z; θð Þ  u, j 2 J:
```
```
(15.45)
```
```
The derivation then follows similar steps as in the derivation of problem (PFT) (see
```
```
Exercise 15.2).
```
As for the flexibility index, we can also formulate it as a mixed-integer programming
problem in terms of active sets, by defining the index F as the smallest deviation δ to the
```
boundary ψ d; θð Þ ¼ 0. That is,
```
F ¼ min δ
```
s:t: ψ d; θð Þ ¼ 0
```
T δð Þ ¼ θjθN  δΔθ  θ  θN þ δΔθþ
 
:
```
(15.46)
```
```
By replacing ψ d; θð Þ by the KKT conditions, and by introducing the binary variables yj ,
```
the flexibility index can be formulated as the following mixed-integer programming problem,
F ¼ minθ, δ, z, λj , sj , y
j
δ
```
s:t: 1 
```
X
j2J
λj ¼ 0
X
j2J
```
λj∂f j d; z; θð Þ∂z ¼ 0
```
```
s j þ f j d; z; θð Þ ¼ 0 j 2 J
```
s j  U 1  yj
 
 0 j 2 J
λj  y j  0 j 2 J
X
j2J
yj  n þ 1 j 2 J
θN  δ Δθ  θ  θN þ δ Δθþ
yj 2 0, 1f g, λj , sj  0, u 2 R1 , δ  0, z 2 Rn
θL  θ  θU:
```
(PFI)
```
```
As in the case of problem (PFT), (PFI) is a mixed-integer program, which corresponds to an
```
MILP or MINLP depending on the nature of the constraint functions, and is not restricted
to assuming vertex solutions. Also, this formulation can be extended to handle models with
```
equality and inequality constraints as in (15.22).
```
```
For the case when f j d; z; θð Þ is monotone in z and the Jacobian J Tz is full rank, the set of
```
n þ 1 active constraints can be identified from the stationary condition in terms of the
control variable z.
160 15 Flexibility Analysis
As an example, consider the inequalities in Fig. 15.16. It is clear from
```
λ1∂f 1∂z þ λ2∂f 2∂z þ λ3∂f 3∂z ¼ 0 (15.47)
```
that, because ∂f 1∂z > 0, ∂f 2∂z < 0, ∂f 3∂z > 0, and that there are n þ 1 ¼ 2 active constraints, the two
```
sets of active constraints are given by f 1 , f 2 and f 2 , f 3 , since these satisfy (15.47) for
```
nonnegative multipliers. Identifying these two active sets, we can simply fix their corres-
```
ponding binary variables in the MI(N)LP either (PFT) or (PFI), and obtain the solution by
```
solving the two corresponding LPs or NLPs.
EXERCISES
15.1 The inequality constraints for feasible operation of a design d are given by
f 1 ¼ 25θ þ z 1  θ=2½  þ d  0
f 2 ¼ 190θ þ z þ d  0
f 3 ¼ 260θ  z  240  d  0,
where θ is an uncertain parameter and z is a control variable. For the design d ¼ 10, do
the following.
```
(a) Plot the feasible region of operation in the z  θ space.
```
```
(b) Obtain the analytical expression for the feasibility function ψ d; θð Þ in the range
```
0:5  θ  2, and plot this function.
```
(c) Determine the critical point for feasible operation in this design. Explain why the
```
critical point is a vertex or a nonvertex solution.
```
(d) Is this design feasible for the parameter range 0:5  θ  2?
```
15.2 Derive the mathematical formulations for the active-set strategy for the following
cases.
```
(a) Feasibility test: only inequalities, no control variables.
```
```
(b) Feasibility test: equalities and inequalities with control variables.
```
```
(c) Flexibility index for two cases above.
```
```
15.3 Given is a set of inequalities f j d; z; θ; σð Þ  0, j 2 J that are linear in d, z, θ, and σ, and
```
where d is a fixed design, z are the control variables, and θ and σ are uncertain
f1
f2
f3

zFigure 15.16 Example with
three inequalities.
Exercises 161
parameters. The difference between parameters θ and σ is that for θ we can manipulate
the variables z to meet the constraints, while σ are parameters for which this is not
possible because we cannot readily measure and react to changes to this parameter. An
example for θ would be inlet flow that can be readily measured. An example for σ would
be a tray efficiency that cannot be readily measured. Assuming that θ and σ are specified
in the bounded sets T ¼ θjθL  θ  θU
 
, S ¼ σjσL  σ  σU
 
, do the following.
```
(a) Formulate a mathematical expression in terms of max and min operators to impose
```
the flexibility condition that the inequalities must be satisfied 8θ 2 T, 8σ 2 S.
```
(b) Derive an MILP formulation to solve the above flexibility test problem.
```
15.4 In the heat-exchanger network shown below, the inlet temperatures of the two hot and
two cold process streams are regarded as uncertain parameters. Given the nominal
values of the temperatures shown in the figure, and expected deviations of 10 K in
each of these streams, determine the flexibility index for this network and its range of
inlet temperatures for feasible operation.
1.5 kW/K
620 K
388 K
CW
350 K C23 kW/K313 K
393 K
323 K
Q c
C1
2 kW/K
H2H1 583 K
1 kW/K
563 K
21
3
You can do the following to solve this problem.
```
(a) Formulate the inequality constraints for feasible heat exchange and the spec T 
```
323 K in terms of the cooling load Q c and the inlet temperatures using
ΔTmin ¼ 0 K:
```
(b) Solve for the flexibility index with a vertex enumeration scheme (i.e., sixteen LPs)
```
and with the MILP formulation.
```
Note: Areas are not specified. Q c at 300 K.
```
15.5 Derive the mixed-integer active-set strategy formulation of the flexibility index for the
case when the model for a fixed design is given by equations and inequalities with state
variables x, with more than one control variable z n z  1ð Þ, and with uncertain param-
eters θ.
162 15 Flexibility Analysis
APPENDIX A
Modeling Systems and Optimization Software
A.1 Modeling Systems
```
Review: Kallrath, J. (2004) Modeling Languages in Mathematical Optimization, Kluwer
```
Academic Publishers.
AIMMS www.aimms.com/
```
AIMMS (Advanced Interactive Multidimensional Modeling System) is a prescriptive ana-
```
lytics software. It has two main product offerings that provide modeling and optimization
capabilities across a variety of industries. The AIMMS Prescriptive Analytics Platform
allows advanced users to develop optimization-based applications and deploy them to
business users. AIMMS SC Navigator, launched in 2017, is built on the AIMMS
Prescriptive Analytics Platform and provides configurable Apps for supply-chain teams.
SC Navigator provides supply-chain analytics to nonadvanced users.
```
Bisschop, J. and Roelofs, M. (2004) “The modeling language AIMMS”, in Kallrath, J. (ed.) Modeling
```
Languages in Mathematical Optimization. Applied Optimization, vol. 88. Boston, MA: Springer.
AMPL https://ampl.com/
The AMPL system is a modeling tool that supports the entire optimization modeling
```
lifecycle: development, testing, deployment, and maintenance. By using a high-level repre-
```
sentation that represents optimization models, AMPL promotes rapid development and
reliable results. AMPL integrates a modeling language for describing optimization data,
```
variables, objectives, and constraints; a command language for browsing models and
```
```
analyzing results; and a scripting language for gathering and manipulating data and for
```
implementing iterative optimization schemes. All use the same concepts and syntax for
streamlined application-building.
```
Fourer, R. (2013) “Algebraic modeling languages for optimization”, in Gass, S. I. and Fu, M.C.
```
```
(eds.) Encyclopedia of Operations Research and Management Science, Springer.
```
FICO XPRESS www.fico.com/en/products/fico-xpress-optimization
The FICO XPRESS optimizer is a commercial optimization solver for linear programming
```
(LP), mixed-integer linear programming (MILP), convex quadratic programming (QP),
```
```
convex quadratically constrained quadratic programming (QCQP), second-order cone pro-
```
```
gramming (SOCP), and their mixed-integer counterparts. XPRESS includes a general
```
purpose nonlinear solver, XPRESS NonLinear, including a successive linear programming
163
```
algorithm (SLP, first-order method), and Artelys Knitro (second-order methods). XPRESS
```
was originally developed by Dash Optimization, and was acquired by FICO in 2008.
```
Ashford, R. (2007) “Mixed integer programming: A historical perspective with Xpress-MP”, Annals of
```
Operations Research, 149, 5–17.
GAMS www.gams.com/
GAMS is one of the leading tool providers for the optimization industry and was the first
software system to combine the language of mathematical algebra with traditional programming
concepts in order to efficiently describe and solve optimization problems. The General Algebraic
```
Modeling System (GAMS) is a high-level modeling system for mathematical programming and
```
optimization. It consists of a language compiler and a stable of integrated high-performance
solvers. GAMS is tailored for complex, large-scale modeling applications, and allows us to build
large maintainable models that can be adapted quickly to new situations. GAMS is specifically
designed for modeling linear, nonlinear, and mixed-integer optimization problems.
```
Bussieck, M.R. and Meeraus, A. (2004) “General Algebraic Modeling System (GAMS)”, in Kallrath,
```
J. (ed.) Modeling Languages in Mathematical Optimization, Applied Optimization, vol. 88. Boston,
```
MA: Springer, pp. 137–157.
```
Julia https://julialang.org/
Julia is a high-level, high-performance dynamic programming language for technical com-
```
puting. It is free (open source) and supports Windows, OSX, and Linux. It has a familiar
```
syntax, works well with external libraries, is fast, and has advanced language features like
metaprogramming that enable interesting possibilities for optimization software.
```
Bezanson, J. et al. (2017) “Julia: A fresh approach to numerical computing”, SIAM Review, 59, 65–98.
```
JuMP https://jump.dev/JuMP.jl/stable/
JuMP is a domain-specific modeling language for mathematical optimization embedded in
Julia. It currently supports a number of open-source and commercial solvers for a variety of
problem classes, including linear programming, mixed-integer programming, second-order
conic programming, semidefinite programming, and nonlinear programming.
```
Dunning, I., Huchette, J. and Lubin, M. (2017) “JuMP: A modeling language for mathematical
```
```
optimization”, SIAM Review, 59(2), 295–320.
```
LINDO Systems www.lindo.com/
LINGO is a comprehensive tool designed to make building and solving linear, nonlinear
```
(convex and nonconvex/global), quadratic, quadratically constrained, second-order cone,
```
semidefinite, stochastic, and integer optimization models faster, easier, and more
efficiently. LINGO provides an integrated package that includes a language for expressing
optimization models, a full featured environment for building and editing problems, and a
set of fast built-in solvers.
164 Appendix A
```
Cunningham, K. and Schrage, L. (2004) “The LINGO algebraic modeling language”, in Kallrath,
```
J. (ed.) Modeling Languages in Mathematical Optimization. Applied Optimization, vol. 88. Boston,
```
MA: Springer.
```
Pyomo www.pyomo.org/
Pyomo was conceived in the mid 2000s at Sandia National Labs, implementing custom
representations, algorithms, and decompositions for large-scale models. Object-oriented
modeling and the natural expression of model concepts are the guiding principles behind
Pyomo, which embeds its modeling objects in Python, granting modelers and developers
easy interoperability to a rich set of extensions and supporting libraries. Traditional alge-
braic modeling languages provide a high-level abstraction between algebraic formulations
and the matrix input to optimization solvers. Pyomo extends these abstractions to support
```
stochastic programming (PySP), differential equations (Pyomo.DAE), and propositional
```
```
logic (Pyomo.GDP). At the same time, it provides automated access to low-level operations
```
on model expressions, such as symbolic differentiation and bounds tightening. Pyomo can
interface to GAMS and AMPL-linked free/commercial solvers, the Z3 satisfiability solver,
or custom algorithms implemented in Pyomo supplies the backbone modeling capabilities
behind the IDAES PSE framework, Egret, and other higher-level engineering analysis tools.
```
Hart, W. E. et al. (2017) Pyomo – Optimization Modeling in Python. Springer.
```
A.2 Optimization Software: LP, MILP, NLP, MINLP, GDP
A.2.1 Optimization Software Reviews
Linear Programming Software Survey, R. Fourer
www.informs.org/ORMS-Today/Public-Articles/June-Volume-40-Number-3/Linear-
Programming-Software-Survey
Nonlinear Programming Software Survey, S. Nash
www.informs.org/ORMS-Today/OR-MS-Today-Software-Surveys/Nonlinear-
Programming-Software-Survey
```
Atamturk, A. and Savelsbergh, M. W. P. (2005) “Integer-programming software systems”, Annals of
```
Operations Research, 140, 67–124.
```
D’Ambrosio, C. and Lodi, A. (2013) “Mixed integer nonlinear programming tools: an updated
```
```
practical overview”, Annals of Operations Research, 204(1), 301–320.
```
```
Gould, N., Orban, D. and Toint, P. (2005) “Numerical methods for large-scale nonlinear optimization”,
```
Acta Numerica, 299–361.
```
Kronqvist, J. et al. (2019) “A review and comparison of solvers for convex MINLP”, Optimization and
```
Engineering, 20, 397–455.
```
Kumar, P. H. and Mageshvaran, R. (2020) “Methods and solvers used for solving mixed integer linear
```
programming and mixed nonlinear programming problems: A review”, International Journal of
Scientific & Technology Research, 9, 1872–1882.
Modeling Systems and Optimization Software 165
```
Linderoth, J. T. and Ralphs, T. K. (2005) “Noncommercial software for mixed-integer linear pro-
```
gramming”. http://homepages.cae.wisc.edu/~linderot/papers/Linderoth-Ralphs-05-TR.pdf
A.2.2 Solvers and Corresponding Links
LP
• CLP https://github.com/coin-or/Clp
• CPLEX www.ibm.com/analytics/cplex-optimizer
• GLPK www.gnu.org/software/glpk/
• GUROBI www.gurobi.com/
• MOSEK www.mosek.com/
• QSOPT www.math.uwaterloo.ca/~bico/qsopt/
• SoPlex https://soplex.zib.de/
• XA www.maximalsoftware.com/solvers/xa.html
• XPRESS www.fico.com/en/products/fico-xpress-optimization
MILP
• CBC https://github.com/coin-or/Cbc
• CPLEX www.ibm.com/analytics/cplex-optimizer
• GLPK www.gnu.org/software/glpk/
• GUROBI www.gurobi.com/
• MOSEK www.mosek.com/
• SCIP www.scipopt.org/
• XA www.maximalsoftware.com/solvers/xa.html
• XPRESS www.fico.com/en/products/fico-xpress-optimization
MIQP
• CPLEX www.ibm.com/analytics/cplex-optimizer
• GUROBI www.gurobi.com/
• XPRESS www.fi co.com/en/products/fi co-xpress-optimization
NLP
• Antigone http://ares.tamu.edu/ANTIGONE/
• BARON www.minlp.com/baron
• CONOPT www.conopt.com/
• COUENNE https://github.com/coin-or/Couenne
• IPOPT https://github.com/coin-or/Ipopt
• KNITRO www.artelys.com/solvers/knitro/
166 Appendix A
• LANCELOT www.swmath.org/software/500
• LGO www.gams.com/latest/docs/S_LGO.html
• LINDO www.lindo.com/index.php/products/lingo-and-optimization-modeling
• LOQO https://vanderbei.princeton.edu/loqo/LOQO.html
• MINOS www.sbsi-sol-optimize.com/asp/sol_product_minos.htm
• SNOPT www.sbsi-sol-optimize.com/asp/sol_product_snopt.htm
MINLP
• Alpha-ECP www.sbsi-sol-optimize.com/asp/sol_product_snopt.htm
• Antigone http://ares.tamu.edu/ANTIGONE/
• BARON www.minlp.com/baron
• Bonmin https://github.com/coin-or/Bonmin
• COUENNE https://github.com/coin-or/Couenne
• DICOPT www.gams.com/latest/docs/S_DICOPT.html
• Filmint www.swmath.org/software/6197
• LaGO https://github.com/coin-or/LaGO
• LINDOGlobal www.lindo.com/index.php/products/lingo-and-optimization-modeling
• MindtPy https://pyomo.readthedocs.io/en/stable/contributed_packages/mindtpy.html
• MINOPT http://titan.princeton.edu/MINOPT/minopt.html
• Minotaur www.anl.gov/mcs/minotaur-toolkit-for-mixed-integer-nonlinear-optimization-
problems
• MOSEK www.mosek.com/
• Pajarito https://github.com/JuliaOpt/Pajarito.jl
• SBB www.gams.com/latest/docs/S_SBB.html
• SCIP www.scipopt.org/
• SHOT https://github.com/coin-or/SHOT
• XPRESS www.fico.com/en/products/fico-xpress-optimization
GDP
• EMP www.gams.com/latest/docs/S_JAMS.html#EMP_DISJUNCTIVE_PROGRAMS
• LOGMIP www.logmip.ceride.gov.ar/
• Pyomo.GDP https://pyomo.readthedocs.io/en/stable/modeling_extensions/gdp.html
NEOS Server
```
https://neos-server.org/neos/
```
The NEOS Server is a free internet-based service for solving numerical optimization
problems.
Modeling Systems and Optimization Software 167
A.2.3 References on Optimization Software
```
Abhishek, K., Leyffer, S. and Linderoth, J. (2010) “FilMINT: An outer approximation-based solver
```
for convex mixed-integer nonlinear programs”, INFORMS Journal on Computing. doi: 10.1287/
ijoc.1090.0373.
```
Aps, M. (2020) “MOSEK documentation”.
```
```
Bandler, J. W., Charalambous, C. and Chen, J. H. K. (1976) “MINOPT – An optimization program
```
```
based on recent minimax results (computer program descriptions)”, IEEE Transactions on
```
Microwave Theory and Techniques. doi: 10.1109/tmtt.1976.1128901.
```
Belotti, P. (2010) COUENNE: A User’s Manual. Available at: https://projects.coin-or.org/Couenne/
```
```
browser/trunk/Couenne/doc/couenne-user-manual.pdf?format=raw (Accessed: 20 May 2018).
```
```
Belotti, P., Berthold, T. and Neves, K. (2016) “Algorithms for discrete nonlinear optimization in
```
FICO Xpress”, in Proceedings of the IEEE Sensor Array and Multichannel Signal Processing
Workshop. doi: 10.1109/SAM.2016.7569658.
```
Bernal, D. E. et al. (2018) “Mixed-integer nonlinear decomposition toolbox for Pyomo
```
```
(MindtPy)”, in Computer Aided Chemical Engineering, pp. 895–900. doi: 10.1016/B978-0-444-
```
64241-7.50144-0.
```
Bernal, D. E. et al. (2020) “Improving the performance of DICOPT in convex MINLP
```
problems using a feasibility pump”, Optimization Methods and Software. doi: 10.1080/10556788
.2019.1641498.
```
Bonami, P. et al. (2008) “An algorithmic framework for convex mixed integer nonlinear programs”,
```
```
Discrete Optimization, 5(2), 186–204. doi: 10.1016/j.disopt.2006.10.011.
```
```
Bussieck, M. R. and Drud, A. S. (2001) “SBB: A new solver for mixed integer nonlinear program-
```
ming”, in Talk at OR2001.
```
Coey, C., Lubin, M. and Vielma, J. P. (2020) “Outer approximation with conic certificates for mixed-
```
integer convex problems”, Mathematical Programming Computation. doi: 10.1007/s12532-020-
00178-3.
```
Conn, A., Gould, N. I. M. and Toint, P. L. (1992) “LANCELOT: a Fortran package for large-scale
```
```
nonlinear optimization (Release A)”, En.Scientificcommons.Org.
```
```
Cook, W. et al. (2011) “An exact rational mixed-integer programming solver”, in Lecture Notes in
```
```
Computer Science (including subseries Lecture Notes in Artificial Intelligence and Lecture Notes in
```
```
Bioinformatics). doi: 10.1007/978-3-642-20807-2_9.
```
```
Drud, A. S. (1994) “CONOPT – A large-scale GRG code”, ORSA Journal on Computing. doi:
```
10.1287/ijoc.6.2.207.
```
Ferris, M. C. et al. (2009) “An extended mathematical programming framework”, Computers and
```
```
Chemical Engineering, 33(12), 1973–1982.
```
```
FICO (2020) “FICO®Xpress Optimization Suite”. FICO San Jose, CA, USA.
```
```
Forrest, J. and Lougee-Heimer, R. (2005) “CBC user guide”, in Emerging Theory, Methods, and
```
Applications. doi: 10.1287/educ.1053.0020.
```
Gamrath, G. et al. (2020) The SCIP Optimization Suite 7.0.
```
```
Gill, P. E., Murray, W. and Saunders, M. A. (2005) “SNOPT: An SQP algorithm for large-scale
```
constrained optimization”, SIAM. doi: 10.1137/S1052623499350013.
```
Grossmann, I. E. et al. (2002) “GAMS/DICOPT: A Discrete Continuous Optimization Package”.
```
```
Gurobi Optimization, L. L. C. (2020) “Gurobi Optimizer Reference Manual”.
```
168 Appendix A
```
Hart, W. E. et al. (2017) Pyomo – Optimization Modeling in Python. Cham: Springer International
```
```
Publishing (Springer Optimization and Its Applications). doi: 10.1007/978-3-319-58821-6.
```
```
IBM (2020) CPLEX Optimizer, IBM.
```
```
Kronqvist, J., Lundell, A. and Westerlund, T. (2016) “The extended supporting hyperplane algorithm
```
```
for convex mixed-integer nonlinear programming”, Journal of Global Optimization, 64(2), 249–272.
```
```
doi: 10.1007/s10898-015-0322-3.
```
```
Kronqvist, J. et al. (2019) “A review and comparison of solvers for convex MINLP”, Optimization and
```
Engineering. Springer, pp. 1–59. doi: 10.1007/s11081-018-9411-8.
```
Lin, Y. and Schrage, L. (2009) “The global solver in the LINDO API”, Optimization Methods and
```
Software. doi: 10.1080/10556780902753221.
```
Misener, R. and Floudas, C. A. (2014) “ANTIGONE: Algorithms for coNTinuous / Integer Global
```
```
Optimization of Nonlinear Equations”, Journal of Global Optimization, 59(2–3), 503–526. doi:
```
10.1007/s10898-014-0166-2.
```
Mittelmann, H. D. (2020) “Benchmarking optimization software – a (Hi)Story”, SN Operations
```
```
Research Forum, 1(1), 2. doi: 10.1007/s43069-020-0002-0.
```
```
Nowak, I., Alperin, H. and Vigerske, S. (2003) “LaGO – An object oriented library for solving
```
```
MINLPs”, in Bliek C., Jermann C. and Neumaier A. (eds.) Global Optimization and Constraint
```
Satisfaction. COCOS 2002. Lecture Notes in Computer Science, vol. 2861. Berlin, Heidelberg:
Springer. doi: 10.1007/978-3-540-39901-8_3.
```
Oki, E. (2012) “GLPK (GNU Linear Programming Kit)”, in Linear Programming and Algorithms for
```
Communication Networks. doi: 10.1201/b12733-4.
```
Pintér, J. D. (2007) “Nonlinear optimization with GAMS /LGO”, Journal of Global Optimization. doi:
```
10.1007/s10898-006-9084-2.
```
Tawarmalani, M. and Sahinidis, N. V. (2002) Convexification and Global Optimization in Continuous
```
and Mixed-Integer Nonlinear Programming. Springer. doi: 10.1007/978-1-4757-3532-1.
```
Vanderbei, R. J. (1999) “LOQO: An interior point code for quadratic programming”, Optimization
```
```
Methods and Software, 11(1–4), 451–484. doi: 10.1080/10556789908805759.
```
```
Vecchietti, A. and Grossmann, I. E. (1999) “LOGMIP: A disjunctive 0-1 non-linear optimizer for
```
process system models”, Computers and Chemical Engineering, 23, 555–565. doi: 10.1016/S0098-
```
1354(98)00293-2.
```
```
Viswanathan, J. and Grossmann, I. E. (1990) “A combined penalty function and outer approximation
```
method for MINLP optimization”, Computers and Chemical Engineering, 14, 769. doi.org/10.1016/
```
0098-1354(90)87085-4.
```
```
Wächter, A. and Biegler, L. T. (2006) “On the implementation of an interior-point filter line-search
```
algorithm for large-scale nonlinear programming”, Mathematical Programming, 106, 25–57. doi:
10.1007/s10107-004-0559-y.
```
Westerlund, T. and Pettersson, F. (1995) “An extended cutting plane method for solving convex
```
```
MINLP problems”, Computers and Chemical Engineering, 19 (Suppl. 1), 131–136. doi: 10.1016/
```
```
0098-1354(95)87027-X.
```
A.2.4 Libraries Test Problems
Mittleman Collection of NLP Problems
```
http://plato.asu.edu/ftp/ampl-nlp.html
```
Modeling Systems and Optimization Software 169
CUTE Test Problems
www.cuter.rl.ac.uk/problems.html
www.cuter.rl.ac.uk/Problems/mastsif.shtml
```
MINLPLib: A Library of Mixed-Integer and Continuous Nonlinear
```
Programming Instances
www.minlplib.org/
```
MINLP (instances minlp.org)
```
www.minlp.org/library/instances.php
CMU-IBM Open Source MINLP Project
```
http://egon.cheme.cmu.edu/ibm/page.htm
```
```
SIPLIB: A Stochastic Integer Programming Test Problem Library
```
www2.isye.gatech.edu/~sahmed/siplib/
170 Appendix A
APPENDIX B
Optimization Models for Process
Systems Engineering
B.1 Web-Based Software for Mixed-Integer Programming Applications
in Process Systems Engineering
```
http://newton.cheme.cmu.edu/interfaces/
```
This weblink, developed at Carnegie Mellon, provides interfaces to problems in the areas of
process synthesis, and planning and scheduling of process systems, through novel mathemat-
ical programming approaches, which rely on linear and nonlinear models with discrete and
```
continuous variables. These include mixed-integer programming (MILP and MINLP), gen-
```
```
eral disjunctive programming (GDP), and global-optimization multiperiod optimization.
```
Both deterministic models as well as models with uncertainty are considered in the list below.
BatchMPC
```
Design of multiproduct batch plants with mixed-product campaigns. (MILP)
```
```
Voudouris, V. and Grossmann, I. E. (1992) “Mixed-integer linear programming models for the
```
optimal design of batch processes”, Industrial & Engineering Chemistry Research, 31, 1315–1325.
BatchSPC
```
Design of multiproduct batch plants with single-product campaigns. (MILP, MINLP)
```
```
Kocis, G. R. and Grossmann, I. E. (1988) “Global optimization of nonconvex MINLP problems in
```
process synthesis”, Industrial & Engineering Chemistry Research, 27, 1407.
```
Voudouris, V. and Grossmann, I. E. (1993) “Optimal synthesis of multiproduct batch plants with
```
cyclic scheduling and inventory considerations”, Industrial & Engineering Chemistry Research, 32,
1962–1980.
CENTRALIZED/DECENTRALIZED
Generalized disjunctive program model for the optimal location of centralized and decen-
```
tralized manufacture facilities. (GDP, MINLP)
```
171
```
Lara, C. L. and Grossmann, I. E. (2016) “Global optimization for a continuous location-allocation
```
model for centralized and distributed manufacturing”, Computer Aided Chemical Engineering, 38,
1009–1014.
```
Lara, C. L., Trespalacios, F. and Grossmann, I. E. (2018) “Global optimization algorithm for capacitated
```
multi-facility continuous location-allocation problems”, Journal of Global Optimization, 71, 871–889.
CHP
Combined heat and power: optimization of heat and power plants under time-sensitive
```
electricity prices. (MILP)
```
```
Mitra, S., Sun, L. and Grossmann, I. E. (2013) “Optimal scheduling of industrial combined heat and
```
power plants under time-sensitive electricity prices”, Energy, 54, 194–211.
CRUDEOIL
Inventory management of a refinery that imports several types of crude oil delivered by
different vessels.
```
CRUDEOIL DISCRETE: (MILP)
```
```
Lee, H., Pinto, J. M., Grossmann, I. E. and Park, S. (1996) “MILP model for refinery short term
```
scheduling of crude oil unloading with inventory management”, Industrial & Engineering Chemistry
Research, 35, 1630–1641.
```
CRUDEOIL CONTINUOUS: (MINLP)
```
```
Mouret, S., Grossmann, I. E. and Pestiaux, P. (2009) “A novel priority-slot based continuous-time
```
formulation for crude-oil scheduling problems”, Industrial & Engineering Chemistry Research, 48
```
(18), 8515–8528.
```
CYCLE
```
Zero-wait scheduling of multi-product batch plants. (LP, MINLP)
```
```
Birewar, D. and Grossmann, I. E. (1989) “Efficient optimization algorithms for zero-wait scheduling
```
of multiproduct bath plants”, Industrial & Engineering Chemistry Research, 28, 1333.
DECAY
Scheduling multiple feeds on parallel units, where the performance of each unit decreases
```
with time. (MINLP)
```
```
Jain, V. and Grossmann, I. E. (1998) “Cyclic scheduling and maintenance of parallel process units
```
with decaying performance”, AIChE Journal, 44, 1623–1636.
172 Appendix B
DISIM
```
Distribution center design with stochastic inventory management. (MINLP)
```
```
You, F. and Grossmann, I. E. (2008) “Mixed-integer nonlinear programming models and algorithms
```
for large-scale supply chain design with stochastic inventory management”, Industrial & Engineering
Chemistry Research, 47, 7802–7817.
EXTRACTOR
Optimal design of multicomponent liquid–liquid extraction processes using multistage
```
countercurrent extractor systems. (GDP)
```
```
Reyes-Labarta, J. A. and Grossmann, I. E. (2001) “Disjunctive programming models for the optimal
```
design of complex liquid–liquid multistage extractors”, AIChE Journal, 47, 2243–2252.
FLEXNET
```
Flexibility index evaluation for heat-exchanger networks. (MILP, MINLP)
```
```
Escobar, M. and Grossmann, I. E. (2011) “SynFlex: A computational framework for synthesis of
```
flexible heat exchanger networks”, Computer Aided Chemical Engineering, 29, 1924–1928.
GDP-DISTILL
```
Synthesizing a single distillation column. (GDP)
```
```
Barttfeld, M., Aguirre, P. A. and Grossmann, I. E. (2003) “Alternative representations and formulations
```
for the economic optimization of multicomponent distillation columns”, Computers and Chemical
Engineering, 27, 363–383.
GREENPLAN
```
Bicriterion optimization of industrial chemical complexes. (MILP)
```
```
Grossmann, I. E., Drabbant, R. and Jain, R. K. (1982) “Incorporating toxicology in the synthesis of
```
```
industrial chemical complexes”, Chemical Engineering Communications, 17(1–6), 151–170.
```
LOGMIP
```
Logic mixed-integer programming solver. (GDP)
```
MINLP Cyberinfrastructure
```
Collaborative site with library of MINLP problems and their formulation. (MINLP,
```
```
MILP)
```
Optimization Models for Process Systems Engineering 173
MULTIPERIOD BLEND
```
Decomposition method for multiperiod blending problem. (MINLP)
```
```
Trespalacios, F. and Grossmann, I. E. (2016) “An MILP-MINLP decomposition method for the
```
global optimization of a source based model of the multiperiod blending problem”, Computers and
Chemical Engineering, 87, 13–35.
MULTISTAGE
```
Optimization of cyclic schedules of multiproduct continuous plants. (MINLP)
```
```
Pinto, J. M. and Grossmann, I. E. (1994) “Optimal scheduling of multistage multiproduct continuous
```
plants”, Computers and Chemical Engineering, 9, 797–816.
NETCHAIN
```
Optimization of the supply chain in continuous flexible process networks. (MILP)
```
```
Bok, J. K., Grossmann, I. E. and Park, S. (2000) “Supply chain optimization in continuous flexible
```
```
process networks”, Industrial & Engineering Chemistry Research, 39(5), 1279–1290.
```
OILGASPLAN
```
Planning of offshore oilfield development. (MINLP)
```
```
Gupta, V. and Grossmann, I. E. (2012) “An efficient multiperiod MINLP model for optimal planning
```
```
of offshore oil and gas infrastructure”, Industrial & Engineering Chemistry Research, 51(19),
```
6823–6840.
PowerSCHEDULE
Simultaneous optimization of production scheduling and electricity procurement for con-
```
tinuous power-intensive processes. (MILP)
```
```
Zhang, Q., Cremer, J. L., Grossmann, I. E., Sundaramoorthy, A. and Pinto, J. M. (2016) “Risk-based
```
integrated production scheduling and electricity procurement for continuous power-intensive
processes”, Computers and Chemical Engineering, 86, 90–105.
PRODEV
```
Scheduling of testing tasks in the new product development. (MILP)
```
```
Maravelias, C. T. and Grossmann, I. E. (2001) “Simultaneous planning for new product development
```
and batch manufacturing facilities”, Industrial & Engineering Chemistry Research, 40, 6147–6164.
```
Schmidt, C. W. and Grossmann, I. E. (1996) “Optimization models for the scheduling of testing tasks
```
in new product development”, Industrial & Engineering Chemistry Research, 35, 3498–3510.
174 Appendix B
REL OPT
```
Optimal Design of Reliable Chemical Plants (MINLP)
```
```
Ye, Y., I. E. Grossmann and J. M. Pinto (2018) “Mixed-integer nonlinear programming models for
```
optimal design of reliable chemical plants”, Computers and Chemical Engineering, 116, 3–16.
Resilient Supply Chain
```
Supply chain with risk of facility disruptions. (MILP)
```
```
Garcia-Herreros, P., Wassick, J. M. and Grossmann, I. E. (2014) “Design of resilient supply chains
```
with risk of facility disruptions”, Industrial & Engineering Chemistry Research, 54, 17240–17251.
SIMPLAN
```
Simultaneous planning and scheduling of a single-stage multiproduct. (MILP)
```
```
Erdirik-Dogan, M. and Grossmann, I. E. (2008) “Simultaneous planning and scheduling of single-
```
stage multi-product continuous plants with parallel lines”, Computers and Chemical Engineering, 32
```
(11), 2664–2683.
```
SIMPRONET
```
Stochastic inventory management for process networks. (MINLP)
```
```
You, F. and Grossmann, I. E. (2011) “Stochastic inventory management for tactical process planning
```
under uncertainties: MINLP models and algorithms”, AIChE Journal, 57, 1250–1277.
STEAM
```
Optimal synthesis and operation of utility plants. (MINLP)
```
```
Bruno, J. C. and Grossmann, I. E. (1998) “A rigorous MINLP model for the optimal synthesis and
```
```
operation of utility plants”, Chemical Research and Design, 76(3), 246–258.
```
STN
```
State Task Network, continuous and discrete models. (MILP)
```
For discrete-time model
```
Kondili, E., Pantelides, C. C. and Sargent, R. W. H. (1993) “A general algorithm for short-term scheduling
```
of batch operations – I. MILP formulation”, Computers and Chemical Engineering, 2, 211–227.
```
Shah, N., Pantelides, C. C. and Sargent, R. W. H. (1993) “A general algorithm for short-term
```
scheduling of batch operations – II. Computational issues”, Computers and Chemical Engineering, 2,
229–244.
Optimization Models for Process Systems Engineering 175
For continuous-time model
```
Maravelias, C. T. and Grossmann, I. E. (2003) “New continuous-time state task network formulation
```
for the scheduling of multipurpose batch plant”, Industrial & Engineering Chemistry Research, 42
```
(13), 3056–3074.
```
SYNHEAT
```
Program for optimizing heat-exchanger networks. (MINLP)
```
```
Ponce-Ortega, J. M., Jimenez-Gutierrez, A. and Grossmann, I. E. (2007) “Optimal synthesis of heat
```
exchanger networks involving isothermal process streams”, Computers and Chemical Engineering,
```
32(8), 1918–1942.
```
```
Yee, T. F. and Grossmann, I. E. (1990) “Simultaneous optimization model for heat integration – II.
```
```
Heat exchanger network synthesis”, Computers and Chemical Engineering, 14 (10), 1165–1184.
```
THERMAL-DIST
Optimal separation sequences based on thermally coupled distillation.
```
Caballero, J. and Grossmann, I. E. (2004) “Design of distillation sequences: from conventional to fully
```
```
thermally coupled distillation systems”, Computers and Chemical Engineering, 28(11), 2307–2329.
```
WATER
```
Design of integrated and distributed wastewater networks. (Global NLP)
```
WATERNET
```
Karuppiah, R. and Grossmann, I. E. (2006) “Global optimization for the synthesis of integrated water
```
```
systems in chemical processes”, Computers and Chemical Engineering, 30(4), 650–673.
```
WATERTREAT
```
Galan, B. and Grossmann, I. E. (1998) “Optimal design of distributed wastewater treatment networks”,
```
```
Industrial & Engineering Chemistry Research, 37(10), 4036–4048.
```
B.2 CMU-IBM Cyber-Infrastructure for MINLP Collaborative Site
www.minlp.org/
This collaborative site, developed at Carnegie Mellon, contains optimization models in
different areas contributed by researchers in the optimization field. The site contains linear
and nonlinear models with one or several alternative model formulations involving discrete
```
and continuous variables through mixed-integer nonlinear programming (MINLP), mixed-
```
```
integer linear programming (MILP), or generalized disjunctive programming (GDP).
```
176 Appendix B
MINLP Library
Problem Title Primary Author Model Types
1 AC Network-Constrained Unit Commitment Anjos, Miguel MINLP
2 Global Optimization Algorithm for Capacitated
Multi-facility Continuous Location-Allocation
Problems
Lara, Cristiana MINLP
3 Mixed-integer nonlinear programming models for
optimal design of reliable chemical plants
Ye, Yixin MINLP
4 Crude Oil Pooling Problem Castro, Pedro MINLP, MILP
5 Industrial gas network operation Puranik, Yash MINLP
6 Optimal Procurement Contract Selection with
Price Optimization under Uncertainty for
Process Networks
Calfa, Bruno MINLP
7 Large-Scale MILP Transshipment Models for
Heat Exchanger Network Synthesis
Chen, Yang MILP
8 Mixed-Integer Linear Fractional Programming You, Fengqi MINLP, LP, MILP
9 Hydro Energy System Scheduling Castro, Pedro MILP, MIQCP
10 Chance-constrained problems with quadratic
constraints
Margot, Francois MINLP
11 Sustainable Integration of Trigeneration Systems
with Heat Exchanger Networks
Ponce-Ortega, Jose
Maria
MINLP
12 Cyclic Scheduling with Heat Sharing Castro, Pedro MILP
13 Multiperiod Blend Scheduling Problem Trespalacios,
Francisco
MILP, MIQCP
14 On the solution of 0-1 Quadratic Programming
Problems with cardinality constraints
Lima, Ricardo MINLP, MILP,
MIQP
15 The optimal design of a three-echelon supply
chain with inventories under uncertainty
Nyberg, Axel MINLP, MILP
16 A Novel Bi-Level Optimization Method for the
Identification of Critical Points in Flow Sheet
Synthesis under Uncertainty
Novak Pintaric, Zorka NLP
17 Continuous-time Representations in Scheduling Castro, Pedro MILP
18 Optimal Design of Water Distribution Networks D’Ambrosio, Claudia MINLP, MILP
19 MINLP and MPCC formulations for the
cascading tanks problem
Gopalakrishnan, Ajit MINLP, NLP
20 Optimal solvent design for reactions using
computer-aided molecular design
Struebing, Heiko MILP
Optimization Models for Process Systems Engineering 177
```
(cont.)
```
Problem Title Primary Author Model Types
21 The kissing number problem Belotti, Pietro QP
22 2-D Orthogonal Strip Packing Castro, Pedro MILP
23 Mixed-Integer Linear Programming Models for
Scheduling in Process Networks
Sundaramoorthy, Arul MILP
```
24 MINLP approach for the TSPN (Traveling
```
```
Salesman Problem with Neighborhoods)
```
Gentilini, Iacopo MINLP
25 Generalized Pooling Problem Misener, Ruth MIQCP
26 Crude-oil Operations Scheduling Mouret, Sylvain MINLP
27 Inventory-Production-Distribution Problems with
Direct Shipments
Margot, Francois MILP
28 Optimal Scheduling of Multistage Batch Plants Castro, Pedro MILP
29 Integrated Process Water Networks Design
Problem
Ahmetović, Elvis MINLP
30 Cutting Stock Optimization Problem for the
Production of Carton Board Boxes
Vecchietti, Aldo MINLP, MILP
31 Mixed-Integer Nonlinear Programming Models
for Optimal Simultaneous Synthesis of Heat
Exchangers Network
Escobar, Marcelo MINLP
32 Optimal Scheduling of Refined Products Pipelines
and Terminal Operations
Cafaro, Diego MILP
33 MPEC strategies for optimization of pipeline
operations
Gopalakrishnan, Ajit NLP
34 Extended Pooling Problem with the Summer
Time Complex Emissions Constraints
Misener, Ruth MINLP
35 Optimization of metabolic networks in
biotechnology
Guillen, Gonzalo MINLP
36 Close-Enough Vehicle Routing Problem Mennell, William MINLP
37 Simultaneous Cyclic Scheduling and Control of a
Multiproduct CSTR
Flores-Tlacuahuac,
Antonio
MINLP
38 Optimal Separation Sequences Based on
```
Distillation: From Conventional to Fully
```
Thermally Coupled Systems
Caballero, Jose MINLP
39 The Close-Enough Traveling Salesman Problem Mennell, William MINLP
40 The Delay Constrained Routing Problem
```
(DCRP)
```
Hijazi, Hassan MINLP
41 A Deterministic Security Constrained Unit
Commitment Model
Zondervan, Edwin MINLP, MIQP
178 Appendix B
GDP Library
```
(cont.)
```
Problem Title Primary Author Model Types
42 Stochastic Portfolio Optimization with Round
Lot Trading Constraints
Lejeune, Miguel MINLP
43 Stabilizing controller design and the Belgian
chocolate problem
Chang, YoungJung MINLP
44 Design of Telecommunication Networks with
Shared Protection
Belotti, Pietro MINLP, MILP
45 Mixed-Integer Nonlinear Programming Models
for the Optimal Design of Multi-product Batch
Plant
You, Fengqi MINLP
46 Solving Mixed-Integer Linear Fractional
Programming Problems with Dinkelbach’s
Algorithm and MINLP Methods
You, Fengqi MINLP
47 Global multi-objective optimization of a
nonconvex MINLP problem and its application
on polygeneration energy systems design
Liu, Pei MINLP
48 Periodic Scheduling of Continuous Multiproduct
Plants
Castro, Pedro MINLP
49 Optimization model for density modification
based on single-crystal X-ray diffraction data
Sahinidis, Nick MINLP, MILP
50 Mixed-Integer Nonlinear Programming Models
and Algorithms for Supply Chain Design with
Stochastic Inventory Management
You, Fengqi MINLP
51 MINLP & MPCC Strategies for Optimization of
a Class of Hybrid Dynamic Systems
Baumrucker, Brian MINLP, NLP,
MIQP
52 Water Treatment Network Design Ruiz, Juan MINLP
Problem Title Primary Author Model type
1 Separation of fiber and stickies Trespalacios, Francisco Nonlinear
2 Design of multi-product batch plant Trespalacios, Francisco Nonlinear
3 Medium-Term Purchasing Contracts Vecchietti, Aldo Linear
4 Process Synthesis Problem Ruiz, Juan Nonlinear
5 Jobshop Scheduling Vecchietti, Aldo Linear
6 Strip Packing Vecchietti, Aldo Linear
7 2-D Constrained Layout Ruiz, Juan Nonlinear
Optimization Models for Process Systems Engineering 179
References
Adjiman, C. S., Dallwig, S., Floudas, C. A. and
```
Neumaier, A. (1998) “A global optimization
```
method, αBB, for general twice-differentiable
constrained NLPs – I. Theoretical advances”,
```
Computers & Chemical Engineering, 22(9),
```
```
1137–1158. doi: 10.1016/S0098-1354(98)
```
00027-1.
Alonso-Ayuso, A., Escudero, L. F, Garín, A.,
```
Ortuño, M. T. and Pérez, G. (2003) “An
```
approach for strategic supply chain planning
under uncertainty based on stochastic 0-1
programming”, Journal of Global
Optimization, 26, 97–124. doi.org/10.1023/
```
A:1023071216923
```
```
Applegate, D. and Cook, W. (1991) “A computa-
```
tional study of the job-shop scheduling problem”,
```
ORSA Journal on Computing, 3(2), 149–156. doi:
```
10.1287/ijoc.3.2.149.
```
Audet, C., Savard, G. and Zghal, W. (2008)
```
“Multiobjective optimization through a series
of single-objective formulations”, SIAM
```
Journal on Optimization, 19(1), 188–210. doi:
```
10.1137/060677513.
```
Balas, E. (1979) “Disjunctive programming”,
```
Annals of Discrete Mathematics, 5, 3–51. doi:
```
10.1016/S0167-5060(08)70342-X.
```
```
Balas, E. (1985) “Disjunctive programming and a
```
hierarchy of relaxations for discrete optimiza-
tion problems”, SIAM Journal on Algebraic
```
Discrete Methods, 6(3), 466–486. doi: 10.1137/
```
0606047.
```
Balas, E. (2010) “Disjunctive programming”, in
```
50 Years of Integer Programming 1958–2008.
Berlin, Heidelberg: Springer, pp. 283–340. doi:
10.1007/978-3-540-68279-0_10.
```
Balas, E. (2018) Disjunctive Programming.
```
Springer Nature Switzerland.
```
Balas, E., Ceria, S. and Cornuéjols, G. (1993) “A lift-
```
and-project cutting plane algorithm for mixed 0–1
```
programs”, Mathematical Programming, 58(1–3),
```
295–324. doi: 10.1007/BF01581273.
Bazaraa, M. S., Sherali, H. D. and Shetty, C. M.
```
(2006) Nonlinear Programming: Theory and
```
Algorithms. Hoboken, NJ: John Wiley &
Sons, Inc. doi: 10.1002/0471787779.
```
Beale, E. M. L. (1979) “Branch and bound
```
methods for mathematical programming
systems”, Annals of Discrete Mathematics, 5,
```
201–219. doi: 10.1016/S0167-5060(08)70351-0.
```
```
Beale, E. M. L. and Forrest, J. J. H. (1976)
```
“Global optimization using special ordered
```
sets”, Mathematical Programming, 10(1),
```
52–69. doi: 10.1007/BF01580653.
```
Ben-Tal, A. and Nemirovski, A. (1999) “Robust
```
solutions of uncertain linear programs”,
```
Operations Research Letters, 25(1), 1–13. doi:
```
```
10.1016/S0167-6377(99)00016-4.
```
Ben-Tal, A., Goryashko, A., Guslitzer, E. and
```
Nemirovski, A. (2004) “Adjustable robust
```
solutions of uncertain linear programs”,
```
Mathematical Programming, 99(2), 351–376.
```
```
doi: 10.1007/s10107-003-0454-y.
```
```
Benders, J. F. (1962) “Partitioning procedures for
```
solving mixed-variables programming prob-
```
lems”, Numerische Mathematik, 4(1),
```
238–252. doi: 10.1007/BF01386316.
```
Bertsekas, D. (1998) Network Optimization:
```
Continuous and Discrete Models. Belmont,
```
Massachusetts: Athena Scientific.
```
Bertsimas, D., Brown, D. B. and Caramanis, C.
```
(2011) “Theory and applications of robust
```
```
optimization”, SIAM Review, 53(3), 464–501.
```
```
doi: 10.1137/080734510.
```
```
Biegler, L. T. (2010) Nonlinear Programming.
```
Society for Industrial and Applied
Mathematics. doi: 10.1137/1.9780898719383. x
```
Biegler, L. T. and Grossmann, I. E. (2004)
```
“Retrospective on optimization”, Computers
180
```
& Chemical Engineering, 28(8), 1169–1192.
```
```
doi: 10.1016/j.compchemeng.2003.11.003.
```
Biegler, L. T., Grossmann, I. E. and Westerberg,
A. W. (1997) Systematic Methods of Chemical
Process Design, New Jersey.
```
Birge, J. R. and Louveaux, F. (2011) Introduction
```
```
to Stochastic Programming (Springer Series in
```
Operations Research and Financial
```
Engineering). New York: Springer. doi:
```
10.1007/978-1-4614-0237-4.
```
Bixby, R. and Rothberg, E. (2007) “Progress in
```
computational mixed integer programming –
A look back from the other side of the tipping
```
point”, Annals of Operations Research, 149(1),
```
37–41. doi: 10.1007/s10479-006-0091-y.
```
Bonami, P., Kilinç, M. and Linderoth, J. (2012)
```
```
Mixed Integer Nonlinear Programming (The
```
IMA Volumes in Mathematics and its
```
Applications), Lee, J. and Leyffer, S. (eds.),
```
New York: Springer. doi: 10.1007/978-1-4614-
1927-3.
```
Bottou, L., Curtis, F. E. and Nocedal, J. (2018)
```
“Optimization methods for large-scale
```
machine learning”, SIAM Review, 60(2),
```
223–311. doi.org/10.1137/16M1080173.
```
Broyden, C. G. (1965) “A class of methods for
```
solving nonlinear simultaneous equations”,
```
Mathematics of Computation, 19(92), 577. doi:
```
10.2307/2003941.
```
Byrd, R. H., Nocedal, J. and Waltz, R. A. (2006)
```
“KNITRO: An integrated package for non-
linear optimization”, in Di Pillo, G. and
```
Roma, M. (eds.) Large-Scale Nonlinear
```
Optimization. Nonconvex Optimization and Its
Applications, vol. 83. Boston, MA: Springer.
```
Carøe, C. C. and Schultz, R. (1999) “Dual
```
decomposition in stochastic integer program-
```
ming”, Operations Research Letters, 24(1–2),
```
```
37–45. doi: 10.1016/S0167-6377(98)00050-9.
```
```
Castro, P. M. and Grossmann, I. E. (2012)
```
“Generalized disjunctive programming as a
systematic modeling framework to derive
scheduling formulations”, Industrial &
Engineering Chemistry Research, 51,
57815792. doi: 10.1021/ie2030486.
```
Ceria, S. and Soares, J. (1999) “Convex program-
```
ming for disjunctive convex optimization”,
```
Mathematical Programming, 86(3), 595–614.
```
```
doi: 10.1007/s101070050106.
```
```
Clocksin, W. F. and Mellish, C. S. (1994)
```
Programming in Prolog. Berlin, Heidelberg:
Springer-Verlag. doi: 10.1007/978-3-642-
97596-7.
Conforti, M., Cornuéjols, G. and Zambelli, G.
```
(2014) “Integer programming models”, in
```
Integer Programming. Springer, pp. 45–84.
```
Cook, W. J. (2012) In Pursuit of the Traveling
```
```
Salesman: Mathematics at the Limits of
```
Computation. Princeton University Press.
Cornuéjols, G., Nemhauser, G. A. and Wolsey,
L. A. (1990) “The uncapacitated facility loca-
tion problem”, in Mirchandani, P. B. and
```
Francis, R. L. (eds.) Discrete Location
```
Theory, New York: Wiley.
Crowder, H., Johnson, E. L. and Padberg, M.
```
(1983) “Solving large-scale zero-one linear pro-
```
gramming problems”, Operations Research, 31
```
(5), 803–834. doi: 10.1287/opre.31.5.803.
```
```
Dakin, R. J. (1965) “A tree-search algorithm
```
for mixed integer programming problems”,
```
The Computer Journal, 8(3), 250–255. doi:
```
10.1093/comjnl/8.3.250.
```
Dantzig, G. (1963) Linear Programming and
```
Extensions. RAND Corporation. doi: 10.7249/
R366.
```
Dantzig, G. B. (1949) “Programming in a linear
```
structure”, Econometrica, 17, 73–74.
```
Drud, A. S. (1994) “CONOPT – A large-scale
```
GRG code”, ORSA Journal on Computing, 6
```
(2), 207–216. doi: 10.1287/ijoc.6.2.207.
```
Duffin, R. J., Peterson, E. L. and Zener, C.
```
(1967) Geometric Programming – Theory and
```
Applications. New York: John Wiley and Sons.
```
Duran, M. A. and Grossmann, I. E. (1986)
```
“An outer-approximation algorithm for a
class of mixed-integer nonlinear programs”,
```
Mathematical Programming, 36(3), 307–339.
```
```
doi: 10.1007/BF02592064.
```
```
Eiben, A. E. and Smith, J. E. (2003) Introduction
```
to Evolutionary Computing, Springer.
```
Fiacco, A. V. and McCormick, G. P. (1968)
```
Nonlinear Programming: Sequential
Unconstrained Minimization Techniques.
New York: John Wiley and Sons.
References 181
```
Fisher, M. L. (1981) “The Lagrangian relaxation
```
method for solving integer programming prob-
```
lems”, Management Science, 27(1), 1–18. doi:
```
10.1287/mnsc.27.1.1.
```
Floudas, C. A. (1995) Nonlinear and Mixed-
```
Integer Optimization: Fundamentals and
Applications. Oxford University Press.
```
Floudas, C. A. and Gounaris, C. E. (2009)
```
“A review of recent advances in global opti-
mization”, Journal of Global Optimization, 45
```
(1), 3–38. doi: 10.1007/s10898-008-9332-8.
```
```
Frangioni, A. (2005) “About Lagrangian
```
methods in integer optimization”, Annals of
```
Operations Research, 139(1), 163–193. doi:
```
10.1007/s10479-005-3447-9.
Furman, K. C., Sawaya, N. W. and Grossmann, I.
E. (2020) “A computationally useful algebraic
representation of nonlinear disjunctive convex
sets using the perspective function”,
Computational Optimization and Applications, 76
```
(2), 589–614. doi: 10.1007/s10589-020-00176-0.
```
```
Geoffrion, A. M. (1972) “Generalized Benders
```
decomposition”, Journal of Optimization
```
Theory and Applications, 10(4), 237–260. doi:
```
10.1007/BF00934810.
```
Geoffrion, A. M. (1974) “Lagrangean relaxation
```
for integer programming”, in Balinski, M. L.
```
(ed.) Approaches to Integer Programming.
```
Mathematical Programming Studies, vol. 2.
Berlin, Heidelberg: Springer, pp. 82–114. doi:
10.1007/BFb0120690.
```
El Ghaoui, L. (1997) “Robust optimization”,
```
```
IFAC Proceedings Volumes, 30(16), 115–117.
```
```
doi: 10.1016/S1474-6670(17)42591-2.
```
```
Gomory, R. E. (1958) “Outline of an algorithm for
```
integer solutions to linear programs”, Bulletin of
```
the American Mathematical Society, 64(5),
```
275–279. doi: 10.1090/S0002-9904-1958-10224-4.
```
Gordan, P. (1873) “Ueber die Auflösung linearer
```
Gleichungen mit reellen Coefficienten”,
```
Mathematische Annalen, 6(1), 23–28. doi:
```
10.1007/BF01442864.
```
Goyal, V. and Ierapetritou, M. G. (2002)
```
“Determination of operability limits using sim-
plicial approximation”, AIChE Journal, 48
```
(12), 2902–2909. doi: 10.1002/aic.690481217.
```
```
Griewank, A. (2000) Evaluating Derivatives:
```
Principles and Techniques of Algorithmic
Differentiation. Philadelphia: SIAM.
```
Griewank, A. and Walther, A. (2008) Evaluating
```
Derivatives. Society for Industrial and
Applied Mathematics. doi: 10.1137/
1.9780898717761.
```
Grossmann, I. E. (2002) “Review of nonlinear
```
mixed-integer and disjunctive programming
techniques”, Optimization and Engineering, 3
```
(3), 227–252. doi: 10.1023/A:1021039126272.
```
```
Grossmann, I. E. and Biegler, L. T. (2004) “Part II.
```
Future perspective on optimization”, Computers
```
& Chemical Engineering, 28(8), 1193–1218. doi:
```
10.1016/j.compchemeng.2003.11.006.
Grossmann, I. E., Calfa, B. A. and Garcia-
```
Herreros, P. (2014) “Evolution of concepts
```
and models for quantifying resiliency and flexi-
bility of chemical processes”, Computers &
Chemical Engineering, 70, 22–34. doi:
10.1016/j.compchemeng.2013.12.013.
```
Grossmann, I. E. and Floudas, C. A. (1987)
```
“Active constraint strategy for flexibility analy-
sis in chemical processes”, Computers &
```
Chemical Engineering, 11(6), 675–693. doi:
```
```
10.1016/0098-1354(87)87011-4.
```
```
Grossmann, I. E. and Trespalacios, F. (2013)
```
“Systematic modeling of discrete-continuous
optimization models through generalized dis-
junctive programming”, AIChE Journal, 59,
3276–3295. doi: 10.1002/aic.14088.
```
Guignard, M. (2003) “Lagrangean relaxation”,
```
TOP, 11, 51–228. doi: 10.1007/BF02579036.
```
Guignard, M. and Kim, S. (1987) “Lagrangean
```
```
decomposition: A model yielding stronger
```
Lagrangean bounds”, Mathematical
```
Programming, 39(2), 215–228. doi: 10.1007/
```
BF02592954.
```
Gupta, O. K. and Ravindran, A. (1985)
```
“Branch and bound experiments in convex non-
linear integer programming”, Management
```
Science, 31(12), 1533–1546. doi: 10.1287/
```
mnsc.31.12.1533.
```
Haar, A. (1918) “Die Minkowskische Geometrie
```
and die Annäherung an stetige Funktionen”,
Mathematische Annalen, 78, 249–311.
182 References
```
Halemane, K. P. and Grossmann, I. E. (1983)
```
“Optimal process design under uncertainty”,
```
AIChE Journal, 29(3), 425–433. doi: 10.1002/
```
aic.690290312.
```
Han, S.-P. (1976) “Superlinearly convergent vari-
```
able metric algorithms for general nonlinear
programming problems”, Mathematical
```
Programming, 11(1), 263–282. doi: 10.1007/
```
BF01580395.
```
Van Hentenryck, P. (1989) Constraint
```
Satisfaction in Logic Programming. MIT Press.
```
Hettich, R. and Kortanek, K. O. (1993) “Semi-
```
infinite programming: Theory, methods, and
```
applications”, SIAM Review, 35(3), 380–429.
```
```
doi: 10.1137/1035089.
```
```
Hiriart-Urruty, J.-B. and Lemaréchal, C. (2001)
```
Fundamentals of Convex Analysis. Berlin,
```
Heidelberg: Springer.
```
```
Hooker, J. N. (2002) “Logic, optimization, and
```
constraint programming”, INFORMS Journal
```
on Computing, 14(4), 295–321. doi: 10.1287/
```
ijoc.14.4.295.2828.
```
Hooker, J. N. and van Hoeve, W.-J. (2018)
```
“Constraint programming and operations
research”, Constraints, 23, 172–195. doi:
10.1007/s10601-017-9280-3.
```
Horst, R. and Tuy, H. (1996) Global
```
```
Optimization: Deterministic Approaches,
```
Springer-Verlag.
```
John, F. (1948) “Extremum problems with
```
inequalities as side conditions”, in Friedrichs,
K. O., Neugebauer, E. and Stoker, J. J. (eds.)
Studies and Essays, Courant Anniversary
```
Volume. New York: Wiley (Interscience),
```
pp. 187–204.
```
Kantorovich, L. V. (1948) “On Newton’s method
```
for functional equations”, Doklady Akademii
```
Nauk (in Russian), 59, 1237–1240.
```
```
Karmarkar, N. (1984) “A new polynomial-time
```
algorithm for linear programming”,
```
Combinatorica, 4(4), 373–395. doi: 10.1007/
```
BF02579150.
```
Karush, W. (1939) Minima of functions of several
```
variables with inequalities as side constraints
```
(M.Sc. thesis). Department of Mathematics,
```
University of Chicago, Chicago, Illinois.
Kesavan, P., Allgor, R. J., Gatzke, E. P. and Barton,
P. I. (2004) “Outer approximation algorithms for
separable nonconvex mixed-integer nonlinear pro-
```
grams”, Mathematical Programming, 100(3),
```
517–535. doi: 10.1007/s10107-004-0503-1.
```
Kocis, G. R. and Grossmann, I. E. (1987)
```
“Relaxation strategy for the structural optimiza-
tion of process flowsheets”, Industrial &
Engineering Chemistry Research, 26, 1869–1880.
Kronqvist, J., Lundell, A. and Westerlund, T.
```
(2016) “The extended supporting hyperplane
```
algorithm for convex mixed-integer nonlinear
programming”, Journal of Global Optimization,
```
64 (2), 249–272. doi: 10.1007/s10898-015-0322-3.
```
Kronqvist, J., Bernal, D. E., Lundell, A. and
```
Grossmann, I. E. (2019) “A review and com-
```
parison of solvers for convex MINLP”,
```
Optimization and Engineering, 20(2), 397–455.
```
```
doi: 10.1007/s11081-018-9411-8.
```
```
Kuhn, H. W. and Tucker, A. W. (1951) “Nonlinear
```
programming”, in Proceedings of the Second
Berkeley Symposium on Mathematical Statistics
and Probability. Berkeley: University of
California Press, pp. 481–492.
```
Land, A. H. and Doig, A. G. (1960) “An auto-
```
matic method of solving discrete programming
```
problems”, Econometrica, 28(3), 497. doi:
```
10.2307/1910129.
```
Laporte, G. (1992) “The traveling salesman prob-
```
```
lem: An overview of exact and approximate
```
algorithms”, European Journal of Operational
```
Research, 59(2), 231–247. doi: 10.1016/0377-
```
```
2217(92)90138-Y.
```
Lasdon, L. S., Waren, A. D., Jain, A. and
```
Ratner, M. (1978) “Design and testing of a
```
generalized reduced gradient code for non-
linear programming”, ACM Transactions on
Mathematical Software, 4, 34–50. doi:
10.1145/355769.355773.
```
Lee, J. and Leyffer, S. (eds.) (2012) Mixed
```
```
Integer Nonlinear Programming (The IMA
```
```
Volumes in Mathematics and Its Applications).
```
New York: Springer. doi: 10.1007/ 978-1-4614-
1927-3.
```
Lee, S. and Grossmann, I. E. (2000) “New algo-
```
rithms for nonlinear generalized disjunctive
References 183
programming”, Computers & Chemical
```
Engineering, 24(9–10), 2125–2141. doi:
```
```
10.1016/S0098-1354(00)00581-0.
```
```
Lin, X., Janak, S. L. and Floudas, C. A. (2004)
```
“A new robust optimization approach for s
cheduling under uncertainty: I. Bounded
uncertainty”, Computers and Chemical
Engineering 28 1069–1085. doi:10.1016/j.
compchemeng.2003.09.020
```
Lovász, L. and Schrijver, A. (1991) “Cones of
```
matrices and set-functions and 0–1 optimiza-
```
tion”, SIAM Journal on Optimization, 1(2),
```
166–190. doi: 10.1137/0801013.
Marsten, R., Subramanian, R., Saltzman, M. J.
```
et al. (1990) “Interior point methods for linear
```
```
programming: Just call Newton, Lagrange,
```
and Fiacco and McCormick!”, Interfaces, 20
```
(4), 105–116.
```
```
McCormick, G. P. (1976) “Computability of global
```
solutions to factorable nonconvex programs:
Part I - Convex underestimating problems”,
```
Mathematical Programming, 10(1), 147–175.
```
```
Minoux, M. (1986) Mathematical Programming:
```
Theory and Algorithms. John Wiley & Sons.
```
Misener, R. and Floudas, C. A. (2013)
```
“GloMIQO: Global mixed-integer quadratic
optimizer”, Journal of Global Optimization, 57
```
(1), 3–50. doi: 10.1007/s10898-012-9874-7.
```
Morrison, D. R., Jacobson, S. H., Sauppe, J.J. and
```
Sewell, E. W. (2016) “Branch-and-bound algo-
```
```
rithms: A survey of recent advances in searching,
```
branching, and pruning”, Discrete Optimization,
19, 79–102. doi: 10.1016/j.disopt.2016.01.005.
```
Murtagh, B. A. and Saunders, M. A. (1978)
```
“Large-scale linearly constrained optimiza-
```
tion”, Mathematical Programming, 14(1),
```
41–72. doi: 10.1007/BF01588950.
```
Murtagh, B. A. and Saunders, M. A. (1982)
```
“A projected Lagrangian algorithm and its
implementation for sparse nonlinear con-
straints”, in Buckley, A. G. and Goffin, J.-L.
```
(eds.) Algorithms for Constrained Minimization
```
of Smooth Nonlinear Functions, Springer,
pp. 84–117. doi: 10.1007/BFb0120949.
```
Murtagh, B. A. and Saunders, M. A. (2003)
```
MINOS 5.5 User’s Guide, Stanford University
Systems Optimization Laboratory.
```
Nemhauser, G. and Wolsey, L. (1988) Integer and
```
Combinatorial Optimization. Hoboken, NJ: John
Wiley & Sons, Inc. doi: 10.1002/9781118627372.
```
Nocedal, J. (1980) “Updating quasi-Newton matri-
```
ces with limited storage”, Mathematics of
Computation, 35, 773–782. doi: 10.2307/2006193.
```
Nocedal, J. and Wright, S. (2006) Numerical
```
Optimization. Springer Science & Business Media.
```
Ortega, J. M. and Rheinbolt, W. C. (1970)
```
Iterative Solution of Non-linear Equations in
Several Variables. New York: Academic Press.
```
Pistikopoulos, E. N. and Grossmann, I. E. (1988)
```
“Optimal retrofit design for improving process
flexibility in linear systems”, Computers &
```
Chemical Engineering, 12(7), 719–731. doi:
```
```
10.1016/0098-1354(88)80010-3.
```
Pistikopoulos, E. N., Georgiadis, M. C. and Dua,
V. (2007) Multi-Parametric Programming:
Volume 1: Theory, Algorithms, and
Applications, Wiley VCH-Verlag & Co.
```
Powell, M. J. D. (1978) “A fast algorithm for non-
```
linearly constrained optimization calculations”,
```
in Watson, G. A. (ed.) Numerical Analysis,
```
Proceedings of the Biennial Conference Held at
Dundee, June 28–July 1, 1977, Springer Lecture
Notes in Mathematics, volume 630, pp. 144–157.
```
doi: 10.1007/BFb0067703.
```
```
Prékopa, A. (1970) “On probabilistic constrained
```
programming”, in Proceedings of the Princeton
Symposium on Mathematical Programming.
```
Princeton: Princeton University Press,
```
pp. 113–138. doi: 10.1515/9781400869930-009.
```
Quesada, I. and Grossmann, I. E. (1992) “An LP/
```
NLP based branch and bound algorithm for
convex MINLP optimization problems”,
```
Computers & Chemical Engineering, 16(10–11),
```
937–947.
```
Quesada, I. and Grossmann, I. E. (1995)
```
“A global optimization algorithm for linear
fractional and bilinear programs”, Journal of
Global Optimization, 6, 39–76. doi: 10.1007/
BF01106605.
```
Raman, R. and Grossmann, I. E. (1994)
```
“Modelling and computational techniques for
logic based integer programming”, Computers
```
& Chemical Engineering, 18(7), 563–578. doi:
```
```
10.1016/0098-1354(93)E0010-7.
```
184 References
```
Rios, L. M. and Sahinidis, N. V. (2013)
```
“Derivative-free optimization: a review of
algorithms and comparison of software imple-
mentations”, Journal of Global Optimization,
```
56(3), 1247–1293. doi: 10.1007/s10898-012-
```
9951-y.
```
Van Roy, T. J. and Wolsey, L. A. (1987) “Solving
```
mixed integer programming problems using
automatic reformulation”, Operations
```
Research, 35(1), 45–57. doi: 10.1287/
```
opre.35.1.45.
```
Ruszczyński, A. (1997) “Decomposition methods
```
in stochastic programming”, Mathematical
```
Programming, 79(1–3), 333–353. doi: 10.1007/
```
BF02614323.
```
Sahinidis, N. V. (2004) “Optimization under
```
```
uncertainty: state-of-the-art and opportun-
```
ities”, Computers & Chemical Engineering,
```
28(6–7), 971–983. doi: 10.1016/j.compchemeng.
```
2003.09.017.
```
Sahinidis, N. V. and Grossmann, I. E. (1991)
```
“Convergence properties of generalized
Benders decomposition”, Computers &
```
Chemical Engineering, 15(7), 481–491. doi:
```
```
10.1016/0098-1354(91)85027-R.
```
```
Saigal, R. (1995) Linear Programming: A Modern
```
Integrated Analysis. New York: Springer
Science + Business Media, LLC.
```
Sargent, R. W. H. (1975) Numerical Optimization
```
```
Techniques (thesis), Department of Chemical
```
Engineering, Imperial College London, UK.
```
Sargent, R. W. H. (2004) “Introduction: 25 years of
```
progress in process systems engineering”,
```
Computers & Chemical Engineering, 28(4), 437–
```
439. doi:10.1016/j.compchemeng.2003.09.032
```
Schultz, R. (2003) “Stochastic programming with
```
integer variables”, Mathematical Programming,
```
97(1), 285–309. doi: 10.1007/s10107-003-0445-z.
```
```
Sherali, H. D. and Adams, W. P. (1990)
```
“A hierarchy of relaxations between the con-
tinuous and convex hull representations for
zero-one programming problems”, SIAM
```
Journal on Discrete Mathematics 3(3),
```
411–430. doi.org/10.1137/0403036.
```
Sherali, H. D. and Alameddine, A. (1992)
```
“A new reformulation-linearization technique
for bilinear programming problems”, Journal
of Global Optimization, 2, 379–410. doi:
10.1007/BF00122429.
```
Sherman, J. (1949) “Adjustment of an inverse
```
matrix corresponding to changes in the elem-
ents of a given column or a given row of the
original matrix”, Annals of Mathematical
```
Statistics, 20(4), 621.
```
```
Van Slyke, R. M. and Wets, R. (1969) “L-shaped
```
linear programs with applications to optimal
control and stochastic programming”, SIAM
```
Journal on Applied Mathematics, 17(4),
```
638–663. doi: 10.1137/0117061.
```
Swaney, R. E. and Grossmann, I. E. (1985a) “An
```
index for operational flexibility in chemical
process design. Part I: Formulation and
```
theory”, AIChE Journal, 31(4), 621–630. doi:
```
10.1002/aic.690310412.
```
Swaney, R. E. and Grossmann, I. E. (1985b) “An
```
index for operational flexibility in chemical
process design. Part II: Computational algo-
```
rithms”, AIChE Journal, 31(4), 631–641. doi:
```
10.1002/aic.690310413.
```
Tawarmalani, M. and Sahinidis, N. V. (2004)
```
“Global optimization of mixed-integer non-
linear programs: A theoretical and computa-
tional study”, Mathematical Programming, 99,
563–591. doi: 10.1007/s10107-003-0467-6.
```
Tawarmalani, M. and Sahinidis, N. V. (2005)
```
“A polyhedral branch-and-cut approach
to global optimization”, Mathematical
```
Programming, 103(2), 225–249. doi: 10.1007/
```
s10107-005-0581-8.
```
Tawarmalani, M. and Sahinidis, N. V (2013)
```
Convexification and Global Optimization in
Continuous and Mixed-Integer Nonlinear
```
Programming: Theory, Algorithms, Software, and
```
Applications. Springer Science & Business Media.
```
Trespalacios, F. and Grossmann, I. E. (2014)
```
“Review of mixed-integer nonlinear and gener-
alized disjunctive programming methods”,
```
Chemie Ingenieur Technik, 86(7), 991–1012.
```
```
doi: 10.1002/cite.201400037.
```
```
Türkay, M. and Grossmann, I. E. (1996) “Logic-
```
based MINLP algorithms for the optimal syn-
thesis of process networks”, Computers &
```
Chemical Engineering, 20(8), 959–978. doi:
```
```
10.1016/0098-1354(95)00219-7.
```
References 185
```
Vanderbei, R. J. (2020) Linear Programming:
```
Foundations and Extensions, Springer Nature
Switzerland AG.
Vassiliadis, V. S., Sargent, R. W. H. and
```
Pantelides, C. C. (1994) “Solution of a
```
class of multistage dynamic optimization prob-
lems. 2. Problems with path constraints”,
Industrial & Engineering Chemistry Research,
```
33(9), 2123–2133. doi: 10.1021/ie00033a015.
```
```
Viswanathan, J. and Grossmann, I. E. (1990)
```
“A combined penalty function and outer-
approximation method for MINLP optimiza-
```
tion”, Computers & Chemical Engineering, 14(7),
```
```
769–782. doi: 10.1016/0098-1354(90)87085-4.
```
```
Wächter, A. and Biegler, L. T. (2006) “On the
```
implementation of an interior-point filter
line-search algorithm for large-scale nonlinear
programming”, Mathematical Programming,
```
106(1), 25–57. doi: 10.1007/s10107-004-0559-y.
```
```
Westerberg, A. W. et al. (1979) Process
```
Flowsheeting. Cambridge University Press.
```
Westerlund, T. and Pettersson, F. (1995) “An
```
extended cutting plane method for solving
convex MINLP problems”, Computers &
Chemical Engineering, 19, 131–136. doi:
```
10.1016/0098-1354(95)87027-X.
```
```
Wilkinson, J. H. (1965) Algebraic Eigenvalue
```
Problem. Oxford University Press.
```
Williams, H. P. (1999) Model Building in
```
Mathematical Programming. Wiley-Interscience.
```
Wilson, R. B. (1963) A simplicial algorithm for
```
concave programming, Ph. D. Dissertation,
Graduate School of Business Administration.
Harvard University.
```
Wolsey, L. A. (1998) Integer Programming. John
```
Wiley & Sons.
```
Zamora, J. M. and Grossmann, I. E. (1999)
```
“A branch and contract algorithm for problems
with concave univariate, bilinear and linear frac-
tional terms”, Journal of Global Optimization, 14
```
(3), 217–249. doi: 10.1023/A:1008312714792.
```
Zhang, Q., Grossmann, I. E. and Lima, R. M.
```
(2016) “On the relation between flexibility
```
analysis and robust optimization for linear
```
systems”, AIChE Journal, 62(9), 3109–3123.
```
```
doi: 10.1002/aic.15221.
```
186 References
Index
α-ECP 82
0-1 constraints
modeling of 62
0-1 integer programming problem 59
0-1 variables 53, 72, 81
active constraints 157–158
active-set strategy 27–28, 156
active strategy 28
adjustable linear functions 140
alternate optima 46
AND 62–63
Antigone 117
Aspen Plus 9
assignment problem 7, 57, 72
generalized 123
augmented Lagrangean 37
augmented penalty 89, 101
BARON 117
barrier problem 38
basic variable 45, 47, 49, 74
basis 45, 47–49, 52
batch scheduling 94
Benders
decomposition method 6, 134
generalized decomposition 8
Benders cut 85
Benders decomposition 7, 73, 119–120,
134, 137
Benders decomposition algorithm 137
best bound rule 78
BFGS 38
big-M 8, 101
big-M constraints 69
big-M formulation 65
big-M reformulation 93, 96
bilinear 111–112, 115
bilinear functions 6
bilinear programs 111
binary tree 75–77
BONMIN 81
Boolean 93
Boolean algebra 62
Boolean variable 68–69, 93, 95
bounds tightening 105
branch and bound 8, 81, 112, 114
disjunctive 98
method 75, 79, 87, 89
search 5, 73, 77–78
spatial 8
branch and cut
method 73, 75
branching rule 114
Broyden’s method 11
Broyden’s update 13
CNF 63–64
complementarity conditions 39, 158
complementary conditions 25
concave 111
concave function 19
conditions
complementarity 158
conjunctive normal form 62–64
CONOPT 32, 35, 38, 40
constrained minimum, necessary
condition for 26
```
constrained optimization (equalities) 22
```
```
constrained optimization (inequalities)
```
24
constrained optimization problem 130
constraint
nonanticipativity 139
constraint programming 103
constraint propagation 105–108
constraint qualification 23, 25, 27
constraints 19
active 25
big-M 69
mixed-integer linear 66
modeling of 62
nonanticipativity 7, 138
upper bound 66
continuous relaxation 55
contraction mapping theorem 9
control variables 143
convex 19
envelopes 8, 113–114
feasible region 54
```
one-dimensional (1-d) 153
```
convex function 20
difference of 111
convex hull 66–67, 94, 122, 126
reformulation 65
convex-hull formulation 69
convex MINLP 82
convex region 153
convex underestimators 111
convexification 109
sequential 72
convexity of a feasible region 19
CP 103–104, 106, 108
CPLEX 44, 75, 79, 108
critical point 146
critical points 150, 153
cumulative distribution function 130
cutting-plane method 126
cutting planes 5, 8, 73, 75
De Morgan’s Theorem 63
declarative model 17, 19
decomposition 82, 119
Benders 7, 73, 119–120, 134
generalized Benders 6, 8, 82, 120
Lagrangean 7–8, 119, 124, 126, 128, 139
degrees of freedom 16
depth first 78, 106
depth-first search 105
descent property 11
design decisions 131
design variables 131
deterministic equivalent 134
DICOPT 82, 90
difference of convex functions 111
direct search techniques 4
187
disaggregated variables 66
discontinuous domains and functions 56
discrete distribution function 130
discrete probability distribution function
133
disjunction 56, 66–67, 95, 97, 106
disjunctions 93
linear 64
modeling of 64
disjunctive branch and bound 8, 94,
97–99, 101
disjunctive cuts 73
disjunctive programming 93
generalized 68
distribution of OR 63
domain reduction 105–106
down and up penalties 77
dual
Lagrangean 121–123
decomposition 125
dual gap 121
dual Simplex algorithm 76
ECP 87, 89
edge-finding conditions 104, 108
eigenvalues 22
envelopes
convex 113
McCormick 113
equation oriented 9
EQUIVALENCE 62
ESH 87
exact differentiation 11
exact linearization 65
exchange rules 49
expected cost 130
expected recourse function 133
extended cutting plane 82
extended cutting-plane method 86
extended supporting-hyperplane method
87
extreme point 45–46
extreme points 57, 126
extremum 21, 23
constrained 22
necessary condition for 21–22
sufficient condition for 21–22
facility location problem 7
feasibility function 147–150
feasibility test 152
feasible region 19, 45
convex 54
nonconvex 54
feasible steady-state operation 142
first-order optimality condition 21
fixed-charge cost model 56
fixed-point problem 9
flexibility 1, 142
flexibility analysis 7–8, 142, 144
flexibility function 145
flexibility index 151–153, 156, 160
sensitivity analysis of 152
flexibility index and vertex search 151
flexibility test 144, 147, 149–150, 153,
156, 159
flexibility test with control variables 147
flexibility test with no control variables
145
full recourse 132
function
Lagrangean 24, 32, 135
GBD 87–89
GDP 68–69, 94, 101, 104
relaxed 98
GDP problem 93
generalized assignment problem 123
generalized Benders decomposition 8,
82, 84–85, 120
generalized Benders decomposition
method 6
generalized disjunctive programming 8,
68, 93
generate and test 105
genetic algorithms 112
geometric programs 110
global minimum 20
global optimization 8, 109, 111,
117
global optimum 46
Gomory cut 74
Gomory cutting planes 74, 79
Gordan’s Transposition Theorem 25
gPROMS 9
gradient 21
gradients 22, 28
gradients, linear dependence of 27
GRG 38
guidelines for formulating NLP
models 40
GUROBI 44, 75, 79, 108
heat-exchanger network 154
here and now 131
Hessian 27, 36
Hessian matrix 21, 30
Hessian of the Lagrangean 33–34
heuristics 109
hull
convex 126
reformulation 8, 69, 93
relaxation 96–97, 101
if then condition 56
implication 62
inequalities 16–17
inequalities, active 25
inequality constraints 44
inequality, active 25
inequality, inactive 25
integer convex hull 72
integer cut 89
integer variable 104
integrality gap 88
interior-point algorithms 5
interior-point method 6, 32, 38
interior point methods 44
IPOPT 32, 40
Jacobian 11, 23
Jacobian matrix 7, 10–11, 37
```
Karush–Kuhn–Tucker (KKT) 6–7,
```
26–27, 30–31
```
Karush–Kuhn–Tucker (KKT)
```
conditions 27, 30, 32, 39, 47,
156–157, 159–160
```
Karush– Kuhn–Tucker (KKT)
```
equations 27
```
Karush– Kuhn–Tucker (KKT)
```
multipliers 135
```
Karush– Kuhn–Tucker (KKT) point 30
```
knapsack 123
knapsack problem 7, 58, 124
KNITRO 39–40
Lagrange 148
Lagrange function 147
Lagrange multipliers 126
Lagrangean 27, 29, 34
augmented 37
decomposition 7–8, 119, 124–125,
128, 139
188 Index
dual 121–122, 124, 126
```
function 24, 32, 85, 135
```
Hessian of 33–34
relaxation 8, 120–121, 123,
126–127
linear fractional 111
linear inequality 54
linear programming 1, 5, 16, 44
mixed-integer 72
linear stochastic programming 132
Lipschitz continuous functions 21
local minimum 20
logic clause 62
logic propositions 93
logic-based generalized Benders
decomposition 94
logic-based outer approximation 8, 94,
100
lower bound 72
LP 44, 147
relaxation 65, 73, 75
relaxed 74–75
LP stochastic programming 132
LP/NLP based branch and bound
82
L-shaped 137
L-shaped method 134
master problem 73, 83–86, 89–90, 101,
134–135
mathematical program 4
mathematical programming 16
McCormick convex envelopes 112
McCormick envelopes 113
method
branch and bound 75
branch and cut 75
MILP 72
relaxed 72
MILP master problems 82
min test ratio 49
minimax strategy 129
minimum, constrained 24
minimum, global 27, 30
minimum, necessary condition 24
MINLP 53, 90, 94, 96, 109
nonconvex 8
MINOS 35, 37–38, 40
mixed-integer constraints 62
mixed-integer linear constraints 66
mixed-integer linear program 5, 53
mixed-integer linear programming 1, 7,
72
mixed-integer linear stochastic
programming 8
mixed-integer nonlinear programming 1,
6, 8, 17, 81
mixed-integer nonlinear programs 53
mixed-integer programming 53, 55
MOA 83
model equations 16
modeling of constraints with logic 62
monomial 110
multiperiod design 119
multiperiod planning 119
multiple-choice constraints 55
multipliers 25
Lagrange 126
multiscenario 144–145
multiscenario problem 143–144
multistage stochastic programming 132,
138
Newton’s method 7, 9, 11–12, 21, 24, 33,
35, 39, 42, 127
NLP 109, 147
nonconvex 8
reduced 100
NLP algorithm
comparison of 40
NLP relaxation 94–95, 110
nonanticipativity constraints 7, 138
nonbasic variable 45, 47, 49, 74
nonconvex 109
feasible region 54
MINLP 8
NLP 8
optimization 109
problems 6
region 153
nonconvexity 89
nonlinear equation 7
nonlinear programming 1, 6–7, 16, 26,
32
nonvertex critical points 156
nonvertex point 155
NOT 62
NP-hard 5, 58–59, 61
OA 87–89, 101
objective function 16, 19
```
one-dimensional (1-d) convex 153–154
```
```
one-dimensional (1-d) convexity 154
```
```
one-dimensional (1-d) quasiconvex
```
154
optimal design of the cooler 17
optimality conditions 27
optimality cut 136
optimization
global 8, 109, 117
nonconvex 109
software 8
optimum trade-off 18
OR 62–63
outer approximation 8, 82
logic-based 100
outer-approximation method 6
parametric region of feasible operation
149
perspective function 95, 97
planning problems 141
plant location problem 58
polyhedral set 140
polyhedral structure 120
polyhedron 45
polytope 57
positive definite 22
positive definiteness of a Hessian matrix
22
posynomial 110
primal relaxation 122
priority rule 77
probability distribution function 130,
133
problems
nonconvex 6
process operations 141
process systems engineering 1, 6, 8
propositional logic 7, 62–63
quadratic program 28, 33
quadratic programming 1
quasiconvex 146, 154
quasi-Newton formula 36
quasi-Newton formula BFGS 34
quasi-Newton method 7, 11
recourse decisions 131
recourse variables 131, 140
reduced costs 47
reduced gradient 36
reduced-gradient algorithm 32
Index 189
reduced-gradient method 6–7, 35, 40–41,
44
reduced NLP 100–101
region
convex 153
elimination 114
nonconvex 153
relaxation 96, 112, 114–115, 123
hull 96–97, 101
Lagrangean 8, 120–121, 123, 126–127
LP 75
matrix 88
NLP 94–95, 110
primal 122
tighter 66
relaxed
GDP 98
LP 74–75
relaxed MILP 72
relaxed NLP 90
robust counterpart formulation 140
robust optimization 7, 129, 139, 141
SBB 81
scenario tree 134, 138
scheduling problems 141
SCIP 75, 117
search
branch and bound 73, 77
second-order convergence 11
semi-infinite programming 7, 129, 143
semipositive definite 22
sensitivity analysis of the flexibility
index 152
sequential convexification 72
sequential modular 9
set-covering problem 7, 59, 101
```
Sherman–Morrison (1949) formula 13
```
Simplex algorithm 5, 44, 47, 49
Simplex tableau 49
simulated annealing 4, 112
SNOPT 32, 40
sparsity of the Jacobian 10
spatial branch and bound 8
method 112
SQP algorithm 32
stationary condition 24, 28, 36
stationary point 21
steepest descent 48
steepest-descent method 127
stochastic methods 111
stochastic programming 7, 129–130, 141
linear 132
multistage 138
strictly convex 22, 30
subgradient method 126
subtour elimination constraints 61
successive-quadratic programming 32, 40
successive-quadratic programming
method 6
superstructure 100
example 101
supply-chain problem 131
supporting hyperplanes 83
synthesis 2
tableau 49
three-stage programming problem 138
tighter relaxation 66
traveling salesman problem 7, 60, 104
tree search 106
Truth Tables 63
two-stage programming 131, 142, 144
two-stage programming problem
131–132
two-stage programming with guaranteed
feasibility 142
two-stage stochastic programming 7,
119, 131
uncertain parameters 7
uncertainty 129
uncertainty set 129, 140
unconstrained optimization 21
unimodular 72
upper-bound constraint 66
variable
basic 45, 47, 49, 74
disaggregated 66
nonbasic 45, 47, 49, 74
variables
0-1 81
vertex 45
vertex search 152
vertex solutions 153, 159
wait and see 131
Wilson–Han–Powell algorithm 32
XOR 62
XPRESS 44, 75, 79, 108
#### 190 Index