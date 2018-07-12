from pymongo import MongoClient
from pymongo import DESCENDING

class MongoReader():
	client = MongoClient('localhost', 27017)
	ropa_db = client['ropa']
	items = ropa_db['items']

	def get_all_brands(self):
		return self.items.distinct("brand")

	def get_all_products_from_brand(self, brand):
		# item_collection = self.items.aggregate([{"$match": {'brand':brand}},{"$sample":{'size':10}}])
		item_collection = self.items.find({'brand':brand}).sort('created_at', DESCENDING)
		item_collection = self.get_only_newest_version(item_collection)
		print('Total found unique items:', len(item_collection))
		return item_collection

	def get_only_newest_version(self, item_collection):
		# Assume newest first and all from same brand
		result_collection = list()
		urls = list()
		for item in item_collection:
			if not item['url'] in urls:
				result_collection.append(item)
				urls.append(item['url'])
		return result_collection