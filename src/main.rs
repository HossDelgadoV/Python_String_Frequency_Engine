use iced::alignment::Horizontal;
use iced::widget::image::Handle;
use iced::widget::{button, column, container, image, row, scrollable, text, text_input, Radio};
use iced::{Alignment, Application, Color, Command, Element, Length, Settings, Theme};
use std::fs;
use std::path::PathBuf;

// Import our API client
mod api_client;
use crate::api_client::VisualizationType;

fn main() -> iced::Result {
    TextAnalyzerApp::run(Settings {
        window: iced::window::Settings {
            size: (1200, 800),
            min_size: Some((800, 600)),
            ..Default::default()
        },
        ..Default::default()
    })
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
enum Tab {
    TextAnalysis,
    Visualizations,
}

#[derive(Debug, Clone)]
struct Visualization {
    image_data: String,
    title: String,
}

struct TextAnalyzerApp {
    // Content
    input_text: String,
    result_text: String,
    analyzing: bool,
    api_status: ApiStatus,

    // UI state
    active_tab: Tab,
    selected_viz_type: VisualizationType,

    // Visualizations
    visualizations: Vec<Visualization>,
    generating_viz: bool,

    // File handling
    selected_file: Option<PathBuf>,
    file_selector_open: bool,
}

#[derive(Debug, Clone, PartialEq)]
enum ApiStatus {
    Unknown,
    Running,
    NotRunning,
}

#[derive(Debug, Clone)]
enum Message {
    // Content messages
    InputTextChanged(String),
    AnalyzeButtonPressed,
    AnalysisComplete(Result<String, String>),
    ApiStatusChecked(bool),
    CheckApiStatus,

    // Tab navigation
    TabSelected(Tab),

    // Visualization messages
    VisualizationTypeSelected(VisualizationType),
    GenerateVisualizationPressed,
    VisualizationComplete(Result<(String, bool), String>),
    ClearVisualizations,

    // File handling messages
    SelectFilePressed,
    FileSelected(Option<PathBuf>),
    AnalyzeFilePressed,
}

impl Application for TextAnalyzerApp {
    type Message = Message;
    type Theme = Theme;
    type Executor = iced::executor::Default;
    type Flags = ();

    fn new(_flags: ()) -> (Self, Command<Message>) {
        let app = Self {
            input_text: String::new(),
            result_text: String::from(
                "Analysis results will appear here...\nMake sure the API server is running.",
            ),
            analyzing: false,
            api_status: ApiStatus::Unknown,
            active_tab: Tab::TextAnalysis,
            selected_viz_type: VisualizationType::CharacterFrequency,
            visualizations: Vec::new(),
            generating_viz: false,
            selected_file: None,
            file_selector_open: false,
        };

        // Check API status on startup
        let command = Command::perform(
            async {
                match api_client::check_api_health().await {
                    Ok(is_running) => is_running,
                    Err(_) => false,
                }
            },
            Message::ApiStatusChecked,
        );

        (app, command)
    }

    fn title(&self) -> String {
        String::from("String Frequency Analyzer")
    }

    fn update(&mut self, message: Message) -> Command<Message> {
        match message {
            // Tab navigation
            Message::TabSelected(tab) => {
                self.active_tab = tab;
                Command::none()
            }

            // Content updates
            Message::InputTextChanged(text) => {
                self.input_text = text;
                Command::none()
            }
            Message::AnalyzeButtonPressed => {
                if !self.input_text.is_empty() && !self.analyzing {
                    self.analyzing = true;
                    self.result_text = "Analyzing...".to_string();

                    // If API status is unknown, check it first
                    if self.api_status == ApiStatus::Unknown {
                        return Command::perform(
                            async {
                                match api_client::check_api_health().await {
                                    Ok(is_running) => is_running,
                                    Err(_) => false,
                                }
                            },
                            Message::ApiStatusChecked,
                        );
                    }

                    // If API is not running, show error
                    if self.api_status == ApiStatus::NotRunning {
                        self.analyzing = false;
                        self.result_text =
                            "ERROR: API server is not running. Please start the Python API server."
                                .to_string();
                        return Command::none();
                    }

                    // Send text to API for analysis
                    let input_text = self.input_text.clone();

                    Command::perform(
                        async move {
                            match api_client::analyze_text(&input_text).await {
                                Ok(result) => Ok(result),
                                Err(e) => Err(e.to_string()),
                            }
                        },
                        Message::AnalysisComplete,
                    )
                } else {
                    Command::none()
                }
            }
            Message::AnalysisComplete(result) => {
                self.analyzing = false;
                match result {
                    Ok(text) => self.result_text = text,
                    Err(e) => {
                        self.result_text = format!("Error: {}", e);

                        // If we got an error, check API status again
                        return Command::perform(
                            async {
                                match api_client::check_api_health().await {
                                    Ok(is_running) => is_running,
                                    Err(_) => false,
                                }
                            },
                            Message::ApiStatusChecked,
                        );
                    }
                }
                Command::none()
            }
            Message::ApiStatusChecked(is_running) => {
                self.api_status = if is_running {
                    ApiStatus::Running
                } else {
                    if self.analyzing {
                        self.analyzing = false;
                        self.result_text =
                            "ERROR: API server is not running. Please start the Python API server."
                                .to_string();
                    }
                    ApiStatus::NotRunning
                };

                // If the button was pressed and API is running, trigger analysis
                if is_running && self.analyzing {
                    let input_text = self.input_text.clone();
                    return Command::perform(
                        async move {
                            match api_client::analyze_text(&input_text).await {
                                Ok(result) => Ok(result),
                                Err(e) => Err(e.to_string()),
                            }
                        },
                        Message::AnalysisComplete,
                    );
                }

                Command::none()
            }
            Message::CheckApiStatus => Command::perform(
                async {
                    match api_client::check_api_health().await {
                        Ok(is_running) => is_running,
                        Err(_) => false,
                    }
                },
                Message::ApiStatusChecked,
            ),

            // Visualization messages
            Message::VisualizationTypeSelected(viz_type) => {
                self.selected_viz_type = viz_type;
                Command::none()
            }
            Message::GenerateVisualizationPressed => {
                if !self.input_text.is_empty() && !self.generating_viz {
                    self.generating_viz = true;

                    // If API status is unknown, check it first
                    if self.api_status == ApiStatus::Unknown {
                        return Command::perform(
                            async {
                                match api_client::check_api_health().await {
                                    Ok(is_running) => is_running,
                                    Err(_) => false,
                                }
                            },
                            Message::ApiStatusChecked,
                        );
                    }

                    // If API is not running, show error
                    if self.api_status == ApiStatus::NotRunning {
                        self.generating_viz = false;
                        self.result_text =
                            "ERROR: API server is not running. Please start the Python API server."
                                .to_string();
                        return Command::none();
                    }

                    // Request visualization from API
                    let input_text = self.input_text.clone();
                    // Use a reference to avoid the move issue
                    let viz_type = self.selected_viz_type;

                    Command::perform(
                        async move {
                            match api_client::visualize_text(&input_text, viz_type, None).await {
                                Ok(result) => Ok(result),
                                Err(e) => Err(e.to_string()),
                            }
                        },
                        Message::VisualizationComplete,
                    )
                } else {
                    Command::none()
                }
            }
            Message::VisualizationComplete(result) => {
                self.generating_viz = false;

                match result {
                    Ok((data, is_multi)) => {
                        if is_multi {
                            // Parse the JSON string containing multiple visualizations
                            if let Ok(viz_map) = serde_json::from_str::<
                                serde_json::Map<String, serde_json::Value>,
                            >(&data)
                            {
                                self.visualizations.clear();

                                // Extract each visualization
                                for (key, value) in viz_map {
                                    let title = match key.as_str() {
                                        "char_freq" => "Character Frequency",
                                        "word_freq" => "Word Frequency",
                                        "word_cloud" => "Word Cloud",
                                        "char_dist" => "Character Distribution",
                                        _ => "Unknown Visualization",
                                    };

                                    if let Some(image_data) = value.as_str() {
                                        self.visualizations.push(Visualization {
                                            image_data: image_data.to_string(),
                                            title: title.to_string(),
                                        });
                                    }
                                }
                            }
                        } else {
                            // Single visualization
                            let title = match self.selected_viz_type {
                                VisualizationType::CharacterFrequency => "Character Frequency",
                                VisualizationType::WordFrequency => "Word Frequency",
                                VisualizationType::WordCloud => "Word Cloud",
                                VisualizationType::CharacterDistribution => {
                                    "Character Distribution"
                                }
                                VisualizationType::All => "All Visualizations",
                            };

                            self.visualizations.push(Visualization {
                                image_data: data,
                                title: title.to_string(),
                            });
                        }
                    }
                    Err(e) => {
                        self.result_text = format!("Visualization Error: {}", e);
                    }
                }

                Command::none()
            }
            Message::ClearVisualizations => {
                self.visualizations.clear();
                Command::none()
            }

            // File handling messages
            Message::SelectFilePressed => {
                if !self.file_selector_open {
                    self.file_selector_open = true;

                    Command::perform(
                        async {
                            rfd::AsyncFileDialog::new()
                                .add_filter("Text Files", &["txt", "md", "csv", "json"])
                                .pick_file()
                                .await
                                .map(|handle| handle.path().to_path_buf())
                        },
                        Message::FileSelected,
                    )
                } else {
                    Command::none()
                }
            }
            Message::FileSelected(file_path) => {
                self.file_selector_open = false;
                self.selected_file = file_path;
                Command::none()
            }
            Message::AnalyzeFilePressed => {
                if let Some(file_path) = &self.selected_file {
                    if !self.analyzing {
                        self.analyzing = true;
                        self.result_text = "Analyzing file...".to_string();

                        // If API status is unknown, check it first
                        if self.api_status == ApiStatus::Unknown {
                            return Command::perform(
                                async {
                                    match api_client::check_api_health().await {
                                        Ok(is_running) => is_running,
                                        Err(_) => false,
                                    }
                                },
                                Message::ApiStatusChecked,
                            );
                        }

                        // If API is not running, show error
                        if self.api_status == ApiStatus::NotRunning {
                            self.analyzing = false;
                            self.result_text = "ERROR: API server is not running. Please start the Python API server.".to_string();
                            return Command::none();
                        }

                        // Read file contents and send to API
                        let file_path_clone = file_path.clone();

                        Command::perform(
                            async move {
                                match fs::read_to_string(&file_path_clone) {
                                    Ok(content) => match api_client::analyze_text(&content).await {
                                        Ok(result) => Ok(result),
                                        Err(e) => Err(format!("API error: {}", e)),
                                    },
                                    Err(e) => Err(format!("File error: {}", e)),
                                }
                            },
                            Message::AnalysisComplete,
                        )
                    } else {
                        Command::none()
                    }
                } else {
                    self.result_text = "Please select a file first.".to_string();
                    Command::none()
                }
            }
        }
    }

    fn view(&self) -> Element<Message> {
        // Title
        let title = text("String Frequency Analyzer")
            .size(32)
            .horizontal_alignment(Horizontal::Center);

        // API status indicator
        let api_status_text = match self.api_status {
            ApiStatus::Running => "API Status: Connected",
            ApiStatus::NotRunning => "API Status: Not Connected (Start the Python API server)",
            ApiStatus::Unknown => "API Status: Checking...",
        };

        let api_status_color = match self.api_status {
            ApiStatus::Running => Color::from_rgb(0.0, 0.8, 0.0),
            ApiStatus::NotRunning => Color::from_rgb(0.8, 0.0, 0.0),
            ApiStatus::Unknown => Color::from_rgb(0.8, 0.8, 0.0),
        };

        let api_status = text(api_status_text)
            .size(14)
            .style(iced::theme::Text::Color(api_status_color))
            .horizontal_alignment(Horizontal::Center);

        // Tab navigation
        let tab_row = row![
            button(text("Text Analysis").size(16))
                .style(if self.active_tab == Tab::TextAnalysis {
                    iced::theme::Button::Primary
                } else {
                    iced::theme::Button::Secondary
                })
                .on_press(Message::TabSelected(Tab::TextAnalysis))
                .width(Length::Fill),
            button(text("Visualizations").size(16))
                .style(if self.active_tab == Tab::Visualizations {
                    iced::theme::Button::Primary
                } else {
                    iced::theme::Button::Secondary
                })
                .on_press(Message::TabSelected(Tab::Visualizations))
                .width(Length::Fill),
        ]
        .spacing(10)
        .padding(10);

        // Input section
        let input_section = column![
            text("Enter text to analyze:").size(16),
            text_input("Type or paste text here...", &self.input_text)
                .on_input(Message::InputTextChanged)
                .padding(10),
            button(
                text(if self.analyzing {
                    "Analyzing..."
                } else {
                    "Analyze Text"
                })
                .horizontal_alignment(Horizontal::Center),
            )
            .on_press(Message::AnalyzeButtonPressed)
            .width(Length::Fill),
        ]
        .spacing(10)
        .padding(20);

        // File input section
        let file_name = self
            .selected_file
            .as_ref()
            .and_then(|path| path.file_name())
            .and_then(|name| name.to_str())
            .unwrap_or("No file selected");

        let file_section = column![
            text("Or analyze a text file:").size(16),
            row![
                text(format!("Selected file: {}", file_name)).width(Length::Fill),
                button(text("Select File")).on_press(Message::SelectFilePressed),
            ]
            .spacing(10),
            button(
                text(if self.analyzing {
                    "Analyzing..."
                } else {
                    "Analyze File"
                })
                .horizontal_alignment(Horizontal::Center),
            )
            .on_press(Message::AnalyzeFilePressed)
            .width(Length::Fill),
        ]
        .spacing(10)
        .padding(20);

        // Tab content
        let content = match self.active_tab {
            Tab::TextAnalysis => {
                // Results section for text analysis
                let results_section = column![
                    text("Analysis Results:").size(16),
                    container(scrollable(
                        text(&self.result_text)
                            .size(14)
                            .horizontal_alignment(Horizontal::Left)
                    ))
                    .padding(10)
                    .height(Length::Fill)
                    .width(Length::Fill)
                    .style(iced::theme::Container::Custom(Box::new(
                        CustomContainerStyle {
                            bg_color: Color::from_rgb(0.15, 0.15, 0.2),
                        },
                    ))),
                ]
                .spacing(10)
                .padding(20)
                .height(Length::Fill);

                // Main layout for text analysis
                column![
                    row![
                        input_section.width(Length::FillPortion(1)),
                        file_section.width(Length::FillPortion(1)),
                    ],
                    results_section,
                ]
                .spacing(15)
                .height(Length::Fill)
            }
            Tab::Visualizations => {
                // Visualization type selection
                let viz_type_selection = column![
                    text("Select Visualization Type:").size(16),
                    row![
                        Radio::new(
                            "Character Frequency",
                            VisualizationType::CharacterFrequency,
                            Some(self.selected_viz_type),
                            Message::VisualizationTypeSelected
                        ),
                        Radio::new(
                            "Word Frequency",
                            VisualizationType::WordFrequency,
                            Some(self.selected_viz_type),
                            Message::VisualizationTypeSelected
                        ),
                    ]
                    .spacing(20),
                    row![
                        Radio::new(
                            "Word Cloud",
                            VisualizationType::WordCloud,
                            Some(self.selected_viz_type),
                            Message::VisualizationTypeSelected
                        ),
                        Radio::new(
                            "Character Distribution",
                            VisualizationType::CharacterDistribution,
                            Some(self.selected_viz_type),
                            Message::VisualizationTypeSelected
                        ),
                        Radio::new(
                            "All Visualizations",
                            VisualizationType::All,
                            Some(self.selected_viz_type),
                            Message::VisualizationTypeSelected
                        ),
                    ]
                    .spacing(20),
                    row![
                        button(
                            text(if self.generating_viz {
                                "Generating..."
                            } else {
                                "Generate Visualization"
                            })
                            .horizontal_alignment(Horizontal::Center),
                        )
                        .on_press(Message::GenerateVisualizationPressed)
                        .width(Length::Fill),
                        button(
                            text("Clear Visualizations").horizontal_alignment(Horizontal::Center),
                        )
                        .on_press(Message::ClearVisualizations)
                        .width(Length::Fill),
                    ]
                    .spacing(10),
                ]
                .spacing(15)
                .padding(20);

                // Visualization display area
                let viz_container = if self.visualizations.is_empty() {
                    container(
                        column![
                            text("No visualizations generated yet.")
                                .size(18)
                                .horizontal_alignment(Horizontal::Center),
                            text("Enter text and select a visualization type to generate.")
                                .size(14)
                                .horizontal_alignment(Horizontal::Center),
                        ]
                        .spacing(10)
                        .width(Length::Fill)
                        .height(Length::Fill)
                        .align_items(Alignment::Center),
                    )
                } else {
                    let mut viz_columns = column![].spacing(20).padding(20);

                    for viz in &self.visualizations {
                        let img_data = base64::decode(&viz.image_data).unwrap_or_default();
                        let img_handle = Handle::from_memory(img_data);

                        viz_columns = viz_columns.push(
                            column![
                                text(&viz.title)
                                    .size(18)
                                    .horizontal_alignment(Horizontal::Center),
                                image(img_handle)
                                    .width(Length::Fill)
                                    .height(Length::Fixed(400.0)),
                            ]
                            .spacing(10)
                            .align_items(Alignment::Center),
                        );
                    }

                    container(
                        scrollable(viz_columns)
                            .height(Length::Fill)
                            .width(Length::Fill),
                    )
                };

                // Place the visualization container in the style container
                let viz_display = container(viz_container)
                    .padding(10)
                    .height(Length::Fill)
                    .width(Length::Fill)
                    .style(iced::theme::Container::Custom(Box::new(
                        CustomContainerStyle {
                            bg_color: Color::from_rgb(0.15, 0.15, 0.2),
                        },
                    )));

                // Main layout for visualizations
                column![
                    row![
                        input_section.width(Length::FillPortion(1)),
                        viz_type_selection.width(Length::FillPortion(1)),
                    ],
                    viz_display,
                ]
                .spacing(15)
                .height(Length::Fill)
            }
        };

        // Footer with API status
        let footer = column![
            api_status,
            button(
                text("Check API Connection")
                    .size(12)
                    .horizontal_alignment(Horizontal::Center),
            )
            .on_press(Message::CheckApiStatus)
            .width(Length::Fixed(200.0))
        ]
        .spacing(10)
        .align_items(iced::Alignment::Center);

        // Main layout with tabs
        let main_content = column![title, tab_row, content, footer,]
            .spacing(15)
            .padding(20)
            .height(Length::Fill);

        // Main container with background color
        container(main_content)
            .width(Length::Fill)
            .height(Length::Fill)
            .style(iced::theme::Container::Custom(Box::new(
                CustomContainerStyle {
                    bg_color: Color::from_rgb(0.12, 0.12, 0.18),
                },
            )))
            .into()
    }
}

// Custom styling
struct CustomContainerStyle {
    bg_color: Color,
}

impl iced::widget::container::StyleSheet for CustomContainerStyle {
    type Style = iced::Theme;

    fn appearance(&self, _style: &Self::Style) -> iced::widget::container::Appearance {
        iced::widget::container::Appearance {
            background: Some(iced::Background::Color(self.bg_color)),
            text_color: Some(Color::WHITE),
            ..Default::default()
        }
    }
}
