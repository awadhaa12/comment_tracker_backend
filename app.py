from bson import ObjectId
from flask import Flask, request, jsonify
from datetime import datetime
import pandas as pd
import os

from db import *
#from db import create_comment

app = Flask(__name__)

create_comment()
create_execution()


    
@app.route('/post_comment', methods=["POST"])
def post_comment():
    try: 
        data = request.json 
        comment_list = data.get('comments')
        
        for comment_data in comment_list:
            note = comment_data.get("note")
            created_by = comment_data.get("created_by")
            
        
            if not note:
                return jsonify({'success': False, 'error': 'Note field cannot be empty'})
            
        existing_comment = get_existing_comment(db1, collection1, {
            "comments": {
                "$elemMatch": {
                    "created_by": created_by,
                    "note": note
                }
            }
        })

        if existing_comment:
            return jsonify({'success': False, 'error': 'The same note cannot be inserted again for the same user'})
 
        new_comment = {
            "note": note,
            "created_by": created_by,
            "created_at": datetime.now()
        }

        res = get_existing_comment(db1,collection1,{"comments": {"$elemMatch": {"created_by": created_by}}})

        if res:
            query = {"_id": ObjectId(res["_id"])}
            result = update_existing_comment(db1,collection1,query,new_comment)
            return result
        else:
            new_data = {
                "feat_name": data.get("feat_name"),
                "test_suite": data.get("test_suite"),
                "platform": data.get("platform"),
                "comments": [new_comment]
            }
            
            result = add_comment_data(db1,collection1,new_data)

            return result
         
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}) 


# @app.route('/upload', methods=['POST'])
# def upload_excel():
    if 'file' not in request.files:
        return jsonify({"error": "No file present"})

    file = request.files['file']

    if file and file.filename.endswith('.xlsx'):
        try:
            df = pd.read_excel(file)
            data = df.to_dict(orient='records')
            result = add_excel_data(db2,collection2,data)
            return result
        
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}) 
    else:
        return jsonify({"error": "Invalid file format. Please upload an Excel file (.xlsx)"})
    

@app.route('/latest_comment/<created_by>', methods=['GET'])
def latest_comment(created_by):
    try:
        pipeline = [
            {
                "$unwind": "$comments"
            },
            {
                "$match": {
                    "comments.created_by": created_by
                }
            },
            {
                "$sort": {
                    "comments.created_at": -1
                }
            },
            {
                "$limit": 1
            }
        ]
        latest_comment = get_latest_comment(db1, collection1, pipeline)

        if latest_comment:
            return jsonify({'success': True, 'latest_comment': latest_comment})
        else:
            return jsonify({'success': False, 'message': 'No comments found for user: {}'.format(created_by)})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
    

# Function to read Excel data
def read_excel_data(file_path):
    try:
        df = pd.read_excel(file_path, engine='openpyxl')
        return df.to_dict(orient='records')
    except Exception as e:
        print(f"Error reading Excel data: {e}")
        return None
    

# Endpoint to fetch data from dtdash
@app.route('/fetch_dtdash', methods=['GET'])
def fetch_dtdash():
    script_directory = os.path.dirname(os.path.abspath(__file__))
    excel_file_path = os.path.join(script_directory, '17_14_1_Cycle1.xlsx')
    print('excel file path:----',excel_file_path)
    data = read_excel_data(excel_file_path)

    if data is not None:
         return jsonify(data)
    else:
        return jsonify({'error': 'Failed to read Excel data'}), 500
    
# API endpoint to add dtdash data to MongoDB
@app.route('/save_dtdash_data', methods=['GET'])
def save_dtdash_data():
    # Fetch data from dtdash
    dtdash_data = fetch_dtdash().json

    if dtdash_data is not None:
        # Add data to MongoDB
        result = add_excel_data(db2,collection2,dtdash_data)
        return result
    else:
        return jsonify({'error': 'Failed to fetch data from dtdash or add data to MongoDB'}), 500
    

# def get_collection_names(data):
#     return data

# @app.route('/send_collections', methods=['POST'])  
# def handle_frontend_data():
#     try:
#         data_recieved = request.json
#         #get_collection(data_recieved) 
#         print('hello py',data_recieved)
#         response_data = {'message':'Data recieved successfully!'}
#         return jsonify(response_data), 200
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500  

@app.route('/send_collections', methods=['POST'])  
def handle_frontend_data():
    try:
        print("----reached here in try")
        data_received =  request.get_json()
        print("data------",data_received)
        collection1 =  data_received['active_release_cycle']
        collection2 =  data_received['baseline_release_cycle']
        get_collection(collection1,collection2)
        # Assuming add_frontend_data is a function that adds data to the database
        print('awadhesh')
        
        if True:
            response_data = {'message': 'Data received and saved successfully!'}
            return jsonify(response_data), 200
        else:
            return jsonify({'error': 'Failed to save data to the database'}), 500

    except Exception as e:
        print("---inside except")
        return jsonify({'error': str(e)}), 500  

# @app.route('/send_collections', methods=['POST'])
# def handle_frontend_data():
#     try:
#         data_received = request.json
#         print(data_received)

#         # Extract the relevant data from the request
#         updated_comment = data_received.get("updated_comment", {})

#         # Assuming that "updated_comment" contains the necessary data
#         # Update the comment in the MongoDB collection
#         result = update_existing_comment(db1, collection1, {"_id": ObjectId(updated_comment["_id"])}, updated_comment)

#         if result:
#             response_data = {'message': 'Updated comment saved successfully!'}
#             return jsonify(response_data), 200
#         else:
#             return jsonify({'error': 'Failed to save updated comment to the database'}), 500

#     except Exception as e:
#         return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)



