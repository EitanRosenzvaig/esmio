from pymongo import MongoClient


class MongoReader():
	client = MongoClient('localhost', 27017)
	ropa_db = client['ropa']
	items = ropa_db['items']

	def get_all_brands(self):
		return self.items.distinct("brand")

	def get_all_products_from_brand(self, brand):
		return self.items.aggregate([{"$match": {'brand':brand}},{"$sample":{'size':5}}])
