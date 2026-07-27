from fastapi import FastAPI
from pydantic import BaseModel

from fomo.scheduling.scheduler import Scheduler

# todo: we should probably hide this somehow, so that polars is not required in case someone runs on pandas
import polars as pl

app = FastAPI()

# I think running in threads would make most sense for now, so that we don't need to hand over 
# dataframes between separate processes (e.g. vLLM uses separate processes)
scheduler = Scheduler()

# todo: move this to another file
class ForecastRequestPolars(BaseModel):
    # todo: fail if extras are handed over
    data: pl.DataFrame
    target_column: str
    time_column: str
    context_data: pl.DataFrame
    model: str  # todo: should be literal
    forecasting_horizon: None | list[int] | int | list[str] = None # list[str] if that can be converted to list[int]
    # todo: should be also possible to use list[datetime.date] as forecasting_horizon
    priority: int | None = None

@app.post("/forecast/")
def forecast(forecast_request: ForecastRequestPolars):
    scheduler.queue_request(forecast_request)



