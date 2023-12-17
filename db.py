from pymongo import MongoClient
from pymongo.operations import IndexModel

url = "mongodb://localhost:27017/"
client = MongoClient(url)

db1 = client["comment"]
db2 = client["execution"]


def create_collection(db, collection_name):
    if collection_name not in db.list_collection_names():
        db.create_collection(collection_name)
        print(f"Collection '{collection_name}' created successfully")
    else:
        print(f"Collection '{collection_name}' already exists")

collections_to_create = ['17.14.1_cycle_1', '17.14.1_cycle_1']
collection1 = collections_to_create[0]
collection2 = collections_to_create[1]


index_keys = [("Feat_Name", 1), ("Suite", 1), ("Platform", 1)]
index_model = IndexModel(index_keys, unique=True)
db2[collection2].create_indexes([index_model])



def create_comment():
    return create_collection(db1,collection1)

def create_execution():
    return create_collection(db2,collection2)


def add_comment_data(db, collection_name, data):
    collection = db[collection_name]
    collection.insert_one(data)
    return "Data added successfully"

def get_existing_comment(db,collection_name,query):
    collection = db[collection_name]
    res = collection.find_one(query)
    return res

def update_existing_comment(db, collection_name, query, new_comment):
    collection = db[collection_name]
    update = {
        "$addToSet": {"comments": new_comment}
    }
    collection.find_one_and_update(query, update, return_document=True)
    return "Data updated successfully"

def add_excel_data(db,collection_name,data):
    collection = db[collection_name]
    collection.insert_many(data)
    return "Excel data added successfully"


def get_latest_comment(db, collection, pipeline):
    try:
        result = db[collection].aggregate(pipeline)

        latest_comment = list(result)

        if latest_comment:
            latest_comment[0]['_id'] = str(latest_comment[0]['_id'])
            return latest_comment[0]
        else:
            return None

    except Exception as e:
        return {'success': False, 'error': str(e)}






