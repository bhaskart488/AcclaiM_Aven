from flask_restful import Resource, Api, reqparse, fields, marshal_with
from maven import db
from maven.models import User, Sponsor, Influencer
from flask_login import login_user
from flask import Blueprint, jsonify

api_bp = Blueprint('api', __name__)
api = Api(api_bp)


user_fields = {
    'id': fields.Integer,
    'username': fields.String,
    'email': fields.String,
    'role': fields.String,
}


        
class Register(Resource):
    @marshal_with(user_fields)
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('username', type=str, required=True, help="Username cannot be blank")
        parser.add_argument('email', type=str, required=True, help="Email cannot be blank")
        parser.add_argument('password', type=str, required=True, help="Password cannot be blank")
        parser.add_argument('role', type=str, required=True, help="Role cannot be blank")
        args = parser.parse_args()

        if User.query.filter_by(email=args['email']).first():
            return {'message': 'Email already registered'}, 400

        user = User(username=args['username'], email=args['email'], role=args['role'])
        user.set_password(args['password'])
        db.session.add(user)
        db.session.commit()

        return user, 201




class Login(Resource):
    @marshal_with(user_fields)
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('email', type=str, required=True, help="Email cannot be blank")
        parser.add_argument('password', type=str, required=True, help="Password cannot be blank")
        args = parser.parse_args()

        user = User.query.filter_by(email=args['email']).first()
        
        if user and user.check_password(args['password']):
            login_user(user)
            return user, 200
        
        return {'message': 'Invalid credentials'}, 401

api.add_resource(Register, '/register')
api.add_resource(Login, '/login')


# # In maven/api.py
# class Campaign(Resource):
#     @marshal_with(campaign_fields)
#     def get(self, campaign_id):
#         campaign = Campaign.query.get(campaign_id)
#         if campaign:
#             return campaign, 200
#         return {'message': 'Campaign not found'}, 404

#     def post(self):
#         parser = reqparse.RequestParser()
#         parser.add_argument('name', type=str, required=True)
#         parser.add_argument('description', type=str, required=True)
#         args = parser.parse_args()

#         campaign = Campaign(name=args['name'], description=args['description'])
#         db.session.add(campaign)
#         db.session.commit()
#         return marshal(campaign, campaign_fields), 201

#     def put(self, campaign_id):
#         parser = reqparse.RequestParser()
#         parser.add_argument('name', type=str, required=True)
#         parser.add_argument('description', type=str, required=True)
#         args = parser.parse_args()

#         campaign = Campaign.query.get(campaign_id)
#         if campaign:
#             campaign.name = args['name']
#             campaign.description = args['description']
#             db.session.commit()
#             return marshal(campaign, campaign_fields), 200
#         return {'message': 'Campaign not found'}, 404

#     def delete(self, campaign_id):
#         campaign = Campaign.query.get(campaign_id)
#         if campaign:
#             db.session.delete(campaign)
#             db.session.commit()
#             return {'message': 'Campaign deleted'}, 200
#         return {'message': 'Campaign not found'}, 404

# api.add_resource(Campaign, '/campaign/<int:campaign_id>', '/campaign')
