class UserLogin:
    def create(self, user):
        self.__user = user
        return self

    def fromDB(self, user_id, db):
        self.__user = db.get_customer_by_id(user_id)
        return self

    def get_id(self):
        return str(self.__user['id'])

    def get_name(self):
        return self.__user['name']

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False
