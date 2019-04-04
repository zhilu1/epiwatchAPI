from mongoengine import Document, EmbeddedDocument, fields


class Location(EmbeddedDocument):
    # id = fields.StringField(required=True)
    country = fields.ListField(fields.StringField())
    location = fields.ListField(fields.StringField())
    # geonames_id = fields.LongField(
    #     required=False, null=True)  # optional/advaned


class EventReport(EmbeddedDocument):
    # id = fields.StringField(required=True)
    vars()['type'] = fields.StringField()
    date = fields.StringField()
    location = fields.EmbeddedDocumentListField(Location)
    number_affected = fields.IntField(min_vale=0)
    # number_affected = fields.StringField()


class Report(EmbeddedDocument):
    # id = fields.StringField(required=True)
    disease = fields.ListField(fields.StringField())
    syndrome = fields.ListField(fields.StringField())
    reported_events = fields.EmbeddedDocumentListField(EventReport)
    comment = fields.StringField()


class Article(Document):
    # id = fields.StringField(primary_key=True)
    url = fields.StringField(required=True)
    headline = fields.StringField(required=True)
    date_of_publication = fields.StringField()
    # is of type either date-exact or date-range
    main_text = fields.StringField()
    reports = fields.EmbeddedDocumentListField(Report)
    # meta = {'collection': 'NULLDB'}
