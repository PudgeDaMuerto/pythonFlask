class UserLogin:
    def fromDB(self, table, user_id):
        res = table.query.all()
        self.__user = res[int(user_id)-1]
        return self

    def create(self, user):
        self.__user = user
        return self

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.__user.admin_id)
