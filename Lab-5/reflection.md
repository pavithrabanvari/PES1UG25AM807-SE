# Lab 5 – Reflection

### 1. What is static code analysis, and why is it useful?

Static code analysis examines source code without executing the program. It helps identify possible bugs, security vulnerabilities, and coding-style problems early. This makes software safer, more readable, and easier to maintain.

### 2. What is the difference between Pylint, Bandit, and Flake8?

- **Pylint:** Checks code quality, naming conventions, unused variables, and possible programming errors.
- **Bandit:** Identifies common security vulnerabilities in Python code.
- **Flake8:** Checks coding style and formatting, including whitespace, indentation, and line length.

Using all three tools provides better code quality and security coverage.

### 3. What important issues did you find and fix?

I fixed several issues, including mutable default arguments, incorrect age calculation, disabled SSL certificate verification, unsafe XML parsing, unsafe archive extraction, hardcoded authentication tokens, and broad exception handling. I also improved file handling, naming conventions, documentation, and code formatting.

### 4. How does static analysis improve software quality?

Static analysis identifies problems before deployment, encourages consistent coding practices, improves readability, and reduces security risks. However, it does not replace testing because it cannot detect every runtime or functional error. Therefore, both static analysis and program testing are important.