from flask import render_template, request, Blueprint
# from maven.models import Post

main = Blueprint('main', __name__)


@main.route("/")
@main.route("/home")
def index():    
    return render_template('main/index.html', title='Welcome')
