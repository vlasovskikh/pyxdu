from io import StringIO

from pyxdu import xdu


def test_parse_empty():
    s = ""
    with StringIO(s) as fd:
        top = xdu.parse_fd(fd)
    assert top.to_json() == {
        "name": "[root]",
        "size": 0,
        "children": [],
    }


def test_parse_simple():
    s = """\
30  /foo
20  /foo/bar
10  /foo/baz
"""
    with StringIO(s) as fd:
        top = xdu.parse_fd(fd)
    assert top.to_json() == {
        "name": "/",
        "size": 30,
        "children": [
            {
                "name": "foo",
                "size": 30,
                "children": [
                    {
                        "name": "bar",
                        "size": 20,
                        "children": [],
                    },
                    {
                        "name": "baz",
                        "size": 10,
                        "children": [],
                    },
                ],
            },
        ],
    }


def test_implicit_size():
    s = """\
20  /foo/bar
10  /foo/baz
"""
    with StringIO(s) as fd:
        root = xdu.parse_fd(fd)
    assert root.name == "/"
    assert root.size == 30
    foo = root.children[0]
    assert foo.name == "foo"
    assert foo.size == 30


def test_no_size_in_between():
    s = """\
10 /foo
20 /foo/bar/baz
"""
    with StringIO(s) as fd:
        root = xdu.parse_fd(fd)
    assert root.name == "/"
    assert root.size == 10
    foo = root.children[0]
    assert foo.name == "foo"
    assert foo.size == 10
    bar = foo.children[0]
    assert bar.name == "bar"
    assert bar.size == 20
