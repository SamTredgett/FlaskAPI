'''
    Program:            Restful Flask API for handling business requests
    Author:             Samuel Tredgett - Sole developer
    Date Last Updated:  19/10/2021

    Description:
    For simplicity sake as this task isn't DB focused i've elected to use a local
    file store for the database with SQLAlchemy to interact with it. 

'''
from datetime import datetime
from random import randint
from enum import unique
from itertools import count
from re import L
from flask import Flask, render_template, request, jsonify, redirect
from flask_sqlalchemy import SQLAlchemy 
from flask_restful import Resource, Api, reqparse
from flask_marshmallow import Marshmallow
from models import Sender,Recipient, Order
from pprint import pprint
import os
import pydantic
import ast
import json


# Init App
app = Flask(__name__)
api = Api(app)


basedir = os.path.abspath(os.path.dirname(__file__))
#  Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///orders.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
#  Init db
db = SQLAlchemy(app)

#  Create database model
class SenderDb(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    street_address = db.Column(db.String, nullable=False )
    city = db.Column(db.String, nullable=False)
    country_code = db.Column(db.String, nullable=False)
    # orders = db.relationship('order', backref='owner')
    order_id = db.column(db.Integer, db.ForeignKey('orderDb.id'))
    #  Create a function to return something when we add it 
    def __repr__(self):
        return '<name %r>' % self.name

class RecipientDb(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    street_address = db.Column(db.String, nullable=False )
    city = db.Column(db.String, nullable=False)
    country_code = db.Column(db.String, nullable=False)
    # order = db.relationship('order', backref='owner')
    order_id = db.column(db.Integer, db.ForeignKey('orderDb.id'))
    #  Create a function to return something when we add it 
    def __repr__(self):
        return '<name %r>' % self.name

# class OrderDb(db.Model):
#     id = db.Column(db.Integer, primary_key=True)

#     sender = db.relationship('sent_by', backref='sender')
#     recipient = db.relationship('received_by', backref='recipient')

    # sender_id = db.Column(db.Integer, db.ForeignKey('senderDb.id'),
    #     nullable=False)
    # recipient_id = db.Column(db.Integer, db.ForeignKey('recipientDb.id'),
    #     nullable=False)
    # sender = db.relationship('SenderDb', 
    #     backref="order")



"""Index page"""
@app.route("/")
def hello_world():
    return render_template('index.html')

"""Example skeleton structure for some request"""
@app.route('/orders/', methods=['PUT'])
def put_orders():
    main_dict = dict(request.json)
    try: 

        sender = Sender(**main_dict['sender'])
        recipient = Recipient(**main_dict['recipient'])
        new_dict = {
            "sender" : sender.dict(),
            "recipient" : recipient.dict(),
            "value" : main_dict['value'],
            "despatch_date": main_dict['despatch_date'],
            "contents declaration" : main_dict['contents declaration'],
            "insurance_required" : main_dict['insurance_required'],
            "tracking_reference" : main_dict['tracking_reference']
        }
        print(new_dict)
        # Now that we actually have the information we need we can begin processing it 

        """
            Checks to make for main logic:
            1 - is insurance present?
                 - add price if it is depending on if: 
                     - UK - 1% of Value
                     - France, Germany, Netherlands, Belgium - 1.5% of value
                     - anywhere else - 4%
            2 - is package value over 10k? if so no insurance and cannot be added 
            3 - is insurance charge under 9 pounds? if so make it 9
            4 - does the tracking number already exist? if so ignore it 
            5 - don't accept orders where despatch date isn't today/tomorrow?
        """


        # order = Order()
        # sender_db = SenderDb(**sender.dict())
        # db.session.add(sender_db)
        # db.session.commit    
    except pydantic.ValidationError as e:
        print(e)
    if request.form:
        print(request.form['sender_name'])

    return redirect('/')

@app.route('/orders/<int:pk>', methods=['GET'])
def get_orders():
    pass

if __name__ == "__main__":
    app.run(debug=True)