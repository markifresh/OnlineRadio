from flask import abort, current_app


class BasicCustomException(Exception):
    def __init__(self, message):
        self.message = message

        if current_app:
            abort(400, self.message)

    def __str__(self):
        return self.message


class UniqueDBObjectError(BasicCustomException):
    def __init__(self, search_filter, obj_count, db_class):
        if obj_count == 0:
            message = f'Failed to get object of table "{db_class}" with filter: "{search_filter}"'

        else:
            message = f'Failed to get unique object of table "{db_class}" with filter: "{search_filter}". ' \
                        f'Found objects: {obj_count}'

        super().__init__(message)
