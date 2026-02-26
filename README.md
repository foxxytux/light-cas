# Light CAS
**A Lightweight Symbolic Algebra System for non-CAS TI-Nspire CX-II and CX-II-T Handhelds**

## 🚀 Overview
Light CAS is a custom Computer Algebra System (CAS) built in MicroPython. It is designed to run on the non-CAS version of the TI-Nspire CX II-T, providing symbolic differentiation and algebraic simplification—features normally locked behind the more expensive CAS models.

This project was developed with a focus on **memory efficiency** and **context-aware parsing**, making it ideal for a handheld environment.

This project was written by Gemini.

---

## 🛠 Features
- **Auto-Differentiation:** Type any function (e.g., `sin(x^2)`) and get the symbolic derivative instantly.
- **Transcendental Support:** Handles `sin`, `cos`, `tan`, `cot`, `ln`, `exp`, `sqrt`, and `atan`.
- **Partial Derivatives:** Differentiate multi-variable expressions by specifying the target (e.g., `x*y,y`).
- **Implicit Multiplication:** Recognizes `5x` as `5*x`.
- **Command History:** Use `..` to recall the last command or `h` to view recent history.
- **Constants:** Native support for `pi` and `e`.

---

## 📖 How to Use

### 1. Basic Derivatives
By default, the system assumes you want the derivative with respect to `x`.
* Input: `x^3 + 5x`
* Output: `3*x^2 + 5`

### 2. Specific Variables
Use a comma to specify which variable to differentiate.
* Input: `x*y,y`
* Output: `x`

### 3. Trigonometry & Chain Rule
The engine handles nested functions automatically.
* Input: `sin(x^2)`
* Output: `cos(x^2)*2*x`

### 4. Simplification Mode
If you want to simplify an expression without differentiating, use the `expand()` wrapper.
* Input: `expand(x + x + 5)`
* Output: `2*x + 5`

---

## ⚙️ Technical Architecture

### **The Pipeline**
1.  **Tokenizer:** Sanitizes input strings and breaks them into typed tokens (`num`, `var`, `fn`, `op`).
2.  **Parser:** A **Recursive Descent Parser** that follows standard order of operations (PEMDAS) to build an Abstract Syntax Tree (AST).
3.  **CAS Engine:** * `diff()`: Applies symbolic math rules (Power Rule, Product Rule, Quotient Rule, Chain Rule).
    * `S()`: A multi-pass simplifier that performs constant folding and identity reduction (e.g., $x \cdot 0 = 0$).
4.  **Stringifier:** Recursively converts the processed AST back into a human-readable string.

### **DevOps & Optimization**
- **Zero Dependencies:** Uses only built-in MicroPython modules.
- **Memory Management:** Utilizes nested tuples instead of heavy classes to minimize heap usage on the TI-Nspire.
- **Portability:** Tested and verified on both Linux (Python 3.10+) and TI-Nspire MicroPython environments.
