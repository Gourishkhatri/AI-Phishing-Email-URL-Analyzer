/**
 * API Service for AI Phishing URL Analyzer
 * Modular service helper to communicate with Flask REST API.
 */

const API_CONFIG = {
  // Base endpoint for URL analysis; can be updated if hosted on an external backend URL
  endpointUrl: '/api/analyze',
  timeoutMs: 15000
};

/**
 * Sends a URL to the Flask backend API for phishing analysis.
 * @param {string} url - The URL to analyze
 * @returns {Promise<Object>} The API response payload
 */
async function analyzeUrl(url) {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), API_CONFIG.timeoutMs);

  try {
    const response = await fetch(API_CONFIG.endpointUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      body: JSON.stringify({ url: url }),
      signal: controller.signal
    });

    clearTimeout(timeoutId);

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error || `Server responded with status ${response.status}`);
    }

    return data;
  } catch (error) {
    clearTimeout(timeoutId);
    if (error.name === 'AbortError') {
      throw new Error('Analysis request timed out. Please check your network connection.');
    }
    throw error;
  }
}

// Export for global browser use / ES module compatibility if required
if (typeof window !== 'undefined') {
  window.ApiService = {
    analyzeUrl,
    config: API_CONFIG
  };
}
