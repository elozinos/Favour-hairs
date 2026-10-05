from database import db


class Product(db.Model):

    id = db.Column(
        db.String(100),
        primary_key=True
    )

    name = db.Column(
        db.String(150),
        nullable=False
    )

    price = db.Column(
        db.Float,
        nullable=False
    )

    category = db.Column(
        db.String(100),
        nullable=False
    )

    description = db.Column(
        db.Text,
        nullable=True
    )

    images = db.Column(
        db.JSON,
        nullable=False,
        default=list
    )

    specifications = db.Column(
        db.JSON,
        nullable=False,
        default=dict
    )

    featured = db.Column(
        db.Boolean,
        nullable=False,
        default=False
    )


class Category(db.Model):

    id = db.Column(
        db.String(100),
        primary_key=True
    )

    name = db.Column(
        db.String(100),
        nullable=False,
        unique=True
    )

    image = db.Column(
        db.Text,
        nullable=True
    )


class Order(db.Model):

    id = db.Column(
        db.String(100),
        primary_key=True
    )

    date = db.Column(
        db.String(100),
        nullable=False
    )

    customer = db.Column(
        db.JSON,
        nullable=False,
        default=dict
    )

    items = db.Column(
        db.JSON,
        nullable=False,
        default=list
    )

    subtotal = db.Column(
        db.Float,
        nullable=False,
        default=0
    )

    total = db.Column(
        db.Float,
        nullable=False,
        default=0
    )

    delivery_option = db.Column(
        db.String(100),
        nullable=True
    )

    note = db.Column(
        db.Text,
        nullable=True
    )

    payment_method = db.Column(
        db.String(100),
        nullable=True
    )

    status = db.Column(
        db.String(50),
        nullable=False,
        default="Pending"
    )


class Booking(db.Model):

    id = db.Column(
        db.String(100),
        primary_key=True
    )

    date = db.Column(
        db.String(100),
        nullable=False
    )

    customer = db.Column(
        db.JSON,
        nullable=False,
        default=dict
    )

    service = db.Column(
        db.String(150),
        nullable=False
    )

    preferred_date = db.Column(
        db.String(100),
        nullable=False
    )

    preferred_time = db.Column(
        db.String(100),
        nullable=False
    )

    message = db.Column(
        db.Text,
        nullable=True
    )

    note = db.Column(
        db.Text,
        nullable=True
    )

    inspiration_image = db.Column(
        db.Text,
        nullable=True
    )

    status = db.Column(
        db.String(50),
        nullable=False,
        default="Pending"
    )


class Review(db.Model):

    id = db.Column(
        db.String(100),
        primary_key=True
    )

    product_id = db.Column(
        db.String(100),
        nullable=False
    )

    name = db.Column(
        db.String(150),
        nullable=False
    )

    rating = db.Column(
        db.Integer,
        nullable=False
    )

    comment = db.Column(
        db.Text,
        nullable=False
    )

    date = db.Column(
        db.String(100),
        nullable=False
    )

    status = db.Column(
        db.String(50),
        nullable=False,
        default="Approved"
    )
