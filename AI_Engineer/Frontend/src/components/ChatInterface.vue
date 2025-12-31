<script setup>
import { ref, nextTick, onMounted, computed } from 'vue'
import axios from 'axios'
import { marked } from 'marked'
import PlotlyChart from './PlotlyChart.vue'

// Use Environment Variables for Cloud Run, fallback to localhost for Dev
const API_URL = import.meta.env.VITE_API_URL + '/api/chat' || 'http://localhost:8005/api/chat'
const AI_CHAT_URL = import.meta.env.VITE_API_URL + '/chat' || 'http://localhost:8005/chat'
const DA_API_URL = import.meta.env.VITE_DA_API_URL + '/analyze' || 'http://localhost:8006/analyze';

const stockOptions = [
  { name: 'Nvidia', ticker: 'NVDA' },
  { name: 'Microsoft', ticker: 'MSFT' },
  { name: 'Google', ticker: 'GOOGL' },
  { name: 'Meta', ticker: 'META' },
  { name: 'Amazon', ticker: 'AMZN' },
  { name: 'AMD', ticker: 'AMD' },
  { name: 'TSMC', ticker: 'TSM' },
  { name: 'Broadcom', ticker: 'AVGO' },
  { name: 'Palantir', ticker: 'PLTR' },
  { name: 'Tesla', ticker: 'TSLA' }
]

const periodOptions = [
  { label: '3 Months', value: '3mo' },
  { label: '6 Months', value: '6mo' },
  { label: '1 Year', value: '1y' },
  { label: '2 Years', value: '2y' },
  { label: '5 Years', value: '5y' }
]

const messages = ref([])
const userInput = ref('')
const isLoading = ref(false)
const inputRef = ref(null)
const messagesContainer = ref(null)
const sessionId = ref(`session_${Date.now()}`)
const activeTab = ref('analysis')

// Saved charts for Portfolio gallery
const savedCharts = ref([])

// Current displayed chart (latest analysis)
const currentChart = ref(null)

// Chart data from DataAgent API (for Plotly)
const chartData = ref(null)
const analysisStats = ref(null)
const newsContext = ref(null)

const selectedStock = ref(stockOptions[0]) 
const selectedPeriodIndex = ref(2) // Default 1y
const predictionDays = ref(5)

const selectedPeriod = computed(() => periodOptions[selectedPeriodIndex.value].value)
const selectedPeriodLabel = computed(() => periodOptions[selectedPeriodIndex.value].label)

onMounted(() => {
  messages.value.push({
    role: 'assistant',
    content: `**Welcome to StockMind AI!**\n\nI'm ready to analyze **${selectedStock.value.name}** for you.\n\nAdjust the settings above, then ask me anything about trends, forecasts, or market news.`
  })
})

const scrollToBottom = async () => {
  await nextTick()
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

const renderMarkdown = (text) => marked.parse(text || '')


  
// Start analysis - calls DataAgent API (Pure Technical)
const startAnalysis = async () => {
  if (isLoading.value) return
  
  isLoading.value = true
  chartData.value = null
  newsContext.value = null
  
  // Clear chat memory for new analysis
  try {
    await axios.delete(`http://localhost:8005/memory/${selectedStock.value.ticker}`)
    messages.value = [] 
  } catch (e) {
    console.warn('Failed to clear memory:', e)
  }
  
  messages.value.push({ role: 'assistant', content: '🕵️ **Starting Analysis...**' })
  
  try {
    // PHASE 1: Load Technical Data (Charts appear immediately)
    // This will NOT block waiting for Agent Search
    messages.value.push({ role: 'assistant', content: '📊 Fetching Technical Data...' })
    
    // Call DA_API
    const response = await axios.post(DA_API_URL, {
      ticker: selectedStock.value.ticker,
      period: selectedPeriod.value,
      prediction_days: parseInt(predictionDays.value)
    })

    const data = response.data
    
    // Store chart data
    chartData.value = data.chart_data
    analysisStats.value = data.statistics
    
    const chartImages = data.chart_images || []
    
    // Add success message
    messages.value.push({
      role: 'assistant',
      content: data.response || `**Analysis Complete for ${selectedStock.value.name}**`,
      sources: data.sources || [],
      chart_analysis: data.chart_analysis,
      charts: chartImages
    })
    
    // Save to portfolio
    if (chartImages.length > 0) {
      const chartDataObj = {
        id: Date.now(),
        ticker: selectedStock.value.ticker,
        name: selectedStock.value.name,
        chart: chartImages[0],
        analysis: data.chart_analysis || '',
        date: new Date().toLocaleString('id-ID')
      }
      savedCharts.value.push(chartDataObj)
      currentChart.value = chartDataObj
    }
    
    // PHASE 2: Load News in Background (Non-blocking)
    // This runs completely independently of the chart UI
    messages.value.push({ role: 'assistant', content: '🌍 Agent Search: Scanning breaking news...' })
    
    // We intentionally do NOT await this, but we handle the promise
    axios.get(`http://localhost:8005/news/${selectedStock.value.ticker}`)
      .then(newsResponse => {
        if (newsResponse.data && newsResponse.data.news) {
          newsContext.value = newsResponse.data.news
          // Inform user that news arrived
          messages.value.push({ role: 'assistant', content: `📰 **Agent Search**: Found updates. Added to context.` })
          scrollToBottom()
        }
      })
      .catch(err => {
        console.warn('News fetch failed (non-blocking):', err)
        // Silent fail or small warning, doesn't break app
      })

  } catch (error) {
    console.error('Analysis error:', error)
    messages.value.push({
      role: 'assistant',
      content: '⚠️ **Error**: Failed to analyze data. Please check backend connections.'
    })
  } finally {
    isLoading.value = false
    scrollToBottom()
  }
}

// ===== CHAT FUNCTIONALITY =====
const isSendingMessage = ref(false)

const captureForecostChart = async () => {
  try {
    const futureChart = document.querySelector('.forecasting-section .chart-card-plotly:nth-child(2) .js-plotly-plot')
    if (futureChart) {
      return await Plotly.toImage(futureChart, { format: 'png', width: 800, height: 600 })
    }
    return null
  } catch (error) {
    console.error('Error capturing chart:', error)
    return null
  }
}

const buildTechnicalContext = () => {
  if (!chartData.value) return null
  return {
    rsi: chartData.value.rsi,
    macd: chartData.value.macd,
    drawdown: chartData.value.drawdown,
    cumulative_returns: chartData.value.cumulative_returns,
    moving_averages: chartData.value.moving_averages,
    forecast: chartData.value.forecast
  }
}

const sendMessage = async () => {
  if (!userInput.value.trim() || isSendingMessage.value) return
  
  const message = userInput.value.trim()
  userInput.value = ''
  
  messages.value.push({ role: 'user', content: message })
  isSendingMessage.value = true
  
  try {
    const payload = {
      ticker: selectedStock.value.ticker,
      message: message,
      technical_data: buildTechnicalContext(),
      news_context: newsContext.value
    }
    
    // Capture screenshot if discussing forecast
    const forecastKeywords = ['prediksi', 'forecast', 'ramalan', 'masa depan']
    if (forecastKeywords.some(kw => message.toLowerCase().includes(kw))) {
      const screenshot = await captureForecostChart()
      if (screenshot) payload.forecast_screenshot = screenshot
    }
    
    // Start Thinking Animation
    isSendingMessage.value = true
    startThinkingTimer()
    
    const response = await axios.post(AI_CHAT_URL, payload)
    
    messages.value.push({
      role: 'assistant',
      content: response.data.response,
      mode: response.data.mode,
      processingTime: response.data.processing_time
    })
    
  } catch (error) {
    console.error('Chat error:', error)
    messages.value.push({
      role: 'assistant',
      content: `⚠️ **Connection Error**: ${error.response?.data?.detail || 'Cannot reach AI Chat Backend on Port 8005.'}`
    })
  } finally {
    isSendingMessage.value = false
    stopThinkingTimer()
    scrollToBottom()
  }
}

// ===== THINKING STATUS LOGIC =====
const thinkingStatus = ref('')
let thinkingInterval = null
const thinkingSteps = [
  '🔍 Reading technical data...',
  '📊 Analyzing chart patterns...',
  '🧮 Checking forecast confidence...', 
  '🌍 Scanning market context...',
  '💡 Synthesizing investment insights...',
  '✍️ Drafting response...'
]

const startThinkingTimer = () => {
  let stepIndex = 0
  thinkingStatus.value = thinkingSteps[0]
  
  thinkingInterval = setInterval(() => {
    stepIndex = (stepIndex + 1) % thinkingSteps.length
    thinkingStatus.value = thinkingSteps[stepIndex]
  }, 2500) // Change status every 2.5s
}

const stopThinkingTimer = () => {
  clearInterval(thinkingInterval)
  thinkingStatus.value = ''
}

</script>

<template>
  <div class="app-container">
    

      

    <!-- MAIN -->
    <main class="main-content">
      
      <!-- HEADER -->
      <header class="top-header">
        <div class="breadcrumb">
          Dashboard <span class="sep">›</span> <strong>Ticker Analysis</strong>
        </div>
        <div class="header-right">
          <div class="user-avatar">JD</div>
        </div>
      </header>

      <!-- SPLIT LAYOUT: Charts Left + Chat Right -->
      <div class="split-layout">
        
        <!-- LEFT: Scrollable Charts Area -->
        <div class="charts-area">
          <div class="content-scroll">
        
        <!-- STOCK ANALYSIS TAB -->
        <template v-if="activeTab === 'analysis'">
        
        <!-- CONFIG CARD -->
        <section class="config-card">
          <div class="card-header">
            <h2>⚙️ Analysis Configuration</h2>
          </div>
          
          <div class="config-grid">
            <!-- Stock Selector -->
            <div class="config-item">
              <label>Target Asset</label>
              <select v-model="selectedStock" class="select-input">
                <option v-for="opt in stockOptions" :key="opt.ticker" :value="opt">
                  {{ opt.name }} ({{ opt.ticker }})
                </option>
              </select>
            </div>
            
            <!-- Period Slider -->
            <div class="config-item">
              <label>Historical Period: <strong>{{ selectedPeriodLabel }}</strong></label>
              <input 
                type="range" 
                min="0" 
                :max="periodOptions.length - 1" 
                v-model.number="selectedPeriodIndex"
                class="slider-input"
              />
            </div>
            
            <!-- Horizon Slider -->
            <div class="config-item">
              <label>Forecast Horizon: <strong>{{ predictionDays }} Days</strong></label>
              <input 
                type="range" 
                min="1" 
                max="30" 
                v-model.number="predictionDays"
                class="slider-input"
              />
            </div>
            
            <!-- START ANALYSIS BUTTON -->
            <div class="config-item button-item">
              <label>&nbsp;</label>
              <button @click="startAnalysis" :disabled="isLoading" class="start-analysis-btn">
                <span v-if="!isLoading">🚀 Start Analysis</span>
                <span v-else>⏳ Analyzing...</span>
              </button>
            </div>
          </div>
        </section>

        <!-- FORECASTING SECTION -->
        <section v-if="chartData && chartData.forecast" class="forecasting-section">
          <div class="card-header">
            <h2>🔮 AI Forecasting Models</h2>
          </div>
          <div class="chart-grid">
            <div class="chart-card-plotly">
              <h4>
                Validation (Backtest)
                <span v-if="chartData.forecast.validation && chartData.forecast.validation.mae" class="mae-badge">
                  MAE: ${{ chartData.forecast.validation.mae }}
                </span>
              </h4>
              <PlotlyChart 
                v-if="chartData.forecast.validation" 
                chart-type="validation" 
                :data="chartData.forecast.validation" 
              />
            </div>
            <div class="chart-card-plotly">
              <h4>
                Future Forecast (30 Days)
                <span v-if="chartData.forecast.validation && chartData.forecast.validation.mae" class="mae-badge">
                  Backtest MAE: ${{ chartData.forecast.validation.mae }}
                </span>
              </h4>
              <PlotlyChart 
                v-if="chartData.forecast.future" 
                chart-type="future" 
                :data="chartData.forecast.future" 
              />
            </div>
          </div>
        </section>

        <!-- CHART DISPLAY SECTION -->
        <section class="chart-display-section">
          <div class="card-header">
            <h2>📊 Technical Analysis Charts</h2>
            <span v-if="chartData" class="chart-badge">{{ selectedStock.ticker }}</span>
          </div>
          
          <!-- Empty State -->
          <div v-if="!chartData" class="chart-empty-state">
            <div class="empty-chart-icon">📈</div>
            <h3>No Charts Generated Yet</h3>
            <p>Click "🚀 Start Analysis" to generate interactive charts.</p>
          </div>
          
          <!-- Plotly Chart Grid -->
          <div v-else class="chart-grid">
            
            
            <!-- 1. Candlestick Chart -->
            <div class="chart-card-plotly">
              <h4>📈 Candlestick Chart</h4>
              <PlotlyChart 
                chart-type="candlestick" 
                :data="chartData.candlestick" 
                :title="`${selectedStock.ticker} OHLC`"
              />
            </div>
            
            <!-- 2. Volume Chart -->
            <div class="chart-card-plotly">
              <h4>📊 Trading Volume</h4>
              <PlotlyChart 
                chart-type="volume" 
                :data="chartData.candlestick" 
              />
            </div>
            
            <!-- 2. RSI -->
            <div class="chart-card-plotly">
              <h4>📉 RSI (14-day)</h4>
              <PlotlyChart 
                chart-type="rsi" 
                :data="chartData.rsi" 
                title="Relative Strength Index"
              />
              <div class="indicator-badge" :class="chartData.rsi.signal">
                {{ chartData.rsi.signal.toUpperCase() }} ({{ chartData.rsi.current.toFixed(1) }})
              </div>
            </div>
            
            <!-- 3. MACD -->
            <div class="chart-card-plotly">
              <h4>📐 MACD</h4>
              <PlotlyChart 
                chart-type="macd" 
                :data="chartData.macd" 
                title="MACD Indicator"
              />
              <div class="indicator-badge" :class="chartData.macd.signal">
                {{ chartData.macd.signal.replace('_', ' ').toUpperCase() }}
              </div>
            </div>
            
            <!-- 4. Bollinger Bands -->
            <div class="chart-card-plotly">
              <h4>🎯 Bollinger Bands</h4>
              <PlotlyChart 
                chart-type="bollinger" 
                :data="chartData.bollinger" 
                title="Bollinger Bands (20, 2)"
              />
            </div>
            
            <!-- 5. Moving Averages -->
            <div class="chart-card-plotly">
              <h4>📊 Moving Averages</h4>
              <PlotlyChart 
                chart-type="ma" 
                :data="chartData.moving_averages" 
                title="MA20 / MA50"
              />
            </div>
            
            <!-- 6. Drawdown Chart -->
            <div class="chart-card-plotly">
              <h4>📉 Maximum Drawdown</h4>
              <PlotlyChart 
                chart-type="drawdown" 
                :data="chartData.drawdown" 
              />
              <div v-if="chartData.drawdown.max_drawdown" class="stat-badge">
                Max DD: {{ chartData.drawdown.max_drawdown }}%
              </div>
            </div>
            
            <!-- 7. Cumulative Returns -->
            <div class="chart-card-plotly">
              <h4>📈 Cumulative Returns</h4>
              <PlotlyChart 
                chart-type="cumulative_returns" 
                :data="chartData.cumulative_returns" 
              />
              <div v-if="chartData.cumulative_returns.total_return" class="stat-badge">
                Total Return: {{ chartData.cumulative_returns.total_return }}%
              </div>
            </div>
            
            <!-- 8. Returns Distribution -->
            <div class="chart-card-plotly">
              <h4>📊 Returns Distribution</h4>
              <PlotlyChart 
                chart-type="returns" 
                :data="chartData.returns" 
                title="Daily Returns Histogram"
              />
            </div>
            
          </div>
          
          <!-- Statistics Summary -->
          <div v-if="analysisStats" class="stats-summary">
            <div class="stat-item">
              <span class="stat-label">Current Price</span>
              <span class="stat-value">${{ analysisStats.current_price.toFixed(2) }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">Change</span>
              <span class="stat-value" :class="analysisStats.change_pct >= 0 ? 'positive' : 'negative'">
                {{ analysisStats.change_pct >= 0 ? '+' : '' }}{{ analysisStats.change_pct.toFixed(1) }}%
              </span>
            </div>
            <div class="stat-item">
              <span class="stat-label">Volatility</span>
              <span class="stat-value">{{ analysisStats.volatility_annual.toFixed(1) }}%</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">Sharpe Ratio</span>
              <span class="stat-value">{{ analysisStats.sharpe_ratio.toFixed(2) }}</span>
            </div>
          </div>
        </section>


        
        </template>

        <!-- PORTFOLIO TAB -->
        <template v-if="activeTab === 'portfolio'">
          <section class="portfolio-section">
            <div class="portfolio-header">
              <h2>📊 Saved Charts</h2>
              <span class="chart-count">{{ savedCharts.length }} chart(s)</span>
            </div>
            
            <!-- Empty State -->
            <div v-if="savedCharts.length === 0" class="empty-portfolio">
              <div class="empty-icon">📈</div>
              <h3>No Charts Yet</h3>
              <p>Analyze a stock in "Stock Analysis" tab to generate charts.</p>
            </div>
            
            <!-- Chart Gallery -->
            <div v-else class="chart-gallery">
              <div v-for="item in savedCharts" :key="item.id" class="chart-card">
                <div class="chart-card-header">
                  <span class="chart-ticker">{{ item.ticker }}</span>
                  <span class="chart-date">{{ item.date }}</span>
                </div>
                <img :src="`data:image/png;base64,${item.chart}`" class="gallery-chart-image" />
                <div class="chart-card-footer">
                  <span class="chart-name">{{ item.name }}</span>
                  <p v-if="item.analysis" class="chart-analysis-text">{{ item.analysis.slice(0, 100) }}...</p>
                </div>
              </div>
            </div>
          </section>
        </template>

        <!-- HISTORY TAB -->
        <template v-if="activeTab === 'history'">
          <section class="placeholder-card">
            <div class="placeholder-icon">📜</div>
            <h2>Research History</h2>
            <p>View your past analyses and saved insights.</p>
            <span class="coming-soon-badge">Coming Soon</span>
          </section>
        </template>
        
        </div><!-- close content-scroll -->
        </div><!-- close charts-area -->
        
        <!-- RIGHT: Chat Sidebar (Fixed) -->
        <aside class="chat-sidebar">
          <div class="chat-sidebar-header">
            <h3>🤖 AI Advisor</h3>
            <span class="live-badge">● LIVE</span>
          </div>
          <div ref="messagesContainer" class="chat-sidebar-messages">
            <div v-for="(msg, index) in messages" :key="index" class="sidebar-message">
              <div v-if="msg.role === 'assistant'" class="ai-bubble" v-html="renderMarkdown(msg.content)"></div>
              <div v-else class="user-bubble">{{ msg.content }}</div>
            </div>
            <div v-if="isLoading" class="ai-bubble loading">
              <span class="loader"></span> Analyzing...
            </div>
            <div v-if="isSendingMessage && thinkingStatus" class="ai-bubble thinking">
              <span class="thinking-icon">🧠</span> {{ thinkingStatus }}
            </div>
          </div>
          <div class="chat-sidebar-input">
            <input 
              v-model="userInput" 
              @keyup.enter="sendMessage"
              placeholder="Tanya soal analisis..." 
              class="sidebar-input"
              type="text"
              :disabled="isLoading"
            />
            <button @click="sendMessage" class="send-btn" :disabled="isLoading || !userInput.trim()">
              {{ isLoading ? '⏳' : '📤' }}
            </button>
          </div>
        </aside>
        
      </div><!-- close split-layout -->



    </main>
  </div>
</template>

<style scoped>
* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

.app-container {
  display: flex;
  height: 100vh;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  background: #f0f2f5;
  color: #1a1a2e;
}



.logo-icon { font-size: 24px; }
.logo-text { font-size: 18px; font-weight: bold; }
.logo-text .accent { color: #6c63ff; }

.nav-menu {
  flex: 1;
  padding: 20px 10px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  color: rgba(255,255,255,0.7);
  text-decoration: none;
  border-radius: 8px;
  margin-bottom: 4px;
  transition: all 0.2s;
}

.nav-item:hover { background: rgba(255,255,255,0.1); color: white; }
.nav-item.active { background: #6c63ff; color: white; }
.nav-icon { font-size: 18px; }

.sidebar-footer {
  padding: 20px;
  border-top: 1px solid rgba(255,255,255,0.1);
}

.status-badge {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: rgba(255,255,255,0.7);
}

.status-badge.online .status-dot {
  width: 8px;
  height: 8px;
  background: #00c853;
  border-radius: 50%;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

/* MAIN CONTENT */
.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* SPLIT LAYOUT: Charts left, Chat right */
.split-layout {
  flex: 1;
  display: flex;
  overflow: hidden;
}

.charts-area {
  flex: 1;
  overflow-y: auto;
  min-width: 0;
}

/* CHAT SIDEBAR (Right Panel) */
.chat-sidebar {
  width: 500px; /* Widened to match user preference */
  background: #1a1a2e;
  color: white;
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
  border-left: 1px solid rgba(255,255,255,0.1);
  height: 100%; /* Ensure full height */
}

.chat-sidebar-header {
  padding: 16px 20px;
  background: linear-gradient(135deg, #1a1a2e 0%, #2d2d44 100%);
  border-bottom: 1px solid rgba(255,255,255,0.1);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chat-sidebar-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
}

.chat-sidebar-messages {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.sidebar-message {
  display: flex;
  flex-direction: column;
}

.ai-bubble {
  background: rgba(108,99,255,0.2);
  padding: 12px 16px;
  border-radius: 12px;
  border-top-left-radius: 4px;
  font-size: 13px;
  line-height: 1.5;
}

.ai-bubble.loading {
  display: flex;
  align-items: center;
  gap: 8px;
  opacity: 0.7;
}

.user-bubble {
  background: #6c63ff;
  padding: 10px 14px;
  border-radius: 12px;
  border-bottom-right-radius: 4px;
  font-size: 13px;
  align-self: flex-end;
  max-width: 80%;
}

.chat-sidebar-input {
  padding: 16px;
  border-top: 1px solid rgba(255,255,255,0.1);
  display: flex;
  gap: 8px;
}

.sidebar-input {
  flex: 1;
  padding: 12px 16px;
  background: rgba(255,255,255,0.1);
  border: 1px solid rgba(255,255,255,0.2);
  border-radius: 8px;
  color: white;
  font-size: 13px;
}

.sidebar-input::placeholder {
  color: rgba(255,255,255,0.5);
}

.sidebar-input:focus {
  outline: none;
  border-color: #6c63ff;
}

.sidebar-input:disabled {
  cursor: not-allowed;
  opacity: 0.7;
}

.send-btn {
  padding: 12px 16px;
  background: #6c63ff;
  border: none;
  border-radius: 8px;
  color: white;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.2s;
}

.send-btn:hover:not(:disabled) {
  background: #5a4fcf;
}

.send-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.top-header {
  height: 60px;
  background: white;
  border-bottom: 1px solid #e0e0e0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 30px;
}

.breadcrumb { color: #666; font-size: 14px; }
.breadcrumb .sep { margin: 0 8px; color: #ccc; }
.breadcrumb strong { color: #1a1a2e; }

.user-avatar {
  width: 36px;
  height: 36px;
  background: #6c63ff;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 14px;
}

.content-scroll {
  flex: 1;
  overflow-y: auto;
  padding: 30px;
}

/* CONFIG CARD */
.config-card, .chat-card {
  background: white;
  border-radius: 16px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.05);
  margin-bottom: 20px;
}

.card-header {
  padding: 20px 24px;
  border-bottom: 1px solid #f0f0f0;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.card-header h2 {
  font-size: 16px;
  font-weight: 600;
  color: #1a1a2e;
}

.live-badge {
  font-size: 11px;
  color: #00c853;
  font-weight: bold;
}

.config-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 24px;
  padding: 24px;
  align-items: end;
}

.button-item {
  display: flex;
  flex-direction: column;
}

.start-analysis-btn {
  width: 100%;
  padding: 14px 20px;
  background: linear-gradient(135deg, #6c63ff, #8b5cf6);
  color: white;
  border: none;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 4px 15px rgba(108, 99, 255, 0.3);
}

.start-analysis-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(108, 99, 255, 0.4);
}

.start-analysis-btn:active {
  transform: translateY(0);
}

.start-analysis-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
  box-shadow: none;
  transform: none;
}

/* CHART DISPLAY SECTION */
.forecasting-section,
.chart-display-section {
  background: white;
  border-radius: 16px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.05);
  margin-bottom: 20px;
  overflow: hidden;
}

.chart-grid {
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding: 20px;
}

.chart-card-plotly {
  background: #fafafa;
  border: 1px solid #e0e0e0;
  border-radius: 12px;
  padding: 16px;
  position: relative;
  width: 100%;
}

.chart-card-plotly h4 {
  margin: 0 0 12px 0;
  font-size: 14px;
  color: #1a1a2e;
}

.indicator-badge {
  position: absolute;
  top: 16px;
  right: 16px;
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 10px;
  font-weight: bold;
  text-transform: uppercase;
}

.indicator-badge.neutral { background: #f0f0f0; color: #666; }
.indicator-badge.overbought { background: #ffebee; color: #ef5350; }
.indicator-badge.oversold { background: #e8f5e9; color: #26a69a; }
.indicator-badge.bullish_crossover { background: #e8f5e9; color: #26a69a; }
.indicator-badge.bearish_crossover { background: #ffebee; color: #ef5350; }

.stats-summary {
  display: flex;
  gap: 20px;
  padding: 20px;
  background: linear-gradient(135deg, #f0ebff 0%, #e8f4ff 100%);
  border-top: 1px solid #e0e0e0;
}

.stat-item {
  flex: 1;
  text-align: center;
}

.stat-label {
  display: block;
  font-size: 11px;
  color: #666;
  text-transform: uppercase;
  margin-bottom: 4px;
}

.stat-value {
  font-size: 18px;
  font-weight: bold;
  color: #1a1a2e;
}

.stat-value.positive { color: #26a69a; }
.stat-value.negative { color: #ef5350; }

.chart-badge {
  background: linear-gradient(135deg, #6c63ff, #8b5cf6);
  color: white;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: bold;
}

.chart-empty-state {
  padding: 60px 40px;
  text-align: center;
  background: linear-gradient(180deg, #fafafa 0%, #f5f5f5 100%);
}

.empty-chart-icon {
  font-size: 56px;
  margin-bottom: 16px;
  opacity: 0.5;
}

.chart-empty-state h3 {
  font-size: 18px;
  color: #1a1a2e;
  margin-bottom: 8px;
}

.chart-empty-state p {
  font-size: 14px;
  color: #888;
  max-width: 400px;
  margin: 0 auto;
}

.chart-display-content {
  padding: 0;
}

.chart-main-image {
  background: #1a1a2e;
  padding: 16px;
}

.chart-main-image img {
  width: 100%;
  border-radius: 8px;
  display: block;
}

.chart-analysis-box {
  padding: 16px 24px;
  background: linear-gradient(135deg, #f0ebff 0%, #e8f4ff 100%);
  border-left: 4px solid #6c63ff;
}

.analysis-label {
  font-size: 12px;
  font-weight: bold;
  color: #6c63ff;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.chart-analysis-box p {
  margin: 8px 0 0 0;
  font-size: 14px;
  color: #333;
  line-height: 1.6;
}

.chart-meta {
  display: flex;
  justify-content: space-between;
  padding: 12px 24px;
  background: #fafafa;
  border-top: 1px solid #f0f0f0;
  font-size: 12px;
  color: #666;
}

.config-item label {
  display: block;
  font-size: 12px;
  color: #666;
  margin-bottom: 10px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.config-item label strong {
  color: #6c63ff;
  font-weight: 600;
}

.select-input {
  width: 100%;
  padding: 12px 16px;
  border: 2px solid #e0e0e0;
  border-radius: 10px;
  font-size: 14px;
  color: #1a1a2e;
  background: #fafafa;
  cursor: pointer;
  transition: border-color 0.2s;
}

.select-input:hover { border-color: #6c63ff; }
.select-input:focus { outline: none; border-color: #6c63ff; }

.slider-input {
  width: 100%;
  height: 8px;
  -webkit-appearance: none;
  appearance: none;
  background: #e0e0e0;
  border-radius: 4px;
  cursor: pointer;
}

.slider-input::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 20px;
  height: 20px;
  background: #6c63ff;
  border-radius: 50%;
  cursor: pointer;
  box-shadow: 0 2px 6px rgba(108,99,255,0.4);
}

.slider-input::-moz-range-thumb {
  width: 20px;
  height: 20px;
  background: #6c63ff;
  border-radius: 50%;
  cursor: pointer;
  border: none;
}

/* CHAT CARD */
.messages-container {
  max-height: 400px;
  overflow-y: auto;
  padding: 20px 24px;
}

.message-wrapper {
  margin-bottom: 20px;
}

.message {
  display: flex;
  gap: 12px;
  align-items: flex-start;
}

.user-message { flex-direction: row-reverse; }

.avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: bold;
  flex-shrink: 0;
}

.ai-avatar { background: linear-gradient(135deg, #6c63ff, #8b5cf6); color: white; }
.user-avatar-small { background: #1a1a2e; color: white; }

.message-content {
  max-width: 70%;
  padding: 14px 18px;
  border-radius: 16px;
  font-size: 14px;
  line-height: 1.6;
}

.message-content.user {
  background: #6c63ff;
  color: white;
  border-bottom-right-radius: 4px;
}

.message-content.ai {
  background: #f5f5f5;
  color: #1a1a2e;
  border-bottom-left-radius: 4px;
}

.message-content.loading {
  display: flex;
  align-items: center;
  gap: 10px;
  color: #666;
}

.loader {
  width: 16px;
  height: 16px;
  border: 2px solid #e0e0e0;
  border-top-color: #6c63ff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.chart-container {
  margin-top: 16px;
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid #e0e0e0;
}

.chart-image {
  width: 100%;
  display: block;
}

.chart-caption {
  padding: 12px;
  background: #f9f7ff;
  font-size: 12px;
  color: #6c63ff;
  font-style: italic;
}

.sources-list {
  margin-top: 12px;
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.source-link {
  font-size: 11px;
  color: #6c63ff;
  text-decoration: none;
  padding: 4px 10px;
  background: rgba(108,99,255,0.1);
  border-radius: 20px;
}

.source-link:hover { background: rgba(108,99,255,0.2); }

/* INPUT BAR */
.input-bar {
  padding: 20px 30px;
  background: white;
  border-top: 1px solid #e0e0e0;
  display: flex;
  gap: 12px;
}

.input-bar.disabled-bar {
  background: #f5f5f5;
  opacity: 0.7;
}

.disabled-input {
  background: #eee !important;
  cursor: not-allowed;
  color: #999;
}

.disabled-btn {
  background: #ccc !important;
  cursor: not-allowed;
}

.chat-input {
  flex: 1;
  padding: 14px 20px;
  border: 2px solid #e0e0e0;
  border-radius: 12px;
  font-size: 14px;
  transition: border-color 0.2s;
}

.chat-input:focus { outline: none; border-color: #6c63ff; }

.send-button {
  padding: 14px 28px;
  background: #6c63ff;
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
}

.send-button:hover { background: #5a52d5; }
.send-button:disabled { background: #ccc; cursor: not-allowed; }

/* PLACEHOLDER CARDS */
.placeholder-card {
  background: white;
  border-radius: 16px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.05);
  padding: 60px 40px;
  text-align: center;
  max-width: 500px;
  margin: 60px auto;
}

.placeholder-icon {
  font-size: 64px;
  margin-bottom: 20px;
}

.placeholder-card h2 {
  font-size: 24px;
  color: #1a1a2e;
  margin-bottom: 12px;
}

.placeholder-card p {
  color: #666;
  font-size: 14px;
  margin-bottom: 24px;
}

.coming-soon-badge {
  display: inline-block;
  padding: 8px 20px;
  background: linear-gradient(135deg, #6c63ff, #8b5cf6);
  color: white;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 1px;
}

/* PORTFOLIO GALLERY */
.portfolio-section {
  background: white;
  border-radius: 16px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.05);
  padding: 24px;
}

.portfolio-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #f0f0f0;
}

.portfolio-header h2 {
  font-size: 18px;
  color: #1a1a2e;
  margin: 0;
}

.chart-count {
  font-size: 12px;
  color: #666;
  background: #f0f0f0;
  padding: 4px 12px;
  border-radius: 20px;
}

.empty-portfolio {
  text-align: center;
  padding: 60px 20px;
  color: #666;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.empty-portfolio h3 {
  font-size: 18px;
  color: #1a1a2e;
  margin-bottom: 8px;
}

.empty-portfolio p {
  font-size: 14px;
  color: #888;
}

.chart-gallery {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.chart-card {
  background: #fafafa;
  border: 1px solid #e0e0e0;
  border-radius: 12px;
  overflow: hidden;
  transition: transform 0.2s, box-shadow 0.2s;
}

.chart-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0,0,0,0.1);
}

.chart-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #1a1a2e;
  color: white;
}

.chart-ticker {
  font-weight: bold;
  font-size: 14px;
  color: #6c63ff;
}

.chart-date {
  font-size: 11px;
  color: rgba(255,255,255,0.6);
}

.gallery-chart-image {
  width: 100%;
  display: block;
}

.chart-card-footer {
  padding: 12px 16px;
}

.chart-name {
  font-weight: 600;
  font-size: 14px;
  color: #1a1a2e;
}

.chart-analysis-text {
  font-size: 12px;
  color: #666;
  margin-top: 8px;
  line-height: 1.5;
  font-style: italic;
}

/* MAE Badge */
.mae-badge {
  display: inline-block;
  margin-left: 10px;
  padding: 4px 12px;
  background: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%);
  color: white;
  font-size: 12px;
  font-weight: 600;
  border-radius: 20px;
  box-shadow: 0 2px 6px rgba(238, 90, 111, 0.3);
}
</style>
