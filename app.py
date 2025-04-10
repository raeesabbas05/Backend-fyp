# from flask import Flask
# from flask_cors import CORS
# from flask_jwt_extended import create_access_token, jwt_required, JWTManager
# from flask import request, jsonify
# from dotenv import load_dotenv

# from models import db, User
# from main import predict_future_dates
# from helper import get_password_hash, verify_password
# import os

# load_dotenv()

# app = Flask(__name__)

# cors = CORS(app, resources={r"/*": {"origins": "*"}})
# jwt = JWTManager(app)
# basedir = os.path.abspath(os.path.dirname(__file__))
# app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(
#     basedir, os.getenv("DB_NAME")
# )
# app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")

# db.init_app(app)

# TRAINING_MODELS = {
#     "data_analytics": "models/data_analytics_prediction.h5",
#     "devops": "models/devops_prediction.h5",
#     "frontend": "models/frontend_prediction.h5",
#     "software_tester": "models/software_tester_prediction.h5",
#     "uiux": "models/uiux_prediction.h5",
# }


# @app.route("/")
# def hello():
#     return "Hello world"


# @app.cli.command("db_create")
# def create_database():
#     db.create_all()
#     print("Database created!")


# @app.cli.command("db_drop")
# def drop_database():
#     db.drop_all()
#     print("Database dropped!")


# @app.cli.command("db_seed")
# def create_test_user():
#     # Create a test user
#     test_user = User(
#         firstname="Shoaib",
#         lastname="Ahmad",
#         email="test@test.com",
#         password=get_password_hash("P@ssw0rd"),
#     )

#     db.session.add(test_user)
#     db.session.commit()
#     print("Database seeded!")


# @app.route("/login", methods=["POST"])
# def login():
#     if not request.is_json:
#         return jsonify(message="Missing request body"), 400

#     data = request.get_json()
#     email = data.get("email")
#     password = data.get("password")

#     user = User.query.filter_by(email=email).first()
#     if not (user and verify_password(password, user.password)):
#         return jsonify(message="Bad email or password"), 401

#     access_token = create_access_token(identity=email)
#     return jsonify(status="success", access_token=access_token)


# @app.route("/register", methods=["POST"])
# def register():
#     if not request.is_json:
#         return jsonify(status="error", error="Missing request body"), 400

#     data = request.get_json()
#     email = data.get("email")
#     if User.query.filter_by(email=email).first():
#         # The email already exists in database
#         return jsonify(status="error", error="Email already exists"), 409

#     firstname = data.get("firstname", "")
#     lastname = data.get("lastname", "")
#     password = data.get("password")

#     if email and password:
#         # Create a new user
#         user = User(
#             firstname=firstname,
#             lastname=lastname,
#             email=email,
#             password=get_password_hash(password),
#         )
#         db.session.add(user)
#         db.session.commit()
#         return jsonify(status="success", message="User created successfully."), 201

#     return jsonify(status="error", error="Missing required data"), 400


# @app.route("/predict/<string:role>", methods=["GET"])
# @jwt_required()
# def predict(role: str = ""):
#     if not role.strip():
#         return jsonify(status="error", error="Missing role"), 400

#     data_path = os.getenv("TRAINING_DATA")
#     model_path = TRAINING_MODELS.get(role.strip().lower().replace(" ", "_"))

#     if not model_path:
#         return jsonify(status="error", error="Invalid role"), 400

#     future_dates, future_predictions = predict_future_dates(data_path, model_path)
#     future_dates = list(map(format_timestamp, future_dates.tolist()))
#     future_predictions = list(map(int, future_predictions.tolist()))
#     return jsonify(
#         status="success",
#         data={"dates": future_dates, "predictions": future_predictions},
#     )


# def format_timestamp(timestamp):
#     return timestamp.strftime("%b-%y")


# if __name__ == "__main__":
#     app.run()



from flask import Flask, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, JWTManager
from flask_cors import CORS  # Import CORS
from dotenv import load_dotenv
from datetime import datetime, timedelta
import os
import logging

from models import db, User
from main import predict_future_dates
from helper import get_password_hash, verify_password

load_dotenv()

app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})  # Enable CORS for the app
jwt = JWTManager(app)

# Setup logging
logging.basicConfig(level=logging.DEBUG)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, os.getenv("DB_NAME"))
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=5)

db.init_app(app)


TRAINING_MODELS = {
    "data_analytics": "models/data_analytics_prediction.h5",
    "devops": "models/devops_prediction.h5",
    "frontend": "models/frontend_prediction.h5",
    "software_tester": "models/software_tester_prediction.h5",
    "uiux": "models/uiux_prediction.h5",
}

@app.route("/")
def hello():
    return "Hello world"

@app.cli.command("db_create")
def create_database():
    db.create_all()
    logging.info("Database created!")

@app.cli.command("db_drop")
def drop_database():
    db.drop_all()
    logging.info("Database dropped!")

@app.cli.command("db_seed")
def create_test_user():
    # Create a test user
    test_user = User(
        firstname="Shoaib",
        lastname="Ahmad",
        email="test@test.com",
        password=get_password_hash("P@ssw0rd"),
    )
    db.session.add(test_user)
    db.session.commit()
    logging.info("Database seeded!")

@app.route("/login", methods=["POST"])
def login():
    if not request.is_json:
        return jsonify(message="Missing request body"), 400

    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    user = User.query.filter_by(email=email).first()
    if not (user and verify_password(password, user.password)):
        return jsonify(message="Bad email or password"), 401

    access_token = create_access_token(identity=email)
    return jsonify(status="success", access_token=access_token)

@app.route("/register", methods=["POST"])
def register():
    app.logger.debug("Register endpoint called")
    if not request.is_json:
        app.logger.error("Missing JSON in request")
        return jsonify(status="error", error="Missing request body"), 400

    data = request.get_json()
    app.logger.debug("Received data: %s", data)

    email = data.get("email")
    if User.query.filter_by(email=email).first():
        app.logger.error("Email already exists: %s", email)
        return jsonify(status="error", error="Email already exists"), 409

    firstname = data.get("firstname", "")
    lastname = data.get("lastname", "")
    password = data.get("password")

    if email and password:
        user = User(
            firstname=firstname,
            lastname=lastname,
            email=email,
            password=get_password_hash(password),
        )
        db.session.add(user)
        db.session.commit()
        app.logger.info("User created successfully: %s", email)
        return jsonify(status="success", message="User created successfully."), 201

    app.logger.error("Missing required data in request")
    return jsonify(status="error", error="Missing required data"), 400

@app.route("/predict/<string:role>", methods=["GET"])
@jwt_required()
def predict(role: str = ""):
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    start_date = datetime.strptime(start_date, "%Y-%m-%d")
    end_date = datetime.strptime(end_date, "%Y-%m-%d")

    app.logger.info("Processing prediction request for role: %s", role)
    if not role.strip():
        app.logger.error("Missing role parameter in prediction request")
        return jsonify(status="error", error="Missing role"), 422

    data_path = os.getenv("TRAINING_DATA")
    model_path = TRAINING_MODELS.get(role.strip().lower().replace(" ", "_"))

    if not model_path:
        app.logger.error("Invalid role specified in prediction request: %s", role)
        return jsonify(status="error", error="Invalid role"), 422

    future_dates, future_predictions = predict_future_dates(data_path, model_path)
    print("fd",  future_dates)
    # future_dates = list(map(format_timestamp, future_dates.tolist()))
    future_predictions = list(map(int, future_predictions.tolist()))

    filter_dates = []
    filter_values = []

    for date, val in zip(future_dates.tolist(), future_predictions):

        if date <= end_date and date >= start_date:
            formated_dated = format_timestamp(date)
            # print('testingdate',formated_dated)
            filter_dates.append(formated_dated)
            filter_values.append(val)

    # Print the response or any value
    print("Future Dates:", filter_dates)
    print("Future Predictions:", filter_values)

    return jsonify(
        status="success",
        data={"dates": filter_dates, "predictions": filter_values},
    )

def format_timestamp(timestamp):
    return timestamp.strftime("%d-%b")

if __name__ == "__main__":
    app.run(debug=True)