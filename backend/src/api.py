import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PATCH, DELETE, OPTIONS')
    return response
    
'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''

db_drop_and_create_all()

## ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks')
def get_drinks():
    drink_list = []
    drinks = Drink.query.all()
    for each_drink in drinks:
        drink_list.append(each_drink.short())

    return jsonify({'success': True,
                    'drinks': drink_list})

'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drinks_detail(payload):
    drink_list = []
    drinks = Drink.query.all()
    for each_drink in drinks:
        drink_list.append(each_drink.long())
    return jsonify({'success': True,
                    'drinks': drink_list})

'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route("/drinks", methods=['POST'])
@requires_auth('post:drinks')
def post_drinks(payload):
    new_drink = request.get_json()
    # add drink to database
    my_drink = Drink(title=new_drink['title'], recipe=json.dumps(new_drink['recipe']))
    my_drink.insert()
    return jsonify({
        'success':True,
        'drinks': [my_drink.long()]})

'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def patch_drinks(payload, id):
    try:
        my_drink = Drink.query.get(id)
        if my_drink is None:
            abort(404)

        my_drink_long = my_drink.long()
        my_drink.title = json.dumps(request.json.get('title', my_drink_long['title']))
        my_drink.recipe = json.dumps(request.json.get('recipe', my_drink_long['recipe']))
        my_drink.update()
        return jsonify({
            'success':True,
            'drinks': [my_drink.long()]})
    except Exception as e:
        print (e)
        abort(422)

'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks/<id>', methods = ['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload, id):
    drink = Drink.query.get(id)
    # abort not found
    if drink is None:
        abort(404)
    drink.delete()
    return jsonify({
        'success':True,
        'delete':id
    })
## Error Handling

@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False, 
                    "error": 422,
                    "message": "unprocessable"
                    }), 422

@app.errorhandler(404)
def not_found(error):
    return jsonify({
                    "success": False,
                    "error": 404,
                    "message": "not_found"
                    }), 404

@app.errorhandler(AuthError)
def auth_error(e):
    return jsonify(e.error), e.status_code