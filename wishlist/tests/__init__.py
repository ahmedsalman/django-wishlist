from django.test.utils import override_settings

from django.core.urlresolvers import reverse

from django_dynamic_fixture import N, G

from django_webtest import WebTest

from ..models import WishlistItem
from ..utils import get_user_model
User = get_user_model()

from .models import TestItemModel


@override_settings(WISHLIST_ITEM_MODEL='tests.TestItemModel')
class WishlistTests(WebTest):
    def test_save(self):
        """ Test saving a WishlistItem. """

        # Create
        item = N(WishlistItem)

        # Validate
        item.clean()

        # Save
        item.save()

    def test_add(self):
        """ Test adding an item. """

        # Get URL for add view
        add_view = reverse('wishlist_add')

        # Create an item to add
        wished_item = G(TestItemModel, slug='test')

        # Create a user and login
        user = G(User)

        # Request add view
        add_page = self.app.get(add_view, user=user)

        # Fill in form and post
        add_form = add_page.form
        add_form['item'] = wished_item.pk
        add_result = add_form.submit()

        # Assert WishlistItem has been created
        self.assertEquals(WishlistItem.objects.count(), 1)

        item = WishlistItem.objects.get()
        self.assertEquals(item.user, user)
        self.assertEquals(item.item_id, wished_item.pk)

        # Test redirect after adding
        result = add_result.follow()

        # Test messages after adding
        self.assertContains(result, unicode(item))
        self.assertContains(result, u'added to the wishlist')

    def test_remove(self):
        """ Test removing an item. """

        # Create wishlist item
        item = G(WishlistItem)

        # Get URL for list view
        list_view = reverse('wishlist')

        # Request view
        list_page = self.app.get(list_view, user=item.user)

        # Find and post remove form
        remove_form = list_page.form
        remove_result = remove_form.submit()

        # Assert WishlistItem has been removed
        self.assertEquals(WishlistItem.objects.count(), 0)

        # Test redirect after adding
        result = remove_result.follow()

        # Test messages after adding
        self.assertContains(result, unicode(item))
        self.assertContains(result, u'remove from the wishlist')
