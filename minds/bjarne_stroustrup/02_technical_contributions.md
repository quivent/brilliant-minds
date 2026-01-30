# C++ Technical Contributions: Language Creation and Evolution

## The Genesis: "C with Classes" (1979-1983)

### Motivation and Background

Bjarne Stroustrup's creation of C++ arose from a specific frustration. During his Ph.D. research at Cambridge, he had used the Simula programming language for distributed systems simulations. Simula, developed in Norway in the 1960s, pioneered object-oriented programming concepts including classes, inheritance, and objects. Stroustrup appreciated Simula's elegant abstractions for organizing complex programs but was deeply disappointed by its poor runtime performance.

When Stroustrup joined AT&T Bell Labs in 1979 and was told to "do something interesting," he decided to fuse the best qualities of two worlds:
- **C's efficiency**: Direct hardware access, predictable performance, minimal runtime overhead
- **Simula's abstractions**: Classes, encapsulation, inheritance for program organization

The result was **"C with Classes"**, begun in October 1979.

### Initial Features (1979-1983)

The first implementation used a preprocessor called **Cpre** that translated C with Classes code into plain C, which could then be compiled by existing C compilers. By March 1980, Cpre supported real projects and experiments, with Stroustrup's records showing use on 16 systems.

The initial C with Classes features included:
- **Classes**: User-defined types with member functions and data
- **Derived classes**: Single inheritance for building class hierarchies
- **Strong typing**: Enhanced type checking beyond C
- **Inlining**: Inline functions for performance
- **Default arguments**: Optional function parameters with default values
- **Public/private access control**: Encapsulation of implementation details

## The Birth of C++ (1983-1985)

### Naming and New Features

In 1982, Stroustrup began developing a successor to C with Classes. In 1983, he chose the name **"C++"** - the increment operator (++) suggesting an evolutionary improvement over C. The name was chosen after considering several alternatives.

The transition from C with Classes to C++ added substantial new capabilities:

#### Virtual Functions
Virtual functions enabled **runtime polymorphism** - the ability for derived classes to override base class behavior, with the correct version selected at runtime based on the actual object type:

```cpp
class Shape {
public:
    virtual void draw() = 0;  // Pure virtual function
    virtual ~Shape() {}       // Virtual destructor
};

class Circle : public Shape {
public:
    void draw() override { /* draw circle */ }
};
```

The `virtual` keyword allows a member function declared in a base class to be appropriately called through a pointer to the base class when pointing to a derived class object. Classes containing virtual functions are called **polymorphic classes**.

#### Function and Operator Overloading
C++ introduced the ability to define multiple functions with the same name but different parameter types, enabling **compile-time (static) polymorphism**:

```cpp
void print(int x);
void print(double x);
void print(const std::string& s);
```

**Operator overloading** extended this to allow user-defined types to use standard operators:

```cpp
Vector operator+(const Vector& a, const Vector& b);
```

#### References
C++ introduced **references** (using the `&` symbol) as an alias to an existing variable, providing cleaner syntax than pointers for many use cases:

```cpp
void swap(int& a, int& b) {
    int temp = a;
    a = b;
    b = temp;
}
```

#### Type-Safe Memory Management
The **new** and **delete** operators replaced C's malloc/free with type-safe memory allocation:

```cpp
int* p = new int(42);      // Allocate and initialize
int* arr = new int[100];   // Allocate array
delete p;                   // Free single object
delete[] arr;               // Free array
```

#### Constants and Single-Line Comments
The **const** keyword provided compile-time enforcement of immutability. BCPL-style **single-line comments** (`//`) were added alongside C's `/* */` comments.

### The Cfront Compiler

Stroustrup developed **Cfront**, a standalone compiler that translated C++ into C source code. This approach had several advantages:
- Leveraged existing, highly-optimized C compilers
- Enabled C++ to run on any platform with a C compiler
- Allowed gradual adoption alongside existing C code

Cfront was implemented first in C with Classes (1982-1983), then rewritten in C++ itself to demonstrate the language's **self-hosting** capability. It saw internal use at Bell Labs starting in August 1983 and was commercially released as **version 1.0 in October 1985**.

Cfront's translation approach created some lasting effects on C++:
- **Name mangling**: Encoding type information in symbol names for linking
- Various corner cases in the language specification

Cfront was abandoned in 1993 when integrating C++ exceptions became too difficult, but its influence persists in modern C++ compilers.

## Object-Oriented Programming in C++

### Classes and Encapsulation

C++ classes combine data and functions into cohesive units with controlled access:
- **public**: Accessible from anywhere
- **protected**: Accessible from the class and derived classes
- **private**: Accessible only from within the class

### Inheritance Hierarchy

C++ supports multiple forms of inheritance:
- **Single inheritance**: One derived class inherits from one base class
- **Multiple inheritance**: A class inherits from multiple base classes
- **Virtual inheritance**: Solves the "diamond problem" when a class inherits from two classes that share a common base

The **diamond problem** occurs in hybrid inheritance when a derived class gets multiple copies of the same base class member. Virtual inheritance ensures only a single copy of the base class is shared.

### Polymorphism

C++ provides two types of polymorphism:

1. **Compile-time (Static) Polymorphism**:
   - Function overloading
   - Operator overloading
   - Templates (generic programming)

2. **Runtime (Dynamic) Polymorphism**:
   - Virtual functions
   - Late binding (vtables)

**Pure virtual functions** (declared with `= 0`) create **abstract base classes** that cannot be instantiated directly.

## RAII: Resource Acquisition Is Initialization

One of C++'s most important idioms, **RAII** (coined by Stroustrup), binds resource lifetime to object lifetime:

```cpp
class FileWrapper {
    FILE* file;
public:
    FileWrapper(const char* name) : file(fopen(name, "r")) {}
    ~FileWrapper() { if (file) fclose(file); }
};
```

The technique was developed for **exception-safe resource management** between 1984-1989, primarily by Stroustrup and Andrew Koenig. RAII guarantees:
- Resources are acquired during object construction
- Resources are released during object destruction
- Resources are released even if exceptions occur (stack unwinding)

This deterministic cleanup is fundamental to C++'s approach to memory management, contrasting with garbage-collected languages.

## Template Metaprogramming and Generic Programming

### Templates Introduction

C++ templates enable **generic programming** - writing code that works with any type satisfying certain requirements:

```cpp
template<typename T>
T max(T a, T b) {
    return (a > b) ? a : b;
}
```

### The Standard Template Library (STL)

The **STL**, designed by Alexander Stepanov, demonstrated the power of generic programming. It provides:
- **Containers**: vector, list, map, set, etc.
- **Algorithms**: sort, find, transform, etc.
- **Iterators**: Abstractions connecting containers and algorithms
- **Functors**: Function objects for customization

The STL achieves **compile-time polymorphism** that is often more efficient than runtime polymorphism through virtual functions.

### Template Metaprogramming

Template metaprogramming allows computation at compile time:

```cpp
template<int N>
struct Factorial {
    static const int value = N * Factorial<N-1>::value;
};

template<>
struct Factorial<0> {
    static const int value = 1;
};
```

This technique is **Turing-complete** - any computation expressible by a program can be computed by template metaprogramming. Uses include:
- Loop unrolling
- Compile-time computation
- Type manipulation
- Policy-based design

### C++20 Concepts

The C++20 standard introduced **Concepts**, allowing explicit specification of template requirements:

```cpp
template<typename T>
concept Sortable = requires(T a) {
    { a < a } -> std::convertible_to<bool>;
};
```

The name "concepts" was coined by Alexander Stepanov, completing a vision for generic programming decades in the making.

---

## Sources

- [A History of C++: 1979-1991 (Stroustrup)](https://www.stroustrup.com/hopl2.pdf)
- [C++ - Wikipedia](https://en.wikipedia.org/wiki/C++)
- [Cfront - Wikipedia](https://en.wikipedia.org/wiki/Cfront)
- [RAII - cppreference.com](https://en.cppreference.com/w/cpp/language/raii.html)
- [Standard Template Library - Wikipedia](https://en.wikipedia.org/wiki/Standard_Template_Library)
- [Template Metaprogramming - Wikipedia](https://en.wikipedia.org/wiki/Template_metaprogramming)
- [Virtual Functions and Runtime Polymorphism - GeeksforGeeks](https://www.geeksforgeeks.org/cpp/virtual-functions-and-runtime-polymorphism-in-cpp/)
- [Resource Acquisition Is Initialization - Wikipedia](https://en.wikipedia.org/wiki/Resource_acquisition_is_initialization)
