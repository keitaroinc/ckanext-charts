from __future__ import annotations

from ckanext.charts import config

from .base import BaseChartBuilder
from .chartjs import ChartJSBarBuilder
from .echarts import EChartsBuilder
from .observable import ObservableBuilder
from .plotly import PlotlyBuilder
from .plotly.bar import PlotlyBarForm

DEFAULT_CHART_FORM = PlotlyBarForm

_CHART_ENGINES: dict[str, type[BaseChartBuilder]] = {
    "plotly": PlotlyBuilder,
    "observable": ObservableBuilder,
    "chartjs": ChartJSBarBuilder,
    "echarts": EChartsBuilder,
}


def get_chart_engines() -> dict[str, type[BaseChartBuilder]]:
    """Get the chart engines available for building charts.

    Engines listed in the `ckanext.charts.disabled_engines` config option are
    excluded, which removes them from the engine dropdown and makes charts
    saved with them unbuildable.
    """
    disabled = config.get_disabled_engines()

    return {
        engine: builder
        for engine, builder in _CHART_ENGINES.items()
        if engine not in disabled
    }


def get_all_chart_engines() -> dict[str, type[BaseChartBuilder]]:
    """Get all registered chart engines, including the disabled ones."""
    return dict(_CHART_ENGINES)
