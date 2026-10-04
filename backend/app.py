from flask import (
    Flask,
    jsonify,
    request,
    send_from_directory,
    session
)

from flask_cors import CORS
from werkzeug.utils import secure_filename

from database import db

from models import (
    Product,
    Category,
    Order,
    Booking,
    Review
)

import os
from datetime import datetime
import uuid


# ============================================================
# APP
# ============================================================

app = Flask(__name__)


# ============================================================
# APP SETTINGS
# ============================================================

app.secret_key = os.environ.get(
    "FLASK_SECRET_KEY",
    "favour-hairs-development-secret-key"
)


# ============================================================
# CORS
# ============================================================

CORS(
    app,
    supports_credentials=True
)


# ============================================================
# ADMIN SETTINGS
# ============================================================

ADMIN_USERNAME = os.environ.get(
    "ADMIN_USERNAME",
    "admin"
)

ADMIN_PASSWORD = os.environ.get(
    "ADMIN_PASSWORD",
    "admin123"
)


# ============================================================
# DATABASE
# ============================================================

app.config[
    "SQLALCHEMY_DATABASE_URI"
] = "sqlite:///favour_hairs.db"

app.config[
    "SQLALCHEMY_TRACK_MODIFICATIONS"
] = False


db.init_app(app)


# ============================================================
# FILE UPLOAD SETTINGS
# ============================================================

UPLOAD_FOLDER = os.path.join(
    app.root_path,
    "uploads"
)

ALLOWED_EXTENSIONS = {
    "png",
    "jpg",
    "jpeg",
    "jfif",
    "webp",
    "gif"
}

app.config[
    "UPLOAD_FOLDER"
] = UPLOAD_FOLDER

app.config[
    "MAX_CONTENT_LENGTH"
] = 10 * 1024 * 1024


os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)


# ============================================================
# HELPERS
# ============================================================

def allowed_file(filename):

    if not filename:
        return False

    return (
        "." in filename
        and
        filename.rsplit(
            ".",
            1
        )[1].lower()
        in ALLOWED_EXTENSIONS
    )


def save_uploaded_image(file):

    if not file or not file.filename:

        raise ValueError(
            "No file was selected."
        )

    if not allowed_file(
        file.filename
    ):

        raise ValueError(
            "Invalid file type. "
            "Only PNG, JPG, JPEG, JFIF, "
            "WEBP and GIF are allowed."
        )

    original_name = secure_filename(
        file.filename
    )

    if "." not in original_name:

        raise ValueError(
            "Invalid filename."
        )

    extension = (
        original_name
        .rsplit(".", 1)[1]
        .lower()
    )

    unique_name = (
        str(uuid.uuid4())
        + "."
        + extension
    )

    file_path = os.path.join(
        app.config["UPLOAD_FOLDER"],
        unique_name
    )

    file.save(file_path)

    image_url = (
        request.host_url.rstrip("/")
        + "/uploads/"
        + unique_name
    )

    return (
        unique_name,
        image_url
    )


def admin_required():

    if not session.get(
        "admin_logged_in"
    ):

        return jsonify({
            "error": "Admin authentication required."
        }), 401

    return None


def product_data(product):

    return {

        "id": product.id,

        "name": product.name,

        "price": product.price,

        "category": product.category,

        "description": product.description,

        "images": product.images or [],

        "specifications": (
            product.specifications or {}
        )

    }


def category_data(category):

    return {

        "id": category.id,

        "name": category.name,

        "image": category.image

    }


def order_data(order):

    return {

        "id": order.id,

        "date": order.date,

        "customer": order.customer or {},

        "items": order.items or [],

        "subtotal": order.subtotal,

        "total": order.total,

        "deliveryOption": (
            order.delivery_option
        ),

        "note": order.note,

        "paymentMethod": (
            order.payment_method
        ),

        "status": order.status

    }


def booking_data(booking):

    return {

        "id": booking.id,

        "date": booking.date,

        "customer": booking.customer or {},

        "service": booking.service,

        "preferredDate": (
            booking.preferred_date
        ),

        "preferredTime": (
            booking.preferred_time
        ),

        "message": booking.message,

        "note": booking.note,

        "inspirationImage": (
            booking.inspiration_image
        ),

        "status": booking.status

    }


def review_data(review):

    return {

        "id": review.id,

        "productId": review.product_id,

        "name": review.name,

        "rating": review.rating,

        "comment": review.comment,

        "date": review.date,

        "status": review.status

    }


# ============================================================
# HOME
# ============================================================

@app.route("/")
def home():

    return jsonify({
        "message": "Favour Hairs API is running."
    })


# ============================================================
# ADMIN LOGIN
# ============================================================

@app.route(
    "/api/admin/login",
    methods=["POST"]
)
def admin_login():

    data = request.get_json() or {}

    username = data.get(
        "username",
        ""
    ).strip()

    password = data.get(
        "password",
        ""
    )

    if (
        username != ADMIN_USERNAME
        or
        password != ADMIN_PASSWORD
    ):

        return jsonify({
            "error": "Invalid username or password."
        }), 401

    session[
        "admin_logged_in"
    ] = True

    session[
        "admin_username"
    ] = username

    return jsonify({

        "message": "Login successful.",

        "authenticated": True,

        "admin": {
            "username": username
        }

    })


# ============================================================
# ADMIN LOGOUT
# ============================================================

@app.route(
    "/api/admin/logout",
    methods=["POST"]
)
def admin_logout():

    session.clear()

    return jsonify({
        "message": "Logout successful."
    })


# ============================================================
# ADMIN STATUS
# ============================================================

@app.route(
    "/api/admin/me",
    methods=["GET"]
)
def admin_me():

    if not session.get(
        "admin_logged_in"
    ):

        return jsonify({

            "authenticated": False

        })

    return jsonify({

        "authenticated": True,

        "admin": {

            "username": session.get(
                "admin_username"
            )

        }

    })


# ============================================================
# UPLOADED FILES
# ============================================================

@app.route(
    "/uploads/<path:filename>"
)
def uploaded_file(filename):

    return send_from_directory(

        app.config[
            "UPLOAD_FOLDER"
        ],

        filename

    )


# ============================================================
# ADMIN IMAGE UPLOAD
# ============================================================

@app.route(
    "/api/upload",
    methods=["POST"]
)
def upload_file():

    auth_error = admin_required()

    if auth_error:
        return auth_error

    if "file" not in request.files:

        return jsonify({
            "error": "No file was uploaded."
        }), 400

    file = request.files["file"]

    if file.filename == "":

        return jsonify({
            "error": "No file was selected."
        }), 400

    try:

        filename, image_url = (
            save_uploaded_image(file)
        )

    except ValueError as error:

        return jsonify({
            "error": str(error)
        }), 400

    return jsonify({

        "message": (
            "File uploaded successfully."
        ),

        "filename": filename,

        "url": image_url

    }), 201


# ============================================================
# BOOKING IMAGE UPLOAD
# ============================================================

@app.route(
    "/api/booking-upload",
    methods=["POST"]
)
def booking_image_upload():

    if "file" not in request.files:

        return jsonify({
            "error": "No file was uploaded."
        }), 400

    file = request.files["file"]

    if file.filename == "":

        return jsonify({
            "error": "No file was selected."
        }), 400

    if not allowed_file(
        file.filename
    ):

        return jsonify({
            "error": (
                "Invalid image type. "
                "Only PNG, JPG, JPEG, JFIF, "
                "WEBP and GIF are allowed."
            )
        }), 400

    file.seek(
        0,
        os.SEEK_END
    )

    file_size = file.tell()

    file.seek(0)

    if file_size > (
        5 * 1024 * 1024
    ):

        return jsonify({
            "error": (
                "Inspiration images must be "
                "5 MB or smaller."
            )
        }), 400

    try:

        filename, image_url = (
            save_uploaded_image(file)
        )

    except ValueError as error:

        return jsonify({
            "error": str(error)
        }), 400

    return jsonify({

        "message": (
            "Booking image uploaded successfully."
        ),

        "filename": filename,

        "url": image_url

    }), 201


# ============================================================
# PRODUCTS
# ============================================================

@app.route(
    "/api/products",
    methods=["GET"]
)
def get_products():

    products = Product.query.all()

    return jsonify([
        product_data(product)
        for product in products
    ])


@app.route(
    "/api/products/<product_id>",
    methods=["GET"]
)
def get_product(product_id):

    product = Product.query.get(
        product_id
    )

    if not product:

        return jsonify({
            "error": "Product not found."
        }), 404

    return jsonify(
        product_data(product)
    )


@app.route(
    "/api/products",
    methods=["POST"]
)
def create_product():

    auth_error = admin_required()

    if auth_error:
        return auth_error

    data = request.get_json() or {}

    product_id = data.get(
        "id"
    )

    if not product_id:

        product_id = str(
            uuid.uuid4()
        )

    if Product.query.get(
        product_id
    ):

        return jsonify({
            "error": (
                "A product with this ID "
                "already exists."
            )
        }), 409

    product = Product(

        id=product_id,

        name=data.get(
            "name",
            ""
        ),

        price=float(
            data.get(
                "price",
                0
            )
        ),

        category=data.get(
            "category",
            ""
        ),

        description=data.get(
            "description",
            ""
        ),

        images=data.get(
            "images",
            []
        ),

        specifications=data.get(
            "specifications",
            {}
        )

    )

    db.session.add(product)

    db.session.commit()

    return jsonify(
        product_data(product)
    ), 201


@app.route(
    "/api/products/<product_id>",
    methods=["PUT"]
)
def update_product(product_id):

    auth_error = admin_required()

    if auth_error:
        return auth_error

    product = Product.query.get(
        product_id
    )

    if not product:

        return jsonify({
            "error": "Product not found."
        }), 404

    data = request.get_json() or {}

    if "name" in data:
        product.name = data["name"]

    if "price" in data:

        product.price = float(
            data["price"]
        )

    if "category" in data:
        product.category = data["category"]

    if "description" in data:

        product.description = (
            data["description"]
        )

    if "images" in data:

        product.images = data[
            "images"
        ]

    if "specifications" in data:

        product.specifications = (
            data["specifications"]
        )

    db.session.commit()

    return jsonify(
        product_data(product)
    )


@app.route(
    "/api/products/<product_id>",
    methods=["DELETE"]
)
def delete_product(product_id):

    auth_error = admin_required()

    if auth_error:
        return auth_error

    product = Product.query.get(
        product_id
    )

    if not product:

        return jsonify({
            "error": "Product not found."
        }), 404

    db.session.delete(product)

    db.session.commit()

    return jsonify({
        "message": (
            "Product deleted successfully."
        )
    })


# ============================================================
# CATEGORIES
# ============================================================

@app.route(
    "/api/categories",
    methods=["GET"]
)
def get_categories():

    categories = Category.query.all()

    return jsonify([
        category_data(category)
        for category in categories
    ])


@app.route(
    "/api/categories",
    methods=["POST"]
)
def create_category():

    auth_error = admin_required()

    if auth_error:
        return auth_error

    data = request.get_json() or {}

    category_id = data.get(
        "id"
    )

    if not category_id:

        category_id = str(
            uuid.uuid4()
        )

    category_name = data.get(
        "name",
        ""
    ).strip()

    if not category_name:

        return jsonify({
            "error": (
                "Category name is required."
            )
        }), 400

    if Category.query.get(
        category_id
    ):

        return jsonify({
            "error": (
                "A category with this ID "
                "already exists."
            )
        }), 409

    category = Category(

        id=category_id,

        name=category_name,

        image=data.get(
            "image",
            ""
        )

    )

    db.session.add(category)

    db.session.commit()

    return jsonify(
        category_data(category)
    ), 201


@app.route(
    "/api/categories/<category_id>",
    methods=["PUT"]
)
def update_category(category_id):

    auth_error = admin_required()

    if auth_error:
        return auth_error

    category = Category.query.get(
        category_id
    )

    if not category:

        return jsonify({
            "error": "Category not found."
        }), 404

    data = request.get_json() or {}

    if "name" in data:

        category.name = data[
            "name"
        ]

    if "image" in data:

        category.image = data[
            "image"
        ]

    db.session.commit()

    return jsonify(
        category_data(category)
    )


@app.route(
    "/api/categories/<category_id>",
    methods=["DELETE"]
)
def delete_category(category_id):

    auth_error = admin_required()

    if auth_error:
        return auth_error

    category = Category.query.get(
        category_id
    )

    if not category:

        return jsonify({
            "error": "Category not found."
        }), 404

    db.session.delete(category)

    db.session.commit()

    return jsonify({
        "message": (
            "Category deleted successfully."
        )
    })


# ============================================================
# ORDERS
# ============================================================

@app.route(
    "/api/orders",
    methods=["GET"]
)
def get_orders():

    auth_error = admin_required()

    if auth_error:
        return auth_error

    orders = Order.query.order_by(
        Order.date.desc()
    ).all()

    return jsonify([
        order_data(order)
        for order in orders
    ])


@app.route(
    "/api/orders",
    methods=["POST"]
)
def create_order():

    data = request.get_json() or {}

    order_id = data.get(
        "id"
    )

    if not order_id:

        order_id = (
            "ORD-"
            + str(
                int(
                    datetime.now().timestamp()
                    * 1000
                )
            )
        )

    while Order.query.get(
        order_id
    ):

        order_id = (
            "ORD-"
            + str(uuid.uuid4())
        )

    order = Order(

        id=order_id,

        date=data.get(
            "date",
            datetime.now().isoformat()
        ),

        customer=data.get(
            "customer",
            {}
        ),

        items=data.get(
            "items",
            []
        ),

        subtotal=float(
            data.get(
                "subtotal",
                0
            )
        ),

        total=float(
            data.get(
                "total",
                0
            )
        ),

        delivery_option=data.get(
            "deliveryOption"
        ),

        note=data.get(
            "note"
        ),

        payment_method=data.get(
            "paymentMethod"
        ),

        status=data.get(
            "status",
            "Pending"
        )

    )

    db.session.add(order)

    db.session.commit()

    return jsonify(
        order_data(order)
    ), 201


@app.route(
    "/api/orders/<order_id>",
    methods=["PUT"]
)
def update_order(order_id):

    auth_error = admin_required()

    if auth_error:
        return auth_error

    order = Order.query.get(
        order_id
    )

    if not order:

        return jsonify({
            "error": "Order not found."
        }), 404

    data = request.get_json() or {}

    if "status" in data:

        order.status = data[
            "status"
        ]

    if "note" in data:

        order.note = data[
            "note"
        ]

    db.session.commit()

    return jsonify(
        order_data(order)
    )


@app.route(
    "/api/orders/<order_id>",
    methods=["DELETE"]
)
def delete_order(order_id):

    auth_error = admin_required()

    if auth_error:
        return auth_error

    order = Order.query.get(
        order_id
    )

    if not order:

        return jsonify({
            "error": "Order not found."
        }), 404

    db.session.delete(order)

    db.session.commit()

    return jsonify({
        "message": (
            "Order deleted successfully."
        )
    })


# ============================================================
# BOOKINGS
# ============================================================

@app.route(
    "/api/bookings",
    methods=["GET"]
)
def get_bookings():

    auth_error = admin_required()

    if auth_error:
        return auth_error

    bookings = Booking.query.order_by(
        Booking.date.desc()
    ).all()

    return jsonify([
        booking_data(booking)
        for booking in bookings
    ])


@app.route(
    "/api/bookings",
    methods=["POST"]
)
def create_booking():

    data = request.get_json() or {}

    booking_id = data.get(
        "id"
    )

    if not booking_id:

        booking_id = (
            "BOOK-"
            + str(
                int(
                    datetime.now().timestamp()
                    * 1000
                )
            )
        )

    while Booking.query.get(
        booking_id
    ):

        booking_id = (
            "BOOK-"
            + str(uuid.uuid4())
        )

    booking = Booking(

        id=booking_id,

        date=data.get(
            "date",
            datetime.now().isoformat()
        ),

        customer=data.get(
            "customer",
            {}
        ),

        service=data.get(
            "service",
            ""
        ),

        preferred_date=data.get(
            "preferredDate",
            ""
        ),

        preferred_time=data.get(
            "preferredTime",
            ""
        ),

        message=data.get(
            "message",
            ""
        ),

        note=data.get(
            "note",
            ""
        ),

        inspiration_image=data.get(
            "inspirationImage",
            ""
        ),

        status=data.get(
            "status",
            "Pending"
        )

    )

    db.session.add(booking)

    db.session.commit()

    return jsonify(
        booking_data(booking)
    ), 201


@app.route(
    "/api/bookings/<booking_id>",
    methods=["PUT"]
)
def update_booking(booking_id):

    auth_error = admin_required()

    if auth_error:
        return auth_error

    booking = Booking.query.get(
        booking_id
    )

    if not booking:

        return jsonify({
            "error": "Booking not found."
        }), 404

    data = request.get_json() or {}

    if "status" in data:

        booking.status = data[
            "status"
        ]

    if "note" in data:

        booking.note = data[
            "note"
        ]

    db.session.commit()

    return jsonify(
        booking_data(booking)
    )


@app.route(
    "/api/bookings/<booking_id>",
    methods=["DELETE"]
)
def delete_booking(booking_id):

    auth_error = admin_required()

    if auth_error:
        return auth_error

    booking = Booking.query.get(
        booking_id
    )

    if not booking:

        return jsonify({
            "error": "Booking not found."
        }), 404

    db.session.delete(booking)

    db.session.commit()

    return jsonify({
        "message": (
            "Booking deleted successfully."
        )
    })


# ============================================================
# REVIEWS
# ============================================================

@app.route(
    "/api/reviews",
    methods=["GET"]
)
def get_reviews():

    product_id = request.args.get(
        "productId"
    )

    if not product_id:

        auth_error = admin_required()

        if auth_error:
            return auth_error

    query = Review.query

    if product_id:

        query = query.filter_by(
            product_id=product_id,
            status="Approved"
        )

    reviews = query.order_by(
        Review.date.desc()
    ).all()

    return jsonify([
        review_data(review)
        for review in reviews
    ])


@app.route(
    "/api/reviews",
    methods=["POST"]
)
def create_review():

    data = request.get_json() or {}

    product_id = data.get(
        "productId"
    )

    name = data.get(
        "name",
        ""
    ).strip()

    comment = data.get(
        "comment",
        ""
    ).strip()

    if not product_id:

        return jsonify({
            "error": "Product ID is required."
        }), 400

    if not name:

        return jsonify({
            "error": "Name is required."
        }), 400

    if not comment:

        return jsonify({
            "error": "Comment is required."
        }), 400

    product = Product.query.get(
        product_id
    )

    if not product:

        return jsonify({
            "error": "Product not found."
        }), 404

    try:

        rating = int(
            data.get(
                "rating"
            )
        )

    except (
        TypeError,
        ValueError
    ):

        return jsonify({
            "error": "Rating must be a number."
        }), 400

    if rating < 1 or rating > 5:

        return jsonify({
            "error": (
                "Rating must be between 1 and 5."
            )
        }), 400

    review_id = data.get(
        "id"
    )

    if not review_id:

        review_id = (
            "REV-"
            + str(
                int(
                    datetime.now().timestamp()
                    * 1000
                )
            )
        )

    while Review.query.get(
        review_id
    ):

        review_id = (
            "REV-"
            + str(uuid.uuid4())
        )

    review = Review(

        id=review_id,

        product_id=product_id,

        name=name,

        rating=rating,

        comment=comment,

        date=data.get(
            "date",
            datetime.now().isoformat()
        ),

        status=data.get(
            "status",
            "Approved"
        )

    )

    db.session.add(review)

    db.session.commit()

    return jsonify(
        review_data(review)
    ), 201


@app.route(
    "/api/reviews/<review_id>",
    methods=["PUT"]
)
def update_review(review_id):

    auth_error = admin_required()

    if auth_error:
        return auth_error

    review = Review.query.get(
        review_id
    )

    if not review:

        return jsonify({
            "error": "Review not found."
        }), 404

    data = request.get_json() or {}

    if "name" in data:

        review.name = data[
            "name"
        ]

    if "rating" in data:

        try:

            rating = int(
                data["rating"]
            )

        except (
            TypeError,
            ValueError
        ):

            return jsonify({
                "error": (
                    "Rating must be a number."
                )
            }), 400

        if rating < 1 or rating > 5:

            return jsonify({
                "error": (
                    "Rating must be between 1 and 5."
                )
            }), 400

        review.rating = rating

    if "comment" in data:

        review.comment = data[
            "comment"
        ]

    if "status" in data:

        if data["status"] not in {
            "Approved",
            "Pending",
            "Hidden"
        }:

            return jsonify({
                "error": (
                    "Invalid review status."
                )
            }), 400

        review.status = data[
            "status"
        ]

    db.session.commit()

    return jsonify(
        review_data(review)
    )


@app.route(
    "/api/reviews/<review_id>",
    methods=["DELETE"]
)
def delete_review(review_id):

    auth_error = admin_required()

    if auth_error:
        return auth_error

    review = Review.query.get(
        review_id
    )

    if not review:

        return jsonify({
            "error": "Review not found."
        }), 404

    db.session.delete(review)

    db.session.commit()

    return jsonify({
        "message": (
            "Review deleted successfully."
        )
    })


# ============================================================
# DATABASE INITIALIZATION
# ============================================================

with app.app_context():

    db.create_all()


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )