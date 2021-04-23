class UniqueDBObjectError(Exception):
    def __init__(self, search_filter, obj_count, db_class):
        # self.search_filter = search_filter
        # self.obj_count = obj_count
        # self.db_class = db_class

        if obj_count == 0:
            self.message = f'Failed to get object of table "{db_class}" with filter: "{search_filter}"'
        else:
            self.message = f'Failed to get unique object of table "{db_class}" with filter: "{search_filter}". ' \
                        f'Found objects: {obj_count}'

    def __str__(self):
        return self.message
