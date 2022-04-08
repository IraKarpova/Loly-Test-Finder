import os
import sys
from flask import Flask, request, abort, jsonify, render_template, url_for, flash, redirect
from flask_cors import CORS
import traceback
from forms import ShowPharmaciesForm, NewPharmacyForm
from models import setup_db, LolliTestCenterModel, db_drop_and_create_all


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    CORS(app)

    SECRET_KEY = os.urandom(32)
    app.config['SECRET_KEY'] = SECRET_KEY

    """ uncomment at the first time running the app """
     #db_drop_and_create_all()

    @app.route("/", methods=['GET', 'POST'])
    def home():
        form = ShowPharmaciesForm()

        if form.validate_on_submit():
            latitude = float(form.coord_latitude.data)
            longitude = float(form.coord_longitude.data)
            return redirect(url_for('map', latitude=latitude, longitude=longitude))

        return render_template(
            'main_page.html',
            form=form,
            map_key=os.getenv('GOOGLE_MAPS_API_KEY',
                              'GOOGLE_MAPS_API_KEY_WAS_NOT_SET?!')
        )

    @app.route('/map', methods=['GET'])
    def map():
        try:
            latitude = float(request.args.get('latitude'))
            longitude = float(request.args.get('longitude'))

            return render_template(
                'map.html',
                latitude=latitude,
                longitude=longitude,
                map_key=os.getenv('GOOGLE_MAPS_API_KEY',
                                  'GOOGLE_MAPS_API_KEY_WAS_NOT_SET?!')
            )
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            app.logger.error(traceback.print_exception(
                exc_type, exc_value, exc_traceback, limit=2))
            abort(500)

    @app.route('/pharmacy_form', methods=['GET', 'POST'])
    def pharmacy_form():
        form = NewPharmacyForm()

        if form.validate_on_submit():
            latitude = float(form.coord_latitude.data)
            longitude = float(form.coord_longitude.data)

            lolliTestCenter = LolliTestCenterModel(
                name=form.name.data,
                address=form.address.data,
                price=form.price.data,
                imageurl=form.imageurl.data,
                geom=LolliTestCenterModel.point_representation(
                    latitude=latitude, longitude=longitude)
            )
            lolliTestCenter.insert()

            flash(f'New pharmacy created!', 'success')
            return redirect(url_for('home'))

        return render_template(
            'pharmacy_form.html',
            form=form,
            map_key=os.getenv('GOOGLE_MAPS_API_KEY',
                              'GOOGLE_MAPS_API_KEY_WAS_NOT_SET?!')
        )

    @app.route("/loginOrRegister", methods=['GET', 'POST'])
    def loginOrRegister():

        return render_template(
            'login_page.html',

        )

    @app.route("/api/store_item")
    def store_item():
        try:
            latitude = float(request.args.get('lat'))
            longitude = float(request.args.get('lng'))
            name = request.args.get('name')
            address = request.args.get('address')
            price = request.args.get('price')
            imageurl = request.args.get('imageurl')

            lolliTestCenter = LolliTestCenterModel(
                name=name,
                address=address,
                price=price,
                imageurl=imageurl,
                geom=LolliTestCenterModel.point_representation(
                    latitude=latitude, longitude=longitude)
            )
            lolliTestCenter.insert()

            return jsonify(
                {
                    "success": True,
                    "location": lolliTestCenter.to_dict()
                }
            ), 200
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            app.logger.error(traceback.print_exception(
                exc_type, exc_value, exc_traceback, limit=2))
            abort(500)

    @app.route("/api/get_items_in_radius")
    def get_items_in_radius():
        try:
            latitude = float(request.args.get('lat'))
            longitude = float(request.args.get('lng'))
            radius = int(request.args.get('radius'))

            lolliTestCenters = LolliTestCenterModel.get_items_within_radius(
                latitude, longitude, radius)
            return jsonify(
                {
                    "success": True,
                    "results": lolliTestCenters
                }
            ), 200
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            app.logger.error(traceback.print_exception(
                exc_type, exc_value, exc_traceback, limit=2))
            abort(500)

    @app.errorhandler(500)
    def server_error(error):
        return jsonify({
            "success": False,
            "error": 500,
            "message": "server error"
        }), 500

    return app


app = create_app()
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='127.0.0.1', port=port, debug=True)
