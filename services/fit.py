import datetime
import os
from typing import Optional, List

import pandas as pd
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from models.fit import Mode, MetricRes, DTypes, ResponseModel, Union

NoneType = type(None)


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
                            metric_value = value['fpVal']
                        else:
                            raise KeyError(
                                f'Parsing client response for "{dtype}" data-type is not supported\n'
                                f'Please choose from: {[d for d in DTypes]}.'
                            )
                        start_dt = datetime.datetime.fromtimestamp(int(point['startTimeNanos']) // 1e9)
                        end_dt = datetime.datetime.fromtimestamp(int(point['endTimeNanos']) // 1e9)
                        _res = MetricRes(start_dt=start_dt, end_dt=end_dt, value=metric_value)
                        res.append(_res)
        return res

    def get_steps(self, start_date: datetime.datetime, end_date: datetime.datetime) -> Union[ResponseModel, NoneType]:
        """Get steps data, agg daily."""
        res_data = self.get_data(mode=Mode.STEPS, start_date=start_date, end_date=end_date)
        if res_data is None or len(res_data) == 0:
            return
        mode_dtype = Mode.get_dtype(Mode.STEPS)
        steps_data_raw = self.parse_data(data=res_data, dtype=mode_dtype)
        if len(steps_data_raw) == 0:
            return
        steps_data = pd.DataFrame.from_records([c.dict() for c in steps_data_raw])
        steps_data['start_dt'] = steps_data['start_dt'].dt.strftime('%Y-%m-%d')
        steps_data = steps_data.groupby(['start_dt'])['value'].sum().reset_index()
        if mode_dtype == DTypes.INT:
            steps_data['value'] = steps_data['value'].astype(int)
        res = ResponseModel(x=steps_data['start_dt'].tolist(), y=steps_data['value'].tolist())
        return res

    def get_sleep(
        self, start_date: datetime.datetime, end_date: datetime.datetime, breakdown=False
    ) -> Union[ResponseModel, NoneType]:
        """Get sleep data, agg daily (repr by start date)."""
        res_data = self.get_data(mode=Mode.SLEEP, start_date=start_date, end_date=end_date)
        if res_data is None or len(res_data) == 0:
            return
        mode_dtype = Mode.get_dtype(Mode.SLEEP)
        sleep_data_raw = self.parse_data(data=res_data, dtype=mode_dtype)
        if len(sleep_data_raw) == 0:
            return
        sleep_data = pd.DataFrame.from_records([c.dict() for c in sleep_data_raw])
        sleep_data.loc[:, 'type'] = sleep_data.loc[:, 'value']
        sleep_data['value'] = ((sleep_data['end_dt'] - sleep_data['start_dt']).dt.total_seconds()).astype(int)
        sleep_data['start_dt'] = sleep_data['start_dt'].dt.strftime('%Y-%m-%d')
        sleep_data = sleep_data.groupby(['start_dt', 'type'])['value'].sum().reset_index()
        if mode_dtype == DTypes.INT:
            sleep_data['value'] = sleep_data['value'].astype(int)
        if breakdown:
            # sleep_types_map = Mode.get_sleep_types(core=False)
            # sleep_data['type'] = sleep_data['type'].replace(sleep_types_map)
            raise NotImplementedError
        else:
            core_sleep_types = list(Mode.get_sleep_types(core=True))
            sleep_data = sleep_data[sleep_data['type'].isin(core_sleep_types)].reset_index(drop=True)
            sleep_data = sleep_data.groupby(['start_dt'])['value'].sum().reset_index()
            sleep_data['value'] = (sleep_data['value'] / 3600).round(1)
            res = ResponseModel(x=sleep_data['start_dt'].tolist(), y=sleep_data['value'].tolist())
        return res
