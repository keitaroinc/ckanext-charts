from __future__ import annotations

import json

import pandas as pd
import pytest

from ckanext.charts import exception, utils


@pytest.mark.ckan_config("ckan.plugins", "datastore charts_view")
@pytest.mark.usefixtures("clean_db", "with_plugins")
class TestPlotlyBuilder:
    """Tests for PlotlyBuilder"""

    def test_build_bar(self, data_frame):
        result = utils.build_chart_for_data(
            {
                "type": "Bar",
                "engine": "plotly",
                "x": "name",
                "y": "age",
            },
            data_frame,
        )

        assert result
        assert "data" in result
        assert "layout" in result

    def test_horizontal_bar(self, data_frame):
        result = utils.build_chart_for_data(
            {
                "type": "Horizontal Bar",
                "engine": "plotly",
                "x": "age",
                "y": "name",
            },
            data_frame,
        )

        assert result
        assert "data" in result
        assert "layout" in result

    def test_build_line(self, data_frame):
        result = utils.build_chart_for_data(
            {
                "type": "Line",
                "engine": "plotly",
                "x": "name",
                "y": ["age"],
            },
            data_frame,
        )

        assert result
        assert "data" in result
        assert "layout" in result

    def test_build_multi_y_line(self, data_frame):
        result = utils.build_chart_for_data(
            {
                "type": "Line",
                "engine": "plotly",
                "x": "name",
                "y": ["age", "surname"],
            },
            data_frame,
        )

        assert result
        assert "data" in result
        assert "layout" in result

        layout = json.loads(result)["layout"]

        assert "yaxis" in layout
        assert "yaxis2" in layout

    def test_build_line_same_x_and_y(self, data_frame):
        """The Y column may be the same as the X column (e.g. both default to
        the first datastore column). This must not crash with a duplicate
        column error from Plotly.
        """
        result = utils.build_chart_for_data(
            {
                "type": "Line",
                "engine": "plotly",
                "x": "name",
                "y": ["name"],
            },
            data_frame,
        )

        assert result
        assert "data" in result
        assert "layout" in result

    def test_build_scatter(self, data_frame):
        result = utils.build_chart_for_data(
            {
                "type": "Scatter",
                "engine": "plotly",
                "x": "name",
                "y": "age",
                "size": "age",
            },
            data_frame,
        )

        assert result
        assert "data" in result
        assert "layout" in result

    def test_build_scatter_no_size(self, data_frame):
        with pytest.raises(
            exception.ChartBuildError,
            match="The 'Size' source should be a field of numeric type",
        ):
            utils.build_chart_for_data(
                {
                    "type": "Scatter",
                    "engine": "plotly",
                    "x": "name",
                    "y": "age",
                },
                data_frame,
            )

    def test_build_pie(self, data_frame):
        result = utils.build_chart_for_data(
            {
                "type": "Pie",
                "engine": "plotly",
                "names": "name",
                "values": "age",
            },
            data_frame,
        )

        assert result
        assert "data" in result
        assert "layout" in result

    def test_build_choropleth(self, map_data_frame):
        result = utils.build_chart_for_data(
            {
                "type": "Choropleth",
                "engine": "plotly",
                "x": "country",
                "y": "population",
            },
            map_data_frame,
        )

        assert result
        assert "data" in result
        assert "layout" in result

    def test_not_supported_chart_type(self, data_frame):
        with pytest.raises(
            exception.ChartTypeNotImplementedError,
            match="Chart type not implemented",
        ):
            utils.build_chart_for_data(
                {"type": "Unknown", "engine": "plotly"},
                data_frame,
            )


@pytest.mark.ckan_config("ckan.plugins", "charts_view")
@pytest.mark.usefixtures("clean_db", "with_plugins")
class TestChartJsBuilder:
    """Tests for ChartJsBuilder"""

    def test_build_bar(self, data_frame):
        result = utils.build_chart_for_data(
            {
                "type": "Bar",
                "engine": "chartjs",
                "x": "name",
                "y": ["age"],
            },
            data_frame,
        )

        assert result
        assert "type" in result
        assert "data" in result
        assert "options" in result

    def test_horizontal_bar(self, data_frame):
        result = utils.build_chart_for_data(
            {
                "type": "Horizontal Bar",
                "engine": "chartjs",
                "x": "name",
                "y": ["age"],
            },
            data_frame,
        )

        assert result
        assert "type" in result
        assert "data" in result
        assert "options" in result

    def test_build_line(self, data_frame):
        result = utils.build_chart_for_data(
            {
                "type": "Line",
                "engine": "chartjs",
                "x": "name",
                "y": ["age"],
            },
            data_frame,
        )

        assert result
        assert "type" in result
        assert "data" in result
        assert "options" in result

    def test_build_multi_y_line(self, data_frame):
        result = utils.build_chart_for_data(
            {
                "type": "Line",
                "engine": "chartjs",
                "x": "name",
                "y": ["age", "surname"],
            },
            data_frame,
        )

        assert result
        assert "type" in result
        assert "data" in result
        assert "options" in result

    def test_build_pie(self, data_frame):
        result = utils.build_chart_for_data(
            {
                "type": "Pie",
                "engine": "chartjs",
                "names": "name",
                "values": "age",
            },
            data_frame,
        )

        assert result
        assert "type" in result
        assert "data" in result
        assert "options" in result

    def test_build_doughnut(self, data_frame):
        result = utils.build_chart_for_data(
            {
                "type": "Doughnut",
                "engine": "chartjs",
                "names": "name",
                "values": "age",
            },
            data_frame,
        )

        assert result
        assert "type" in result
        assert "data" in result
        assert "options" in result

    def test_scatter(self, data_frame):
        result = utils.build_chart_for_data(
            {
                "type": "Scatter",
                "engine": "chartjs",
                "x": "name",
                "y": "age",
            },
            data_frame,
        )

        assert result
        assert "type" in result
        assert "data" in result
        assert "options" in result

    def test_bubble(self, data_frame):
        result = utils.build_chart_for_data(
            {
                "type": "Bubble",
                "engine": "chartjs",
                "x": "name",
                "y": "age",
                "size": "age",
            },
            data_frame,
        )

        assert result
        assert "type" in result
        assert "data" in result
        assert "options" in result

    def test_bubble_not_numeric_column(self, data_frame):
        with pytest.raises(
            exception.ChartBuildError,
            match="Column 'surname' is not numeric",
        ):
            utils.build_chart_for_data(
                {
                    "type": "Bubble",
                    "engine": "chartjs",
                    "x": "name",
                    "y": "age",
                    "size": "surname",
                },
                data_frame,
            )

    def test_not_supported_chart_type(self, data_frame):
        with pytest.raises(
            exception.ChartTypeNotImplementedError,
            match="Chart type not implemented",
        ):
            utils.build_chart_for_data(
                {"type": "Unknown", "engine": "chartjs"},
                data_frame,
            )


@pytest.mark.ckan_config("ckan.plugins", "charts_view")
@pytest.mark.usefixtures("clean_db", "with_plugins")
class TestObservableBuilder:
    """Tests for ObservableBuilder"""

    def test_build_bar(self, data_frame):
        result = utils.build_chart_for_data(
            {
                "type": "Bar",
                "engine": "observable",
                "x": "name",
                "y": ["age"],
            },
            data_frame,
        )

        assert result
        assert "data" in result
        assert "plot" in result
        assert "settings" in result
        assert "bar" in result

    def test_build_bar_with_numeric_x(self):
        """Plot groups the digits of numeric ticks, so a year would read
        as `2,000` on the category axis of a bar chart."""
        result = json.loads(
            utils.build_chart_for_data(
                {
                    "type": "Bar",
                    "engine": "observable",
                    "x": "Year",
                    "y": "amount",
                },
                pd.DataFrame({"Year": [2000.0, 2001.0], "amount": [1.0, 2.0]}),
            ),
        )

        assert result["plot"]["x"]["tickFormat"] == "d"

    def test_build_bar_keeps_group_separator_of_value_axis(self, data_frame):
        """Only the category axis prints its numbers verbatim, the values
        keep the separator that makes big numbers readable."""
        result = json.loads(
            utils.build_chart_for_data(
                {
                    "type": "Bar",
                    "engine": "observable",
                    "x": "name",
                    "y": "age",
                },
                data_frame,
            ),
        )

        assert "tickFormat" not in result["plot"]["x"]
        assert "tickFormat" not in result["plot"]["y"]

    def test_horizontal_bar(self, data_frame):
        result = utils.build_chart_for_data(
            {
                "type": "Horizontal Bar",
                "engine": "observable",
                "x": "name",
                "y": ["age"],
            },
            data_frame,
        )

        assert result
        assert "data" in result
        assert "plot" in result
        assert "settings" in result
        assert "horizontal-bar" in result

    def test_horizontal_bar_with_numeric_y(self):
        """A horizontal bar chart carries its categories on the y axis, so
        that is the axis whose years must not read as `2,000`."""
        result = json.loads(
            utils.build_chart_for_data(
                {
                    "type": "Horizontal Bar",
                    "engine": "observable",
                    "x": "amount",
                    "y": "Year",
                },
                pd.DataFrame({"Year": [2000.0, 2001.0], "amount": [1.0, 2.0]}),
            ),
        )

        assert result["plot"]["y"]["tickFormat"] == "d"
        assert "tickFormat" not in result["plot"]["x"]

    def test_horizontal_bar_with_skipped_null_categories(self):
        """Skipping the null values leaves the category column holding the
        string `null`, which the numeric format would print as `NaN`."""
        result = json.loads(
            utils.build_chart_for_data(
                {
                    "type": "Horizontal Bar",
                    "engine": "observable",
                    "x": "amount",
                    "y": "Year",
                    "skip_null_values": True,
                },
                pd.DataFrame(
                    {"Year": [2000.0, None], "amount": [1.0, 2.0]},
                ),
            ),
        )

        assert "tickFormat" not in result["plot"]["y"]

    def test_build_line(self, data_frame):
        result = utils.build_chart_for_data(
            {
                "type": "Line",
                "engine": "observable",
                "x": "name",
                "y": ["age"],
            },
            data_frame,
        )

        assert result
        assert "data" in result
        assert "plot" in result
        assert "settings" in result
        assert "line" in result

    def test_build_multi_y_line(self, data_frame):
        result = utils.build_chart_for_data(
            {
                "type": "Line",
                "engine": "observable",
                "x": "name",
                "y": ["age", "surname"],
            },
            data_frame,
        )

        assert result
        assert "data" in result
        assert "plot" in result
        assert "settings" in result
        assert "line" in result

    def test_build_line_with_numeric_x(self):
        """A numeric column such as `Year` holds plain numbers, not dates.

        On a `utc` scale Plot reads those numbers as milliseconds since the
        epoch, so every year would collapse onto 1970-01-01.
        """
        result = json.loads(
            utils.build_chart_for_data(
                {
                    "type": "Line",
                    "engine": "observable",
                    "x": "Year",
                    "y": ["amount"],
                },
                pd.DataFrame({"Year": [2000.0, 2001.0], "amount": [1.0, 2.0]}),
            ),
        )

        assert "type" not in result["plot"]["x"]
        assert result["plot"]["x"]["tickFormat"] == "d"
        assert [row["Year"] for row in result["data"]] == [2000.0, 2001.0]

    def test_build_pie(self, data_frame):
        result = utils.build_chart_for_data(
            {
                "type": "Pie",
                "engine": "observable",
                "names": "name",
                "values": "age",
            },
            data_frame,
        )

        assert result
        assert "data" in result
        assert "settings" in result
        assert "pie" in result

    def test_build_scatter(self, data_frame):
        result = utils.build_chart_for_data(
            {
                "type": "Scatter",
                "engine": "observable",
                "x": "name",
                "y": "age",
                "size": "age",
            },
            data_frame,
        )

        assert result
        assert "data" in result
        assert "plot" in result
        assert "settings" in result
        assert "scatter" in result

    def test_build_scatter_with_numeric_x(self):
        result = json.loads(
            utils.build_chart_for_data(
                {
                    "type": "Scatter",
                    "engine": "observable",
                    "x": "Year",
                    "y": "amount",
                    "size_max": 10,
                },
                pd.DataFrame({"Year": [2000.0, 2001.0], "amount": [1.0, 2.0]}),
            ),
        )

        assert result["plot"]["x"]["tickFormat"] == "d"

    def test_not_supported_chart_type(self, data_frame):
        with pytest.raises(
            exception.ChartTypeNotImplementedError,
            match="Chart type not implemented",
        ):
            utils.build_chart_for_data(
                {"type": "Unknown", "engine": "observable"},
                data_frame,
            )
