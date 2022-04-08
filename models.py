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
        name="Good Pharm",
        address="Swinemünder Straße 106, 10435 Berlin",
        price="10",
        imageurl="https://images.unsplash.com/photo-1604145942179-63cd583fcf64?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=1241&q=80",
        geom=LolliTestCenterModel.point_representation(
            latitude=52.5391655,
            longitude=13.3979498
        )
    )
    loc1.insert()

    loc2 = LolliTestCenterModel(
        name="Super Pharm",
        address="Eberswalder Straße 41 ,10437 Berlin",
        price="2",
        imageurl="https://images.unsplash.com/photo-1576602976047-174e57a47881?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=1469&q=80",
        geom=LolliTestCenterModel.point_representation(
            latitude=52.5418862,
            longitude=13.4079601
        )
    )
    loc2.insert()

    loc3 = LolliTestCenterModel(
        name="New Pharm",
        address="Wolliner Str. 51 ,10435 Berlin",
        price="3",
        imageurl="https://images.unsplash.com/photo-1585435557343-3b092031a831?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=1470&q=80",
        geom=LolliTestCenterModel.point_representation(
            latitude=52.5389381,
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

        # TODO: The arbitrary limit = 100 is just a quick way to make sure
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
