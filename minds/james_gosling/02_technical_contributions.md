# James Gosling: Technical Contributions

## Overview of Technical Achievements

James Gosling's technical contributions span four decades and have fundamentally shaped modern computing. Beyond creating Java, he developed innovative systems including Gosling Emacs, the NeWS window system, and laid the conceptual groundwork for virtual machine architectures. This document examines these technical achievements in detail.

## Gosling Emacs (Gosmacs) - 1981

### The First Unix Emacs

Gosling Emacs (often shortened to "Gosmacs" or "gmacs") was written by James Gosling in 1981 in C. It holds the distinction of being the first Emacs implementation to run under Unix, making sophisticated text editing available to a much broader audience of Unix users.

### Technical Innovation: The Redisplay Algorithm

Gosling Emacs was especially noteworthy for its effective redisplay code. Gosling employed a dynamic programming technique to solve the classical string-to-string correction problem - determining the minimum number of operations needed to transform one string into another.

The algorithm was remarkably sophisticated. The section of the source code containing the display logic was famously headed by a skull and crossbones in ASCII art, warning would-be improvers that "even if they thought they understood how the display code worked, they actually did not." Gosling published this work as "A Redisplay Algorithm" in the Proceedings of the ACM SIGPLAN Symposium on Text Manipulation in June 1981.

### Mocklisp Extension Language

For extensibility, Gosling created Mocklisp, an extension language with syntax that appears similar to Lisp. However, unlike true Lisp, Mocklisp does not have lists - only strings and arrays. This pragmatic design decision made the interpreter simpler while still providing adequate extensibility for a text editor.

### Historical Impact

Gosling initially allowed Gosling Emacs to be redistributed with no formal restrictions, only asking for a letter acknowledging his authorship. Later, seeking to move on and after a failed search for maintainers who would preserve these rights, he sold his version to UniPress, who began selling it commercially in 1983.

Richard Stallman used some Gosling Emacs code in the initial version of GNU Emacs, including rewriting the infamous skull-and-crossbones display code to make it "shorter, faster, clearer and more extensible." The dispute between Stallman and UniPress over this code inspired the creation of the first formal license for Emacs, which later evolved into the GNU General Public License (GPL).

## NeWS (Network extensible Window System) - 1984

### PostScript-Based Windowing

NeWS (Network extensible Window System), originally known as "SunDew," was developed by James Gosling and David S. H. Rosenthal at Sun Microsystems starting in 1984. It represented a radically different approach to windowing systems.

The NeWS interpreter was based on Adobe's PostScript language, extending it to allow interaction and multiple "contexts" to support windows. Unlike PostScript in a printer, NeWS ran multiple PostScript programs simultaneously on one screen using cooperative multitasking.

### Technical Architecture

NeWS expanded the original PostScript stack-based language into a complete object-oriented (OO) programming style with inheritance. Key technical features included:

- **Complete Programming Environment**: Unlike basic PostScript, NeWS could create complete interactive programs with mouse support and GUI elements
- **Object-Oriented Extensions**: Eliminated the need for an external OO language to build applications
- **Native PostScript Applications**: Simple PostScript code could result in running, onscreen, interactive programs

### Comparison to X Window System

Compared to X, NeWS was vastly more powerful due to its programmable nature - applications could download code to the server rather than just making drawing requests. However, NeWS was also slower, especially for local connections.

A critical factor in X's eventual dominance was licensing: Sun charged a fee to license the NeWS source code, while the MIT X11 code was free. Gosling later reflected that Sun's decision not to open source NeWS was a significant mistake that limited its adoption.

### Notable NeWS Applications

Don Hopkins developed a NeWS version of SimCity using HyperLook, and Altsys created Virtuoso, a commercial drawing program that was a port of FreeHand with additional functionality taking advantage of the PostScript environment.

### Publications

Gosling co-authored "The NeWS Book: An Introduction to the Network/Extensible Window System" with David S.H. Rosenthal and Michelle J. Arden, published as part of the Sun Technical Reference Library.

## Java and the Java Virtual Machine

### Origins in UCSD Pascal P-Code

The conceptual foundation for the Java Virtual Machine came from Gosling's graduate work at Carnegie Mellon University. He had PERQ workstations built by hardware engineers who didn't want to develop software. The only available free compiler was UCSD Pascal, so they made the hardware interpret UCSD Pascal p-codes directly.

His thesis advisor, Raj Reddy, asked Gosling to spend a summer figuring out how to run software from these PERQ machines on their VAXes. He started by writing a hardware emulator to understand the p-codes, effectively translating PERQ Q-Code to VAX assembler while emulating the hardware. This experience of architecture-neutral execution through bytecode interpretation directly inspired the Java Virtual Machine design.

### The Star7 and Oak Language

In 1990, Gosling joined the Green Project at Sun Microsystems to explore consumer technologies. By fall of 1992, the team had produced the Star7, a prototype PDA-like device with a five-inch color touchscreen - remarkably advanced for its time.

For the Star7, Gosling created the Oak language (later renamed Java). The cartoon character Duke, which appeared on the Star7's display, later became Java's mascot. The Star7 demonstration has been preserved and is available on the Internet Archive.

### Original Compiler and Virtual Machine

Gosling designed and implemented Java's original compiler and virtual machine largely on his own. He remembered his experience with UCSD Pascal and consulted with people involved in the Smalltalk virtual machine. The project leadership viewed the language as just a tool rather than a standalone product, so Gosling was responsible for the language design, compiler, and virtual machine simultaneously.

### Key Language Design Decisions

Java incorporated several deliberate design decisions that distinguished it from C++:

1. **Automatic Garbage Collection**: Java automatically allocates and deallocates memory, eliminating the risks of manual memory management such as dangling pointers and memory leaks. No destructors or delete operators are required.

2. **References Instead of Pointers**: Java uses references instead of C/C++ style pointers. As Gosling noted, "You cannot forge a pointer in Java," which eliminated entire classes of security vulnerabilities.

3. **Simplified Object-Oriented Model**: Java was designed to produce code simpler to write and maintain than C or C++. It retained class structure, polymorphism, and inheritance from C++ while removing complex features.

4. **Platform Independence**: The "Write Once, Run Anywhere" philosophy meant compiled Java bytecode could run on any Java Virtual Machine regardless of underlying architecture.

### JVM Security Model

Gosling built extensive security and reliability features into the JVM, primarily centered on memory model integrity. He later noted that Microsoft's approach of building a virtual machine to support C and C++ was problematic because "as soon as you support C and C++, you blow away most of the security story."

### Just-In-Time Compilation

Gosling popularized the term "Just-in-time compilation" (borrowed from manufacturing terminology) starting in 1993. He explained that achieving significant JIT performance improvements "helps dramatically to have a statically-typed language. For dynamically-typed languages, like Python, it's really, really hard."

### Repurposing for the Web

After an unsuccessful foray into interactive cable TV through Sun's spin-out company FirstPerson, Gosling's team repurposed Java for the Web in 1994. This pivot proved transformative, enabling dynamic and interactive web pages at a time when most were static HTML.

## Technical Publications

James Gosling has authored or co-authored several significant technical publications:

- **"A Redisplay Algorithm"** - Proceedings of the ACM SIGPLAN Symposium on Text Manipulation, June 1981
- **"The NeWS Book: An Introduction to the Network/Extensible Window System"** - Sun Technical Reference Library, 1989
- **"The Java Language Specification"** - Co-authored with Bill Joy, Guy L. Steele Jr., Gilad Bracha, and Alex Buckley

## Legacy of Technical Contributions

Gosling's technical work shows a consistent thread: making complex systems more accessible and portable. From Gosling Emacs bringing sophisticated editing to Unix, to NeWS attempting to bring programmable graphics to workstations, to Java's universal portability, each project tackled the challenge of platform independence and ease of use.

His early work with p-code virtual machines at Carnegie Mellon directly informed the JVM design. His experience with the skull-and-crossbones display code taught him to make systems "shorter, faster, clearer and more extensible." These lessons culminated in Java, which combined all these principles into a language that transformed enterprise computing.

---

## Sources

- [James Gosling - Wikipedia](https://en.wikipedia.org/wiki/James_Gosling)
- [Gosling Emacs - Wikipedia](https://en.wikipedia.org/wiki/Gosling_Emacs)
- [NeWS - Wikipedia](https://en.wikipedia.org/wiki/NeWS)
- [A Conversation with James Gosling - ACM Queue](https://queue.acm.org/detail.cfm?id=1017013)
- [How The JVM Spec Came To Be - InfoQ](https://www.infoq.com/presentations/gosling-jvm-lang-summit-keynote/)
- [Java Creator James Gosling Interview - DZone](https://dzone.com/articles/java-creator-james-gosling-interview)
- [Star7 Demo - Internet Archive](https://archive.org/details/Star7Demo)
- [The NeWS Book - Google Books](https://books.google.com/books/about/The_NeWS_Book.html?id=YEQUfzsxa9UC)
- [Computer History Museum - James Gosling](https://computerhistory.org/profile/james-gosling/)
