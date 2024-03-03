from utils import error
from flask import session

def check_csrf(request):
    if session["csrf_token"] != request.form["csrf_token"]:
        return error.throw(403)