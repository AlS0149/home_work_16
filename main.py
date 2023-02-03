import json
from _datetime import datetime
from time import strptime

from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy

import data

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JSON_AS_ASCII'] = False
db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    age = db.Column(db.Integer)
    email = db.Column(db.String(200))
    role = db.Column(db.String(100))
    phone = db.Column(db.String(100))

    def to_dict(self):
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'age': self.age,
            'email': self.email,
            'role': self.role,
            'phone': self.phone
        }


class Order(db.Model):
    __tablename__ = 'order'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    description = db.Column(db.String)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    address = db.Column(db.String(200))
    price = db.Column(db.Integer)
    customer_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    executor_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'address': self.address,
            'price': self.price,
            'customer_id': self.customer_id,
            'executor_id': self.executor_id
        }


class Offer(db.Model):
    __tablename__ = 'offer'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'))
    executor_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def to_dict(self):
        return {
            'id': self.id,
            'order_id': self.order_id,
            'executor_id': self.executor_id
        }


with app.app_context():
    db.create_all()

    for user_ in data.users:
        new_user = User(**user_)
        db.session.add(new_user)

    for order_ in data.orders:
        order_['start_date'] = datetime.strptime(order_['start_date'], '%m/%d/%Y').date()
        order_['end_date'] = datetime.strptime(order_['end_date'], '%m/%d/%Y').date()
        new_order = Order(**order_)
        db.session.add(new_order)

    for offer_ in data.offers:
        new_offer = Offer(**offer_)
        db.session.add(new_offer)

    db.session.commit()  # Подтверждаем действия.


@app.route('/users', methods=['GET', 'POST'])
def users():
    if request.method == 'GET':

        raw_users = User.query.all()
        result = [raw_user.to_dict() for raw_user in raw_users]
        return json.dumps(result)
    elif request.method == 'POST':

        user_data = json.loads(request.data)
        db.session.add(User(**user_data))
        db.session.commit()
        return 'Ok'


@app.route('/users/<uid>', methods=['GET', 'PUT', 'DELETE'])
def user(uid):
    if request.method == 'GET':
        user = User.query.get(uid)
        result = user.to_dict()
        return json.dumps(result)
    elif request.method == 'DELETE':
        user = User.query.get(uid)
        db.session.delete(user)
        db.session.commit()
        return 'Ok'
    elif request.method == 'PUT':
        user_data = json.loads(request.data)
        user = User.query.get(uid)
        user.first_name = user_data['first_name']
        user.last_name = user_data['last_name']
        user.age = user_data['age']
        user.email = user_data['email']
        user.role = user_data['role']
        user.phone = user_data['phone']
        db.session.add(user)
        db.session.commit()
        return 'Ok'


@app.route('/orders', methods=['GET', 'POST'])
def orders():
    if request.method == 'GET':

        raw_orders = Order.query.all()
        result = []
        for raw_order in raw_orders:
            order_dict = raw_order.to_dict()
            order_dict['start_date'] = str(order_dict['start_date'])
            order_dict['end_date'] = str(order_dict['end_date'])
            result.append(order_dict)
        return json.dumps(result)
    elif request.method == 'POST':

        order_data = json.loads(request.data)
        order_data['start_date'] = datetime.strptime(order_data['start_date'], '%Y-%m-%d').date()

        order_data['end_date'] = datetime.strptime(order_data['end_date'], '%Y-%m-%d').date()

        order = Order(
            name=order_data['name'],
            description=order_data['description'],
            start_date=order_data['start_date'],
            end_date=order_data['end_date'],
            price=order_data['price'],
            customer_id=order_data['customer_id'],
            executor_id=order_data['executor_id']
        )
        db.session.add(order)
        db.session.commit()

        return 'Ok'


@app.route('/orders/<oid>', methods=['GET', 'PUT', 'DELETE'])
def order(oid):
    if request.method == 'GET':

        result = Order.query.get(oid)
        order = result.to_dict()
        order['start_date'] = str(order['start_date'])
        order['end_date'] = str(order['end_date'])
        return json.dumps(order)
    elif request.method == 'DELETE':

        order = Order.query.get(oid)
        db.session.delete(order)
        db.session.commit()
        return 'Ok'
    elif request.method == 'PUT':

        order_data = json.loads(request.data)
        order_data['start_date'] = datetime.strptime(order_data['start_date'], '%Y-%m-%d').date()
        order_data['end_date'] = datetime.strptime(order_data['end_date'], '%Y-%m-%d').date()

        order = Order.query.get(oid)
        order.name = order_data['name']
        order.description = order_data['description']
        order.start_date = order_data['start_date']
        order.end_date = order_data['end_date']
        order.price = order_data['price']
        order.customer_id = order_data['customer_id']
        order.executor_id = order_data['executor_id']
        db.session.add(order)
        db.session.commit()
        return 'Ok'


@app.route('/offers', methods=['GET', 'POST'])
def offers():
    if request.method == 'GET':

        raw_offers = Offer.query.all()
        result = [raw_offer.to_dict() for raw_offer in raw_offers]
        return json.dumps(result)
    elif request.method == 'POST':

        offer_data = json.loads(request.data)
        db.session.add(Offer(**offer_data))
        db.session.commit()
        return 'Ok'


@app.route('/offers/<ofid>', methods=['GET', 'PUT', 'DELETE'])
def offer(ofid):
    if request.method == 'GET':

        offer = Offer.query.get(ofid)
        result = offer.to_dict()
        return json.dumps(result)
    elif request.method == 'DELETE':

        offer = Offer.query.get(ofid)
        db.session.delete(offer)
        db.session.commit()
        return 'Ok'
    elif request.method == 'PUT':

        offer_data = json.loads(request.data)
        offer = Offer.query.get(ofid)
        offer.order_id = offer_data['order_id']
        offer.executor_id = offer_data['executor_id']
        db.session.add(offer)
        db.session.commit()
        return 'Ok'


if __name__ == "__main__":
    app.run()
