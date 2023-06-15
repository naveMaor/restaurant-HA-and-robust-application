from flask import Flask, jsonify, request
import requests
import json
import pymongo
app = Flask(__name__)

dishCounter = 0

client = pymongo.MongoClient("mongodb://mongo:27017/")
db = client["meal_diets"]

meals_collection = db["meals"]
if meals_collection.find_one({"_id": 0}) is None:
    meals_collection.insert_one({"_id": 0, "curr_key": 0})
    print('inserted key into the collection')

dishes_collection = db["dishes"]
if dishes_collection.find_one({"_id": 0}) is None:
    dishes_collection.insert_one({"_id": 0, "curr_key": 0})
    print('inserted key into the collection')

def getCurrDishId():
    docID = {"_id": 0}
    curr_key = dishes_collection.find_one(docID)["curr_key"] + 1
    dishes_collection.update_one(docID, {"$set": {"curr_key": curr_key}})
    return str(curr_key)


def getCurrMealId():
    docID = {"_id": 0}
    curr_key = meals_collection.find_one(docID)["curr_key"] + 1
    meals_collection.update_one(docID, {"$set": {"curr_key": curr_key}})
    return str(curr_key)


@app.route('/dishes', methods=['POST'])
def add_dish():
    content_type = request.headers.get('Content-Type')
    if content_type != 'application/json':
        return jsonify(0), 415
    if 'name' not in request.json:
        return jsonify(-1), 400
    name = request.json['name']
    if name == '':
        return jsonify(-1), 400
    dish = dishes_collection.find_one({"name": name})
    if dish:
        return jsonify(-2), 400

    api_call = call_api_ninjas(name)
    if api_call == -3 or api_call == -4:
        return jsonify(api_call), 400

    dishes_collection.insert_one(api_call)
    return jsonify(api_call['_id']), 201


@app.route('/meals', methods=['POST'])
def create_meal():

    if request.content_type != 'application/json':
        return jsonify(0), 415

    data = request.json
    if 'name' not in data or 'appetizer' not in data or 'main' not in data or 'dessert' not in data:
        return jsonify(-1), 400

    meal = meals_collection.find_one({"name": data['name']})
    if meal:
        return jsonify(-2), 400

    appetizer = dishes_collection.find_one({"_id": int(data["appetizer"])})
    main = dishes_collection.find_one({"_id": int(data["main"])})
    dessert = dishes_collection.find_one({"_id": int(data["dessert"])})
    if appetizer is None or main is None or dessert is None:
        return jsonify(-5), 404

    meal_cal = appetizer['cal'] + main['cal'] + dessert['cal']
    meal_size = appetizer['size'] + main['size'] + dessert['size']
    meal_sodium = appetizer['sodium'] + main['sodium'] + dessert['sodium']
    meal_sugar = appetizer['sugar'] + main['sugar'] + dessert['sugar']

    docID = {"_id": 0}
    curr_key = meals_collection.find_one(docID)["curr_key"] + 1
    meals_collection.update_one(docID, {"$set": {"curr_key": curr_key}})
    meals_collection.insert_one({
        "name": data['name'], "_id": curr_key, "appetizer": data['appetizer'], "main": data['main'], "dessert": data['dessert'],
        "cal": meal_cal,
        "size": meal_size,
        "sodium": meal_sodium,
        "sugar": meal_sugar})

    return jsonify(curr_key), 201


@app.route('/meals/<int:meal_id>', methods=['PUT'])
def update_meal(meal_id):
    json_string = json.dumps(request.get_json(), indent=4)
    data = json.loads(json_string)
    try:
        meal_name = data["name"]
        appetizer = int(data["appetizer"])
        main = int(data["main"])
        dessert = int(data["dessert"])
    except:
        return jsonify(-1), 400

    meal = meals_collection.find_one({"name": meal_name})
    if meal:
        return jsonify(-2), 400
    meal_obj = {}
    meal__id = [appetizer, main, dessert]
    match = 0
    for i in meal__id:
        dish = dishes_collection.find_one({'_id': i})
        if dish is not None:
            meal_obj[i] = dish
            match += 1

    if match != 3:
        return jsonify(-5), 400

    meal = {"name": meal_name, "_id": meal_id, "appetizer": appetizer, "main": main, "dessert": dessert,
            "cal": meal_obj[appetizer]["cal"] + meal_obj[main]["cal"] + meal_obj[dessert]["cal"],
            "size": meal_obj[appetizer]["size"] + meal_obj[main]["size"] + meal_obj[dessert]["size"],
            "sodium": meal_obj[appetizer]["sodium"] + meal_obj[main]["sodium"] + meal_obj[dessert]["sodium"],
            "sugar": meal_obj[appetizer]["sugar"] + meal_obj[main]["sugar"] + meal_obj[dessert]["sugar"]}
    result = meals_collection.update_one({'_id': meal_id}, {'$set': meal})

    if result.modified_count > 0:
        return jsonify(meal_id), 200
    else:
        return jsonify(-2), 404


@app.route('/dishes', methods=['GET'])
def get_dishes():
    cursor = dishes_collection.find({"_id": {"$gte": 1}})
    cursor.rewind()
    cursor = list(cursor)
    for doc in cursor:
        doc["ID"] = doc["_id"]
        del doc["_id"]
    return cursor, 200


@app.route('/dishes/<int:dish_id>', methods=['GET'])
def get_dish_by_id(dish_id):
    dishes = dishes_collection.find_one({"_id": dish_id})
    if dishes is None:
        return jsonify(-5), 404
    else:
        dishes["ID"] = dishes["_id"]
        del dishes["_id"]
        return dishes, 200


@app.route('/dishes/<string:dish_name>', methods=['GET'])
def get_dish_by_name(dish_name):
    dishes = dishes_collection.find_one({"name": dish_name})
    if dishes is None:
        return jsonify(-5), 404
    else:
        dishes["ID"] = dishes["_id"]
        del dishes["_id"]
        return dishes, 200


@app.route('/meals', methods=['GET'])
def get_all_meals():
    query_params = request.args
    if len(query_params) == 0:
        meals = list(meals_collection.find({"_id": {"$gte": 1}}))
        return meals, 200

    url = 'http://172.17.0.1:5002/diets/' + str(query_params['diet'])
    print(url)
    response = requests.get(url)
    print(response)

    response_data = response.json()
    if response.status_code == 404:
        return jsonify(-5), 400

    meals = list(meals_collection.find({"_id": {"$gte": 1}}))
    res = []

    for meal in meals:
        if meal["cal"] <= response_data["cal"] and meal["sodium"] <= response_data["sodium"] and meal["sugar"] <= \
                response_data["sugar"]:
            res.append(meal)

    return res, 200


@app.route('/meals/<int:meal_id>', methods=['GET'])
def get_meal_by_id(meal_id):
    meal = meals_collection.find_one({"_id": meal_id})
    if meal is None:
        return jsonify(-5), 404
    else:
        meal["ID"] = meal["_id"]
        del meal["_id"]
        return meal, 200


@app.route('/meals/<string:meal_name>', methods=['GET'])
def get_meal_by_name(meal_name):
    meal = meals_collection.find_one({"name": meal_name})
    if meal is None:
        return jsonify(-5), 404
    else:
        meal["ID"] = meal["_id"]
        del meal["_id"]
        return meal, 200


@app.route('/meals/<int:meal_id>', methods=['DELETE'])
def delete_meal_by_id(meal_id):
    result = meals_collection.delete_one({'_id': meal_id})

    if result.deleted_count > 0:
        return jsonify(meal_id), 200
    else:
        return jsonify(-5), 404


@app.route('/meals/<string:meal_name>', methods=['DELETE'])
def delete_meal_by_name(meal_name):
    result = meals_collection.delete_one({'name': meal_name})

    if result.deleted_count > 0:
        return jsonify(meal_name), 200
    else:
        return jsonify(-5), 404


@app.route('/dishes/<int:dish_id>', methods=['DELETE'])
def delete_dish_by_id(dish_id):
    dish = dishes_collection.find_one({'_id': dish_id})
    if dish:
        dishes_collection.delete_one({'_id': dish_id})
        return jsonify(dish_id), 200
    else:
        return jsonify(-5), 404


@app.route('/dishes/<string:dish_name>', methods=['DELETE'])
def delete_dish_by_name(dish_name):
    dish = dishes_collection.find_one({'name': dish_name})
    if dish is None:
        return jsonify(-5), 404
    else:
        dishes_collection.delete_one({'name': dish_name})
        return jsonify(dish_name), 200


@app.route('/dishes', methods=['DELETE'])
def delete_dishes():
    return jsonify(-1), 400


@app.route('/meals', methods=['DELETE'])
def delete_meals():
    return jsonify(-1), 400


def call_api_ninjas(dish_name):
    import requests
    url = "https://api.api-ninjas.com/v1/nutrition"
    querystring = {"query": dish_name}
    headers = {
        'x-api-key': "QnxHXQzWaSixiioKDlLGSw==JhgDyvuOvc9up9Xj",
    }
    response = requests.request("GET", url, headers=headers, params=querystring)

    if response.status_code != requests.codes.ok:
        return -4
    if response.text == '[]':
        return -3

    total_calories = 0
    total_serving_size_g = 0
    total_sodium_mg = 0
    total_sugar_g = 0

    for dish in response.json():
        total_calories += dish['calories']
        total_serving_size_g += dish['serving_size_g']
        total_sodium_mg += dish['sodium_mg']
        total_sugar_g += dish['sugar_g']

    curr_id = getCurrDishId()

    dish = {'name': dish_name
        , '_id': int(curr_id)
        , 'cal': total_calories
        , 'size': total_serving_size_g
        , 'sodium': total_sodium_mg
        , 'sugar': total_sugar_g
            }
    return dish


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
