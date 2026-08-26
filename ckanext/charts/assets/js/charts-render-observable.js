ckan.module("charts-render-observable", function($, _) {
    "use strict";

    // Plot draws a tick for every value of a band/point scale and never thins or
    // rotates them, so an ordinal axis with many categories overlaps itself.
    // These constants approximate the metrics of the tick font (10px sans-serif)
    // to decide when the labels stop fitting side by side.
    var TICK_CHAR_WIDTH = 6.5;
    var TICK_LINE_HEIGHT = 12;
    var TICK_GAP = 6;
    var TICK_ROTATE = -45;
    var DEFAULT_PLOT_WIDTH = 640;
    var DEFAULT_PLOT_HEIGHT = 400;
    var DEFAULT_MARGIN_X = 60;
    var DEFAULT_MARGIN_BOTTOM = 30;
    var DEFAULT_MARGIN_LEFT = 40;
    // The tick line plus the gap Plot keeps between it and the tick label
    var TICK_OFFSET = 9;
    // A rotated axis label takes a line of text and sits 3px off the edge
    var AXIS_LABEL_ROOM = TICK_LINE_HEIGHT + 3;
    // Long categories may not push the drawing area off the plot
    var MAX_MARGIN_LEFT_RATIO = 1 / 3;

    return {
        options: {
            config: null,
        },

        initialize: function() {
            $.proxyAll(this, /_/);

            this.chartControl = this.el.next(".chart-control");
            this.chartId = this.el[0].id;

            window.charts_obvservable = window.charts_obvservable || {};

            if (!this.options.config) {
                console.error("No configuration provided");
                return;
            }

            var config = this.options.config;

            this._fitOrdinalXAxis(config);
            this._fitOrdinalYAxis(config);

            var plot = this._draw(config);

            if (!plot) {
                return;
            }

            this.el[0].replaceChildren(plot);

            // The margins of the plot have to be measured on the drawn chart,
            // so a chart whose tick labels do not fit is drawn a second time.
            plot = this._fitValueAxis(config, plot) || plot;

            window.charts_obvservable[this.chartId] = plot;

            this.chartControl.find("#makeSnapshot").on(
                "click", (e) => this._makeSnapshot(e, this.chartId)
            );
        },

        /**
         * Draw the chart of the given config.
         *
         * Plot reports the problems it finds in the data by printing them to
         * the console and marking the chart with a warning sign whose tooltip
         * says no more than that, leaving anyone looking at the chart with an
         * unexplained sign. Collect the messages and put them where the sign
         * points.
         */
        _draw: function(config) {
            var warnings = [];
            var warn = console.warn;
            var plot;

            console.warn = function() {
                warnings.push(Array.prototype.join.call(arguments, " "));
                warn.apply(console, arguments);
            };

            try {
                switch (config.type) {
                    case "bar":
                        plot = Plot.barY(config.data, config.settings).plot(config.plot);
                        break;
                    case "horizontal-bar":
                        plot = Plot.barX(config.data, config.settings).plot(config.plot);
                        break;
                    case "scatter":
                        plot = Plot.dot(config.data, config.settings).plot(config.plot);
                        break;
                    case "line":
                        plot = Plot.line(config.data, config.settings).plot(config.plot);
                        break;
                    case "pie":
                        plot = PieChart(config.data, config.settings);
                        break;
                    default:
                        return null;
                }
            } finally {
                console.warn = warn;
            }

            this._explainWarnings(plot, warnings);

            return plot;
        },

        /**
         * Replace the tooltip of the warning sign with the warnings themselves.
         */
        _explainWarnings: function(plot, warnings) {
            if (!warnings.length || !plot.querySelector) {
                return;
            }

            var title = plot.querySelector('text[font-family="initial"] > title');

            if (title) {
                title.textContent = warnings.join("\n\n");
            }
        },

        /**
         * Widen the left margin of the plot so that the tick labels of the
         * value axis fit, and draw the chart again when it has to grow.
         *
         * Plot keeps the left margin at its default width no matter how wide
         * the tick labels grow, and its SVG has a viewBox, so a label longer
         * than the margin is cut off at the edge of the chart rather than
         * spilling over it. Values in the hundreds of thousands take a label
         * of `500,000`, which is wider than the default margin.
         */
        _fitValueAxis: function(config, plot) {
            if (!config.plot) {
                return null;
            }

            var overflow = this._yTickOverflow(plot);

            if (overflow <= 0) {
                return null;
            }

            var width = config.plot.width || DEFAULT_PLOT_WIDTH;
            var margin = Math.min(
                (config.plot.marginLeft || DEFAULT_MARGIN_LEFT) + Math.ceil(overflow),
                Math.floor(width * MAX_MARGIN_LEFT_RATIO)
            );

            if (margin <= (config.plot.marginLeft || DEFAULT_MARGIN_LEFT)) {
                return null;
            }

            config.plot.marginLeft = margin;

            var refitted = this._draw(config);

            if (refitted) {
                this.el[0].replaceChildren(refitted);
            }

            return refitted;
        },

        /**
         * How far the y axis tick labels reach past the left edge of the
         * chart, in the coordinates of its viewBox.
         */
        _yTickOverflow: function(plot) {
            if (!plot.querySelectorAll) {
                return 0;
            }

            // Ask the labels which SVG they belong to: a chart with a colour
            // legend comes wrapped in a figure whose swatches are SVGs of
            // their own, standing before the one holding the chart.
            var labels = plot.querySelectorAll('[aria-label="y-axis tick label"] text');
            var overflow = 0;

            labels.forEach(function(label) {
                var svg = label.ownerSVGElement;

                if (!svg || !svg.viewBox || !svg.viewBox.baseVal.width) {
                    return;
                }

                var box = svg.getBoundingClientRect();

                // A chart of a hidden panel has no size to measure
                if (!box.width) {
                    return;
                }

                var scale = svg.viewBox.baseVal.width / box.width;

                overflow = Math.max(overflow, (box.left - label.getBoundingClientRect().left) * scale);
            });

            return overflow;
        },

        /**
         * Collect a scale domain in the order Plot builds it: the distinct
         * values of the column, keeping the order they appear in the data.
         */
        _domain: function(config, field) {
            var seen = {};
            var domain = [];

            (config.data || []).forEach(function(row) {
                var value = row[field];
                var key = String(value);

                if (!seen.hasOwnProperty(key)) {
                    seen[key] = true;
                    domain.push(value);
                }
            });

            return domain;
        },

        /**
         * Whether the x axis ends up as a band/point scale, i.e. one tick per
         * category with no automatic thinning.
         */
        _hasOrdinalXAxis: function(config, domain) {
            if (!config.plot || !config.plot.x || config.plot.x.type) {
                return false;
            }

            // barY always puts the categories on the x axis
            if (config.type === "bar") {
                return true;
            }

            if (config.type !== "line" && config.type !== "scatter") {
                return false;
            }

            return domain.every(function(value) {
                return typeof value !== "number";
            });
        },

        /**
         * Rotate the x axis tick labels when there are too many categories to
         * print them horizontally, and drop every n-th one when even rotated
         * labels would not stand apart.
         */
        _fitOrdinalXAxis: function(config) {
            if (!config.settings || !config.settings.x) {
                return;
            }

            var domain = this._domain(config, config.settings.x);

            if (!this._hasOrdinalXAxis(config, domain)) {
                return;
            }

            // Name the scale Plot would infer anyway. Left to infer it, Plot
            // warns whenever the categories look like dates - which the ones
            // of a date column always do - and the reason for its warning sign
            // only ever reaches the console.
            config.plot.x.type = config.type === "bar" ? "band" : "point";

            // Values of an ordinal axis are identifiers rather than measured
            // quantities, so print them verbatim instead of letting Plot group
            // the digits of numbers (a year 1995 would read as "1,995").
            config.plot.x.tickFormat = String;

            if (domain.length < 2) {
                return;
            }

            var labels = domain.map(String);
            var width = config.plot.width || DEFAULT_PLOT_WIDTH;
            var band = (width - DEFAULT_MARGIN_X) / labels.length;
            var labelWidth = TICK_CHAR_WIDTH * labels.reduce(function(longest, label) {
                return Math.max(longest, label.length);
            }, 0);

            if (labelWidth + TICK_GAP <= band) {
                return;
            }

            config.plot.x.tickRotate = TICK_ROTATE;

            // A label rotated by 45 degrees reaches labelWidth * sin(45) below
            // the axis, so the bottom margin has to grow by that much. Give the
            // plot the same extra height to keep the drawing area intact.
            var rotatedHeight = Math.ceil(labelWidth * Math.SQRT1_2);

            config.plot.marginBottom = rotatedHeight + DEFAULT_MARGIN_BOTTOM;
            config.plot.height = (config.plot.height || DEFAULT_PLOT_HEIGHT) + rotatedHeight;

            // Rotating buys vertical room, not horizontal: rotated labels still
            // need a line height of space between them.
            var step = Math.ceil(TICK_LINE_HEIGHT / band);

            if (step > 1) {
                config.plot.x.ticks = domain.filter(function(_value, index) {
                    return index % step === 0;
                });
            }
        },

        /**
         * Widen the left margin of a horizontal bar chart so that its tick
         * labels fit.
         *
         * A horizontal bar chart carries its categories on the y axis, where
         * Plot centers the axis label and rotates it against the left edge.
         * The margin keeps its default width no matter how wide the tick
         * labels grow, so anything longer than a few characters runs into
         * that label.
         */
        _fitOrdinalYAxis: function(config) {
            if (config.type !== "horizontal-bar" || !config.settings || !config.settings.y) {
                return;
            }

            // barX always puts the categories on the y axis, so name that
            // scale too rather than let Plot warn about date-like categories
            config.plot.y.type = "band";

            var labels = this._domain(config, config.settings.y).map(String);
            var labelWidth = TICK_CHAR_WIDTH * labels.reduce(function(longest, label) {
                return Math.max(longest, label.length);
            }, 0);

            var width = config.plot.width || DEFAULT_PLOT_WIDTH;
            var axisLabelRoom = config.plot.y.label ? AXIS_LABEL_ROOM : 0;
            var margin = Math.min(
                Math.ceil(labelWidth) + TICK_OFFSET + axisLabelRoom,
                Math.floor(width * MAX_MARGIN_LEFT_RATIO)
            );

            if (margin > (config.plot.marginLeft || DEFAULT_MARGIN_LEFT)) {
                config.plot.marginLeft = margin;
            }
        },

        _makeSnapshot: function(event, chartId) {
            event.preventDefault();

            var chart = window.charts_obvservable[chartId];

            if (!chart) {
                console.error("Chart not found");
                return;
            }

            //get svg element.
            var svg = chart.querySelector("svg");

            //get svg source.
            var serializer = new XMLSerializer();
            var source = serializer.serializeToString(svg);

            //add name spaces.
            if(!source.match(/^<svg[^>]+xmlns="http\:\/\/www\.w3\.org\/2000\/svg"/)){
                source = source.replace(/^<svg/, '<svg xmlns="http://www.w3.org/2000/svg"');
            }

            if(!source.match(/^<svg[^>]+"http\:\/\/www\.w3\.org\/1999\/xlink"/)){
                source = source.replace(/^<svg/, '<svg xmlns:xlink="http://www.w3.org/1999/xlink"');
            }

            //add xml declaration
            source = '<?xml version="1.0" standalone="no"?>\r\n' + source;

            //convert svg source to URI data scheme.
            var dataUrl = "data:image/svg+xml;charset=utf-8,"+encodeURIComponent(source);
            var link = document.createElement('a')
            link.download = 'view-snapshot-' + Date.now() + '.svg';
            link.href = dataUrl
            link.click()

        }
    };
});

// Copyright 2018-2023 Observable, Inc.
// Released under the ISC license.
// https://observablehq.com/@d3/pie-chart

function PieChart(data, {
    names, // given d in data, returns the (ordinal) label
    values, // given d in data, returns the (quantitative) value
    title, // given d in data, returns the title text
    width = 640, // outer width, in pixels
    height = 400, // outer height, in pixels
    innerRadius = 0, // inner radius of pie, in pixels (non-zero for donut)
    outerRadius = Math.min(width, height) / 2, // outer radius of pie, in pixels
    labelRadius = (innerRadius * 0.2 + outerRadius * 0.8), // center radius of labels
    format = ",", // a format specifier for values (in the label)
    // names, // array of names (the domain of the color scale)
    colors, // array of colors for names
    stroke = innerRadius > 0 ? "none" : "white", // stroke separating widths
    strokeWidth = 1, // width of stroke separating wedges
    strokeLinejoin = "round", // line join of stroke separating wedges
    padAngle = stroke === "none" ? 1 / outerRadius : 0, // angular separation between wedges, in radians
    opacity = 1, // opacity of svg
    fontSize = 12 // font size of labels
} = {}) {
    // Compute values.
    const N = d3.map(data, (data) => data[names]);
    const V = d3.map(data, (data) => data[values]);

    const I = d3.range(N.length).filter(i => !isNaN(V[i]));

    // Unique the names.
    if (names === undefined) names = N;
    names = new d3.InternSet(names);

    // Chose a default color scheme based on cardinality.
    if (colors === undefined) colors = d3.schemeSpectral[names.size];
    if (colors === undefined) colors = d3.quantize(t => d3.interpolateSpectral(t * 0.8 + 0.1), names.size);

    // Construct scales.
    const color = d3.scaleOrdinal(names, colors);

    // Compute titles.
    if (title === undefined) {
        const formatValue = d3.format(format);
        title = i => `${N[i]}\n${formatValue(V[i])}`;
    } else {
        const O = d3.map(data, d => d);
        const T = title;
        title = i => T(O[i], i, data);
    }

    // Construct arcs.
    const arcs = d3.pie().padAngle(padAngle).sort(null).value(i => V[i])(I);
    const arc = d3.arc().innerRadius(innerRadius).outerRadius(outerRadius);
    const arcLabel = d3.arc().innerRadius(labelRadius).outerRadius(labelRadius);

    const svg = d3.create("svg")
        .attr("width", width)
        .attr("height", height)
        .attr("viewBox", [-width / 2, -height / 2, width, height])
        .attr("style", "max-width: 100%; height: auto; height: intrinsic;");

    svg.append("g")
        .attr("stroke", stroke)
        .attr("stroke-width", strokeWidth)
        .attr("stroke-linejoin", strokeLinejoin)
        .selectAll("path")
        .data(arcs)
        .join("path")
        .attr("fill", d => color(N[d.data]))
        .attr("d", arc)
        .append("title")
        .text(d => title(d.data));

    svg.append("g")
        .attr("font-family", "sans-serif")
        .attr("font-size", fontSize)
        .attr("text-anchor", "middle")
        .selectAll("text")
        .data(arcs)
        .join("text")
        .attr("transform", d => `translate(${arcLabel.centroid(d)})`)
        .selectAll("tspan")
        .data(d => {
            const lines = `${title(d.data)}`.split(/\n/);
            return (d.endAngle - d.startAngle) > 0.25 ? lines : lines.slice(0, 1);
        })
        .join("tspan")
        .attr("x", 0)
        .attr("y", (_, i) => `${i * 1.1}em`)
        .attr("font-weight", (_, i) => i ? null : "bold")
        .text(d => d);

    const resultSvg = Object.assign(svg.node(), {
        scales: {
            color
        }
    });

    resultSvg.setAttribute("opacity", opacity);

    return resultSvg;
}
