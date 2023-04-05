import pymongo


class DatabaseClient:
    """

    """
    def __init__(self, conn_url: str, db_name: str):
        """Create or retrieve a collection from a db connection

          Parameters:
              conn_url: connection used to create database client connection
              db_name: name of the database

          Return: database client connection
          """
        self.__client = pymongo.MongoClient(conn_url)
        self.db_conn = self.__client[db_name]

    def set_database_conn(self, db_name: str):
        """Create or retrieve a collection from a db connection

         Parameters:
             db_name: name of database to be retrieved or created

         Return: database connection
         """
        # Create a database object. If the db does not exist, it will be
        # created when content is added
        self.db_conn = self.__client[db_name]

    def get_collection_conn(self, coll_name: str):
        """Create or retrieve a collection from a db connection

        Parameters:
            coll_name: name of collection to be retrieved or created

        Return: collection connection
        """
        # Create collection
        return self.db_conn[coll_name]

    @staticmethod
    def upsert_items(collection_obj, items: list) -> None:
        """Insert or update items into collection

        Parameters:
            collection_obj: collection object where data will be inserted
            items: list of items to be added to the collection

        Returns:
        """
        for _ in items:
            collection_obj.update_one(_["key"], {"$set": _["updates"]}, upsert=True)

    @staticmethod
    def insert_item(collection_obj, item: dict) -> None:
        """Insert or update items into collection

        Parameters:
            collection_obj: collection object where data will be inserted
            item: items to be added to the collection

        Returns:
        """
        collection_obj.insert_one(item)

    @staticmethod
    def find_items(collection_obj, items: dict = None) -> list:
        """Insert or update items into collection

        Parameters:
            collection_obj: collection object where data will be inserted
            items: items to be found to the collection

        Returns: list of items found in db
        """
        return collection_obj.find(items)

    @staticmethod
    def aggregate_items(collection_obj, pipeline: list = None) -> list:
        """Insert or update items into collection

        Parameters:
            collection_obj: collection object where data will be inserted
            pipeline: list of items to aggregate into the collection

        Returns: list of items found in db
        """
        return collection_obj.aggregate(pipeline)
