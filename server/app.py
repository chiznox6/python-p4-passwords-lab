#!/usr/bin/env python3

from flask import request, session
from flask_restful import Resource

from config import app, db, api
from models import User

class ClearSession(Resource):

    def delete(self):

        session['page_views'] = None
        session['user_id'] = None

        return {}, 204

class Signup(Resource):

    def post(self):
        json_data = request.get_json() or {}
        username = json_data.get('username')
        password = json_data.get('password')

        if not username or not password:
            return {"error": "Username and password required"}, 400

        if User.query.filter_by(username=username).first():
            return {"error": "Username already taken"}, 409

        user = User(username=username)
        user.password_hash = password

        db.session.add(user)
        db.session.commit()

        session['user_id'] = user.id
        return user.to_dict(), 201

class CheckSession(Resource):
    def get(self):
        user_id = session.get('user_id')
        if user_id:
            user = User.query.get(user_id)
            if user:
                return user.to_dict(), 200
        return {}, 204

class Login(Resource):
    def post(self):
        json_data = request.get_json() or {}
        username = json_data.get('username')
        password = json_data.get('password')

        if not username or not password:
            return {"error": "Username and password required"}, 400

        user = User.query.filter_by(username=username).first()
        if user and user.authenticate(password):
            session['user_id'] = user.id
            return user.to_dict(), 200

        return {"error": "Invalid username or password"}, 401

class Logout(Resource):
    def delete(self):
        session.pop('user_id', None)  # safely remove user_id
        return {}, 204

# Register routes
api.add_resource(ClearSession, '/clear', endpoint='clear')
api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
