from flask import abort

def throw(errorcode):
    """Returns an error based on the code given as a parameter."""
    if errorcode == 403:
        return abort(403, "Access forbidden: You do not have permission to access this resource.")
    
    if errorcode == 404:
        return abort(404, "The requested resource could not be found.")

    return abort(400)
