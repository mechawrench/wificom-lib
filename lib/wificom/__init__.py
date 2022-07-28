# This file is part of the DMComm project by BladeSabre. License: MIT.

class ApiError(ValueError):
	"""Exception raised when there is problem communicationg with the backend API server."""

class ConnectError(Exception):
	"""Exception raised when there is a problem connecting to the Wireless network."""
