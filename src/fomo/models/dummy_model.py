"""TODO: this should be replaced with other models as soon as possible. This serves only for instruction."""
import narwhals as nw
from narwhals.typing import IntoFrameT

class DummyFoundationModel:
    def __init__(self):
        pass

    def forecast(X: IntoFrameT, context: IntoFrameT):
        # todo: make this more efficient for other classes, e.g. if this is already pandas, then don't collect again, maybe narwhals
        # does this on its own.
        X_pd = X.to_pandas()
        context_pd = context.to_pandas()
        last_row = [context_pd.tail(1)] * len(X_pd)
        return last_row


