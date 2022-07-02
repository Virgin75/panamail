import operator
from functools import reduce
from django.db.models import Q
from .models import Segment, Condition, Contact

def retrieve_segment_members(segment_id):
    #Mapping check_types <> django Q filters
    mapping = {
        'IS': ('exact', True),
        'IS NOT': ('exact', False),
        'CONTAINS': ('contains', True),
        'DOES NOT CONTAIN': ('contains', False),
        'IS EMPTY': ('isnull', True),
        'IS NOT EMPTY': ('isnull', False),

        'EQUALS': ('exact', True),
        'SUPERIOR': ('gt', True),
        'SUPOREQUALS': ('gte', True),
        'INFERIOR': ('lt', True),
        'INFOREQUALS': ('lte', True),

        'IS TRUE': ('exact', True),
        'IS FALSE': ('exact', True),

        'AT': ('exact', True),
        'BEFORE': ('exact', True),
        'AFTER': ('exact', True),
        'LAST': ('exact', True),
        'BETWEEN': ('exact', True)
    }
    #Get all conditions of the segment
    segment = Segment.objects.select_related('workspace').get(id=segment_id)
    conditions = segment.conditions.all()
    filter_queries = []

    for condition in conditions:
        if condition.condition_type == 'EMAIL':
            if 'NOT' in condition.check_type:
                key = f"email__i{condition.check_type.lower()}"
                value = condition.input_value
                filter_queries.append(~Q(**{ key: value}))
            else:
                key = f"email__i{condition.check_type.lower()}"
                value = condition.input_value
                filter_queries.append(Q(**{ key: value}))

    #Generate final Contacts queryset
    if segment.operator == 'AND':
        queryset = Contact.objects.filter(
            reduce(operator.and_, filter_queries),
            workspace=segment.workspace,
        )
    else:
        queryset = Contact.objects.filter(
            reduce(operator.or_, filter_queries),
            workspace=segment.workspace,
        )
    print(queryset)
