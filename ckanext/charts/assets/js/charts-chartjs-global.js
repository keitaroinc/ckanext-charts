/**
 * Keep a private reference to the Chart.js build shipped with this bundle.
 *
 * Other extensions may load their own, older Chart.js afterwards and take over
 * the `window.Chart` global (e.g. ckanext-visualize loads Chart.js 2.9.2 from
 * its `base.html` on every page). Capturing the constructor here, right after
 * our vendor files ran, keeps the renderer working no matter who wins the
 * global.
 */
window.charts_chartjs_lib = window.charts_chartjs_lib || window.Chart;
