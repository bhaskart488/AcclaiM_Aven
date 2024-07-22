from flask import render_template, request, Blueprint
# from maven.models import Post

main = Blueprint('main', __name__)


@main.route("/")
@main.route("/home")
def index():    
    return render_template('main/index.html', title='Welcome')

@main.route("/pricing")
def pricing():    
    return render_template('main/pricing.html', title='Pricing')

@main.route("/contacts")
def contacts():    
    return render_template('main/contacts.html', title='Contacts')
