from unittest import TestCase

from app.adjustment import Adjustment, AdjustmentDescription


class TestAdjustment(TestCase):

    def setUp(self):
        self.a = Adjustment("A25E3EE9AFA248A79DF07D2565410784", "", "Back to school 10% off", "", "Promotion % Off")

    # def test_ajustment_can_be_created(self):
    #     pass

    def test_adjustment_oid(self):
        self.assertEqual(self.a.oid, "A25E3EE9AFA248A79DF07D2565410784")

    def test_adjustment_name(self):
        self.assertEqual(self.a.name, "Back to school 10% off")

    def test_adjustment_external_id(self):
        self.assertEqual(self.a.external_id, "")

    def test_adjustment_event(self):
        self.assertEqual(self.a.event, "")

    def test_adjustment_rule_name(self):
        self.assertEqual(self.a.rule_name, "Promotion % Off")


class TestAdjustmentDescription(TestCase):

    def setUp(self):
        self.d = AdjustmentDescription("Pen", "Back to school", "")

    # def test_adjustment_description_can_be_created(self):
    #     pass

    def test_adjustment_description_language_id(self):
        self.assertEqual(self.d.language_id, "Pen")

    def test_adjustment_description_text(self):
        self.assertEqual(self.d.description, "Back to school")


    def test_adjustment_description_image(self):
        self.assertEqual(self.d.image, "")
