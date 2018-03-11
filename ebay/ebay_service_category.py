from ebay.ebay_service import EbayService
from utils.log import get_logger


logger = get_logger(__name__)


class EbayServiceCategory(EbayService):

    def __init__(self):
        super().__init__()

    def categories(self, parent_id: str=None):
        callData = {
            'DetailLevel': 'ReturnAll',
            'CategorySiteID': 101,
            'LevelLimit': 4,
        }
        if not(parent_id is None):
            callData['CategoryParent'] = int(parent_id)
        response = self._api.execute('GetCategories', callData)
        categories = response.reply.CategoryArray.Category
        category_parents = {}
        category_ids = {}
        category_leaf = {}

        for category in categories:
            category_parents[category.CategoryParentID] = category
            category_ids[category.CategoryID] = category
            if bool(category.get('LeafCategory')) is True:
                category_leaf[category.CategoryID] = category

        if callData.get('CategoryParent') is None:
            first_level = 1
        else:
            first_level = int(category_ids.get(str(parent_id)).CategoryLevel)

        category_result = []
        for category_key in category_leaf:
            category = category_leaf.get(category_key)
            category_current = []
            category_current.append(self.ebayobject_to_dict(category))
            if (category.CategoryLevel is None):
                logger.error('No Category Level defined for [%s]' % (category))
            category_level = int(category.CategoryLevel)
            for i in range(category_level - first_level):
                parent_id = category_current[len(
                    category_current) - 1].get('CategoryParentID')
                cat_by_id = category_ids.get(parent_id)
                category_current.append(self.ebayobject_to_dict(cat_by_id))
            # category_current.append(self.object_to_dict(category_ids.get(parent_id)))
            reverse_category = category_current[::-1]
            category_path = ""
            for i, cat in enumerate(reverse_category):
                if i == 0:
                    category_path = cat.get('CategoryName')
                else:
                    category_path = category_path + \
                        " > " + cat.get('CategoryName')
            category_result.append({
                'categoryResult': reverse_category,
                'categoryPath': category_path
            })

        return category_result

    def _category_to_dict(self, cat_by_id):
        return {
            'CategoryParentID': cat_by_id.CategoryParentID,
            'CategoryID': cat_by_id.CategoryID,
            'CategoryLevel': cat_by_id.CategoryLevel,
            'CategoryName': cat_by_id.CategoryName
        }


ebay_service_category = EbayServiceCategory()
logger.info('Ebay service [category] started')
