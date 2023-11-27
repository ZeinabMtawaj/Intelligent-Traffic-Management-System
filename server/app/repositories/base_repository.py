class BaseRepository:
    def __init__(self, collection):
        self.collection = collection

    def insert(self, data):
        return self.collection.insert_one(data).inserted_id

    def get_all_by_item(self, item):
        return list(self.collection.find(item))

    def get_by_item(self, item):
        return self.collection.find_one(item)

    def update_by_id(self, item_id, updated_data):
        result = self.collection.update_one({'id': item_id}, {'$set': updated_data})
        return result.modified_count


    def delete_by_id(self, item_id):
        result = self.collection.delete_one({'id': item_id})
        return result.deleted_count

    def delete_documents(self, item):
        result = self.collection.delete_many(item)
        return result.deleted_count

    def insert_documents(self, item):
        result = self.collection.insert_many(item)
        return result

    def replace(self, item, new_data):
        result = self.collection.replace_one(item, new_data)
        return result.modified_count


