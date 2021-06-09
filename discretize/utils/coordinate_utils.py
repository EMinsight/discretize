import numpy as np
from discretize.utils.matrix_utils import mkvc
from discretize.utils.code_utils import deprecate_function


def cylindrical_to_cartesian(grid, vec=None):
    """
    Transform a grid or a vector from cylindrical coordinates :math:`(r, \\theta, z)` to
    Cartesian coordinates :math:`(x, y, z)`.

    Parameters
    ----------
    grid : numpy.ndarray
        Location points defined in cylindrical coordinates :math:`(r, \\theta, z)`. Array
        has shape (n, 3)
    vec : numpy.ndarray, optional
        Vector defined in cylindrical coordinates as either:

        - An array of shape (n, 3) whose columns are organized [ :math:`r, \\theta, z` ]
        - A vector of length (3n,) organized :math:`r, \\theta, z`

    Returns
    -------
    numpy.ndarray
        If input parameter *vec* = *None*, the function returns xyz locations as a 
        numpy array of shape (n, 3). Otherwise, the vector defined in Cartesian
        coordinates is returned as a numpy array of shape (3n,) organized
        :math:`x, y, z`

    Examples
    --------

    Here, we convert a series of vectors in 3D space from cylindrical coordinates
    to Cartesian coordinates.

    >>> from discretize.utils import cylindrical_to_cartesian
    >>> import numpy as np
    >>> 
    >>> r = np.ones(9)
    >>> phi = (np.pi/4)*np.linspace(0, 8, 9)
    >>> z = np.linspace(-4., 4., 9)
    >>> 
    >>> u = np.c_[r, phi, z]
    >>> print('Locations in cylindrical coordinates')
    >>> print(u)
    >>> 
    >>> v = cylindrical_to_cartesian(u)
    >>> print('Locations in Cartesian coordinates')
    >>> print(v)

    """
    grid = np.atleast_2d(grid)

    if vec is None:
        return np.hstack(
            [
                mkvc(grid[:, 0] * np.cos(grid[:, 1]), 2),
                mkvc(grid[:, 0] * np.sin(grid[:, 1]), 2),
                mkvc(grid[:, 2], 2),
            ]
        )

    if len(vec.shape) == 1 or vec.shape[1] == 1:
        vec = vec.reshape(grid.shape, order="F")

    x = vec[:, 0] * np.cos(grid[:, 1]) - vec[:, 1] * np.sin(grid[:, 1])
    y = vec[:, 0] * np.sin(grid[:, 1]) + vec[:, 1] * np.cos(grid[:, 1])

    newvec = [x, y]
    if grid.shape[1] == 3:
        z = vec[:, 2]
        newvec += [z]

    return np.vstack(newvec).T


def cyl2cart(grid, vec=None):
    """An alias for cylindrical_to_cartesian"""
    return cylindrical_to_cartesian(grid, vec)


def cartesian_to_cylindrical(grid, vec=None):
    """
    Transform a grid or a vector from Cartesian coordinates :math:`(x, y, z)` to
    cylindrical coordinates :math:`(r, \\theta, z)`.
    

    Parameters
    ----------
    grid : numpy.ndarray
        Location points defined in Cartesian coordinates :math:`(x, y z)`. Array
        has shape (n, 3)
    vec : numpy.ndarray, optional
        Vector defined in Cartesian coordinates as either:

        - An array of shape (n, 3) whose columns are organized [ :math:`x, y, z` ]
        - A vector of length (3n,) organized :math:`x, y, z`

    Returns
    -------
    numpy.ndarray
        If input parameter *vec* = *None*, the function returns :math:`(r, \\theta, z)`
        locations as a numpy array of shape (n, 3). Otherwise, the vector defined in
        cylindrical coordinates is returned as a numpy array of shape (3n,) organized
        :math:`r, \\theta, z`

    Examples
    --------

    Here, we convert a series of vectors in 3D space from Cartesian coordinates
    to cylindrical coordinates.

    >>> from discretize.utils import cartesian_to_cylindrical
    >>> import numpy as np
    >>> 
    >>> r = np.ones(9)
    >>> phi = (np.pi/4)*np.linspace(0, 8, 9)
    >>> z = np.linspace(-4., 4., 9)
    >>> 
    >>> x = r*np.cos(phi)
    >>> y = r*np.sin(phi)
    >>> u = np.c_[x, y, z]
    >>> print('Locations in Cartesian coordinates')
    >>> print(u)
    >>> 
    >>> v = cartesian_to_cylindrical(u)
    >>> print('Locations in cylindrical coordinates')
    >>> print(v)

    """
    if vec is None:
        vec = grid

    vec = np.atleast_2d(vec)
    grid = np.atleast_2d(grid)

    theta = np.arctan2(grid[:, 1], grid[:, 0])

    return np.hstack(
        [
            mkvc(np.cos(theta) * vec[:, 0] + np.sin(theta) * vec[:, 1], 2),
            mkvc(-np.sin(theta) * vec[:, 0] + np.cos(theta) * vec[:, 1], 2),
            mkvc(vec[:, 2], 2),
        ]
    )


def cart2cyl(grid, vec=None):
    """An alias for cartesian_to_cylindrical"""
    return cylindrical_to_cartesian(grid, vec)


def rotation_matrix_from_normals(v0, v1, tol=1e-20):
    """
    Generate a 3x3 rotation matrix defining the rotation from vector v0 to v1.

    This function uses Rodrigues' rotation formula to generate the rotation
    matrix :math:`\\mathbf{A}` going from vector :math:`\\mathbf{v_0}` to
    vector :math:`\\mathbf{v_1}`. Thus:

    .. math::
        \\mathbf{Av_0} = \\mathbf{v_1}

    For detailed desciption of the algorithm, see
    https://en.wikipedia.org/wiki/Rodrigues%27_rotation_formula

    Parameters
    ----------
    v0 : numpy.ndarray
        Vector of length 3
    v1 : numpy.ndarray
        Vector of length 3
    tol : float (optional)
        Numerical tolerance. Default = 1e-20

    Returns
    -------
    numpy.ndarray
        A 3x3 numpy array representing the rotation matrix from v0 to v1
    
    
    """

    # ensure both v0, v1 are vectors of length 1
    if len(v0) != 3:
        raise ValueError("Length of n0 should be 3")
    if len(v1) != 3:
        raise ValueError("Length of n1 should be 3")

    # ensure both are true normals
    n0 = v0 * 1.0 / np.linalg.norm(v0)
    n1 = v1 * 1.0 / np.linalg.norm(v1)

    n0dotn1 = n0.dot(n1)

    # define the rotation axis, which is the cross product of the two vectors
    rotAx = np.cross(n0, n1)

    if np.linalg.norm(rotAx) < tol:
        return np.eye(3, dtype=float)

    rotAx *= 1.0 / np.linalg.norm(rotAx)

    cosT = n0dotn1 / (np.linalg.norm(n0) * np.linalg.norm(n1))
    sinT = np.sqrt(1.0 - n0dotn1 ** 2)

    ux = np.array(
        [
            [0.0, -rotAx[2], rotAx[1]],
            [rotAx[2], 0.0, -rotAx[0]],
            [-rotAx[1], rotAx[0], 0.0],
        ],
        dtype=float,
    )

    return np.eye(3, dtype=float) + sinT * ux + (1.0 - cosT) * (ux.dot(ux))


def rotate_points_from_normals(xyz, v0, v1, x0=np.r_[0.0, 0.0, 0.0]):
    """Rotate a set of xyz locations about a specified point.

    Rotate a grid of Cartesian points about a location x0 according to the
    rotation defined from vector v0 to v1.

    Let :math:`\\mathbf{x}` represent an input xyz location, let :math:`\\mathbf{x_0}` be
    the origin of rotation, and let :math:`\\mathbf{R}` denote the rotation matrix from
    vector v0 to v1. Where :math:`\\mathbf{x'}` is the new xyz location, this function
    outputs the following operation for all input locations:
    
    .. math::
        \\mathbf{x'} = \\mathbf{R (x - x_0)} + \\mathbf{x_0}


    Parameters
    ----------
    xyz : numpy.ndarray
        A numpy array (*, 3) of xyz locations
    v0 : numpy.ndarray
        Vector of length 3
    v1 : numpy.ndarray
        Vector of length 3
    x0 : numpy.ndarray, optional
        Vector of length 3 denoting the origin of rotation. Default is (0,0,0).

    Returns
    -------
    numpy.ndarray
        A numpy array of shape (*, 3) containing the rotated xyz locations.


    """

    # Compute rotation matrix between v0 and v1
    R = rotation_matrix_from_normals(v0, v1)

    if xyz.shape[1] != 3:
        raise ValueError("Grid of xyz points should be n x 3")
    if len(x0) != 3:
        raise ValueError("x0 should have length 3")

    # Define origin
    X0 = np.ones([xyz.shape[0], 1]) * mkvc(x0)

    return (xyz - X0).dot(R.T) + X0  # equivalent to (R*(xyz - X0)).T + X0


rotationMatrixFromNormals = deprecate_function(
    rotation_matrix_from_normals, "rotationMatrixFromNormals", removal_version="1.0.0"
)
rotatePointsFromNormals = deprecate_function(
    rotate_points_from_normals, "rotatePointsFromNormals", removal_version="1.0.0"
)
