lillebror
=========

Library for system monitoring and logging


Usage
=====

Class
-----

```python
```


Decorator
---------

NOT YET IMPLEMENTED!

The simplest use case is as a function decorator. In that case it will output
usage statistics in the console after the function returns.

```python
from lillebror import monitor

@monitor
def run():
    pass

if __name__ == '__main__':
    run()
```
