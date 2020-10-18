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
        "name": "[root]",
        "size": 30,
        "children": [
            {
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
            },
        ],
    }


def test_implicit_size():
    s = """\
20  /foo/bar
10  /foo/baz
"""
    with StringIO(s) as fd:
        top = xdu.parse_fd(fd)
    root = top.children[0]
    assert root.name == "/"
    assert root.size == 30
    foo = root.children[0]
    assert foo.name == "foo"
    assert foo.size == 30
