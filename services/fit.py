import datetime
import os
from typing import Optional, List

import pandas as pd
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from models.fit import Mode, MetricRes, DTypes, ResponseModel, Union, SleepTypes, HRRestRange

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
        if breakdown:
            # sleep_types_map = Mode.get_sleep_types(core=False)
            # sleep_data['type'] = sleep_data['type'].replace(sleep_types_map)
            raise NotImplementedError
        else:
            core_sleep_types = list(SleepTypes.get_sleep_types(core=True))
            sleep_data = sleep_data[sleep_data['type'].isin(core_sleep_types)].reset_index(drop=True)
            sleep_data = sleep_data.groupby(['start_dt'])['value'].sum().reset_index()
            sleep_data['value'] = (sleep_data['value'] / 3600).round(1)
            res = ResponseModel(x=sleep_data['start_dt'].tolist(), y=sleep_data['value'].tolist())
        return res

    def get_met_hours(
        self, start_date: datetime.datetime, end_date: datetime.datetime
    ) -> Union[ResponseModel, NoneType]:
        """Get MET hours, agg daily."""
        res_data = self.get_data(mode=Mode.MET, start_date=start_date, end_date=end_date)
        if res_data is None or len(res_data) == 0:
            return
        mode_dtype = Mode.get_dtype(Mode.MET)
        met_data_raw = self.parse_data(data=res_data, dtype=mode_dtype)
        if len(met_data_raw) == 0:
            return
        met_data = pd.DataFrame.from_records([c.dict() for c in met_data_raw])
        met_data['timedelta'] = (((met_data['end_dt'] - met_data['start_dt']).dt.total_seconds()) / 60).astype(int)
        met_data['norm_value'] = (met_data['value'] / met_data['delta_mins']).astype(int)
        met_data.loc[:, 'met'] = 4.5
        met_data.loc[met_data['norm_value'] == 2, 'met'] = 6.0
        met_data['start_dt'] = met_data['start_dt'].dt.strftime('%Y-%m-%d')
        met_data = met_data.groupby(['start_dt', 'met'])['timedelta'].sum().reset_index()
        met_data['value'] = (met_data['met'] * met_data['delta_mins'] / 60).round(1)
        met_data = met_data.groupby('start_dt')['value'].sum().reset_index()
        res = ResponseModel(x=met_data['start_dt'].tolist(), y=met_data['value'].tolist())
        return res

    @staticmethod
    def _is_ts_in_intervals(ts: datetime.datetime, intervals: List[List[datetime.datetime]]) -> bool:
        """Check if the timestamp falls between an interval, among a list of intervals."""
        s = 0
        e = len(intervals) - 1
        while s < e:
            mid = (s + e) // 2
            if intervals[mid][0] <= ts <= intervals[mid][1]:
                return True
            elif ts > intervals[mid][0]:
                s = mid + 1
            else:
                e = mid
        return False

    def get_rhr(self, start_date: datetime.datetime, end_date: datetime.datetime) -> Union[ResponseModel, NoneType]:
        """Get resting heart rate, agg daily"""
        # fetch heart rate data (bpm)
        res_data = self.get_data(mode=Mode.RHR, start_date=start_date, end_date=end_date)
        if res_data is None or len(res_data) == 0:
            return
        mode_dtype = Mode.get_dtype(Mode.RHR)
        rhr_data_raw = self.parse_data(data=res_data, dtype=mode_dtype)
        if len(rhr_data_raw) == 0:
            return
        rhr_data = pd.DataFrame.from_records([c.dict() for c in rhr_data_raw])
        rhr_data['start_dt'] = pd.to_datetime(rhr_data['start_dt'].dt.strftime('%Y-%m-%d %H:%M'))
        rhr_data = rhr_data.groupby('start_dt')['value'].mean().reset_index()
        # remove outliers
        rhr_data = rhr_data[
            (rhr_data['value'] < HRRestRange.MAX_RHR) & (rhr_data['value'] > HRRestRange.MIN_RHR)
        ].reset_index(drop=True)
        # fetch all periods of activity
        activity_res_data = self.get_data(mode=Mode.ACTIVITY, start_date=start_date, end_date=end_date)
        activity_periods = None
        if activity_res_data:
            activity_periods = []
            activity_data: List[MetricRes] = self.parse_data(data=activity_res_data)
            for a in sorted(activity_data, key=lambda x: (x.start_dt, x.end_dt)):
                if (a.end_dt - a.start_dt).total_seconds() < 60:
                    continue
                activity_periods.append([a.start_dt, a.end_dt])
        # truncate HR data coinciding with some period of activity (non-rest HR)
        if activity_periods:
            rhr_data['active'] = rhr_data['start_dt'].apply(lambda x: self._is_ts_in_intervals(x, activity_periods))
            rhr_data = rhr_data[~rhr_data['active']].reset_index(drop=True)
        # agg to daily
        rhr_data['start_dt'] = rhr_data['start_dt'].dt.strftime('%Y-%m-%d')
        rhr_data = rhr_data.groupby('start_dt')['value'].mean().reset_index()
        rhr_data['value'] = rhr_data['value'].round(1)
        res = ResponseModel(x=rhr_data['start_dt'].tolist(), y=rhr_data['value'].tolist())
        return res

    def get_body_fat(
        self, start_date: datetime.datetime, end_date: datetime.datetime
    ) -> Union[ResponseModel, NoneType]:
        """Get body fat (%), agg daily"""
        res_data = self.get_data(mode=Mode.BODY_FAT, start_date=start_date, end_date=end_date)
        if res_data is None or len(res_data) == 0:
            return
        mode_dtype = Mode.get_dtype(Mode.BODY_FAT)
        bf_data_raw = self.parse_data(data=res_data, dtype=mode_dtype)
        if len(bf_data_raw) == 0:
            return
        bf_data = pd.DataFrame.from_records([c.dict() for c in bf_data_raw])
        bf_data['start_dt'] = bf_data['start_dt'].dt.strftime('%Y-%m-%d')
        bf_data = bf_data.groupby('start_dt')['value'].mean().reset_index()
        bf_data['value'] = bf_data['value'].round(1)
        res = ResponseModel(x=bf_data['start_dt'].tolist(), y=bf_data['value'].tolist())
        return res
