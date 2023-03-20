import csv
import datetime
import logging
import pickle

from django.core.files.storage import default_storage
from django_rq import job

from commons.models import ExportHistory

logger = logging.getLogger(__name__)


@job
def generate_async_export(export_task_id):
    export = ExportHistory.objects.get(id=export_task_id)
    logger.info(f'Generating export task ID: {export_task_id}')
    try:
        query = pickle.loads(export.query)
        serializer = pickle.loads(export.export_serializer)

        queryset = serializer.Meta.model.objects.all()
        queryset.query = query

        data = serializer(queryset, many=True).data
        file_name = f"{serializer.Meta.model.__name__.lower()}-{datetime.datetime.now().timestamp()}.csv"
        with open(file_name, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=data[0].keys())
            writer.writeheader()
            for row in data:
                writer.writerow(row)
            default_storage.save(file_name, csvfile)

        export.status = 'SUCCESS'
        export.save()

    except Exception as e:
        logger.error(f'Error while generating async export with ID : {export_task_id}')
        export.status = 'FAILURE'
        export.save()
    return 1
