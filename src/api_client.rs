// src/api_client.rs
use serde::{Deserialize, Serialize};
use std::error::Error;

#[derive(Serialize)]
struct AnalyzeRequest {
    text: String,
    format: String,
}

#[derive(Deserialize, Debug)]
struct AnalyzeResponse {
    results: serde_json::Value,
    format: String,
}

#[derive(Serialize)]
struct VisualizeRequest {
    text: String,
    max_words: Option<usize>,
}

#[derive(Deserialize, Debug)]
struct VisualizeResponse {
    image: String,
    format: String,
}

#[derive(Deserialize, Debug)]
struct MultiVisualizeResponse {
    visualizations: serde_json::Map<String, serde_json::Value>,
    format: String,
}

#[derive(Deserialize, Debug)]
struct ErrorResponse {
    error: String,
}

/// Visualization types supported by the API
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum VisualizationType {
    CharacterFrequency,
    WordFrequency,
    WordCloud,
    CharacterDistribution,
    All,
}

impl VisualizationType {
    pub fn as_str(&self) -> &'static str {
        match self {
            VisualizationType::CharacterFrequency => "char_freq",
            VisualizationType::WordFrequency => "word_freq",
            VisualizationType::WordCloud => "word_cloud",
            VisualizationType::CharacterDistribution => "char_dist",
            VisualizationType::All => "all",
        }
    }
}

/// Sends text to the Python API server for analysis
pub async fn analyze_text(text: &str) -> Result<String, Box<dyn Error>> {
    // API endpoint URL
    let url = "http://127.0.0.1:5000/analyze";

    // Create request payload
    let request = AnalyzeRequest {
        text: text.to_string(),
        format: "text".to_string(), // We want formatted text results
    };

    // Convert to JSON
    let request_json = serde_json::to_string(&request)?;

    // Send HTTP request to API
    let client = reqwest::Client::new();
    let response = client
        .post(url)
        .header("Content-Type", "application/json")
        .body(request_json)
        .send()
        .await?;

    // Check status code
    if !response.status().is_success() {
        // Get the status code before trying to parse the response body
        let status = response.status();

        // Try to parse error response
        match response.json::<ErrorResponse>().await {
            Ok(error_response) => return Err(format!("API error: {}", error_response.error).into()),
            Err(_) => return Err(format!("HTTP error: {}", status).into()),
        }
    }

    // Parse successful response
    let analyze_response = response.json::<AnalyzeResponse>().await?;

    // Return formatted results
    if analyze_response.format == "text" {
        if let serde_json::Value::String(text_result) = analyze_response.results {
            Ok(text_result)
        } else {
            Ok(analyze_response.results.to_string())
        }
    } else {
        Ok(serde_json::to_string_pretty(&analyze_response.results)?)
    }
}

/// Generate visualization for text analysis
pub async fn visualize_text(
    text: &str,
    viz_type: VisualizationType,
    max_words: Option<usize>,
) -> Result<(String, bool), Box<dyn Error>> {
    // API endpoint URL
    let url = format!("http://127.0.0.1:5000/visualize/{}", viz_type.as_str());

    // Create request payload
    let mut request = serde_json::Map::new();
    request.insert(
        "text".to_string(),
        serde_json::Value::String(text.to_string()),
    );

    if let Some(max) = max_words {
        request.insert(
            "max_words".to_string(),
            serde_json::Value::Number(serde_json::Number::from(max)),
        );
    }

    // Convert to JSON
    let request_json = serde_json::to_string(&request)?;

    // Send HTTP request to API
    let client = reqwest::Client::new();
    let response = client
        .post(url)
        .header("Content-Type", "application/json")
        .body(request_json)
        .send()
        .await?;

    // Check status code
    if !response.status().is_success() {
        let status = response.status();

        // Try to parse error response
        match response.json::<ErrorResponse>().await {
            Ok(error_response) => return Err(format!("API error: {}", error_response.error).into()),
            Err(_) => return Err(format!("HTTP error: {}", status).into()),
        }
    }

    // Check if this is a single visualization or multiple
    if viz_type == VisualizationType::All {
        // Parse multi-visualization response
        let viz_response = response.json::<MultiVisualizeResponse>().await?;

        // Convert to JSON string for easy transfer to GUI
        let viz_json = serde_json::to_string(&viz_response.visualizations)?;

        Ok((viz_json, true)) // true indicates multiple visualizations
    } else {
        // Parse single visualization response
        let viz_response = response.json::<VisualizeResponse>().await?;

        Ok((viz_response.image, false)) // false indicates single visualization
    }
}

/// Checks if the API server is running
pub async fn check_api_health() -> Result<bool, Box<dyn Error>> {
    let url = "http://127.0.0.1:5000/health";

    // Send HTTP request to health check endpoint
    let client = reqwest::Client::new();
    let response = client
        .get(url)
        .timeout(std::time::Duration::from_secs(2)) // Short timeout for health check
        .send()
        .await;

    match response {
        Ok(resp) => Ok(resp.status().is_success()),
        Err(_) => Ok(false), // API server is not running
    }
}
