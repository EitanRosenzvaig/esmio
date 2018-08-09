from pymongo import MongoClient
from pymongo import DESCENDING
import logging

logger = logging.getLogger('import_logger')

class MongoReader():
	client = MongoClient('localhost', 27017)
	ropa_db = client['ropa']
	items = ropa_db['items']

	def get_all_brands(self):
		return self.items.distinct("brand")

	def get_all_valid_products_from_brand(self, brand):
		# item_collection = self.items.aggregate([{"$match": {'brand':brand}},{"$sample":{'size':10}}])
		item_collection = self.items.find({'brand':brand}).sort('created_at', DESCENDING)
		item_collection = self.get_only_newest_version(item_collection)
		item_collection = self.remove_invalid_items(item_collection)
		logger.info('Total found unique items:: %s', len(item_collection))
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

	def remove_invalid_items(self, item_collection):
		result_collection = list()
		for item in item_collection:
			if self.item_is_valid(item):
				result_collection.append(item)
		return result_collection

	def item_is_valid(self, item):
		try:
			is_valid = len(item['sizes']) > 0 and len(item['image_urls']) > 0
			return is_valid
		except Exception:
			if 'url' in item:
				logger.info('Item %s is invalid', item['url'])
			else:
				logger.info('Invalid item without URL')
			return False