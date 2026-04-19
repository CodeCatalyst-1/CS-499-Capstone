from pymongo import MongoClient
from pymongo.errors import PyMongoError
from urllib.parse import quote_plus

class AnimalShelter:
    def __init__(self, user, passwd, host='nv-desktop-services.apporto.com', port=30091, db='AAC', collection='animals'):
        try:
            user_enc = quote_plus(user)
            passwd_enc = quote_plus(passwd)
            uri = f"mongodb://{user_enc}:{passwd_enc}@{host}:{port}/{db}?authSource=admin"
            self.client = MongoClient(uri)
            self.client.admin.command('ismaster')  # Test connection
            self.database = self.client[db]
            self.collection = self.database[collection]
            print(f" Connected to MongoDB as user '{user}' successfully.")
        except PyMongoError as e:
            print(f" Connection or Authentication failed: {e}")
            self.client = None

    def create(self, data):
        if not self.client:
            return False
        try:
            result = self.collection.insert_one(data)
            return result.acknowledged
        except Exception as e:
            print(f" Create failed: {e}")
            return False

    def read(self, query):
        if not self.client:
            return []
        try:
            return list(self.collection.find(query))
        except Exception as e:
            print(f" Read failed: {e}")
            return []

    def update(self, query, update_data):
        if not self.client:
            return 0
        try:
            result = self.collection.update_many(query, {'$set': update_data})
            return result.modified_count
        except Exception as e:
            print(f" Update failed: {e}")
            return 0

    def delete(self, query):
        if not self.client:
            return 0
        try:
            result = self.collection.delete_many(query)
            return result.deleted_count
        except Exception as e:
            print(f" Delete failed: {e}")
            return 0

