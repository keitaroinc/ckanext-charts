from __future__ import annotations

import pytest

from ckanext.charts import config, helpers, utils
from ckanext.charts.chart_builders import get_all_chart_engines, get_chart_engines


class TestDisabledEngines:
    """Tests for the ckanext.charts.disabled_engines config option"""

    def test_no_engine_is_disabled_by_default(self):
        assert config.get_disabled_engines() == []
        assert get_chart_engines() == get_all_chart_engines()

    @pytest.mark.ckan_config("ckanext.charts.disabled_engines", "chartjs")
    def test_disabled_engine_is_excluded_from_the_registry(self):
        assert config.get_disabled_engines() == ["chartjs"]
        assert "chartjs" not in get_chart_engines()
        assert "plotly" in get_chart_engines()

    @pytest.mark.ckan_config("ckanext.charts.disabled_engines", "chartjs")
    def test_disabled_engine_stays_registered(self):
        """A disabled engine is only filtered out, not unregistered."""
        assert "chartjs" in get_all_chart_engines()

    @pytest.mark.ckan_config("ckanext.charts.disabled_engines", "chartjs echarts")
    def test_multiple_engines_could_be_disabled(self):
        assert config.get_disabled_engines() == ["chartjs", "echarts"]
        assert "chartjs" not in get_chart_engines()
        assert "echarts" not in get_chart_engines()

    @pytest.mark.ckan_config("ckanext.charts.disabled_engines", "chartjs")
    def test_disabled_engine_is_not_offered_by_the_form(self):
        options = helpers.get_available_chart_engines_options()

        assert {"value": "chartjs", "text": "chartjs"} not in options
        assert {"value": "plotly", "text": "plotly"} in options

    @pytest.mark.ckan_config("ckanext.charts.disabled_engines", "chartjs")
    def test_engine_enabled_helper(self):
        assert not helpers.charts_is_engine_enabled("chartjs")
        assert helpers.charts_is_engine_enabled("plotly")

    def test_chart_is_built_when_the_engine_is_enabled(self, data_frame):
        assert utils.build_chart_for_data(
            {"type": "Bar", "engine": "chartjs", "x": "name", "y": "age"},
            data_frame,
        )

    @pytest.mark.ckan_config("ckanext.charts.disabled_engines", "chartjs")
    def test_chart_is_not_built_when_the_engine_is_disabled(self, data_frame):
        with pytest.raises(NotImplementedError):
            utils.build_chart_for_data(
                {"type": "Bar", "engine": "chartjs", "x": "name", "y": "age"},
                data_frame,
            )
