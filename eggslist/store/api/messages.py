from django.utils.translation import gettext_lazy as _

SELLER_NEEDS_MORE_INFO = _(
    "You need to fill out: first and last names, phone number, "
    "and location in your profile to be able to post an article."
)

ONLY_SELLER_CAN_UPDATE = _(
    "Only Product seller can adjust their products. Current user is not the owner of this product."
)

PRODUCT_ARTICLE_DOES_NOT_EXIST = _("There is no such Product Article in the database.")
