import pytest


@pytest.fixture(scope="function")
def original_example_input() -> dict:
    """The example delivered with a task has mismatch with openapi yml definition of the body.
    'Key' plane was renamed to 'projection_plane'

    Note:
        fixtures scope set to function instead of session since the returned value is mutable.
        I do not want to be forced to making copies inside tests when I'm modifying something.

    Perhaps I should Django's HttpRequest... but I decided to let that as-is for now.
    """
    return {
        "geometry": [
            {"x1": -207, "x2": -332, "y1": 9, "y2": 191, "z1": 0, "z2": 18},
            {"x1": -207, "x2": -332, "y1": 209, "y2": 391, "z1": 0, "z2": 18},
            {"x1": 207, "x2": 332, "y1": 9, "y2": 191, "z1": 0, "z2": 18},
            {"x1": 207, "x2": 332, "y1": 209, "y2": 391, "z1": 0, "z2": 18},
            {"x1": -8, "x2": 10, "y1": 9, "y2": 191, "z1": 0, "z2": 320},
            {"x1": -8, "x2": 10, "y1": 209, "y2": 391, "z1": 0, "z2": 320},
            {"x1": -350, "x2": -332, "y1": 9, "y2": 191, "z1": 0, "z2": 320},
            {"x1": -350, "x2": -332, "y1": 209, "y2": 391, "z1": 0, "z2": 320},
            {"x1": 332, "x2": 350, "y1": 9, "y2": 191, "z1": 0, "z2": 320},
            {"x1": 332, "x2": 350, "y1": 209, "y2": 391, "z1": 0, "z2": 320},
            {"x1": -350, "x2": 350, "y1": 391, "y2": 409, "z1": 0, "z2": 320},
            {"x1": -350, "x2": 350, "y1": 191, "y2": 209, "z1": 0, "z2": 320},
            {"x1": -350, "x2": 350, "y1": -9, "y2": 9, "z1": 0, "z2": 320},
        ],
        "projection_plane": "XY",
    }