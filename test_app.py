import unittest
from flask_testing import TestCase
from flask import url_for
from datafood import app, db, Foods  # Import modul-modul yang diperlukan

# Kelas MyTest untuk melakukan testing pada aplikasi
class MyTest(TestCase):

    # Metode untuk membuat aplikasi dalam mode testing
    def create_app(self):
        app.config['TESTING'] = True  # Mengaktifkan mode testing
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///food.db'  # Menggunakan database in-memory untuk testing
        return app

    # Metode yang dijalankan sebelum setiap test
    def setUp(self):
        db.create_all()  # Membuat semua tabel dalam database

    # Metode yang dijalankan setelah setiap test
    def tearDown(self):
        db.session.remove()  # Menghapus sesi database
        db.drop_all()  # Menghapus semua tabel dalam database

    # Test untuk endpoint index '/'
    def test_index(self):
        response = self.client.get('/')  # Melakukan request GET ke '/'
        self.assert200(response)  # Memastikan response adalah 200 OK
        self.assert_template_used('index.html')  # Memastikan template yang digunakan adalah 'index.html'

    # Test untuk membuat food baru
    def test_create_food(self):
        # Melakukan request POST ke '/food' dengan data food baru
        response = self.client.post('/food', json={
            'food_id': '8',
            'name': 'pizza',
            'price': '80000',
            'category': 'Main Course'
        })
        self.assertStatus(response, 201)  # Memastikan response adalah 201 Created
        food = Foods.query.first()  # Mengambil food pertama dari database
        self.assertEqual(food.name, 'pizza')  # Memastikan nama food adalah 'pizza'

    # Test untuk menghapus food
    def test_delete_food(self):
        # Membuat objek food baru dan menyimpannya ke database
        food = Foods(name='Macaroni', price='20000', category='Dessert')
        db.session.add(food)
        db.session.commit()

        # Melakukan request DELETE ke '/food/{food_id}'
        response = self.client.delete(f'/food/{food.food_id}')
        self.assert200(response)  # Memastikan response adalah 200 OK
        self.assertIsNone(Foods.query.get(food.food_id))  # Memastikan food dengan id tersebut sudah dihapus

    # Test untuk mendapatkan semua food
    def test_get_all_food(self):
        # Membuat dua objek food baru dan menyimpannya ke database
        food1 = Foods(name='pizza', price='80000', category='Main Course')
        food2 = Foods(name='pizza', price='90000', category='Main Course')
        db.session.add(food1)
        db.session.add(food2)
        db.session.commit()

        # Melakukan request GET ke '/displayfood'
        response = self.client.get('/display_food')
        self.assert200(response)  # Memastikan response adalah 200 OK
        self.assert_template_used('displayfood.html')  # Memastikan template yang digunakan adalah 'displayfood.html'
        self.assertIn(b'pizza', response.data)  # Memastikan 'John Doe' ada dalam response data
        self.assertIn(b'pizza', response.data)  # Memastikan 'Jane Doe' ada dalam response data

    # Test untuk mendapatkan satu food berdasarkan id
    # def test_get_one_food(self):
    #     # Membuat objek food baru dan menyimpannya ke database
    #     food = Foods(name='pizza', price='80000', category='Main Course')
    #     db.session.add(food)
    #     db.session.commit()

        # # Melakukan request GET ke '/food/{food_id}'
        # response = self.client.get(f'/food/{Foods.food_id}')
        # self.assert200(response)  # Memastikan response adalah 200 OK

    # Test untuk menghapus food melalui UI
    # def test_delete_food_ui(self):
    #     # Membuat objek food baru dan menyimpannya ke database
    #     food = Foods(food_id='8', name='pizza', price='80000', category='Main Course')
    #     db.session.add(food)
    #     db.session.commit()

    #     # Melakukan request POST ke '/delete_food' dengan data nama food
    #     response = self.client.post('/delete_food', data={'food_id': '8'})
    #     self.assert200(response)  # Memastikan response adalah 200 OK
    #     self.assert_template_used('deletefood.html')  # Memastikan template yang digunakan adalah 'deletefood.html'
    #     self.assertIn(b'pizza', response.data)  # Memastikan 'pizza' ada dalam response data

if __name__ == '__main__':
    unittest.main()  # Menjalankan semua test