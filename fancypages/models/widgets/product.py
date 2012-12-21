from django.db import models
from django.utils.translation import ugettext_lazy as _

from fancypages.models.base import Widget

Product = models.get_model('catalogue', 'Product')


class SingleProductWidget(Widget):
    name = _("Single Product")
    code = 'single-product'
    template_name = "fancypages/widgets/productwidget.html"

    product = models.ForeignKey(
        'catalogue.Product',
        verbose_name=_("Single Product"), null=True, blank=False)

    def __unicode__(self):
        if self.product:
            return u"Product '%s'" % self.product.upc
        return u"Product '%s'" % self.id

    class Meta:
        app_label = 'fancypages'


class HandPickedProductsPromotionWidget(Widget):
    name = _("Hand Picked Products Promotion")
    code = 'promotion-hand-picked-products'
    template_name = "fancypages/widgets/promotionwidget.html"

    promotion = models.ForeignKey(
        'promotions.HandPickedProductList',
        verbose_name=_("Hand Picked Products Promotion"), null=True, blank=False)

    def __unicode__(self):
        if self.promotion:
            return u"Promotion '%s'" % self.promotion.pk
        return u"Promotion '%s'" % self.id

    class Meta:
        app_label = 'fancypages'


class AutomaticProductsPromotionWidget(Widget):
    name = _("Automatic Products Promotion")
    code = 'promotion-ordered-products'
    template_name = "fancypages/widgets/promotionwidget.html"

    promotion = models.ForeignKey(
        'promotions.AutomaticProductList',
        verbose_name=_("Automatic Products Promotion"), null=True, blank=False)

    def __unicode__(self):
        if self.promotion:
            return u"Promotion '%s'" % self.promotion.pk
        return u"Promotion '%s'" % self.id

    class Meta:
        app_label = 'fancypages'


class OfferWidget(Widget):
    name = _("Offer Products")
    code = 'products-range'
    template_name = "fancypages/widgets/offerwidget.html"

    offer = models.ForeignKey(
        'offer.ConditionalOffer',
        verbose_name=_("Offer"), null=True, blank=False)

    @property
    def products(self):
        range = self.offer.condition.range
        if range.includes_all_products:
            return Product.browsable.filter(is_discountable=True)
        return range.included_products.filter(is_discountable=True)

    def __unicode__(self):
        if self.offer:
            return u"Offer '%s'" % self.offer.pk
        return u"Offer '%s'" % self.id

    class Meta:
        app_label = 'fancypages'
