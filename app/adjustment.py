class Adjustment(object):

    def __init__(self, oid, external_id, name, event, rule_name):
        self.oid = oid
        self.external_id = external_id
        self.name = name
        self.event = event
        self.rule_name = rule_name

class AdjustmentDescription(object):

    def __init__(self, language_id, description, image):
        self.language_id = language_id
        self.description = description
        self.image = image