import reflex as rx
import jwt
import requests
from pathlib import Path
import os
from dotenv import load_dotenv

env_path = Path(__file__).resolve().parents[2] / "backend" / ".env"
load_dotenv(env_path)
SECRET_KEY = os.getenv("SECRET_KEY")


class State(rx.State):
    username : str = ""
    role : str = ""
    token : str = ""
    token_type : str = ""

    def set_user_data(self, username=None, role=None, token=None, token_type=None):
        if username is not None:
            self.username = username
        if role is not None:
            self.role = role
        if token is not None:
            self.token = token
        if token_type is not None:
            self.token_type = token_type
        print(self.username, self.role)
    def logout(self):
        self.username = ""
        self.role = ""
        self.token = ""
        self.token_type = ""

    def user_authorization(self):
        if not self.user_check():
            return rx.redirect("/login")
    def admin_authorization(self):
        # print("Role: ", self.role)
        if not self.admin_check():
            return rx.redirect("/")
    def admin_check(self):
        return (self.username != "" and self.token != "")
    def user_check(self):
        return (self.username != "" and self.token != "" and self.role == "admin")


    def verify_token(self):
        if self.token == "":
            return({"message" : "token not found",
                   "status" : "ERROR"})
        try:
            decoded = jwt.decode(self.token, SECRET_KEY, algorithms=["HS256"])
            return({"message" : decoded,
                   "status" : "OK"})
        except jwt.ExpiredSignatureError:
            return({"message" : "Token expired",
                   "status" : "ERROR"})
        except jwt.InvalidTokenError:
            return({"message" : "Invalid token",
                   "status" : "ERROR"})

