"""Core API functions."""
from diffy.core import baseline, analysis
from diffy_api.extensions import rq
from diffy_api.schemas import baseline_input_schema, analysis_input_schema


@rq.job()
def async_baseline(kwargs):
    """Wrap our standard baseline task."""
    # we can't pickle our objects for remote works so we pickle the raw request
    # and then load it here.
    data = baseline_input_schema.load(kwargs).data
    return baseline(**data)


@rq.job()
def async_analysis(kwargs):
    """Wrap our standard analysis task."""
    # we can't pickle our objects for remote works so we pickle the raw request
    # and then load it here.
    data = analysis_input_schema.load(kwargs).data
    return analysis(**data)
