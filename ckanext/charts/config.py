import ckan.plugins.toolkit as tk

CONF_CACHE_STRATEGY = "ckanext.charts.cache_strategy"
CONF_REDIS_CACHE_TTL = "ckanext.charts.redis_cache_ttl"
CONF_FILE_CACHE_TTL = "ckanext.charts.file_cache_ttl"
CONF_ENABLE_CACHE = "ckanext.charts.enable_cache"
CONF_SERVERSIDE_RENDER = "ckanext.charts.use_serverside_rendering"
CONF_ENABLE_HTMX = "ckanext.charts.include_htmx_asset"
CONF_REINIT_JS = "ckanext.charts.reinit_ckan_js_modules"
CONF_ALLOW_ANON_CHART = "ckanext.charts.allow_anon_building_charts"
CONF_MAX_FETCH_SIZE = "ckanext.charts.max_fetch_size"
CONF_DISABLED_ENGINES = "ckanext.charts.disabled_engines"
CONF_DISABLED_CHART_TYPES = "ckanext.charts.disabled_chart_types"


def get_cache_strategy() -> str:
    """Get an active cache strategy from the configuration."""
    return tk.config[CONF_CACHE_STRATEGY]


def get_redis_cache_ttl() -> int:
    """Get the redis cache time-to-live from the configuration."""
    return tk.asint(tk.config[CONF_REDIS_CACHE_TTL])


def get_file_cache_ttl() -> int:
    """Get the file cache time-to-live from the configuration."""
    return tk.asint(tk.config[CONF_FILE_CACHE_TTL])


def is_cache_enabled() -> bool:
    """Check if the cache is enabled."""
    return tk.asbool(tk.config[CONF_ENABLE_CACHE])


def use_serverside_rendering() -> bool:
    """Check if the server-side rendering is enabled."""
    return tk.asbool(tk.config[CONF_SERVERSIDE_RENDER])


def include_htmx_asset() -> bool:
    """Include HTMX library asset. Disable it, if no other library do it."""
    return tk.asbool(tk.config[CONF_ENABLE_HTMX])


def reinit_ckan_js_modules() -> bool:
    """Reinitialize CKAN JS modules."""
    return tk.asbool(tk.config[CONF_REINIT_JS])


def allow_anon_building_charts() -> bool:
    """Allow anonymous users to build charts."""
    return tk.asbool(tk.config[CONF_ALLOW_ANON_CHART])


def get_max_fetch_size() -> int:
    """Get the maximum allowed fetch size in bytes.

    The configuration value is expressed in megabytes for readability and
    converted to bytes here.
    """
    return tk.asint(tk.config[CONF_MAX_FETCH_SIZE]) * 1024 * 1024


def get_disabled_engines() -> list[str]:
    """Get the list of chart engines excluded from the chart views.

    A disabled engine is not offered in the engine dropdown and cannot be
    used to build a chart.
    """
    engines = tk.config[CONF_DISABLED_ENGINES]

    if isinstance(engines, str):
        engines = engines.split()

    return [engine.strip() for engine in engines if engine.strip()]


def get_disabled_chart_types() -> list[str]:
    """Get the list of chart types excluded from the chart views.

    Entries are comma-separated, unlike the space-separated engine list,
    because a chart type name may contain a space, e.g. `Horizontal Bar`.

    An entry is either a bare type name, which disables the type in every
    engine, or an `engine:type` pair, which disables it in that engine only.
    """
    chart_types = tk.config[CONF_DISABLED_CHART_TYPES]

    if isinstance(chart_types, str):
        chart_types = chart_types.split(",")

    return [chart_type.strip() for chart_type in chart_types if chart_type.strip()]


def is_chart_type_disabled(engine: str, chart_type: str) -> bool:
    """Check if the chart type is disabled for the given engine.

    A disabled type is not offered in the chart type dropdown and cannot be
    used to build a chart. Matching ignores case on both the engine and the
    type name.
    """
    for entry in get_disabled_chart_types():
        disabled_engine, _, disabled_type = entry.rpartition(":")

        if disabled_engine and disabled_engine.strip().lower() != engine.lower():
            continue

        if disabled_type.strip().lower() == chart_type.lower():
            return True

    return False
