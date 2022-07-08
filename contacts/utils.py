import operator
from datetime import datetime, timedelta
from functools import reduce
from django.db.models import Q
from .models import Segment, Condition, Contact, CustomField, CustomFieldOfContact

def retrieve_segment_members(segment_id):
    #Mapping check_types <> django Q filters
    mapping = {
        'IS': ('iexact', True),
        'IS NOT': ('iexact', False),
        'CONTAINS': ('icontains', True),
        'DOES NOT CONTAIN': ('icontains', False),
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
        'BEFORE': ('lt', True),
        'AFTER': ('gt', True),
        'LASTDAYS': ('gte', True),
        'BETWEEN': ('range', True)
    }

    #Get all conditions of the segment
    segment = Segment.objects.select_related('workspace').get(id=segment_id)
    conditions = segment.conditions.all()
    filter_queries = []

    for condition in conditions:
        if condition.condition_type == 'EMAIL':
            key = f"email__{mapping[condition.check_type][0]}"
            value = condition.input_value
            if mapping[condition.check_type][1]:
                filter_queries.append(Q(**{ key: value}))
            else:
                filter_queries.append(~Q(**{ key: value}))

        if condition.condition_type == 'CUSTOM FIELD':
            if condition.custom_field.type == 'str':
                key = f"custom_fields__value_str__{mapping[condition.check_type][0]}"
                value = condition.input_value
                if mapping[condition.check_type][1]:
                    filter_queries.append(Q(**{ key: value}))
                else:
                    filter_queries.append(~Q(**{ key: value}))
            if condition.custom_field.type == 'int':
                key = f"custom_fields__value_int__{mapping[condition.check_type][0]}"
                value = condition.input_value
                if mapping[condition.check_type][1]:
                    filter_queries.append(Q(**{ key: value}))
                else:
                    filter_queries.append(~Q(**{ key: value}))
            if condition.custom_field.type == 'bool':
                key = f"custom_fields__value_bool__{mapping[condition.check_type][0]}"
                value = condition.input_value
                if mapping[condition.check_type][1]:
                    filter_queries.append(Q(**{ key: value}))
                else:
                    filter_queries.append(~Q(**{ key: value}))
            if condition.custom_field.type == 'date':
                key = f"custom_fields__value_date__{mapping[condition.check_type][0]}"
                value = condition.input_value
                if condition.check_type == 'LASTDAYS':
                    value = datetime.now()-timedelta(days=int(condition.input_value))
                elif condition.check_type == 'BETWEEN':
                    value = (condition.input_value, condition.input_value2)

                if mapping[condition.check_type][1]:
                    filter_queries.append(Q(**{ key: value}))
                else:
                    filter_queries.append(~Q(**{ key: value}))
        
        if condition.condition_type == 'LIST':
            key = f"lists__id__{mapping[condition.check_type][0]}"
            value = condition.input_value
            if mapping[condition.check_type][1]:
                filter_queries.append(Q(**{ key: value}))
            else:
                filter_queries.append(~Q(**{ key: value}))


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
        ).distinct()
    return queryset


'''
DOCUMENTATION REQUEST:
    Create EMAIL condition:
        - condition_type = EMAIL
        - check_type = WHATEVER str type
        - input_value = email to search

    Create CUSTOM FIELD condition:
        - condition_type = CUSTOM FIELD
        - custom_field = int ID of the Custom Field 
        - check_type = WHATEVER related type
        - input_value = value to search
        - input_value2 = value 2 to search (in case we need a 2nd date)

    Create LIST condition:
        - condition_type = LIST
        - check_type = EQUALS
        - input_value = UUID of the List instance
    
    Create EVENT condition:
        - condition_type = EVENT
        - check_type = EQUALS
        - input_value = UUID of the Event instance
    
    Create PAGE condition:
        - condition_type = PAGE
        - check_type = EQUALS
        - input_value = UUID of the Page instance


'''