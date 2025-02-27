# Generated by Django 3.0.14 on 2023-10-07 01:59

import cms.models.fields
from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.db.models.manager
import django.utils.timezone
import django_fsm
import djangocms_text_ckeditor.fields
import filer.fields.image
import parler.fields
import parler.models
import phonenumber_field.modelfields
import shop.models.address
import shop.models.fields
import shop.models.product
import shop.money.fields
import shop.payment.workflows
import shop.shipping.workflows
import shop_paypal.payment
import shop_stripe.workflows


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('cms', '0022_auto_20180620_1551'),
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.FILER_IMAGE_MODEL),
        ('email_auth', '0005_auto_20191123_2051'),
    ]

    operations = [
        migrations.CreateModel(
            name='BillingAddress',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('priority', models.SmallIntegerField(db_index=True, default=0, help_text='Priority for using this address')),
                ('name', models.CharField(max_length=1024, verbose_name='Full name')),
                ('company_name', models.CharField(blank=True, max_length=1024, null=True, verbose_name='Company name')),
                ('address', models.CharField(max_length=1024, verbose_name='Address line')),
                ('house_number', models.CharField(max_length=12, verbose_name='House number')),
                ('postal_code', models.CharField(max_length=12, verbose_name='ZIP / Postal code')),
                ('city', models.CharField(max_length=1024, verbose_name='City')),
                ('country', shop.models.address.CountryField(verbose_name='Country')),
            ],
            options={
                'verbose_name': 'Billing Address',
                'verbose_name_plural': 'Billing Addresses',
            },
        ),
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated at')),
                ('extra', shop.models.fields.JSONField(verbose_name='Arbitrary information for this cart')),
                ('billing_address', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.SET_DEFAULT, related_name='+', to='myshop.BillingAddress')),
            ],
        ),
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='customer', serialize=False, to=settings.AUTH_USER_MODEL)),
                ('recognized', shop.models.fields.ChoiceEnumField(help_text='Designates the state the customer is recognized as.', verbose_name='Recognized as')),
                ('last_access', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Last accessed')),
                ('extra', shop.models.fields.JSONField(editable=False, verbose_name='Extra information about this customer')),
                ('number', models.PositiveIntegerField(default=None, null=True, unique=True, verbose_name='Customer Number')),
                ('salutation', models.CharField(choices=[('mrs', 'Mrs.'), ('mr', 'Mr.'), ('na', '(n/a)')], max_length=5, verbose_name='Salutation')),
                ('phone_number', phonenumber_field.modelfields.PhoneNumberField(blank=True, max_length=128, null=True, region=None, verbose_name='Phone number')),
            ],
        ),
        migrations.CreateModel(
            name='Delivery',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('shipping_id', models.CharField(blank=True, help_text="The transaction processor's reference", max_length=255, null=True, verbose_name='Shipping ID')),
                ('fulfilled_at', models.DateTimeField(blank=True, help_text='Timestamp of delivery fulfillment', null=True, verbose_name='Fulfilled at')),
                ('shipped_at', models.DateTimeField(blank=True, help_text='Timestamp of delivery shipment', null=True, verbose_name='Shipped at')),
                ('shipping_method', models.CharField(help_text='The shipping backend used to deliver items of this order', max_length=50, verbose_name='Shipping method')),
            ],
            options={
                'verbose_name': 'Delivery',
                'verbose_name_plural': 'Deliveries',
                'get_latest_by': 'shipped_at',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Manufacturer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True, verbose_name='Name')),
            ],
        ),
        migrations.CreateModel(
            name='OperatingSystem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True, verbose_name='Name')),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', django_fsm.FSMField(default='new', max_length=50, protected=True, verbose_name='Status')),
                ('currency', models.CharField(editable=False, help_text='Currency in which this order was concluded', max_length=7)),
                ('_subtotal', models.DecimalField(decimal_places=2, max_digits=30, verbose_name='Subtotal')),
                ('_total', models.DecimalField(decimal_places=2, max_digits=30, verbose_name='Total')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated at')),
                ('extra', shop.models.fields.JSONField(help_text='Arbitrary information for this order object on the moment of purchase.', verbose_name='Extra fields')),
                ('stored_request', shop.models.fields.JSONField(help_text='Parts of the Request objects on the moment of purchase.')),
                ('number', models.PositiveIntegerField(default=None, null=True, unique=True, verbose_name='Order Number')),
                ('shipping_address_text', models.TextField(blank=True, help_text='Shipping address at the moment of purchase.', null=True, verbose_name='Shipping Address')),
                ('billing_address_text', models.TextField(blank=True, help_text='Billing address at the moment of purchase.', null=True, verbose_name='Billing Address')),
                ('token', models.CharField(editable=False, help_text='Secret key to verify ownership on detail view without requiring authentication.', max_length=40, null=True, verbose_name='Token')),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='orders', to='myshop.Customer', verbose_name='Customer')),
            ],
            options={
                'verbose_name': 'Order',
                'verbose_name_plural': 'Orders',
            },
            bases=(shop.payment.workflows.ManualPaymentWorkflowMixin, shop.payment.workflows.CancelOrderWorkflowMixin, shop.shipping.workflows.PartialDeliveryWorkflowMixin, shop_paypal.payment.OrderWorkflowMixin, shop_stripe.workflows.OrderWorkflowMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated at')),
                ('active', models.BooleanField(default=True, help_text='Is this product publicly visible.', verbose_name='Active')),
                ('product_name', models.CharField(max_length=255, verbose_name='Product Name')),
                ('slug', models.SlugField(unique=True, verbose_name='Slug')),
                ('order', models.PositiveIntegerField(db_index=True, verbose_name='Sort by')),
            ],
            options={
                'verbose_name': 'Product',
                'verbose_name_plural': 'Products',
                'ordering': ('order',),
            },
            bases=(shop.models.product.CMSPageReferenceMixin, parler.models.TranslatableModelMixin, models.Model),
        ),
        migrations.CreateModel(
            name='SmartCard',
            fields=[
                ('product_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='myshop.Product')),
                ('unit_price', shop.money.fields.MoneyField(decimal_places=3, help_text='Net price for this product', verbose_name='Unit price')),
                ('card_type', models.CharField(choices=[('SD', 'SD'), ('micro SD', 'micro SD'), ('SDXC', 'SDXC'), ('micro SDXC', 'micro SDXC'), ('SDHC', 'SDHC'), ('micro SDHC', 'micro SDHC'), ('SDHC II', 'SDHC II'), ('micro SDHC II', 'micro SDHC II')], max_length=15, verbose_name='Card Type')),
                ('speed', models.CharField(choices=[('4', '4 MB/s'), ('20', '20 MB/s'), ('30', '30 MB/s'), ('40', '40 MB/s'), ('48', '48 MB/s'), ('80', '80 MB/s'), ('95', '95 MB/s'), ('280', '280 MB/s')], max_length=8, verbose_name='Transfer Speed')),
                ('product_code', models.CharField(max_length=255, unique=True, verbose_name='Product code')),
                ('storage', models.PositiveIntegerField(help_text='Storage capacity in GB', verbose_name='Storage Capacity')),
                ('quantity', models.PositiveIntegerField(default=0, help_text='Available quantity in stock', validators=[django.core.validators.MinValueValidator(0)], verbose_name='Quantity')),
            ],
            options={
                'verbose_name': 'Smart Card',
                'verbose_name_plural': 'Smart Cards',
                'ordering': ['order'],
            },
            bases=(shop.models.product.AvailableProductMixin, 'myshop.product'),
            managers=[
                ('default_manager', django.db.models.manager.Manager()),
                ('objects', django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name='SmartPhoneModel',
            fields=[
                ('product_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='myshop.Product')),
                ('battery_type', models.PositiveSmallIntegerField(choices=[(1, 'Lithium Polymer (Li-Poly)'), (2, 'Lithium Ion (Li-Ion)')], verbose_name='Battery type')),
                ('battery_capacity', models.PositiveIntegerField(help_text='Battery capacity in mAh', verbose_name='Capacity')),
                ('ram_storage', models.PositiveIntegerField(help_text='RAM storage in MB', verbose_name='RAM')),
                ('wifi_connectivity', models.PositiveIntegerField(choices=[(1, '802.11 b/g/n')], help_text='WiFi Connectivity', verbose_name='WiFi')),
                ('bluetooth', models.PositiveIntegerField(choices=[(1, 'Bluetooth 4.0'), (2, 'Bluetooth 3.0'), (3, 'Bluetooth 2.1')], help_text='Bluetooth Connectivity', verbose_name='Bluetooth')),
                ('gps', models.BooleanField(default=False, help_text='GPS integrated', verbose_name='GPS')),
                ('width', models.DecimalField(decimal_places=1, help_text='Width in mm', max_digits=4, verbose_name='Width')),
                ('height', models.DecimalField(decimal_places=1, help_text='Height in mm', max_digits=4, verbose_name='Height')),
                ('weight', models.DecimalField(decimal_places=1, help_text='Weight in gram', max_digits=5, verbose_name='Weight')),
                ('screen_size', models.DecimalField(decimal_places=2, help_text='Diagonal screen size in inch', max_digits=4, verbose_name='Screen size')),
                ('operating_system', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myshop.OperatingSystem', verbose_name='Operating System')),
            ],
            options={
                'verbose_name': 'Smart Phone',
                'verbose_name_plural': 'Smart Phones',
            },
            bases=('myshop.product',),
            managers=[
                ('default_manager', django.db.models.manager.Manager()),
                ('objects', django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name='ShippingAddress',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('priority', models.SmallIntegerField(db_index=True, default=0, help_text='Priority for using this address')),
                ('name', models.CharField(max_length=1024, verbose_name='Full name')),
                ('company_name', models.CharField(blank=True, max_length=1024, null=True, verbose_name='Company name')),
                ('address', models.CharField(max_length=1024, verbose_name='Address line')),
                ('house_number', models.CharField(max_length=12, verbose_name='House number')),
                ('postal_code', models.CharField(max_length=12, verbose_name='ZIP / Postal code')),
                ('city', models.CharField(max_length=1024, verbose_name='City')),
                ('country', shop.models.address.CountryField(verbose_name='Country')),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myshop.Customer')),
            ],
            options={
                'verbose_name': 'Shipping Address',
                'verbose_name_plural': 'Shipping Addresses',
            },
        ),
        migrations.CreateModel(
            name='ProductPage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('page', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cms.Page')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myshop.Product')),
            ],
            options={
                'verbose_name': 'Category',
                'verbose_name_plural': 'Categories',
                'abstract': False,
                'unique_together': {('page', 'product')},
            },
        ),
        migrations.CreateModel(
            name='ProductImage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.SmallIntegerField(default=0)),
                ('image', filer.fields.image.FilerImageField(on_delete=django.db.models.deletion.CASCADE, to=settings.FILER_IMAGE_MODEL)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myshop.Product')),
            ],
            options={
                'verbose_name': 'Product Image',
                'verbose_name_plural': 'Product Images',
                'ordering': ['order'],
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='product',
            name='cms_pages',
            field=models.ManyToManyField(help_text='Choose list view this product shall appear on.', through='myshop.ProductPage', to='cms.Page'),
        ),
        migrations.AddField(
            model_name='product',
            name='images',
            field=models.ManyToManyField(through='myshop.ProductImage', to=settings.FILER_IMAGE_MODEL),
        ),
        migrations.AddField(
            model_name='product',
            name='manufacturer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myshop.Manufacturer', verbose_name='Manufacturer'),
        ),
        migrations.AddField(
            model_name='product',
            name='polymorphic_ctype',
            field=models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='polymorphic_myshop.product_set+', to='contenttypes.ContentType'),
        ),
        migrations.CreateModel(
            name='OrderPayment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', shop.money.fields.MoneyField(help_text='How much was paid with this particular transfer.', verbose_name='Amount paid')),
                ('transaction_id', models.CharField(help_text="The transaction processor's reference", max_length=255, verbose_name='Transaction ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Received at')),
                ('payment_method', models.CharField(help_text='The payment backend used to process the purchase', max_length=50, verbose_name='Payment method')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myshop.Order', verbose_name='Order')),
            ],
            options={
                'verbose_name': 'Order payment',
                'verbose_name_plural': 'Order payments',
            },
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product_name', models.CharField(blank=True, help_text='Product name at the moment of purchase.', max_length=255, null=True, verbose_name='Product name')),
                ('product_code', models.CharField(blank=True, help_text='Product code at the moment of purchase.', max_length=255, null=True, verbose_name='Product code')),
                ('_unit_price', models.DecimalField(decimal_places=2, help_text='Products unit price at the moment of purchase.', max_digits=30, null=True, verbose_name='Unit price')),
                ('_line_total', models.DecimalField(decimal_places=2, help_text='Line total on the invoice at the moment of purchase.', max_digits=30, null=True, verbose_name='Line Total')),
                ('extra', shop.models.fields.JSONField(help_text='Arbitrary information for this order item', verbose_name='Extra fields')),
                ('quantity', models.PositiveIntegerField(verbose_name='Ordered quantity')),
                ('canceled', models.BooleanField(default=False, verbose_name='Item canceled ')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='myshop.Order', verbose_name='Order')),
                ('product', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='myshop.Product', verbose_name='Product')),
            ],
        ),
        migrations.CreateModel(
            name='DeliveryItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField(default=0, verbose_name='Delivered quantity')),
                ('delivery', models.ForeignKey(help_text='Refer to the shipping provider used to ship this item', on_delete=django.db.models.deletion.CASCADE, related_name='items', to='myshop.Delivery', verbose_name='Delivery')),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='deliver_item', to='myshop.OrderItem', verbose_name='Ordered item')),
            ],
        ),
        migrations.AddField(
            model_name='delivery',
            name='order',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myshop.Order'),
        ),
        migrations.CreateModel(
            name='CartItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product_code', models.CharField(blank=True, help_text='Product code of added item.', max_length=255, null=True, verbose_name='Product code')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated at')),
                ('extra', shop.models.fields.JSONField(verbose_name='Arbitrary information for this cart item')),
                ('quantity', models.PositiveIntegerField()),
                ('cart', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='myshop.Cart')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myshop.Product')),
            ],
        ),
        migrations.AddField(
            model_name='cart',
            name='customer',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='cart', to='myshop.Customer', verbose_name='Customer'),
        ),
        migrations.AddField(
            model_name='cart',
            name='shipping_address',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.SET_DEFAULT, related_name='+', to='myshop.ShippingAddress'),
        ),
        migrations.AddField(
            model_name='billingaddress',
            name='customer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myshop.Customer'),
        ),
        migrations.CreateModel(
            name='SmartPhoneVariant',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product_code', models.CharField(max_length=255, unique=True, verbose_name='Product code')),
                ('unit_price', shop.money.fields.MoneyField(decimal_places=3, help_text='Net price for this product', verbose_name='Unit price')),
                ('storage', models.PositiveIntegerField(help_text='Internal storage in GB', verbose_name='Internal Storage')),
                ('quantity', models.PositiveIntegerField(default=0, help_text='Available quantity in stock', validators=[django.core.validators.MinValueValidator(0)], verbose_name='Quantity')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='variants', to='myshop.SmartPhoneModel', verbose_name='Smartphone Model')),
            ],
            bases=(shop.models.product.AvailableProductMixin, models.Model),
        ),
        migrations.CreateModel(
            name='ProductTranslation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('language_code', models.CharField(db_index=True, max_length=15, verbose_name='Language')),
                ('caption', djangocms_text_ckeditor.fields.HTMLField(blank=True, help_text="Short description used in the catalog's list view of products.", null=True, verbose_name='Caption')),
                ('master', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='translations', to='myshop.Product')),
            ],
            options={
                'unique_together': {('language_code', 'master')},
            },
            bases=(parler.models.TranslatedFieldsModelMixin, models.Model),
        ),
        migrations.AlterUniqueTogether(
            name='delivery',
            unique_together={('shipping_method', 'shipping_id')},
        ),
        migrations.CreateModel(
            name='Commodity',
            fields=[
                ('product_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='myshop.Product')),
                ('unit_price', shop.money.fields.MoneyField(decimal_places=3, help_text='Net price for this product', verbose_name='Unit price')),
                ('product_code', models.CharField(max_length=255, unique=True, verbose_name='Product code')),
                ('quantity', models.PositiveIntegerField(default=0, help_text='Available quantity in stock', validators=[django.core.validators.MinValueValidator(0)], verbose_name='Quantity')),
                ('placeholder', cms.models.fields.PlaceholderField(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, slotname='Commodity Details', to='cms.Placeholder')),
            ],
            options={
                'verbose_name': 'Commodity',
                'verbose_name_plural': 'Commodities',
            },
            bases=(shop.models.product.AvailableProductMixin, 'myshop.product'),
            managers=[
                ('default_manager', django.db.models.manager.Manager()),
                ('objects', django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name='SmartPhoneModelTranslation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('language_code', models.CharField(db_index=True, max_length=15, verbose_name='Language')),
                ('description', djangocms_text_ckeditor.fields.HTMLField(help_text="Full description used in the catalog's detail view of Smart Phones.", verbose_name='Description')),
                ('master', parler.fields.TranslationsForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='multilingual', to='myshop.SmartPhoneModel')),
            ],
            options={
                'verbose_name': 'Smart Phone Translation',
                'db_table': 'myshop_smartphonemodel_translation',
                'db_tablespace': '',
                'managed': True,
                'default_permissions': (),
                'unique_together': {('language_code', 'master')},
            },
            bases=(parler.models.TranslatedFieldsModelMixin, models.Model),
        ),
        migrations.CreateModel(
            name='SmartCardTranslation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('language_code', models.CharField(db_index=True, max_length=15, verbose_name='Language')),
                ('description', djangocms_text_ckeditor.fields.HTMLField(help_text="Full description used in the catalog's detail view of Smart Cards.", verbose_name='Description')),
                ('master', parler.fields.TranslationsForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='multilingual', to='myshop.SmartCard')),
            ],
            options={
                'verbose_name': 'Smart Card Translation',
                'db_table': 'myshop_smartcard_translation',
                'db_tablespace': '',
                'managed': True,
                'default_permissions': (),
                'unique_together': {('language_code', 'master')},
            },
            bases=(parler.models.TranslatedFieldsModelMixin, models.Model),
        ),
    ]
