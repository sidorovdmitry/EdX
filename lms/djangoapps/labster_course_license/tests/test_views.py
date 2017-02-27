"""
Tests labster course license views.
./manage.py lms test --verbosity=1 lms/djangoapps/labster_course_license   --traceback --settings=labster_test
"""
import mock
from django.core.urlresolvers import reverse
from django.test.utils import override_settings
from rest_framework import status
from ccx_keys.locator import CCXLocator
from openedx.core.djangoapps.labster.tests.base import CCXCourseTestBase
from xmodule.modulestore.tests.factories import ItemFactory
from xmodule.modulestore.django import modulestore
from xmodule.modulestore.tests.django_utils import ModuleStoreTestCase
from xblock.field_data import DictFieldData
from courseware.field_overrides import OverrideFieldData
from lms.djangoapps.ccx.overrides import get_override_for_ccx
from labster_course_license.models import LicensedCoursewareItems, CourseLicense


@override_settings(
    FIELD_OVERRIDE_PROVIDERS=('labster_course_license.licensed_blocks_override.LicensedBlocksOverrideProvider',)
)
class TestSetLicense(CCXCourseTestBase):
    """
    Tests for set_license method.
    """

    def setUp(self):
        super(TestSetLicense, self).setUp()
        self.url = reverse("labster_license_handler", kwargs={'course_id': self.ccx_key})
        self.data = {'license': 'YildVfefwmrTwNPPeapcNrugbkyb34sFoKiolPtk', 'update': True}
        self.client.login(username=self.user.username, password="test")
        OverrideFieldData.provider_classes = None
        self.override = OverrideFieldData.wrap(self.user, self.course, DictFieldData({}))

    def is_visible_to_staff_only(self, block):
        """
        Get `visible_to_staff_only` property value of block.
        """
        is_visible = self.override.get_override(block, 'visible_to_staff_only')
        print(is_visible)
        if not isinstance(is_visible, bool):
            is_visible = False
        return is_visible

    @mock.patch('labster_course_license.views.get_licensed_simulations')
    @mock.patch('labster_course_license.views.get_consumer_secret')
    def test_valid_simulation_ids(self, mock_get_consumer_secret, mock_get_licensed_simulations):
        """
        Test that the licence page is returned with no invalid simulations.
        """
        mock_get_consumer_secret.return_value = ('123', '__secret_key__')
        mock_get_licensed_simulations.return_value = ['*']
        # create 3 lti xmodules with valid launch urls
        data = [
            ('https://example.com/simulation/a0Kw0000000/', 'LTI0'),
            ('https://example.com/simulation/a0Kw0000001/', 'LTI1'),
            ('https://example.com/simulation/a0Kw00000002', 'LTI2'),
        ]
        licenced_simulations = [ItemFactory.create(
            category='lti', modulestore=self.store, display_name=display_name,
            metadata={'lti_id': 'correct_lti_id', 'launch_url': url}
        ) for url, display_name in data]

        res = self.client.post(self.url, data=self.data, follow=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertNotIn('Please verify LTI URLs are correct for the following simulations', res.content)

    @mock.patch('labster_course_license.views.get_licensed_simulations')
    @mock.patch('labster_course_license.views.get_consumer_secret')
    def test_hides_unlicensed_simulations(self, mock_get_consumer_secret, mock_get_licensed_simulations):
        """
        Ensure hides only unlicensed simulations.
        """
        mock_get_consumer_secret.return_value = ('123', '__secret_key__')
        mock_get_licensed_simulations.return_value = ['a0Kw0000000']

        data = [
            ('https://example.com/simulation/a0Kw0000000/', 'LTI0'),
            ('https://example.com/dashboards/teacher/', 'LTI1'),
            ('http://127.0.0.1/some/path/here/', 'LTI2'),
            ('https://example.com/simulation/a0Kw0000055', 'LTI3'),
            ('https://example.com/simulation/a0Kw0000035', 'LTI4'),
        ]

        chapter = ItemFactory.create(parent=self.course, category='chapter')
        sequential = ItemFactory.create(parent=chapter, category='sequential')
        verticals = [ItemFactory.create(parent=sequential, category='vertical') for i in range(len(data))]

        blocks = [ItemFactory.create(
            parent=verticals[index],
            category='lti', modulestore=self.store, display_name=item[1],
            metadata={'lti_id': 'correct_lti_id', 'launch_url': item[0]}
        ) for index, item in enumerate(data)]

        res = self.client.post(self.url, data=self.data, follow=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        chapter = self.ccx.course.get_children()[0]
        self.assertFalse(self.is_visible_to_staff_only(chapter))
        sequential = chapter.get_children()[0]
        self.assertFalse(self.is_visible_to_staff_only(sequential))
        verticals = sequential.get_children()

        self.assertEqual(
            [False, False, False, True, True],
            [self.is_visible_to_staff_only(i) for i in verticals]
        )

    @mock.patch('labster_course_license.views.get_licensed_simulations')
    @mock.patch('labster_course_license.views.get_consumer_secret')
    def test_correctly_updates_visibility(self, mock_get_consumer_secret, mock_get_licensed_simulations):
        """
        Ensure hides only unlicensed simulations.
        """
        mock_get_consumer_secret.return_value = ('123', '__secret_key__')
        mock_get_licensed_simulations.return_value = ['a0Kw0000001']

        data = ('https://example.com/simulation/a0Kw0000000/', 'LTI0')

        chapter = ItemFactory.create(parent=self.course, category='chapter')
        sequential = ItemFactory.create(parent=chapter, category='sequential')
        vertical = ItemFactory.create(parent=sequential, category='vertical')

        block = ItemFactory.create(
            parent=vertical,
            category='lti', modulestore=self.store, display_name=data[1],
            metadata={'lti_id': 'correct_lti_id', 'launch_url': data[0]}
        )

        res = self.client.post(self.url, data=self.data, follow=True)
        vertical = self.ccx.course.get_children()[0].get_children()[0].get_children()[0]
        self.assertTrue(self.is_visible_to_staff_only(vertical))

        mock_get_licensed_simulations.return_value = ['a0Kw0000000']

        res = self.client.post(self.url, data=self.data, follow=True)
        vertical = self.ccx.course.get_children()[0].get_children()[0].get_children()[0]
        self.assertIsNone(get_override_for_ccx(self.ccx, vertical, 'visible_to_staff_only'))
        # Flush field cache to make sure it returns most actual value.
        vertical._field_data_cache = {}  # pylint: disable=protected-access
        self.assertFalse(self.is_visible_to_staff_only(vertical))

    @mock.patch('labster_course_license.views.get_licensed_simulations')
    @mock.patch('labster_course_license.views.get_consumer_secret')
    def test_can_hide_all_blocks(self, mock_get_consumer_secret, mock_get_licensed_simulations):
        """
        Test can hide all the blocks if there are no licensed simulations.
        """
        mock_get_consumer_secret.return_value = ('123', '__secret_key__')
        mock_get_licensed_simulations.return_value = []

        data = [
            ('https://example.com/simulation/a0Kw0000000/', 'LTI0'),
            ('https://example.com/dashboards/teacher/', 'LTI1'),
            ('http://127.0.0.1/some/path/here/', 'LTI2'),
            ('https://example.com/simulation/a0Kw0000055', 'LTI3'),
        ]

        chapter = ItemFactory.create(parent=self.course, category='chapter')
        sequential = ItemFactory.create(parent=chapter, category='sequential')
        verticals = [ItemFactory.create(parent=sequential, category='vertical') for i in range(len(data))]

        blocks = [ItemFactory.create(
            parent=verticals[index],
            category='lti', modulestore=self.store, display_name=item[1],
            metadata={'lti_id': 'correct_lti_id', 'launch_url': item[0]}
        ) for index, item in enumerate(data)]

        res = self.client.post(self.url, data=self.data, follow=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        chapter = self.ccx.course.get_children()[0]
        self.assertTrue(self.is_visible_to_staff_only(chapter))

    @mock.patch('labster_course_license.views.get_licensed_simulations')
    @mock.patch('labster_course_license.views.get_consumer_secret')
    def test_invalid_simulation_ids(self, mock_get_consumer_secret, mock_get_licensed_simulations):
        """
        Test that license page is returned with error containing invalid simulations.
        """
        mock_get_consumer_secret.return_value = ('123', '__secret_key__')
        mock_get_licensed_simulations.return_value = ["*"]

        data = [
            ('https://example.com/simulation/a0Kw0000000 /', 'LTI0', 'a0Kw0000000 '),
            ('https://example.com/simulation/a0Kw0000001 ', 'LTI1', 'a0Kw0000001 '),
            ('https://example.com/simulation/ a0Kw0000002/', 'LTI2', ' a0Kw0000002'),
            ('https://example.com/simulation/   a0Kw00000003  /', 'LTI3', '   a0Kw00000003  '),
            ('https://example.com/simulation/a0Kw0000 004/', 'LTI4', 'a0Kw0000 004'),
            ('/simulation/a0Kw0000005', 'LTI5', 'a0Kw0000005'),
            ('localhost/simulation/a0Kw0000006/', 'LTI6', 'a0Kw0000006'),
        ]
        licenced_simulations = [ItemFactory.create(
            category='lti', modulestore=self.store, display_name=display_name,
            metadata={'lti_id': 'correct_lti_id', 'launch_url': url}
        ) for url, display_name, __ in data]

        resp = self.client.post(self.url, data=self.data, follow=True)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(7, resp.content.count('Enter a valid URL.'))
        self.assertEqual(5, resp.content.count('Enter a valid simulation id.'))

        for item in data:
            self.assertContains(resp, item[1])  # Display name
            self.assertContains(resp, item[2])  # Simulation id

    @mock.patch('labster_course_license.views.get_licensed_simulations')
    @mock.patch('labster_course_license.views.get_consumer_secret')
    def test_access_structure_stored_correctly(self, mock_get_consumer_secret, mock_get_licensed_simulations):
        """
        Test that the licence page is returned with no invalid simulations.
        """
        mock_get_consumer_secret.return_value = ('123', '__secret_key__')
        mock_get_licensed_simulations.return_value = ['a0Kw0000001']

        data = [
            ('https://example.com/simulation/a0Kw0000000/', 'LTI0'),
            ('https://example.com/simulation/a0Kw0000001/', 'LTI1'),
            ('https://example.com/simulation/a0Kw00000002', 'LTI2'),
        ]

        chapter = ItemFactory.create(parent=self.course, category='chapter')
        sequential = ItemFactory.create(parent=chapter, category='sequential')
        vertical = ItemFactory.create(parent=sequential, category='vertical')

        sequential2 = ItemFactory.create(parent=chapter, category='sequential')
        vertical2 = ItemFactory.create(parent=sequential2, category='vertical')

        blocks = [ItemFactory.create(
            parent=vertical,
            category='lti', modulestore=self.store, display_name=item[1],
            metadata={'lti_id': 'correct_lti_id', 'launch_url': item[0]}
        ) for index, item in enumerate(data)]
        ItemFactory.create(
            parent=vertical2,
            category='lti', modulestore=self.store, display_name='LTI3',
            metadata={
                'lti_id': 'correct_lti_id',
                'launch_url': 'https://example.com/simulation/a0Kw00000003'
            }
        )
        ItemFactory.create(parent=vertical2, category='overview', modulestore=self.store, display_name='Text')

        res = self.client.post(self.url, data=self.data, follow=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        course_license = CourseLicense.objects.get(
            course_id=CCXLocator.from_course_locator(self.course.id, self.ccx.id)
        )
        lci = LicensedCoursewareItems.objects.filter(course_license=course_license)

        # check chapter, both sequentials and both verticals are saved
        self.assertEqual(lci.count(), 5)

        # check text block parent is visible to students
        vertical2 = self.ccx.course.get_children()[0].get_children()[1].get_children()[0]
        self.assertFalse(self.is_visible_to_staff_only(vertical2))

    def setup_patch(self, function_name, return_value):
        """
        Patch a function with a given return value, and return the mock
        """
        _mock = mock.MagicMock(return_value=return_value)
        new_patch = mock.patch(function_name, new=_mock)
        new_patch.start()
        self.addCleanup(new_patch.stop)
        return _mock

    def test_update_course_signal(self):
        """
        Ensure that course_published signal is called with correct params.
        """
        from xmodule.modulestore.django import SignalHandler

        signal_mock = self.setup_patch('xmodule.modulestore.django.SignalHandler.course_published.send', None)

        course_key = self.course.location.course_key
        SignalHandler.course_published.send(sender=self.course, course_key=course_key)

        signal_mock.assert_called_once_with(course_key=course_key, sender=self.course)
