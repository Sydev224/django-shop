
from decimal import Decimal
from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import ugettext_lazy as _
from djangocms_text_ckeditor.fields import HTMLField
from polymorphic.query import PolymorphicQuerySet
from parler.managers import TranslatableManager, TranslatableQuerySet
from parler.models import TranslatableModelMixin, TranslatedFieldsModel, TranslatedFields
from parler.fields import TranslatedField
from cms.models.fields import PlaceholderField
from shop.money import Money, MoneyMaker
from shop.money.fields import MoneyField
from shop.models.product import BaseProduct, BaseProductManager, AvailableProductMixin, CMSPageReferenceMixin
from shop.models.defaults.cart import Cart
from shop.models.defaults.cart_item import CartItem
from shop.models.order import BaseOrderItem
from shop.models.defaults.delivery import Delivery
from shop.models.defaults.delivery_item import DeliveryItem
from shop.models.defaults.order import Order
from shop.models.defaults.mapping import ProductPage, ProductImage
from shop_sendcloud.models.address import BillingAddress, ShippingAddress
from shop_sendcloud.models.customer import Customer


__all__ = ['Cart', 'CartItem', 'Order', 'Delivery', 'DeliveryItem',
           'BillingAddress', 'ShippingAddress', 'Customer',]


class OrderItem(BaseOrderItem):
    quantity = models.PositiveIntegerField(_("Ordered quantity"))
    canceled = models.BooleanField(_("Item canceled "), default=False)

    def populate_from_cart_item(self, cart_item, request):
        super().populate_from_cart_item(cart_item, request)
        # the product's unit_price must be fetched from the product's variant
        try:
            variant = cart_item.product.get_product_variant(
                product_code=cart_item.product_code)
            self._unit_price = Decimal(variant.unit_price)
        except (KeyError, ObjectDoesNotExist) as e:
            raise CartItem.DoesNotExist(e)


class Manufacturer(models.Model):
    name = models.CharField(
        _("Name"),
        max_length=50,
        unique=True,
    )

    def __str__(self):
        return self.name


class ProductQuerySet(TranslatableQuerySet, PolymorphicQuerySet):
    pass


class ProductManager(BaseProductManager, TranslatableManager):
    queryset_class = ProductQuerySet

    def get_queryset(self):
        qs = self.queryset_class(self.model, using=self._db)
        return qs.prefetch_related('translations')


class Product(CMSPageReferenceMixin, TranslatableModelMixin, BaseProduct):
    """
    Base class to describe a polymorphic product. Here we declare common fields available in all of
    our different product types. These common fields are also used to build up the view displaying
    a list of all products.
    """
    product_name = models.CharField(
        _("Product Name"),
        max_length=255,
    )

    slug = models.SlugField(
        _("Slug"),
        unique=True,
    )

    caption = TranslatedField()

    # common product properties
    manufacturer = models.ForeignKey(
        Manufacturer,
        on_delete=models.CASCADE,
        verbose_name=_("Manufacturer"),
    )

    # controlling the catalog
    order = models.PositiveIntegerField(
        _("Sort by"),
        db_index=True,
    )

    cms_pages = models.ManyToManyField(
        'cms.Page',
        through=ProductPage,
        help_text=_("Choose list view this product shall appear on."),
    )

    images = models.ManyToManyField(
        'filer.Image',
        through=ProductImage,
    )

    class Meta:
        ordering = ('order',)
        verbose_name = _("Product")
        verbose_name_plural = _("Products")

    objects = ProductManager()

    # filter expression used to lookup for a product item using the Select2 widget
    lookup_fields = ['product_name__icontains']

    def __str__(self):
        return self.product_name

    @property
    def sample_image(self):
        return self.images.first()


class ProductTranslation(TranslatedFieldsModel):
    master = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='translations',
        null=True,
    )

    caption = HTMLField(
        verbose_name=_("Caption"),
        blank=True,
        null=True,
        configuration='CKEDITOR_SETTINGS_CAPTION',
        help_text=_(
            "Short description used in the catalog's list view of products."),
    )

    class Meta:
        unique_together = [('language_code', 'master')]


class Commodity(AvailableProductMixin, Product):
    """
    This Commodity model inherits from polymorphic Product, and therefore has to be redefined.
    """
    unit_price = MoneyField(
        _("Unit price"),
        decimal_places=3,
        help_text=_("Net price for this product"),
    )

    product_code = models.CharField(
        _("Product code"),
        max_length=255,
        unique=True,
    )

    quantity = models.PositiveIntegerField(
        _("Quantity"),
        default=0,
        validators=[MinValueValidator(0)],
        help_text=_("Available quantity in stock")
    )

    # controlling the catalog
    placeholder = PlaceholderField("Commodity Details")
    show_breadcrumb = True  # hard coded to always show the product's breadcrumb

    class Meta:
        verbose_name = _("Commodity")
        verbose_name_plural = _("Commodities")

    default_manager = ProductManager()

    def get_price(self, request):
        return self.unit_price


class SmartCard(AvailableProductMixin, Product):
    multilingual = TranslatedFields(
        description=HTMLField(
            verbose_name=_("Description"),
            configuration='CKEDITOR_SETTINGS_DESCRIPTION',
            help_text=_(
                "Full description used in the catalog's detail view of Smart Cards."),
        ),
    )
    unit_price = MoneyField(
        _("Unit price"),
        decimal_places=3,
        help_text=_("Net price for this product"),
    )

    card_type = models.CharField(
        _("Card Type"),
        choices=[2 * ('{}{}'.format(s, t),)
                 for t in ['SD', 'SDXC', 'SDHC', 'SDHC II'] for s in ['', 'micro ']],
        max_length=15,
    )

    speed = models.CharField(
        _("Transfer Speed"),
        choices=[(str(s), "{} MB/s".format(s))
                 for s in [4, 20, 30, 40, 48, 80, 95, 280]],
        max_length=8,
    )

    product_code = models.CharField(
        _("Product code"),
        max_length=255,
        unique=True,
    )

    storage = models.PositiveIntegerField(
        _("Storage Capacity"),
        help_text=_("Storage capacity in GB"),
    )

    quantity = models.PositiveIntegerField(
        _("Quantity"),
        default=0,
        validators=[MinValueValidator(0)],
        help_text=_("Available quantity in stock")
    )

    class Meta:
        verbose_name = _("Smart Card")
        verbose_name_plural = _("Smart Cards")
        ordering = ['order']

    # filter expression used to lookup for a product item using the Select2 widget
    lookup_fields = ['product_code__startswith', 'product_name__icontains']

    def get_price(self, request):
        return self.unit_price

    default_manager = ProductManager()


class OperatingSystem(models.Model):
    name = models.CharField(
        _("Name"),
        max_length=50,
        unique=True,
    )

    def __str__(self):
        return self.name


class SmartPhoneModel(Product):
    """
    A generic smart phone model, which must be concretized by a `SmartPhoneVariant` - see below.
    """
    BATTERY_TYPES = [
        (1, "Lithium Polymer (Li-Poly)"),
        (2, "Lithium Ion (Li-Ion)"),
    ]
    WIFI_CONNECTIVITY = [
        (1, "802.11 b/g/n"),
    ]
    BLUETOOTH_CONNECTIVITY = [
        (1, "Bluetooth 4.0"),
        (2, "Bluetooth 3.0"),
        (3, "Bluetooth 2.1"),
    ]
    battery_type = models.PositiveSmallIntegerField(
        _("Battery type"),
        choices=BATTERY_TYPES,
    )

    battery_capacity = models.PositiveIntegerField(
        _("Capacity"),
        help_text=_("Battery capacity in mAh"),
    )

    ram_storage = models.PositiveIntegerField(
        _("RAM"),
        help_text=_("RAM storage in MB"),
    )

    wifi_connectivity = models.PositiveIntegerField(
        _("WiFi"),
        choices=WIFI_CONNECTIVITY,
        help_text=_("WiFi Connectivity"),
    )

    bluetooth = models.PositiveIntegerField(
        _("Bluetooth"),
        choices=BLUETOOTH_CONNECTIVITY,
        help_text=_("Bluetooth Connectivity"),
    )

    gps = models.BooleanField(
        _("GPS"),
        default=False,
        help_text=_("GPS integrated"),
    )

    operating_system = models.ForeignKey(
        OperatingSystem,
        on_delete=models.CASCADE,
        verbose_name=_("Operating System"),
    )

    width = models.DecimalField(
        _("Width"),
        max_digits=4,
        decimal_places=1,
        help_text=_("Width in mm"),
    )

    height = models.DecimalField(
        _("Height"),
        max_digits=4,
        decimal_places=1,
        help_text=_("Height in mm"),
    )

    weight = models.DecimalField(
        _("Weight"),
        max_digits=5,
        decimal_places=1,
        help_text=_("Weight in gram"),
    )

    screen_size = models.DecimalField(
        _("Screen size"),
        max_digits=4,
        decimal_places=2,
        help_text=_("Diagonal screen size in inch"),
    )

    multilingual = TranslatedFields(
        description=HTMLField(
            verbose_name=_("Description"),
            configuration='CKEDITOR_SETTINGS_DESCRIPTION',
            help_text=_(
                "Full description used in the catalog's detail view of Smart Phones."),
        ),
    )

    class Meta:
        verbose_name = _("Smart Phone")
        verbose_name_plural = _("Smart Phones")

    default_manager = ProductManager()

    def get_price(self, request):
        """
        Return the starting price for instances of this smart phone model.
        """
        if not hasattr(self, '_price'):
            if self.variants.exists():
                currency = self.variants.first().unit_price.currency
                aggr = self.variants.aggregate(models.Min('unit_price'))
                self._price = MoneyMaker(currency)(aggr['unit_price__min'])
            else:
                self._price = Money()
        return self._price

    def get_availability(self, request, **kwargs):
        variant = self.get_product_variant(**kwargs)
        return variant.get_availability(request)

    def deduct_from_stock(self, quantity, **kwargs):
        variant = self.get_product_variant(**kwargs)
        variant.deduct_from_stock(quantity)

    def is_in_cart(self, cart, watched=False, **kwargs):
        try:
            product_code = kwargs['product_code']
        except KeyError:
            return
        cart_item_qs = CartItem.objects.filter(cart=cart, product=self)
        for cart_item in cart_item_qs:
            if cart_item.product_code == product_code:
                return cart_item

    def get_product_variant(self, **kwargs):
        try:
            product_code = kwargs.get('product_code')
            return self.variants.get(product_code=product_code)
        except SmartPhoneVariant.DoesNotExist as e:
            raise SmartPhoneModel.DoesNotExist(e)

    def get_product_variants(self):
        return self.variants.all()


class SmartPhoneVariant(AvailableProductMixin, models.Model):
    product = models.ForeignKey(
        SmartPhoneModel,
        on_delete=models.CASCADE,
        verbose_name=_("Smartphone Model"),
        related_name='variants',
    )

    product_code = models.CharField(
        _("Product code"),
        max_length=255,
        unique=True,
    )

    unit_price = MoneyField(
        _("Unit price"),
        decimal_places=3,
        help_text=_("Net price for this product"),
    )

    storage = models.PositiveIntegerField(
        _("Internal Storage"),
        help_text=_("Internal storage in GB"),
    )

    quantity = models.PositiveIntegerField(
        _("Quantity"),
        default=0,
        validators=[MinValueValidator(0)],
        help_text=_("Available quantity in stock")
    )

    def __str__(self):
        return _("{product} with {storage} GB").format(product=self.product, storage=self.storage)

    def get_price(self, request):
        return self.unit_price
