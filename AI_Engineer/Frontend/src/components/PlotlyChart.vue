<template>
  <div ref="chartContainer" class="plotly-chart"></div>
</template>

<script setup>
import { ref, onMounted, watch, onUnmounted } from 'vue'
import Plotly from 'plotly.js-dist'

const props = defineProps({
  chartType: {
    type: String,
    required: true,
    validator: (v) => ['candlestick', 'volume', 'rsi', 'macd', 'bollinger', 'ma', 'returns', 'drawdown', 'cumulative_returns', 'validation', 'future'].includes(v)
  },
  data: {
    type: Object,
    required: true
  },
  title: {
    type: String,
    default: ''
  }
})

const chartContainer = ref(null)

const renderChart = () => {
  if (!chartContainer.value || !props.data) return

  let traces = []
  let layout = {
    title: { text: props.title, font: { size: 14 } },
    autosize: true,
    paper_bgcolor: 'rgba(0,0,0,0)',
    plot_bgcolor: 'rgba(0,0,0,0)',
    font: { family: 'Segoe UI, sans-serif', color: '#333' },
    margin: { t: 40, r: 20, b: 40, l: 50 },
    xaxis: { gridcolor: '#eee', automargin: true },
    yaxis: { gridcolor: '#eee', automargin: true },
    showlegend: true,
    legend: { orientation: 'h', y: -0.15 }
  }

  switch (props.chartType) {
    case 'candlestick':
      traces = [
        {
          x: props.data.dates,
          open: props.data.open,
          high: props.data.high,
          low: props.data.low,
          close: props.data.close,
          type: 'candlestick',
          name: 'OHLC',
          increasing: { line: { color: '#26a69a' } },
          decreasing: { line: { color: '#ef5350' } }
        }
      ]
      break
    
    case 'volume':
      traces = [
        {
          x: props.data.dates,
          y: props.data.volume,
          type: 'bar',
          name: 'Volume',
          marker: { 
            color: props.data.volume.map((v, i) => {
              // Color based on price movement
              if (i === 0) return 'rgba(108,99,255,0.6)'
              return props.data.close[i] >= props.data.close[i-1] 
                ? 'rgba(38,166,154,0.6)'  // Green for up
                : 'rgba(239,83,80,0.6)'   // Red for down
            })
          }
        }
      ]
      break

    case 'rsi':
      traces = [
        {
          x: props.data.dates,
          y: props.data.values,
          type: 'scatter',
          mode: 'lines',
          name: 'RSI',
          line: { color: '#6c63ff', width: 2 }
        }
      ]
      // Add overbought/oversold zones
      layout.shapes = [
        { type: 'line', y0: 70, y1: 70, x0: 0, x1: 1, xref: 'paper', line: { color: '#ef5350', dash: 'dash' } },
        { type: 'line', y0: 30, y1: 30, x0: 0, x1: 1, xref: 'paper', line: { color: '#26a69a', dash: 'dash' } }
      ]
      layout.yaxis = { range: [0, 100], gridcolor: '#eee' }
      break

    case 'macd':
      traces = [
        {
          x: props.data.dates,
          y: props.data.macd_line,
          type: 'scatter',
          mode: 'lines',
          name: 'MACD',
          line: { color: '#2196f3', width: 2 }
        },
        {
          x: props.data.dates,
          y: props.data.signal_line,
          type: 'scatter',
          mode: 'lines',
          name: 'Signal',
          line: { color: '#ff9800', width: 2 }
        },
        {
          x: props.data.dates,
          y: props.data.histogram,
          type: 'bar',
          name: 'Histogram',
          marker: { 
            color: props.data.histogram.map(v => v >= 0 ? 'rgba(38,166,154,0.7)' : 'rgba(239,83,80,0.7)') 
          }
        }
      ]
      break

    case 'bollinger':
      traces = [
        {
          x: props.data.dates,
          y: props.data.upper,
          type: 'scatter',
          mode: 'lines',
          name: 'Upper Band',
          line: { color: '#ef5350', width: 1 }
        },
        {
          x: props.data.dates,
          y: props.data.middle,
          type: 'scatter',
          mode: 'lines',
          name: 'MA20',
          line: { color: '#ff9800', width: 1 }
        },
        {
          x: props.data.dates,
          y: props.data.lower,
          type: 'scatter',
          mode: 'lines',
          name: 'Lower Band',
          line: { color: '#26a69a', width: 1 },
          fill: 'tonexty',
          fillcolor: 'rgba(108,99,255,0.1)'
        },
        {
          x: props.data.dates,
          y: props.data.close,
          type: 'scatter',
          mode: 'lines',
          name: 'Close',
          line: { color: '#6c63ff', width: 2 }
        }
      ]
      break

    case 'ma':
      traces = [
        { x: props.data.dates, y: props.data.close, type: 'scatter', mode: 'lines', name: 'Close', line: { color: '#ccc', width: 1 } },
        { x: props.data.dates, y: props.data.ma20, type: 'scatter', mode: 'lines', name: 'MA20', line: { color: '#ff9800', width: 1.5 } },
        { x: props.data.dates, y: props.data.ma50, type: 'scatter', mode: 'lines', name: 'MA50', line: { color: '#2196f3', width: 1.5 } }
      ]
      break

    case 'returns':
      traces = [
        {
          x: props.data.values,
          type: 'histogram',
          name: 'Daily Returns',
          marker: { color: '#9fa8da' },
          opacity: 0.75
        }
      ]
      break
    
    case 'drawdown':
      traces = [
        {
          x: props.data.dates,
          y: props.data.drawdown,
          type: 'scatter',
          mode: 'lines',
          name: 'Drawdown %',
          fill: 'tozeroy',
          fillcolor: 'rgba(239,83,80,0.3)',
          line: { color: '#ef5350', width: 2 }
        }
      ]
      layout.yaxis = { title: 'Drawdown (%)', gridcolor: '#eee' }
      layout.shapes = [
        { type: 'line', y0: 0, y1: 0, x0: 0, x1: 1, xref: 'paper', line: { color: '#666', dash: 'dash', width: 1 } }
      ]
      break
    
    case 'cumulative_returns':
      traces = [
        {
          x: props.data.dates,
          y: props.data.cumulative,
          type: 'scatter',
          mode: 'lines',
          name: 'Cumulative Return %',
          fill: 'tozeroy',
          fillcolor: 'rgba(76,175,80,0.2)',
          line: { color: '#4caf50', width: 2 }
        }
      ]
      layout.yaxis = { title: 'Return (%)', gridcolor: '#eee' }
      layout.shapes = [
        { type: 'line', y0: 0, y1: 0, x0: 0, x1: 1, xref: 'paper', line: { color: '#666', dash: 'dash', width: 1 } }
      ]
      break
    
    // FORECASTING CHARTS
    case 'validation':
      traces = [
        {
          x: props.data.full_dates || props.data.dates,
          y: props.data.full_actual || props.data.actual,
          type: 'scatter',
          mode: 'lines',
          name: 'Actual Price (Full History)',
          line: { color: '#2196f3', width: 2 }
        },
        {
          x: props.data.dates,
          y: props.data.predicted,
          type: 'scatter',
          mode: 'lines+markers',
          name: 'Predicted (Last 30 Days)',
          line: { color: '#f44336', width: 2, dash: 'dot' },
          marker: { size: 4 }
        }
      ]
      break

    case 'future':
      // Plot history first
      if (props.data.history && props.data.history_dates) {
        traces.push({
          x: props.data.history_dates,
          y: props.data.history,
          type: 'scatter',
          mode: 'lines',
          name: 'Historical Data',
          line: { color: '#2196f3', width: 2 }
        })
      }
      
      // Get last history point for connection
      const lastHistoryDate = props.data.history_dates ? props.data.history_dates[props.data.history_dates.length - 1] : null
      const lastHistoryValue = props.data.history ? props.data.history[props.data.history.length - 1] : null
      
      // Plot 3 prediction lines with confidence interval
      // Lower bound (Pessimistic - Red)
      if (props.data.predicted_lower && lastHistoryDate) {
        traces.push({
          x: [lastHistoryDate, ...props.data.dates],
          y: [lastHistoryValue, ...props.data.predicted_lower],
          type: 'scatter',
          mode: 'lines',
          name: 'Lower Bound (-MAE)',
          line: { color: '#ef5350', width: 1.5, dash: 'dot' }
        })
      }
      
      // Main prediction (Orange)
      if (lastHistoryDate) {
        traces.push({
          x: [lastHistoryDate, ...props.data.dates],
          y: [lastHistoryValue, ...props.data.predicted],
          type: 'scatter',
          mode: 'lines+markers',
          name: 'Main Prediction',
          line: { color: '#ff9800', width: 2.5 },
          marker: { size: 5 }
        })
      } else {
        traces.push({
          x: props.data.dates,
          y: props.data.predicted,
          type: 'scatter',
          mode: 'lines+markers',
          name: 'Main Prediction',
          line: { color: '#ff9800', width: 2.5 },
          marker: { size: 5 }
        })
      }
      
      // Upper bound (Optimistic - Green)
      if (props.data.predicted_upper && lastHistoryDate) {
        traces.push({
          x: [lastHistoryDate, ...props.data.dates],
          y: [lastHistoryValue, ...props.data.predicted_upper],
          type: 'scatter',
          mode: 'lines',
          name: 'Upper Bound (+MAE)',
          line: { color: '#4caf50', width: 1.5, dash: 'dot' }
        })
      }
      break
  }

  Plotly.newPlot(chartContainer.value, traces, layout, { responsive: true, displayModeBar: false })
}

onMounted(() => {
  renderChart()
})

watch(() => props.data, () => {
  renderChart()
}, { deep: true })

onUnmounted(() => {
  if (chartContainer.value) {
    Plotly.purge(chartContainer.value)
  }
})
</script>

<style scoped>
.plotly-chart {
  width: 100%;
  min-height: 300px;
}
</style>
