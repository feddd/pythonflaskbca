import sqlite3
from sqlalchemy import create_engine, Column, Integer, String, Float, Date, MetaData, Table, ForeignKey

# DATABASE_URI = 'sqlite:///food.db'
DATABASE_URI = 'mysql://root:mSVCivGq4m22uLGjZLKD@containers-us-west-204.railway.app:8059/railway'
engine = create_engine(DATABASE_URI, echo=True)
metadata = MetaData()

#table master
foods = Table('foods', metadata,
    Column('food_id',Integer, primary_key=True),
    Column('name', String),
    Column('price', Float),
    Column('category', String)
)
#table transaction
orders = Table('orders', metadata,
    Column('order_id',Integer, primary_key=True),
    Column('customer_name', String),
    Column('food_id', Integer, ForeignKey('foods.food_id')), 
    Column('quantity', Integer),
    Column('total_price', Float),
    Column('order_date', Date)
)
metadata.create_all(engine)

print("Database food.db dan table makanan telah berhasil dibuat!")