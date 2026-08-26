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

    def test_bar_skips_null_categories(self):
        """A row without a category has nothing to sit above on the category
        axis, so skipping the null values has to drop it rather than draw a
        bar of its own."""
        result = json.loads(
            utils.build_chart_for_data(
                {
                    "type": "Bar",
                    "engine": "plotly",
                    "x": "name",
                    "y": "amount",
                    "skip_null_values": True,
                },
                pd.DataFrame({"name": ["Alice", None], "amount": [1.0, 2.0]}),
            ),
        )

        assert list(result["data"][0]["x"]) == ["Alice"]

    def test_bar_skips_null_values(self):
        """A row without a value cannot be measured, so it goes as well."""
        result = json.loads(
            utils.build_chart_for_data(
                {
                    "type": "Bar",
                    "engine": "plotly",
                    "x": "name",
                    "y": "amount",
                    "skip_null_values": True,
                },
                pd.DataFrame({"name": ["Alice", "Bob"], "amount": [1.0, None]}),
            ),
        )

        assert list(result["data"][0]["x"]) == ["Alice"]

    def test_horizontal_bar_skips_null_categories(self):
        """A horizontal bar carries its categories on the y axis."""
        result = json.loads(
            utils.build_chart_for_data(
                {
                    "type": "Horizontal Bar",
                    "engine": "plotly",
                    "x": "name",
                    "y": "amount",
                    "skip_null_values": True,
                },
                pd.DataFrame({"name": ["Alice", None], "amount": [1.0, 2.0]}),
            ),
        )

        assert list(result["data"][0]["y"]) == ["Alice"]

    def test_scatter_skips_null_categories(self):
        result = json.loads(
            utils.build_chart_for_data(
                {
                    "type": "Scatter",
                    "engine": "plotly",
                    "x": "name",
                    "y": "amount",
                    "size": "amount",
                    "skip_null_values": True,
                },
                pd.DataFrame({"name": ["Alice", None], "amount": [1.0, 2.0]}),
            ),
        )

        assert list(result["data"][0]["x"]) == ["Alice"]

    def test_scatter_keeps_zero_values(self):
        """A zero is a value of its own, not a missing one."""
        result = json.loads(
            utils.build_chart_for_data(
                {
                    "type": "Scatter",
                    "engine": "plotly",
                    "x": "name",
                    "y": "amount",
                    "size": "amount",
                    "skip_null_values": True,
                },
                pd.DataFrame({"name": ["Alice", "Bob"], "amount": [1.0, 0.0]}),
            ),
        )

        assert list(result["data"][0]["x"]) == ["Alice", "Bob"]

    def test_line_skips_null_categories(self):
        """A point without a category cannot be placed on the category axis,
        while a missing value stays to leave a gap in the line."""
        result = json.loads(
            utils.build_chart_for_data(
                {
                    "type": "Line",
                    "engine": "plotly",
                    "x": "name",
                    "y": ["amount"],
                    "skip_null_values": True,
                },
                pd.DataFrame(
                    {"name": ["Alice", None, "Bob"], "amount": [1.0, 2.0, None]},
                ),
            ),
        )

        # `Bob` carries no value and stays behind to leave the gap
        assert list(result["data"][0]["x"]) == ["Alice", "Bob"]

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

    def test_bar_skips_null_categories(self):
        """A row without a category has nothing to label, so skipping the null
        values has to drop it rather than leave an unlabelled bar."""
        result = json.loads(
            utils.build_chart_for_data(
                {
                    "type": "Bar",
                    "engine": "chartjs",
                    "x": "name",
                    "y": ["amount"],
                    "skip_null_values": True,
                },
                pd.DataFrame({"name": ["Alice", None], "amount": [1.0, 2.0]}),
            ),
        )

        assert result["data"]["labels"] == ["Alice"]

    def test_bar_skips_null_values(self):
        result = json.loads(
            utils.build_chart_for_data(
                {
                    "type": "Bar",
                    "engine": "chartjs",
                    "x": "name",
                    "y": ["amount"],
                    "skip_null_values": True,
                },
                pd.DataFrame({"name": ["Alice", "Bob"], "amount": [1.0, None]}),
            ),
        )

        assert result["data"]["labels"] == ["Alice"]

    def test_bar_with_several_y_keeps_rows_of_the_other_series(self):
        """With several columns graphed a row missing one of the values still
        carries the others, so only the rows without a category go."""
        result = json.loads(
            utils.build_chart_for_data(
                {
                    "type": "Bar",
                    "engine": "chartjs",
                    "x": "name",
                    "y": ["amount", "total"],
                    "skip_null_values": True,
                },
                pd.DataFrame(
                    {
                        "name": ["Alice", "Bob", None],
                        "amount": [1.0, None, 3.0],
                        "total": [4.0, 5.0, 6.0],
                    },
                ),
            ),
        )

        assert result["data"]["labels"] == ["Alice", "Bob"]

    def test_horizontal_bar_skips_null_categories(self):
        result = json.loads(
            utils.build_chart_for_data(
                {
                    "type": "Horizontal Bar",
                    "engine": "chartjs",
                    "x": "name",
                    "y": ["amount"],
                    "skip_null_values": True,
                },
                pd.DataFrame({"name": ["Alice", None], "amount": [1.0, 2.0]}),
            ),
        )

        assert result["data"]["labels"] == ["Alice"]

    def test_line_skips_null_categories(self):
        """A point without a category cannot be placed on the category axis,
        while a missing value stays to leave a gap in the line."""
        result = json.loads(
            utils.build_chart_for_data(
                {
                    "type": "Line",
                    "engine": "chartjs",
                    "x": "name",
                    "y": ["amount"],
                    "skip_null_values": True,
                },
                pd.DataFrame(
                    {"name": ["Alice", None, "Bob"], "amount": [1.0, 2.0, None]},
                ),
            ),
        )

        assert result["data"]["labels"] == ["Alice", "Bob"]
        assert result["data"]["datasets"][0]["data"] == [1.0, "null"]

    def test_scatter_skips_null_rows(self):
        result = json.loads(
            utils.build_chart_for_data(
                {
                    "type": "Scatter",
                    "engine": "chartjs",
                    "x": "name",
                    "y": "amount",
                    "skip_null_values": True,
                },
                pd.DataFrame(
                    {"name": ["Alice", None, "Bob"], "amount": [1.0, 2.0, None]},
                ),
            ),
        )

        assert [point["x"] for point in result["data"]["datasets"][0]["data"]] == [
            "Alice",
        ]

    def test_bubble_skips_null_rows(self):
        result = json.loads(
            utils.build_chart_for_data(
                {
                    "type": "Bubble",
                    "engine": "chartjs",
                    "x": "name",
                    "y": "amount",
                    "size": "amount",
                    "skip_null_values": True,
                },
                pd.DataFrame(
                    {"name": ["Alice", None, "Bob"], "amount": [1.0, 2.0, None]},
                ),
            ),
        )

        assert [point["x"] for point in result["data"]["datasets"][0]["data"]] == [
            "Alice",
        ]

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
        """Skipping the null values drops the rows without a category, so the
        category column keeps its numeric type and its verbatim format."""
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

        assert [row["Year"] for row in result["data"]] == [2000.0]
        assert result["plot"]["y"]["tickFormat"] == "d"

    def test_bar_skips_null_categories(self):
        """A row without a category has nothing to sit above on the category
        axis, so skipping the null values has to drop it rather than gather
        every such row into a bar labelled `null`."""
        result = json.loads(
            utils.build_chart_for_data(
                {
                    "type": "Bar",
                    "engine": "observable",
                    "x": "name",
                    "y": "amount",
                    "skip_null_values": True,
                },
                pd.DataFrame(
                    {"name": ["Alice", None], "amount": [1.0, 2.0]},
                ),
            ),
        )

        assert [row["name"] for row in result["data"]] == ["Alice"]

    def test_bar_skips_null_values(self):
        """A row without a value cannot be measured, so it goes as well."""
        result = json.loads(
            utils.build_chart_for_data(
                {
                    "type": "Bar",
                    "engine": "observable",
                    "x": "name",
                    "y": "amount",
                    "skip_null_values": True,
                },
                pd.DataFrame(
                    {"name": ["Alice", "Bob"], "amount": [1.0, None]},
                ),
            ),
        )

        assert [row["name"] for row in result["data"]] == ["Alice"]

    def test_bar_keeps_null_rows_by_default(self):
        """Without the setting the null values keep their filler, so that the
        rows stay on the chart."""
        result = json.loads(
            utils.build_chart_for_data(
                {
                    "type": "Bar",
                    "engine": "observable",
                    "x": "name",
                    "y": "amount",
                },
                pd.DataFrame(
                    {"name": ["Alice", None], "amount": [1.0, 2.0]},
                ),
            ),
        )

        assert [row["name"] for row in result["data"]] == ["Alice", 0]

    def test_horizontal_bar_skips_null_values(self):
        """A horizontal bar carries its values on the x axis."""
        result = json.loads(
            utils.build_chart_for_data(
                {
                    "type": "Horizontal Bar",
                    "engine": "observable",
                    "x": "amount",
                    "y": "name",
                    "skip_null_values": True,
                },
                pd.DataFrame(
                    {"name": ["Alice", "Bob"], "amount": [1.0, None]},
                ),
            ),
        )

        assert [row["name"] for row in result["data"]] == ["Alice"]

    def test_bar_skips_null_rows_of_a_single_column(self):
        """The same column may carry both the categories and the values."""
        result = json.loads(
            utils.build_chart_for_data(
                {
                    "type": "Bar",
                    "engine": "observable",
                    "x": "amount",
                    "y": "amount",
                    "skip_null_values": True,
                },
                pd.DataFrame({"amount": [1.0, None]}),
            ),
        )

        assert [row["amount"] for row in result["data"]] == [1.0]

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

    def test_line_skips_null_categories(self):
        """A point without a category cannot be placed on the category axis."""
        result = json.loads(
            utils.build_chart_for_data(
                {
                    "type": "Line",
                    "engine": "observable",
                    "x": "name",
                    "y": ["amount"],
                    "skip_null_values": True,
                },
                pd.DataFrame(
                    {"name": ["Alice", None], "amount": [1.0, 2.0]},
                ),
            ),
        )

        assert [row["name"] for row in result["data"]] == ["Alice"]

    def test_pie_skips_null_names(self):
        """A wedge without a name has no label and no colour of its own."""
        result = json.loads(
            utils.build_chart_for_data(
                {
                    "type": "Pie",
                    "engine": "observable",
                    "names": "name",
                    "values": "amount",
                    "skip_null_values": True,
                },
                pd.DataFrame(
                    {"name": ["Alice", None], "amount": [1.0, 2.0]},
                ),
            ),
        )

        assert [row["name"] for row in result["data"]] == ["Alice"]

    def test_not_supported_chart_type(self, data_frame):
        with pytest.raises(
            exception.ChartTypeNotImplementedError,
            match="Chart type not implemented",
        ):
            utils.build_chart_for_data(
                {"type": "Unknown", "engine": "observable"},
                data_frame,
            )
