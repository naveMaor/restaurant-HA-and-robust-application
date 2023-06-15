from flask import Flask, request, jsonify
import pymongo

app = Flask(__name__)

diets = []

client = pymongo.MongoClient("mongodb://mongo:27017/")

db = client["meal_diets"]
collection = db["diets"]
if collection.find_one({"_id": 0}) is None:
    collection.insert_one({"_id": 0, "curr_key": 0})
    print("Inserted document containing cur_key with _id == 0 into the collection")


@app.route('/diets', methods=['GET'])
def get_all_diets():
    cursor = collection.find({"_id": {"$gte": 1}}, {'_id': False})
    cursor.rewind()
    cursor_list = list(cursor)
    return cursor_list, 200


@app.route('/diets/<string:name>', methods=['GET'])
def get_diet_by_name(name):
    res = collection.find_one({"name": name}, {"_id": 0})
    if res is None:
        return jsonify(f'Diet {name} not found'), 404
    else:
        return res, 200


@app.route('/diets', methods=['POST'])
def post_diets_from_user():
    if request.content_type != 'application/json':
        return jsonify('POST expects content type to be application/json'), 415

    data = request.json
    if 'name' not in data or 'cal' not in data or 'sodium' not in data or 'sugar' not in data:
        return jsonify('Incorrect POST format'), 422
    try:
        name = data['name']
        calories = data['cal']
        sodium = data['sodium']
        sugar = data['sugar']
    except:
        return jsonify(-1), 422

    diet = collection.find_one({"name": name})
    if diet is not None:
        return jsonify(f'Diet with {name} already exists'), 422
    id = {"_id": 0}
    curr_key = collection.find_one(id)["curr_key"] + 1
    collection.update_one(id, {"$set": {"curr_key": curr_key}})
    collection.insert_one({"_id": curr_key, "name": name,
                           "cal": calories, "sodium": sodium, "sugar": sugar})
    return jsonify(f'Diet {name} created successfully'), 201


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
