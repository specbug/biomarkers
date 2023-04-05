import datetime
import os
from typing import Optional, List

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from models.fit import Mode, MetricRes, DTypes


class FitClient:
    def __init__(self, scopes):
        creds = Credentials.from_authorized_user_file(os.environ['gfit_credentials_file'], scopes)
        self.client = build(os.environ['gfit_service'], os.environ['gfit_version'], credentials=creds)

    def get_all_datasources(self) -> dict:
        """Get all datasources."""
        return self.client.users().dataSources().list(userId='me').execute()

    def _aggregate(self, body, user_id='me') -> dict:
        request = self.client.users().dataset().aggregate(userId=user_id, body=body)
        return request.execute()

    def get_data(
        self, mode: Mode, start_date: datetime.datetime, end_date: datetime.datetime, bucket_by: Optional[int] = None
    ) -> dict:
        """Get data for a date-range. Optionally bucket data (n days)."""
        start_time_ms = int(start_date.strftime('%s')) * 1000
        end_time_ms = int(end_date.strftime('%s')) * 1000
        req_body = dict(
            aggregateBy=[dict(dataTypeName=Mode.get_mode_uri(mode))],
            startTimeMillis=start_time_ms,
            endTimeMillis=end_time_ms,
        )
        if bucket_by is not None:
            duration_ms = bucket_by * 24 * 3600 * 1000
            req_body.update(dict(bucketByTime=dict(durationMillis=duration_ms)))
        return self._aggregate(body=req_body)

    @classmethod
    def parse_data(cls, data: dict, dtype: DTypes = DTypes.INT) -> List[MetricRes]:
        """Parse Fit client response data."""
        res = []
        for bucket in data.get('bucket', []):
            for dataset in bucket.get('dataset', []):
                for point in dataset.get('point', []):
                    for value in point.get('value', []):
                        if dtype == DTypes.INT:
                            metric_value = value['intVal']
                        elif dtype == DTypes.FLOAT:
                            metric_value = value['intVal']
                        else:
                            raise KeyError(
                                f'Parsing client response for "{dtype}" data-type is not supported\nPlease choose from: {[d for d in DTypes]}.'
                            )
                        start_dt = datetime.datetime.fromtimestamp(int(point['startTimeNanos']) // 1e9)
                        end_dt = datetime.datetime.fromtimestamp(int(point['endTimeNanos']) // 1e9)
                        _res = MetricRes(start_dt=start_dt, end_dt=end_dt, value=metric_value)
                        res.append(_res)
        return res
