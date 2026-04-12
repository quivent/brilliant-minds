# Brian Kernighan: Key Works and Publications

## Books (Chronological)

| Year | Title | Co-author(s) | Impact |
|------|-------|-------------|--------|
| 1974 | *The Elements of Programming Style* | P.J. Plauger | The Strunk & White of code; 62 maxims |
| 1976 | *Software Tools* | P.J. Plauger | Programs as composable filters |
| 1978 | *The C Programming Language* (K&R) | Dennis Ritchie | Defined C for a generation |
| 1981 | *Software Tools in Pascal* | P.J. Plauger | Pascal edition of Software Tools |
| 1984 | *The Unix Programming Environment* | Rob Pike | The definitive Unix philosophy text |
| 1988 | *The AWK Programming Language* | Aho, Weinberger | AWK reference (2nd ed. 2023) |
| 1999 | *The Practice of Programming* | Rob Pike | Style, debugging, testing, design |
| 2003 | *AMPL* (2nd ed.) | Fourer, Gay | Modeling language reference |
| 2015 | *The Go Programming Language* | Alan Donovan | K&R for Go |
| 2017 | *Understanding the Digital World* | — | Computing for general audience |
| 2018 | *Millions, Billions, Zillions* | — | Defending against number abuse |
| 2019 | *UNIX: A History and a Memoir* | — | Personal Bell Labs history |

## Algorithms

### Kernighan-Lin Algorithm (1970)
With Shen Lin. Heuristic for graph partitioning: divide vertices into two equal subsets minimizing edge cut. Uses variable-depth search — swap pairs of vertices greedily, then commit the best prefix of swaps. O(n^2 log n) per pass. Foundational in VLSI layout and electronic design automation.

### Lin-Kernighan Heuristic (1973)
With Shen Lin. One of the most effective heuristics for the Travelling Salesman Problem. Uses variable-depth search: at each step, consider a sequence of edge swaps (not just single swaps), commit the best prefix. Still competitive with modern approaches for TSP instances.

## Software

### AWK (1977)
Pattern-action language for text processing. Co-created with Alfred Aho and Peter Weinberger. The canonical Unix text tool alongside grep and sed. Kernighan maintains the "one true awk" implementation, recently adding Unicode support.

### AMPL (1990s)
A Modeling Language for Mathematical Programming. Co-designed with Robert Fourer and David Gay. Algebraic language for expressing large-scale optimization problems. Kernighan was co-designer and initial implementor.

### "Hello, World" (1972)
First appeared in Kernighan's Bell Labs internal memo *A Tutorial Introduction to the Language B*. Republished in *Programming in C: A Tutorial* (1974). Immortalized in K&R Section 1.1 (1978). The most reproduced program in history.

## The Name "Unix" (1970)
Kernighan coined "Unics" (Uniplexed Information and Computing Service) as a pun on the failed Multics project. The spelling was later changed to "Unix."
