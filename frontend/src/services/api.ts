// API configuration for NIRNAY.AI backend
const API_BASE_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

// Helper function to make API calls
const apiCall = async (endpoint, options = {}) => {
  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
      ...options,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || "API request failed");
    }

    return await response.json();
  } catch (error) {
    console.error(`API Error [${endpoint}]:`, error);
    throw error;
  }
};

// API endpoints
export const api = {
  // Health check
  health: () => apiCall("/"),

  // Submit analysis
  submitAnalysis: (query) =>
    apiCall("/analyze", {
      method: "POST",
      body: JSON.stringify({ query }),
    }),

  // Get report
  getReport: (analysisId) =>
    apiCall(`/report/${analysisId}`, {
      method: "GET",
    }),

  // Get history
  getHistory: () =>
    apiCall("/history", {
      method: "GET",
    }),
};

export default api;
