"""Code for the scheduler/resource allocator."""
from typing import Literal
from narwhals.typing import IntoFrameT
from queue import Queue


class Scheduler:
    def __init__(self, mode: Literal["fifo"] = "fifo"):
        self.mode = mode
        self.request_queue = Queue()  # fifo queue, a priority queue is available as well, check this: https://docs.python.org/3/library/queue.html

    def queue_request(self, request) -> None:
        self.request_queue.put(request)

    def _get_model_from_request(self, request) -> Literal["DummyFoundationModel"]:
        return request.model

    def _get_data_from_request(self, request) -> tuple[IntoFrameT, IntoFrameT]:
        return request.data, request.context

    def _initialize_model(self, model: Literal["DummyFoundationModel"]):
        match model:
            case "DummyFoundationModel":
                from fomo.models.dummy_model import DummyFoundationModel
                model_obj = DummyFoundationModel()
            case _:
                raise ValueError("No valid model found.")
        return model_obj

    def execute_request(self):
        if len(self.request_queue) > 0:
            request = self.request_queue.get()
            model = self._get_model_from_request(request)
            data, context = self._get_data_from_request(request)
            model_obj = self._initialize_model(model)
            return model_obj.forecast(data, context)
        else:
            raise ValueError("Request Queue does not contain any elements. Please add requests before execution.")

