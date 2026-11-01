# Lab 5 – Static Code Analysis Issue Table

| No. | Original issue | Tool / Finding | Fix implemented |
|---|---|---|---|
| 1 | Mutable default argument `[]` | Pylint W0102 | Changed to `None` and initialized inside the function. |
| 2 | Missing module and function docstrings | Pylint C0114, C0116 | Added descriptive docstrings. |
| 3 | Function names used camelCase | Pylint C0103 | Renamed functions to snake_case. |
| 4 | Hardcoded underwriter token | Bandit B105 | Read token from an environment variable. |
| 5 | Binding to all network interfaces | Bandit B104 | Removed the unnecessary hardcoded host setting. |
| 6 | Unsafe XML parsing | Bandit B405, B314 | Used `defusedxml.ElementTree`. |
| 7 | SSL certificate verification disabled | Bandit B323 | Used the default verified HTTPS connection. |
| 8 | Unsafe archive extraction | Bandit B202 | Used `tarfile.extractall()` with the `data` filter. |
| 9 | Weak random number generator | Bandit B311 | Used the `secrets` module. |
| 10 | Bare exception handling | Bandit B112, Flake8 E722 | Replaced bare `except` with specific exceptions. |
| 11 | File opened without context manager or encoding | Pylint W1514, R1732 | Used `with` and specified UTF-8 encoding. |
| 12 | Long lines and incorrect blank-line spacing | Flake8 E501, E302, E305 | Reformatted the code. |

## Before and After Results

- Original Pylint score: 5.73/10
- Updated Pylint score: 9.81/10
- Original Bandit findings: 10
- Updated Bandit findings: 0
- Original Flake8: 19 reported violations
- Updated Flake8: 0 violations

## Remaining Pylint Warnings

The updated code has two remaining warnings:
- R0913: Too many arguments.
- R0917: Too many positional arguments.

The final Pylint score is 9.81/10, which meets the target of above 9.5.