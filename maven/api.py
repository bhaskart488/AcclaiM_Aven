from flask_restful import Resource, Api, reqparse, fields, marshal_with
from maven import db
from maven.models import User, Sponsor, Influencer, Campaign, campaign_schema, campaigns_schema, AdRequest, adRequest_schema, adRequests_schema
from flask_login import login_user
from flask import Blueprint, jsonify, request
from datetime import datetime, timezone
# from marshmallow import fields


api_bp = Blueprint('api', __name__)
api = Api(api_bp)


user_fields = {
    'id': fields.Integer,
    'username': fields.String,
    'email': fields.String,
    'role': fields.String,
    'flagged': fields.Boolean
}

        
class Register(Resource):
    @marshal_with(user_fields)
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('username', type=str, required=True, help="Username cannot be blank")
        parser.add_argument('email', type=str, required=True, help="Email cannot be blank")
        parser.add_argument('password', type=str, required=True, help="Password cannot be blank")
        parser.add_argument('role', type=str, required=True, help="Role cannot be blank")
        parser.add_argument('flagged', type=bool, default=False)
        args = parser.parse_args()

        if User.query.filter_by(email=args['email']).first():
            return {'message': 'Email already registered'}, 400

        user = User(username=args['username'], email=args['email'], role=args['role'], flagged=args['flagged'])
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

        if not user:
            return {'message': 'Account does not exist'}, 404
        
        if user and user.check_password(args['password']):
            login_user(user)
            return user, 200
        
        return {'message': 'Invalid credentials'}, 401

api.add_resource(Register, '/register')
api.add_resource(Login, '/login')


# -----------------------------

# API Resources for campaigns

# -----------------------------


# Define the fields for marshalling
campaign_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'description': fields.String,
    'start_date': fields.String,  # Use DateTime and specify format if needed
    'end_date': fields.String, 
    'budget': fields.Integer,
    'visibility': fields.String,
    'goals': fields.String,
    'sponsor_id': fields.Integer,
    'flagged': fields.Boolean
}


class CampaignResource(Resource):
    @marshal_with(campaign_fields)
    def get(self, campaign_id=None):
        if campaign_id:
            campaign = Campaign.query.get(campaign_id)
            if campaign:
                return campaign, 200
            return {'message': 'Campaign not found'}, 404
        campaigns = Campaign.query.all()
        return campaigns_schema.dump(campaigns), 200


    def post(self):
        
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, required=True, help='Name of the campaign is required')
        parser.add_argument('description', type=str, required=True, help='Description is required')
        parser.add_argument('start_date', type=str, required=True, help='Start date is required')
        parser.add_argument('end_date', type=str, required=True, help='End date is required')
        parser.add_argument('budget', type=float, required=True, help='Budget is required')
        parser.add_argument('visibility', type=str, required=True, help='Visibility is required')
        parser.add_argument('goals', type=str, required=True, help='Goals are required')
        parser.add_argument('sponsor_id', type=int, required=True, help='Sponsor ID is required')
        parser.add_argument('flagged', type=bool, default=False)
        
        args = parser.parse_args()

        # Convert date strings to date objects
        start_date_str = args.get('start_date')
        end_date_str = args.get('end_date')

        # Initialize start_date and end_date with default values
        start_date = None
        end_date = None

        if start_date_str and end_date_str:
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            except ValueError:
                return {'message': 'Invalid date format, expected YYYY-MM-DD'}, 400
            
        # print("Request data:", args)  # Debugging line


        campaign = Campaign(
            name=args['name'],
            description=args['description'],
            start_date=start_date,
            end_date=end_date,
            budget=args['budget'],
            visibility=args['visibility'],
            goals=args['goals'],
            sponsor_id=args['sponsor_id'],
            flagged=args['flagged']
        )
        db.session.add(campaign)


        try:
            db.session.commit()
            return {'message': 'Campaign created successfully'}, 201
        except Exception as e:
            db.session.rollback()
            return {'message': str(e)}, 500

        
    
    @marshal_with(campaign_fields)
    def put(self, campaign_id):
        data = request.get_json()

        # Convert string dates to datetime.date objects
        try:
            start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
            end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
        except ValueError:
            return {'message': 'Invalid date format. Use YYYY-MM-DD.'}, 400

        # Find the campaign
        campaign = Campaign.query.get(campaign_id)
        if not campaign:
            return {'message': 'Campaign not found'}, 404

        # Update the campaign with new data
        campaign.name = data['name']
        campaign.description = data['description']
        campaign.start_date = start_date
        campaign.end_date = end_date
        campaign.budget = data['budget']
        campaign.visibility = data['visibility']
        campaign.goals = data['goals']
        campaign.flagged = data['flagged']

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return {'message': str(e)}, 500

        return {'message': 'Campaign updated successfully'}, 200


    def delete(self, campaign_id):
        # print('delete api called!!!')
        campaign = Campaign.query.get(campaign_id)
        
        if campaign:
            db.session.delete(campaign)
            db.session.commit()
            return {'message': 'Campaign deleted'}, 200
        return {'message': 'Campaign not found'}, 404

    
api.add_resource(CampaignResource, '/campaign/<int:campaign_id>', '/campaigns')



# -----------------------------

# api resourcer for ad-requests

# -----------------------------


# Fields for marshalling AdRequests
ad_request_fields = {
    'id': fields.Integer,
    'campaign_id': fields.Integer,
    'influencer_id': fields.Integer,
    'messages': fields.String,
    'requirements': fields.String,
    'status': fields.String,
    'offer_amount': fields.Float,
    'created_at': fields.String,
    'updated_at': fields.String,
}

class AdRequestResource(Resource):
    @marshal_with(ad_request_fields)
    def get(self, ad_request_id=None):
        if ad_request_id:
            ad_request = AdRequest.query.get(ad_request_id)
            if ad_request:
                return ad_request, 200
            return {'message': 'AdRequest not found'}, 404
        ad_requests = AdRequest.query.all()
        return adRequests_schema.dump(ad_requests), 200

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('campaign_id', type=int, required=True, help='Campaign ID is required')
        parser.add_argument('influencer_id', type=int, required=True, help='Influencer ID is required')
        parser.add_argument('messages', type=str, required=True, help='Message(s) is required')
        parser.add_argument('requirements', type=str, required=True, help='Requirements are required')
        parser.add_argument('status', type=str, required=True, help='Status is required')
        parser.add_argument('offer_amount', type=float, required=True, help='Offer is required')

        args = parser.parse_args()
        
        ad_request = AdRequest(
            campaign_id=args['campaign_id'],
            influencer_id=args['influencer_id'],
            messages=args['messages'],
            requirements=args['requirements'],
            status=args['status'],
            offer_amount=args['offer_amount'],
        )
        db.session.add(ad_request)
        try:
            db.session.commit()
            return {'message': 'AdRequest created successfully'}, 201
        except Exception as e:
            db.session.rollback()
            return {'message': str(e)}, 500

    @marshal_with(ad_request_fields)
    def put(self, ad_request_id):
        ad_request = AdRequest.query.get(ad_request_id)
        if not ad_request:
            return {'message': 'AdRequest not found'}, 404
        
        data = request.get_json()
        ad_request.campaign_id = data['campaign_id']
        ad_request.influencer_id = data['influencer_id']
        ad_request.messages = data['messages']
        ad_request.requirements = data['requirements']
        ad_request.status = data['status']
        ad_request.offer_amount = data['offer_amount']
        ad_request.updated_at = datetime.now(timezone.utc)

        try:
            db.session.commit()
            return {'message': 'AdRequest updated successfully'}, 200
        except Exception as e:
            db.session.rollback()
            return {'message': str(e)}, 500

    def delete(self, ad_request_id):
        ad_request = AdRequest.query.get(ad_request_id)
        if ad_request:
            db.session.delete(ad_request)
            db.session.commit()
            return {'message': 'AdRequest deleted'}, 200
        return {'message': 'AdRequest not found'}, 404

api.add_resource(AdRequestResource, '/ad_request/<int:ad_request_id>', '/ad_requests')