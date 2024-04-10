# Generated by Django 4.1.7 on 2023-03-02 06:03

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Address",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "locality",
                    models.CharField(max_length=150, verbose_name="Nearest Location"),
                ),
                ("city", models.CharField(max_length=150, verbose_name="City")),
                ("state", models.CharField(max_length=150, verbose_name="State")),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="User",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Brand",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=50, verbose_name="Brand Name")),
                (
                    "logo",
                    models.ImageField(
                        blank=True,
                        null=True,
                        upload_to="category",
                        verbose_name="Brand Logo",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Category",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "title",
                    models.CharField(max_length=50, verbose_name="Category Title"),
                ),
                ("slug", models.SlugField(max_length=55, verbose_name="Category Slug")),
                (
                    "description",
                    models.TextField(blank=True, verbose_name="Category Description"),
                ),
                (
                    "category_image",
                    models.ImageField(
                        blank=True,
                        null=True,
                        upload_to="category",
                        verbose_name="Category Image",
                    ),
                ),
                ("is_active", models.BooleanField(verbose_name="Is Active?")),
                ("is_featured", models.BooleanField(verbose_name="Is Featured?")),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Created Date"
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, verbose_name="Updated Date"),
                ),
            ],
            options={
                "verbose_name_plural": "Categories",
                "ordering": ("-created_at",),
            },
        ),
        migrations.CreateModel(
            name="Product",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "title",
                    models.CharField(max_length=150, verbose_name="Product Title"),
                ),
                ("slug", models.SlugField(max_length=160, verbose_name="Product Slug")),
                (
                    "sku",
                    models.CharField(
                        max_length=255,
                        unique=True,
                        verbose_name="Unique Product ID (SKU)",
                    ),
                ),
                (
                    "short_description",
                    models.TextField(verbose_name="Short Description"),
                ),
                (
                    "detail_description",
                    models.TextField(
                        blank=True, null=True, verbose_name="Detail Description"
                    ),
                ),
                (
                    "product_image",
                    models.ImageField(
                        blank=True,
                        null=True,
                        upload_to="product",
                        verbose_name="Product Image",
                    ),
                ),
                ("price", models.DecimalField(decimal_places=2, max_digits=8)),
                ("stock", models.PositiveIntegerField(verbose_name="Stock")),
                ("is_active", models.BooleanField(verbose_name="Is Active?")),
                ("is_featured", models.BooleanField(verbose_name="Is Featured?")),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Created Date"
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, verbose_name="Updated Date"),
                ),
                (
                    "brand",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="store.brand",
                        verbose_name="Product Brand",
                    ),
                ),
                (
                    "category",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="store.category",
                        verbose_name="Product Categoy",
                    ),
                ),
            ],
            options={"verbose_name_plural": "Products", "ordering": ("-created_at",),},
        ),
        migrations.CreateModel(
            name="Wishlist",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Created Date"
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, verbose_name="Updated Date"),
                ),
                (
                    "product",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="store.product",
                        verbose_name="Product",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="User",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Order",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("quantity", models.PositiveIntegerField(verbose_name="Quantity")),
                (
                    "ordered_date",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Ordered Date"
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("Pending", "Pending"),
                            ("Accepted", "Accepted"),
                            ("Packed", "Packed"),
                            ("On The Way", "On The Way"),
                            ("Delivered", "Delivered"),
                            ("Cancelled", "Cancelled"),
                        ],
                        default="Pending",
                        max_length=50,
                    ),
                ),
                (
                    "address",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="store.address",
                        verbose_name="Shipping Address",
                    ),
                ),
                (
                    "product",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="store.product",
                        verbose_name="Product",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="User",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Cart",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "quantity",
                    models.PositiveIntegerField(default=1, verbose_name="Quantity"),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Created Date"
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, verbose_name="Updated Date"),
                ),
                (
                    "product",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="store.product",
                        verbose_name="Product",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="User",
                    ),
                ),
            ],
        ),
    ]
