from __future__ import annotations

import pytest

from ckanext.charts import config, exception
from ckanext.charts.chart_builders.chartjs import ChartJsBuilder
from ckanext.charts.chart_builders.plotly.bar import PlotlyBarForm
from ckanext.charts.chart_builders.plotly.base import PlotlyBuilder


def form_names(builder) -> list[str]:
    return [form.name for form in builder.get_supported_forms()]


class TestDisabledChartTypes:
    """Tests for the ckanext.charts.disabled_chart_types config option"""

    def test_no_chart_type_is_disabled_by_default(self):
        assert config.get_disabled_chart_types() == []
        assert "Choropleth" in form_names(PlotlyBuilder)

    @pytest.mark.ckan_config("ckanext.charts.disabled_chart_types", "plotly:Choropleth")
    def test_qualified_entry_hides_the_type_from_its_engine(self):
        assert "Choropleth" not in form_names(PlotlyBuilder)
        assert "Bar" in form_names(PlotlyBuilder)

    @pytest.mark.ckan_config("ckanext.charts.disabled_chart_types", "plotly:Bar")
    def test_qualified_entry_leaves_other_engines_alone(self):
        assert "Bar" not in form_names(PlotlyBuilder)
        assert "Bar" in form_names(ChartJsBuilder)

    @pytest.mark.ckan_config("ckanext.charts.disabled_chart_types", "Bar")
    def test_bare_entry_hides_the_type_from_every_engine(self):
        assert "Bar" not in form_names(PlotlyBuilder)
        assert "Bar" not in form_names(ChartJsBuilder)

    @pytest.mark.ckan_config(
        "ckanext.charts.disabled_chart_types",
        "plotly:Horizontal Bar, plotly:Pie",
    )
    def test_entries_are_comma_separated_so_names_may_contain_spaces(self):
        names = form_names(PlotlyBuilder)

        assert "Horizontal Bar" not in names
        assert "Pie" not in names
        assert "Bar" in names

    @pytest.mark.ckan_config("ckanext.charts.disabled_chart_types", "PLOTLY:choropleth")
    def test_matching_is_case_insensitive(self):
        assert "Choropleth" not in form_names(PlotlyBuilder)

    @pytest.mark.ckan_config("ckanext.charts.disabled_chart_types", "plotly:Choropleth")
    def test_a_saved_view_of_a_disabled_type_no_longer_resolves(self):
        """This is what degrades an existing Choropleth resource view."""
        with pytest.raises(exception.ChartTypeNotImplementedError):
            PlotlyBuilder.get_form_for_type("Choropleth")

    @pytest.mark.ckan_config("ckanext.charts.disabled_chart_types", "plotly:Bar")
    def test_the_default_type_falls_through_to_the_first_enabled_one(self):
        """An empty chart type picks the first form that is still enabled."""
        assert PlotlyBuilder.get_form_for_type("").name != "Bar"

    @pytest.mark.ckan_config(
        "ckanext.charts.disabled_chart_types",
        "plotly:Bar, plotly:Horizontal Bar, plotly:Pie, plotly:Line,"
        " plotly:Scatter, plotly:Choropleth",
    )
    def test_disabling_every_type_of_an_engine_raises_instead_of_index_error(self):
        assert form_names(PlotlyBuilder) == []

        with pytest.raises(exception.ChartTypeNotImplementedError):
            PlotlyBuilder.get_form_for_type("")

    @pytest.mark.ckan_config("ckanext.charts.disabled_chart_types", "plotly:Choropleth")
    def test_the_type_dropdown_of_a_form_drops_the_disabled_type(self):
        """`get_form_fields` builds the type dropdown off `builder.get_supported_forms`."""
        chart_types = [form.name for form in PlotlyBarForm.builder.get_supported_forms()]

        assert "Choropleth" not in chart_types
        assert "Bar" in chart_types
