class Adjustment(object):

    def __init__(self, oid, external_id, name, event, rule_name):
        self.oid = oid
        self.external_id = external_id
        self.name = name
        self.event = event
        self.rule_name = rule_name
        self.descriptions = {} # language id -> AdjustmentDescription()

class AdjustmentDescription(object):

    def __init__(self, language_id, description, image):
        self.language_id = language_id
        self.description = description
        self.image = image

class AdjustmentSchedule(object):

    def __init__(self, start_date, end_date, start_time, duration, mon, tue, wed, thu, fri, sat, sun):
        self.start_date = start_date
        self.end_date = end_date
        self.start_time = start_time
        self.duration = duration
        self.mon = mon
        self.tue = tue
        self.wed = wed
        self.thu = thu
        self.fri = fri
        self.sat = sat
        self.sun = sun
