import datetime

from django.conf import settings
from django.db.models import fields
from django.db.models.expressions import Expression


class Date(Expression):
    """
    Add a date selection column.
    NOTE: This is backported from Django 1.9.x as it has been removed from
    Django >=1.10.
    """
    def __init__(self, lookup, lookup_type):
        super(Date, self).__init__(output_field=fields.DateField())
        self.lookup = lookup
        self.col = None
        self.lookup_type = lookup_type

    def __repr__(self):
        return "{}({}, {})".format(self.__class__.__name__, self.lookup, self.lookup_type)

    def get_source_expressions(self):
        return [self.col]

    def set_source_expressions(self, exprs):
        self.col, = exprs

    def resolve_expression(self, query=None, allow_joins=True, reuse=None, summarize=False, for_save=False):
        copy = self.copy()
        copy.col = query.resolve_ref(self.lookup, allow_joins, reuse, summarize)
        field = copy.col.output_field
        assert isinstance(field, fields.DateField), "%r isn't a DateField." % field.name
        if settings.USE_TZ:
            assert not isinstance(field, fields.DateTimeField), (
                "%r is a DateTimeField, not a DateField." % field.name
            )
        return copy

    def as_sql(self, compiler, connection):
        sql, params = self.col.as_sql(compiler, connection)
        assert not(params)
        return connection.ops.date_trunc_sql(self.lookup_type, sql), []

    def copy(self):
        copy = super(Date, self).copy()
        copy.lookup = self.lookup
        copy.lookup_type = self.lookup_type
        return copy

    def convert_value(self, value, expression, connection, context):
        if isinstance(value, datetime.datetime):
            value = value.date()
        return value
