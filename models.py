import os
from sqlalchemy import Column, String, Integer, create_engine
from flask_sqlalchemy import SQLAlchemy
from geoalchemy2.types import Geometry
from shapely.geometry import Point
from geoalchemy2.shape import to_shape
from geoalchemy2.elements import WKTElement
from geoalchemy2.functions import ST_DWithin
from geoalchemy2.types import Geography
from sqlalchemy.sql.expression import cast
from geoalchemy2.shape import from_shape

db = SQLAlchemy()

'''
setup_db(app):
    binds a flask application and a SQLAlchemy service
'''
def setup_db(app):
    database_path = os.getenv('DATABASE_URL', 'DATABASE_URL_WAS_NOT_SET?!')

    # https://stackoverflow.com/questions/62688256/sqlalchemy-exc-nosuchmoduleerror-cant-load-plugin-sqlalchemy-dialectspostgre
    database_path = database_path.replace('postgres://', 'postgresql://')

    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)

'''
    drops the database tables and starts fresh
    can be used to initialize a clean database
'''
def db_drop_and_create_all():
    db.drop_all()
    db.create_all()

    # Initial sample data:
    insert_db_premium_pharmacies()

def insert_db_premium_pharmacies():
    loc1 = LolliTestCenterModel(
        name="temp_name1",
        address="temp_address1",
        price="10$",
        imageurl="https://libreshot.com/wp-content/uploads/2016/03/coffee-beans-861x631.jpg",
        geom=LolliTestCenterModel.point_representation(
            latitude=52.516247, 
            longitude=13.377711
        )
    )
    loc1.insert()

    loc2 = LolliTestCenterModel(
        name="temp_name2",
        address="temp_address2",
        price="20$",
        imageurl="https://libreshot.com/wp-content/uploads/2016/03/coffee-beans-861x631.jpg",
        geom=LolliTestCenterModel.point_representation(
            latitude=52.520608, 
            longitude=13.295581
        )
    )
    loc2.insert()

    loc3 = LolliTestCenterModel(
        name="temp_name3",
        address="temp_address3",
        price="30$",
        imageurl="https://libreshot.com/wp-content/uploads/2016/03/coffee-beans-861x631.jpg",
        geom=LolliTestCenterModel.point_representation(
            latitude=52.473580, 
            longitude=13.405252
        )
    )
    loc3.insert()

class SpatialConstants:
    SRID = 4326

class LolliTestCenterModel(db.Model):
    __tablename__ = 'lolli_test_centers_table'

    id = Column(Integer, primary_key=True)
    name = Column(String(80))
    address = Column(String(80))
    price = Column(String(80))
    imageurl = Column(String(200))
    geom = Column(Geometry(geometry_type='POINT', srid=SpatialConstants.SRID))  

    @staticmethod
    def point_representation(latitude, longitude):
        point = 'POINT(%s %s)' % (longitude, latitude)
        wkb_element = WKTElement(point, srid=SpatialConstants.SRID)
        return wkb_element

    @staticmethod
    def get_items_within_radius(lat, lng, radius):
        """Return all sample locations within a given radius (in meters)"""

        #TODO: The arbitrary limit = 100 is just a quick way to make sure 
        # we won't return tons of entries at once, 
        # paging needs to be in place for real usecase
        results = LolliTestCenterModel.query.filter(
            ST_DWithin(
                cast(LolliTestCenterModel.geom, Geography),
                cast(from_shape(Point(lng, lat)), Geography),
                radius)
            ).limit(100).all() 

        return [l.to_dict() for l in results]    

    def get_location_latitude(self):
        point = to_shape(self.geom)
        return point.y

    def get_location_longitude(self):
        point = to_shape(self.geom)
        return point.x  

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'address': self.address,
            'price': self.price,
            'imageurl': self.imageurl,
            'location': {
                'lng': self.get_location_longitude(),
                'lat': self.get_location_latitude()
            }
        }    

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def update(self):
        db.session.commit()         