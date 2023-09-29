# Import Library
from flask import Flask, jsonify, request, render_template
from flask import redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flasgger import Swagger, swag_from
from datetime import datetime

import os

# app definition
app = Flask(__name__)
# database config
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + DATABASE_PATH
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:mSVCivGq4m22uLGjZLKD@containers-us-west-204.railway.app:8059/railway'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Swagger config
app.config['SWAGGER'] = {
    'title':'GasFood API - Food Data',
    'uiversion':3,
    'headers':[],
    'specs':[
        {
            'endpoint':'apispec_1',
            'route':'/apispec_1.json',
            'rule_filter':lambda rule:True,
            'model_filter':lambda tag:True,
        }
    ],
    'static_url_path':'/flasgger_static',
    'swagger_ui':True,
    'specs_route':'/apidocs'
}
swagger= Swagger(app)

db = SQLAlchemy(app)

# model def

class Foods(db.Model):
    food_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100),nullable=False)
    price = db.Column(db.Float,nullable=False)
    category = db.Column(db.String(100),nullable=False)
    
class Orders(db.Model):
    order_id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(100),nullable=False)
    food_id = db.Column(db.Integer, db.ForeignKey('foods.food_id'), nullable=False)
    quantity = db.Column(db.Integer,nullable=False)    
    total_price = db.Column(db.Float,nullable=False)
    order_date = db.Column(db.Date,nullable=False)
    
@app.before_first_request
def create_tables():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')
@app.route('/indexfood')
def indexfood():
    return render_template('indexfood.html')
@app.route('/indexorder')
def indexorder():
    return render_template('indexorder.html')

#API Connection for Create Food Data
@app.route('/food', methods=['POST'])
@swag_from('swagger_docs/create_data_food.yaml')
def create_food():
    data = request.json

    new_food = Foods(
        food_id=data['food_id'],
        name=data['name'],
        price=data['price'],
        category=data['category']
    )
    
    db.session.add(new_food)
    db.session.commit()
    
    return jsonify({'message': 'Food successfully added'}),201
    
#API Connection for Create Order
@app.route('/order', methods=['POST'])
@swag_from('swagger_docs/create_order.yaml')
def create_order():
    data = request.json
    keyword = Foods.query.filter(Foods.food_id==data['food_id']).add_columns(Foods.price).first()
    new_order = Orders(
        order_id=data['order_id'],
        customer_name=data['customer_name'],
        food_id=data['food_id'],
        quantity=data['quantity'],
        total_price=data['total_price'],
        order_date=datetime.strptime(data['order_date'],'%Y-%m-%d') 
    )
    
    db.session.add(new_order)
    db.session.commit()
    
    return jsonify({'message': 'Order successfully added'}),201

#Connection API Show Food List
@app.route('/display_food', methods=['GET'])
@swag_from('swagger_docs/get_all_food.yaml')
def get_all_food():
    food_list = []
    try:
        all_food = Foods.query.all()
        
        for food in all_food:
            food_data = {
                'food_id': food.food_id,
                'name': food.name,
                'price': food.price,
                'category': food.category
            }  
            food_list.append(food_data)
    except Exception as e:
        return render_template('error.html', message="Error : {}".format(str(e))),500
    finally:
        if food_list:
            return render_template('displayfood.html', food_list=food_list)
        else: 
            return render_template('error.html', message= "Food Data Not Found"),404



# #API Connection to Show Food Data
# @app.route('/food<int:food_id>', methods=['GET'])
# #@swag_from('swagger_docs/get_one_food.yaml')
# def get_one_food(food_id):
#     pass  

#Func to Add Food
@app.route('/addfood', methods=['GET', 'POST'])
def input_food():
    if request.method == 'POST':
        #get data
        name = request.form.get('name')
        price = request.form.get('price')
        category = request.form.get('category')
        
        #empty data validation
        if not name or not price or not category:
            return render_template('createfood.html', error="All field must be filled!")
        
        #price number validation
        if not price.isdigit():
            return render_template('createfood.html', error="price must be in number!")
        
        #create object
        new_food = Foods(
            name=name,
            price=price,
            category=category
        )

        #save data
        db.session.add(new_food)
        db.session.commit()
        return render_template('confirmation.html')
    return render_template('createfood.html')
       
#Func to Update Food
@app.route('/updatefood',methods=['GET', 'POST'])
def updatefood():
    if request.method == 'POST':
        keyword = request.form.get('name')
        data_list = Foods.query.filter(Foods.name.like(f"%{keyword}%")).all()
        return render_template('updatefood.html', data_list=data_list)
    return render_template('updatefood.html')

@app.route('/update_food/<int:food_id>',methods=['POST'])
@swag_from('swagger_docs/update_data_food.yaml')
def update_food(food_id):
    try:
        getfood = request.json
        
         #empty data validation
        if not getfood['name'] or not getfood['price'] or not getfood['category']:
            return render_template('updatefood.html', error="All field must be filled!")
        
        #price number validation
        # if not int(getfood['price']).isdigit():
        #     return render_template('updatefood.html', error="price must be in number!")
        food_to_update = Foods.query.filter_by(food_id=food_id).first()
        if not food_to_update:
            return jsonify({'message': 'Food not found'}),404
        food_to_update.name=getfood['name']
        food_to_update.price=getfood['price']
        food_to_update.category=getfood['category']
        # food_id = request.form.get('food_id')
        # name = request.form.get('name')
        # price = request.form.get('price')
        # category = request.form.get('category')
        # food = Foods.query.get(food_id)
        # food.name = name
        # food.price = price
        # food.category = category 
        db.session.commit()
    
        return redirect(url_for('get_all_food'))
    except Exception as e:
        print(str(e))
        return jsonify({'message': f'Something trouble: {str(e)}'}),500

@app.route('/deletefood',methods=['GET', 'POST'])
def deletefood():
    data_list = []
    try:
        if request.method == 'POST':
            search_name = request.form['name'].lower()
            all_food = Foods.query.all()
            data_list = [food for food in all_food if search_name in food.name.lower()]
    except Exception as e:
        error_message = f"Something Trouble Happen!: {e}"
        print(error_message)
        return render_template('error.html', message=error_message),500
    finally:
        return render_template('deletefood.html', data_list=data_list),500

#API delete food   
@app.route('/food/<int:food_id>',methods=['DELETE'])
@swag_from('swagger_docs/delete_data_food.yaml')
def delete_food(food_id):
    try:
        food_to_delete = Foods.query.filter_by(food_id=food_id).first()
        
        if food_to_delete:
            db.session.delete(food_to_delete)
            db.session.commit()
            return jsonify({'message': f'Food with ID {food_id} has been removed'}),200
        else:
            return jsonify({'message': f'Food with ID {food_id} not found'}),404
    except Exception as e:
        return jsonify({'message':f"Something troble happen! {e}"}),500
    


#Connection API Show Order List
@app.route('/display_order', methods=['GET'])
@swag_from('swagger_docs/get_all_order.yaml')
def get_all_order():
    order_list = []
    all_order = []
    try:
        all_order = Orders.query.join(Foods, Orders.food_id==Foods.food_id).add_columns(Orders.order_id, Orders.customer_name, Orders.quantity, Orders.total_price, Orders.order_date, Foods.name).all()
       
        for order in all_order:
            print(order)
            order_data = {
                'order_id': order.order_id,
                'customer_name': order.customer_name,
                'quantity': order.quantity,
                'total_price': order.total_price,
                'order_date' : order.order_date,
                'name' : order.name
            }  
            order_list.append(order_data)
        
    except Exception as e:
        return render_template('error.html', message="Error : {}".format(str(e))),500
    finally:
        if order_list:
            return render_template('displayorder.html', order_list=order_list)
        else: 
            return render_template('error.html', message= "Order Data Not Found"),404
        
#Func to Add Order
@app.route('/addorder', methods=['GET', 'POST'])
# @swag_from('swagger_dcos/create_order.yaml')
def input_order():
    if request.method == 'GET':
    
        data_list = Foods.query.all()
        
    if request.method == 'POST':
        #get data
        order_id = request.form.get('order_id')
        customer_name = request.form.get('customer_name')
        food_id = request.form.get('food_id')
        quantity = request.form.get('quantity')
        
        #empty data validation
        if not customer_name or not food_id:
            return render_template('createorder.html', error="All field must be filled!")
        
        #quantity number validation
        if not quantity.isdigit():
            return render_template('createorder.html', error="price must be in number!")
        
        order_date = datetime.strptime(request.form.get('order_date'),'%Y-%m-%d')
        keyword = Foods.query.filter(Foods.food_id==food_id).add_columns(Foods.price).first()

        total_price = keyword.price * float(quantity)
        
        #create object
        new_order = Orders(
            order_id=order_id,
            customer_name=customer_name,
            food_id=food_id,
            quantity=quantity,
            total_price=total_price,
            order_date=order_date,
        )
        

        #save data
        db.session.add(new_order)
        db.session.commit()
        return render_template('confirmation.html')
    return render_template('createorder.html', data_list=data_list)

#Func to Update Order
@app.route('/updateorder',methods=['GET', 'POST'])
def updateorder():
    if request.method == 'POST':
        food_list = Foods.query.all()
        keyword = request.form.get('order_id')
        # data_list = Orders.query.filter(Orders.order_id.like(f"%{keyword}%")).all()
        data_list = Orders.query.join(Foods, Orders.food_id==Foods.food_id).add_columns(Orders.order_id, Orders.customer_name, Foods.name, Orders.quantity, Orders.total_price, Orders.order_date).filter(Orders.order_id.like(f"%{keyword}%")).all()
        return render_template('updateorder.html', data_list=data_list, food_list=food_list)
    return render_template('updateorder.html')

@app.route('/update_order/<int:order_id>',methods=['POST'])
@swag_from('swagger_docs/update_data_order.yaml')
def update_order(order_id):
    try:
        getorder = request.json
        
         #empty data validation
        if not getorder['customer_name'] or not getorder['quantity'] or not getorder['total_price'] or not getorder['food_id'] or not getorder['order_date']:
            return render_template('updateorder.html', error="All field must be filled!")

        order_to_update = Orders.query.filter_by(order_id=order_id).first()
        if not order_to_update:
            return jsonify({'message': 'Order not found'}),404
        order_to_update.customer_name=getorder['customer_name']
        order_to_update.food_id=getorder['food_id']
        order_to_update.quantity=getorder['quantity']
        order_to_update.total_price = getorder['total_price']
        

        #save data
        db.session.add(new_order)
        if not order_to_update:
            return jsonify({'message': 'Order not found'}),404

        db.session.commit()
    
        return redirect(url_for('get_all_order'))
    except Exception as e:
        return jsonify({'message': f'Something trouble: {str(e)}'}),500

# delete order
@app.route('/order/<int:order_id>',methods=['DELETE'])
@swag_from('swagger_docs/delete_data_order.yaml')
def delete_order(order_id):
    try:
        order_to_delete = Orders.query.filter_by(order_id=order_id).first()    
            
        if order_to_delete:
            db.session.delete(order_to_delete)
            db.session.commit()
            return jsonify({'message': f'Order with ID {order_id} has been removed'}),200
        else:
            return jsonify({'message': f'Order with ID {order_id} not found'}),404
    except Exception as e:
        return jsonify({'message':f"Something trouble happen! {e}"}),500
    
@app.route('/deleteorder',methods=['GET', 'POST'])
def deleteorder():
    data_list = []
    try:
        if request.method == 'POST':
            keyword = request.form.get('order_id')
            # data_list = Orders.query.filter(Orders.order_id.like(f"%{keyword}%")).all()
            data_list = Orders.query.join(Foods, Orders.food_id==Foods.food_id).add_columns(Orders.order_id, Orders.customer_name, Foods.name, Orders.quantity, Orders.total_price, Orders.order_date).filter(Orders.order_id.like(f"%{keyword}%")).all()

    except Exception as e:
        error_message = f"Something Trouble Happen!: {e}"
        print(error_message)
        return render_template('error.html', message=error_message),500
    finally:
        return render_template('deleteorder.html', data_list=data_list),500

# if __name__ == '__main__':
#     app.run(debug=True, port=5030)

if __name__ == '__main__':
    app.run(debug=True)
