/**
 * Main Application Logic for AI Phishing URL Analyzer
 */

document.addEventListener('DOMContentLoaded', () => {
  // DOM Elements
  const urlForm = document.getElementById('urlForm');
  const urlInput = document.getElementById('urlInput');
  const analyzeBtn = document.getElementById('analyzeBtn');
  const clearBtn = document.getElementById('clearBtn');
  const errorContainer = document.getElementById('errorContainer');
  const errorMessage = document.getElementById('errorMessage');
  
  const loadingCard = document.getElementById('loadingCard');
  const resultsCard = document.getElementById('resultsCard');
  
  // Results Elements
  const predictionBadge = document.getElementById('predictionBadge');
  const predictionText = document.getElementById('predictionText');
  const predictionIcon = document.getElementById('predictionIcon');
  const riskTag = document.getElementById('riskTag');
  
  const riskBarValue = document.getElementById('riskBarValue');
  const riskProgressFill = document.getElementById('riskProgressFill');
  
  const confidenceValue = document.getElementById('confidenceValue');
  const phishingProbValue = document.getElementById('phishingProbValue');
  const legitimateProbValue = document.getElementById('legitimateProbValue');
  
  const indicatorsGrid = document.getElementById('indicatorsGrid');
  const sampleChips = document.querySelectorAll('.sample-chip');

  // Event Listeners
  if (urlForm) {
    urlForm.addEventListener('submit', handleAnalyze);
  }

  if (clearBtn) {
    clearBtn.addEventListener('click', handleClear);
  }

  // Quick-test sample URL click handler
  sampleChips.forEach(chip => {
    chip.addEventListener('click', () => {
      const sampleUrl = chip.getAttribute('data-url');
      if (sampleUrl) {
        urlInput.value = sampleUrl;
        triggerAnalysis(sampleUrl);
      }
    });
  });

  /**
   * Handles the URL analysis form submission
   */
  async function handleAnalyze(e) {
    if (e) e.preventDefault();
    const rawUrl = urlInput.value.trim();
    if (!rawUrl) {
      showError("Please enter a valid URL to analyze.");
      return;
    }
    triggerAnalysis(rawUrl);
  }

  /**
   * Executes the analysis pipeline via ApiService helper
   */
  async function triggerAnalysis(url) {
    hideError();
    showLoading(true);
    hideResults();

    try {
      // Call REST API helper
      const data = await window.ApiService.analyzeUrl(url);

      showLoading(false);
      renderResults(data);
    } catch (err) {
      showLoading(false);
      showError(err.message || "An unexpected error occurred while analyzing the URL.");
    }
  }

  /**
   * Renders the analysis results payload into the UI
   */
  function renderResults(data) {
    const { prediction, confidence, phishing_probability, legitimate_probability, risk, indicators } = data;

    // 1. Prediction Badge
    const isLegitimate = prediction === 'LEGITIMATE';
    predictionBadge.className = `prediction-badge ${isLegitimate ? 'legitimate' : 'phishing'}`;
    predictionText.textContent = prediction;

    // Icon rendering
    if (isLegitimate) {
      predictionIcon.innerHTML = `
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
          <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
          <polyline points="22 4 12 14.01 9 11.01"></polyline>
        </svg>`;
    } else {
      predictionIcon.innerHTML = `
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
          <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
          <line x1="12" y1="9" x2="12" y2="13"></line>
          <line x1="12" y1="17" x2="12.01" y2="17"></line>
        </svg>`;
    }

    // 2. Risk Level Tag
    const riskLower = (risk || 'LOW').toLowerCase();
    riskTag.className = `risk-tag ${riskLower}`;
    riskTag.textContent = `Risk Level: ${risk}`;

    // 3. Visual Risk Progress Bar
    const pProb = phishing_probability !== undefined ? phishing_probability : 0;
    riskBarValue.textContent = `${pProb.toFixed(2)}% Phishing Risk`;
    riskProgressFill.style.width = `${Math.min(Math.max(pProb, 2), 100)}%`;
    riskProgressFill.className = `progress-fill ${riskLower}`;

    // 4. Probability Stat Cards
    confidenceValue.textContent = `${confidence.toFixed(2)}%`;
    phishingProbValue.textContent = `${phishing_probability.toFixed(2)}%`;
    legitimateProbValue.textContent = `${legitimate_probability.toFixed(2)}%`;

    // 5. Security Indicators Grid
    renderIndicators(indicators || []);

    // Show Results Card
    resultsCard.style.display = 'block';
    resultsCard.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  }

  /**
   * Renders security indicator cards
   */
  function renderIndicators(indicators) {
    indicatorsGrid.innerHTML = '';

    indicators.forEach(ind => {
      const card = document.createElement('div');
      card.className = 'indicator-card';

      const statusClass = (ind.status || 'safe').toLowerCase();

      card.innerHTML = `
        <div>
          <div class="indicator-header">
            <span class="indicator-name">${escapeHtml(ind.name)}</span>
            <span class="status-pill ${statusClass}">${escapeHtml(ind.status)}</span>
          </div>
          <div class="indicator-value">${escapeHtml(ind.value)}</div>
        </div>
        <div class="indicator-desc">${escapeHtml(ind.description)}</div>
      `;

      indicatorsGrid.appendChild(card);
    });
  }

  /**
   * Handles the Clear button click
   */
  function handleClear() {
    urlInput.value = '';
    hideError();
    hideResults();
    urlInput.focus();
  }

  function showLoading(isLoading) {
    if (isLoading) {
      loadingCard.style.display = 'block';
      analyzeBtn.disabled = true;
      clearBtn.disabled = true;
      analyzeBtn.innerHTML = `
        <span class="scanner-spinner" style="width:16px;height:16px;border-width:2px;margin:0;"></span>
        Analyzing...
      `;
    } else {
      loadingCard.style.display = 'none';
      analyzeBtn.disabled = false;
      clearBtn.disabled = false;
      analyzeBtn.innerHTML = `
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="11" cy="11" r="8"></circle>
          <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
        </svg>
        Analyze URL
      `;
    }
  }

  function showError(msg) {
    errorMessage.textContent = msg;
    errorContainer.style.display = 'flex';
  }

  function hideError() {
    errorContainer.style.display = 'none';
  }

  function hideResults() {
    resultsCard.style.display = 'none';
  }

  function escapeHtml(str) {
    if (!str) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }
});
