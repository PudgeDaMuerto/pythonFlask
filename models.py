from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()


class Quests(db.Model):
    quest_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    quest_text = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f'<Quest {self.quest_id}>'


class Admin_User(db.Model):
    admin_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    login = db.Column(db.VARCHAR(100), nullable=False)
    password = db.Column(db.VARCHAR(300), nullable=False)

    def __repr__(self):
        return f'<AdminUser {self.admin_id}>'


class Answs(db.Model):
    answer_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    text = db.Column(db.Text, nullable=False)
    value = db.Column(db.Integer, nullable=False)
    quest_id = db.Column(db.Integer, db.ForeignKey("quests.quest_id"), nullable=False)

    def __repr__(self):
        return f'<Answer {self.answer_id}>'


class Results(db.Model):
    res_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.VARCHAR(300), nullable=False)
    result = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f'<Result {self.res_id}>'

