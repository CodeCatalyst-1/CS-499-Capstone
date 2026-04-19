# crud_original.py
# Original CRUD module for the Grazioso Salvare Animal Shelter Dashboard
# Developed during CS 340: Client/Server Development
# Author: Ethan Chapman
#
# This module provides a basic Create, Read, Update, Delete (CRUD) interface
# for interacting with the Austin Animal Center (AAC) MongoDB collection.
# It uses PyMongo to connect to a MongoDB instance and perform operations
# on a specified database and collection.

from pymongo import MongoClient
from pymongo.errors import PyMongoError
from urllib.parse import quote_plus

class AnimalShelter:
    """CRUD operations class for the AAC animals collection in MongoDB."""

    def __init__(self, user, passwd, host='nv-desktop-services.apporto.com', port=30091, db='AAC', collection='animals'):
        """
        Initialize the AnimalShelter connection to MongoDB.

        Parameters:
            user (str): MongoDB username for authentication
            passwd (str): MongoDB password for authentication
            host (str): MongoDB server hostname
            port (int): MongoDB server port number
            db (str): Name of the database to connect to
            collection (str): Name of the collection to use
        """
        try:
            # URL-encode the username and password to handle special characters
            user_enc = quote_plus(user)
            passwd_enc = quote_plus(passwd)

            # Build the MongoDB connection URI with authentication source
            uri = f"mongodb://{user_enc}:{passwd_enc}@{host}:{port}/{db}?authSource=admin"

            # Create the MongoDB client connection
            self.client = MongoClient(uri)

            # Test the connection by sending the ismaster command
            self.client.admin.command('ismaster')  # Test connection

            # Store references to the database and collection for use in CRUD methods
            self.database = self.client[db]
            self.collection = self.database[collection]
            print(f" Connected to MongoDB as user '{user}' successfully.")
        except PyMongoError as e:
            # If connection fails, print the error and set client to None
            # so CRUD methods can check before attempting operations
            print(f" Connection or Authentication failed: {e}")
            self.client = None

    def create(self, data):
        """
        Insert a single document into the collection.

        Parameters:
            data (dict): The document to insert into the collection

        Returns:
            bool: True if the insertion was acknowledged, False otherwise
        """
        # Check that the client connection exists before attempting the operation
        if not self.client:
            return False
        try:
            # Insert the document and return whether MongoDB acknowledged the write
            result = self.collection.insert_one(data)
            return result.acknowledged
        except Exception as e:
            print(f" Create failed: {e}")
            return False

    def read(self, query):
        """
        Retrieve documents from the collection matching the given query.

        Parameters:
            query (dict): MongoDB query filter to match documents

        Returns:
            list: A list of matching documents, or an empty list on failure
        """
        # Check that the client connection exists before attempting the operation
        if not self.client:
            return []
        try:
            # Execute the find query and convert the cursor to a list of documents
            return list(self.collection.find(query))
        except Exception as e:
            print(f" Read failed: {e}")
            return []

    def update(self, query, update_data):
        """
        Update all documents matching the query with the provided data.

        Parameters:
            query (dict): MongoDB query filter to select documents to update
            update_data (dict): Fields and values to update using the $set operator

        Returns:
            int: The number of documents that were modified
        """
        # Check that the client connection exists before attempting the operation
        if not self.client:
            return 0
        try:
            # Use update_many with $set to modify all matching documents
            result = self.collection.update_many(query, {'$set': update_data})
            return result.modified_count
        except Exception as e:
            print(f" Update failed: {e}")
            return 0

    def delete(self, query):
        """
        Delete all documents matching the given query from the collection.

        Parameters:
            query (dict): MongoDB query filter to select documents to delete

        Returns:
            int: The number of documents that were deleted
        """
        # Check that the client connection exists before attempting the operation
        if not self.client:
            return 0
        try:
            # Delete all documents that match the query filter
            result = self.collection.delete_many(query)
            return result.deleted_count
        except Exception as e:
            print(f" Delete failed: {e}")
            return 0
