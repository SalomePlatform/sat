# SAT -  SALOME Builder Tool

SAT is a tool developed in the Python language that aims to provide a universal and unified approach for the preparation, compilation and packaging of the different components of the SALOME platform.


SAT currently supports the following platforms:

- CentOS: 7, 8
- Rocky: 8, 9
- Fedora: 32, 34, 36, 38
- Debian: 9, 10, 11, 12
- Ubuntu: 20.04, 22.04
- Windows 10

To build a SALOME archive using the SAT tool, proceed as follows:

- first, the sources of the various products used for the build are retrieved and any platform-specific patches are applied.
- The various products are then constructed. The build order of the various products is managed by SAT, based on the construction of a dependency graph associated with the application.
- once a product has been compiled, if this later is a prerequisite for another product, the associated runtime environment is automatically set.
 
