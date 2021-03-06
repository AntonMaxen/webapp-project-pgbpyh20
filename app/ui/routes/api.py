# external imports
from flask import (
    Blueprint, request, send_file, flash, redirect
)
import datetime
from werkzeug.utils import secure_filename
import os
import json
# internal imports
import app.bl.location_controller as lc
import app.bl.utility_controller as uc
import app.bl.picture_controller as pc
import app.bl.picture_like_controller as plc
import app.bl.review_like_controller as rlc
import app.bl.review_controller as rc
import app.bl.category_controller as cc
import app.bl.user_controller as user_c
from app.utils import (
    make_list_of_dicts_jsonable,
    make_dict_jsonable,
    get_project_root
)
import app.ui.external.api.mapquest.geocoding as geocoding

bp = Blueprint('api', __name__, url_prefix='/api')


@bp.route('/resource/location/all')
def all_locations():
    locations = lc.get_all_locations()
    if locations is None:
        return json.dumps({
            'status': 404
        })

    location_dicts = uc.rows_to_dicts(locations)
    location_dicts = make_list_of_dicts_jsonable(location_dicts)
    return json.dumps(location_dicts)


@bp.route('/resource/location/<location_id>/picture/all')
def location_pictures_all(location_id):
    location = lc.get_location_by_id(location_id)
    if location is None:
        return json.dumps({
            'status': 404
        })

    pictures = sorted(location.picture, key=lambda x: x.Id, reverse=True)
    picture_dicts = uc.rows_to_dicts(pictures)
    picture_dicts = make_list_of_dicts_jsonable(picture_dicts)
    return json.dumps(picture_dicts)


@bp.route('/resource/location/<location_id>/picture')
def location_picture(location_id):
    location = lc.get_location_by_id(location_id)
    if location is None:
        return json.dumps({
            'status': 404
        })

    amount = request.args.get('amount')
    amount = 1 if not amount or int(amount) < 1 else int(amount)
    pictures = sorted(location.picture, key=lambda x: x.Id, reverse=True)
    pictures = pictures[:amount]
    picture_dicts = uc.rows_to_dicts(pictures)
    picture_dicts = make_list_of_dicts_jsonable(picture_dicts)
    return json.dumps(picture_dicts)


@bp.route('/resource/location/<location_id>/review')
def location_review(location_id):
    location = lc.get_location_by_id(location_id)
    if location is None:
        return json.dumps({
            'status': 404
        })

    amount = request.args.get('amount')
    amount = 1 if not amount or int(amount) < 1 else int(amount)
    reviews = sorted(location.review, key=lambda x: x.Id, reverse=True)
    reviews = reviews[:amount]
    review_dicts = uc.rows_to_dicts(reviews)
    review_dicts = make_list_of_dicts_jsonable(review_dicts)
    return json.dumps(review_dicts)


@bp.route('/resource/location/<location_id>/review/all')
def location_reviews_all(location_id):
    location = lc.get_location_by_id(location_id)
    if location is None:
        return json.dumps({
            'status': 404
        })

    reviews = sorted(location.review, key=lambda x: x.Id, reverse=True)
    review_dicts = uc.rows_to_dicts(reviews)
    review_dicts = make_list_of_dicts_jsonable(review_dicts)
    return json.dumps(review_dicts)


@bp.route('/resource/category')
def category():
    amount = request.args.get('amount')
    amount = 1 if not amount or int(amount) < 1 else int(amount)
    categories = cc.get_all_categories()
    categories = categories[:amount]
    category_dicts = uc.rows_to_dicts(categories)
    category_dicts = make_list_of_dicts_jsonable(category_dicts)
    return json.dumps(category_dicts)


@bp.route('/resource/picture/<picture_id>/like/count')
def picture_likes(picture_id):
    amount_of_likes = plc.get_amount_of_likes_by_picture_id(picture_id)
    if amount_of_likes is None:
        amount_of_likes = {
            'status': 404
        }
    return json.dumps(amount_of_likes)


@bp.route('/resource/review/<review_id>/like/count')
def review_likes(review_id):
    amount_of_likes = rlc.get_amount_of_likes_by_review_id(review_id)
    if amount_of_likes is None:
        amount_of_likes = {
            'status': 404
        }

    return json.dumps(amount_of_likes)


@bp.route('/static/image/<file_name>')
def picture(file_name):
    image_folder = 'Photos'
    img_path = os.path.join(get_project_root(), image_folder, file_name)
    return send_file(img_path, mimetype='image/gif')


@bp.route('/external/geocoding/reverse')
def geocoding_reverse():
    lat_lng = request.args.get('latlng').split(',')
    geo_dict = geocoding.get_geoinformation_by_latlng(lat_lng[0], lat_lng[1])
    return json.dumps(geo_dict)


@bp.route('/add/image', methods=['POST'])
def add_image():
    image_name = request.form.get('image_name')
    user_id = request.form.get('user_id')
    location_id = request.form.get('location_id')
    if 'image' not in request.files:
        flash('No files', 'error')
        return redirect('/map')

    image = request.files.get('image')

    if image.filename == '':
        flash('No selected file', 'error')
        return redirect('/map')

    if image and allowed_file(image.filename):
        recent_row = pc.get_most_recent_row()
        highest_id = recent_row.Id if recent_row is not None else 1
        flash('success', 'success')

        photo_dir = os.path.join(get_project_root(), 'Photos')
        fixed_filename = secure_filename(image.filename)
        s_filename = fixed_filename.split('.')
        file_name = f'{s_filename[0]}-{highest_id+1}.{s_filename[1]}'
        image.save(os.path.join(photo_dir, file_name))

        pc.add_picture({
            'ImageName': image_name,
            'Date': datetime.date.today(),
            'UserId': user_id,
            'LocationId': location_id,
            'FileName': file_name
        })
        return redirect('/map')
    else:
        flash('not allowed file ending', 'error')
        return redirect('/map')


@bp.route('/add/review', methods=['POST'])
def add_review():
    title = request.form.get('title')
    review_text = request.form.get('review_text')
    score = request.form.get('score')
    location_id = request.form.get('location_id')
    user_id = request.form.get('user_id')
    rc.add_review({
        'Title': title,
        'ReviewText': review_text,
        'Score': score,
        'DateCreated': datetime.date.today(),
        'UserId': user_id,
        'LocationId': location_id
    })

    return redirect('/map')


@bp.route('/add/location', methods=['POST'])
def add_location():
    place = request.form.get('place')
    longitude = request.form.get('longitude')
    latitude = request.form.get('latitude')
    name = request.form.get('name')
    user_id = request.form.get('user_id')
    category_id = request.form.get('category_id')
    location = lc.add_location({
        'Place': place,
        'Longitude': longitude,
        'Latitude': latitude,
        'Name': name,
        'UserId': user_id,
        'CategoryId': category_id
    })

    uc.refresh_row(location)
    location_dict = uc.row_to_dict(location)
    location_dict = make_dict_jsonable(location_dict)

    return json.dumps(location_dict)


@bp.route('/update/user', methods=['POST'])
def update_user():
    user_id = request.form.get('user_id')
    token = request.form.get('token')
    if not request_ok(user_id, token):
        return json.dumps({
            'status': 401,
            'category': 'error',
            'message': "You are not authorized"
        })

    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    email = request.form.get('email')
    username = request.form.get('username')
    phone = request.form.get('phone')
    date_of_birth = request.form.get('date_of_birth')
    columns_to_update = {
        "FirstName": first_name,
        "LastName": last_name,
        "Email": email,
        "Username": username,
        "PhoneNumber": phone,
    }
    if date_of_birth:
        columns_to_update['DateOfBirth'] = datetime.date.fromisoformat(
            date_of_birth)

    user = user_c.get_user_by_id(int(user_id))
    user_c.update_user_columns(user, columns_to_update)
    user_dict = uc.row_to_dict(user)
    user_dict = make_dict_jsonable(user_dict)

    return json.dumps({
        'status': 200,
        'category': 'success',
        'message': 'Profile Updated',
        'user': user_dict
    })


def request_ok(user_id, token):
    db_user = user_c.get_user_by_token(token)
    return db_user and db_user.Id == int(user_id)


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ['png', 'jpg', 'jpeg', 'gif']
