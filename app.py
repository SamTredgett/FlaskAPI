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
from sqlalchemy import DateTime
from sqlalchemy.sql import func
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

class OrderDb(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    sender = db.Column(db.Integer,db.ForeignKey('senderDb.id'))
    recipient = db.Column(db.Integer, db.ForeignKey('recipientDb.id'))


    value = db.Column(db.Float, nullable=False)
    despatch_date = db.Column(db.String, nullable=False)
    contents_declaration = db.Column(db.String, nullable=False)
    insurance_required = db.Column(db.Boolean, nullable=False)
    tracking_reference = db.Column(db.String, nullable=False, unique=True)

    #  Holding on to this in case i messed up the key relationships
    # sender_id = db.Column(db.Integer, db.ForeignKey('senderDb.id'),
    #     nullable=False)
    # recipient_id = db.Column(db.Integer, db.ForeignKey('recipientDb.id'),
    #     nullable=False)
    # sender = db.relationship('SenderDb', 
    #     backref="order")

#  Create database model
class SenderDb(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    street_address = db.Column(db.String, nullable=False )
    city = db.Column(db.String, nullable=False)
    country_code = db.Column(db.String, nullable=False)
    orders = db.relationship('OrderDb' , db.ForeignKey('orderDb.id'),backref='owner')
    # order_id = db.column(db.Integer, db.ForeignKey('orderDb.id'))
    #  Create a function to return something when we add it 
    def __repr__(self):
        return '<name %r>' % self.name

class RecipientDb(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    street_address = db.Column(db.String, nullable=False )
    city = db.Column(db.String, nullable=False)
    country_code = db.Column(db.String, nullable=False)
    order = db.relationship('OrderDb', backref='owner')
    # orders = db.column(db.Integer, db.ForeignKey('orderDb.id'))
    #  Create a function to return something when we add it 
    def __repr__(self):
        return '<name %r>' % self.name





"""Index page"""
@app.route("/")
def hello_world():
    return render_template('index.html')

"""Example skeleton structure for some request"""
@app.route('/orders', methods=['PUT'])
def put_orders():
    main_dict = dict(request.json)
    try: 
        # Validate the sender and recipient objects against the pydantic models
        sender = Sender(**main_dict['sender'])
        recipient = Recipient(**main_dict['recipient'])
        new_dict = {
            "sender" : sender.dict(),
            "recipient" : recipient.dict(),
            "value" : main_dict['value'],
            "despatch_date": main_dict['despatch_date'],
            "contents declaration" : main_dict['contents declaration'],
            "insurance_required" : bool(main_dict['insurance_required']),
            "tracking_reference" : main_dict['tracking_reference']
        }
        new_order = Order(**new_dict)
        print(new_dict)

        #  Insurance Checks
        # Is it too expensive for insurance and shipping?
        if float(new_dict['value']) >= 10000:
            insurance_required = False
            return 'Item too valuable, cannot be shipped'
            
        # Did they want to insure the package?
        if new_dict['insurance_required']: 
            insurance_required=True
            # Where is it going to?
            if new_dict['recipient']['country_code'].lower() == 'gb':
                total_insurance_cost = float(new_dict['value']) * 1.01
            if new_dict['recipient']['country_code'].lower() in ['de', 'fr', 'be', 'nl']:
                total_insurance_cost = float(new_dict['value']) * 1.015
            else:
                total_insurance_cost = float(new_dict['value']) * 1.04

        if total_insurance_cost < 9:
            total_insurance_cost = 9
        
        # Calculate the Insurance Premium Tax
        ipt_included_in_charge =  total_insurance_cost * 0.12

        





        #    Check to see if date is outside of today/tomorrow

        try:
            parsed_time =  datetime.strptime(new_dict['despatch_date'], '%Y-%m-%d')
            date = datetime.today()
            delta = date-parsed_time
            if delta.days > 1:
                print("Order too far in the future! Please choose a date that is today/tomorrow.")
                return redirect('/')
        except ValueError as e:
            print("Please structure date requests as year/month/date - like this: 2000-12-31")
            print(e)
            redirect('/')
        


        """
            Checks to make for main logic:
            4 - does the tracking number already exist? if so ignore it 
        """
        #  time to query database for the order tracking reference
        # tracking_ref = OrderDb.query.filter_by(tracking_reference = new_dict['tracking_reference'])
        # print(tracking_ref)
        # if OrderDb.query.filter_by(tracking_reference = new_dict['tracking_reference']).all():
        #     print('Already exists!')
        # if new_dict['tracking_reference'] in db.Query.filter_by().all():
        #     return "this order already exists!"


        # Generate ID
        order_id = randint(1,1000000)
        accepted_date = datetime.now()

        package = {
            "Order" : new_order.dict(),
            "order_url" : f"http://localhost:8080/order/{order_id}",
            "accepted_at" : str(accepted_date),
            "insurance_provided" : insurance_required,
            "total_insurance_charge" : str(total_insurance_cost),
            "ipt_included_in_charge" : str(ipt_included_in_charge)
        }

        # print(package)
        '''Add Valid orders to the database and return new "package" object
            this should contain new dictionary data:
            "order_url": "http://localhost:8080/order/<order.id>",
            "accepted_at": "2021-09-01T12:22:43.406768",
            "insurance_provided": true,
            "total_insurance_charge": str(insurance_cost),
            "ipt_included_in_charge": "1.98"
        '''

        return jsonify(package)
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