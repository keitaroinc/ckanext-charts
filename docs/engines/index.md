The `ckanext-charts` implements supports different chart engines, such as `plotly`, `observable`, `chartjs` and `echarts`.

Each engine consists of two classes - chart builder and form builder. The chart builder is responsible for generating a JSON-string representation of the chart data, that will be passed to a respective JS module, that will render a chart based on the data.

The form builder is responsible for generating a form that allows users to configure the chart from the UI.

Any of these engines can be excluded from the chart and chart builder views with the
[`ckanext.charts.disabled_engines`](../configuration.md) configuration option.

Also, you can implement support of a chart library of your choice by creating a custom chart engine. Read more about it  [here](./custom.md).

