pyxdu
=====

Display the output of "du" in a window.

"pyxdu" is a Python port of "xdu", an X window utility last updated on 
1994-06-05.

Current status: pyxdu is **not released yet**. It's in active development.


Development
-----------

Development requirements:

* Python 3.7+
* [Poetry](https://python-poetry.org)

Set up a development environment:

```shell
$ git clone https://github.com/vlasovskikh/pyxdu.git
$ poetry run pyxdu --help
$ du | poetry run pyxdu
```
