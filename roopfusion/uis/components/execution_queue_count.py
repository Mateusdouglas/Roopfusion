from typing import Optional
import gradio

import roopfusion.globals
import roopfusion.choices
from roopfusion import wording

EXECUTION_QUEUE_COUNT_SLIDER : Optional[gradio.Slider] = None


def render() -> None:
	global EXECUTION_QUEUE_COUNT_SLIDER

	EXECUTION_QUEUE_COUNT_SLIDER = gradio.Slider(
		label = wording.get('uis.execution_queue_count_slider'),
		value = roopfusion.globals.execution_queue_count,
		step = roopfusion.choices.execution_queue_count_range[1] - roopfusion.choices.execution_queue_count_range[0],
		minimum = roopfusion.choices.execution_queue_count_range[0],
		maximum = roopfusion.choices.execution_queue_count_range[-1]
	)


def listen() -> None:
	EXECUTION_QUEUE_COUNT_SLIDER.release(update_execution_queue_count, inputs = EXECUTION_QUEUE_COUNT_SLIDER)


def update_execution_queue_count(execution_queue_count : int = 1) -> None:
	roopfusion.globals.execution_queue_count = execution_queue_count
