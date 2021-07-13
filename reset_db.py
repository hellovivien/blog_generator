import pymongo

client = pymongo.MongoClient("adresse de ta base mongodb: https://www.mongodb.com/try")
db = client.blog

def reset_db(exclude_collections = []):
    for table_name in db.list_collection_names():
        if table_name not in exclude_collections:
            table = db[table_name]
            table.drop()
            print('{} has been dropped'.format(table_name))
    print('reset done!')

reset_db()
