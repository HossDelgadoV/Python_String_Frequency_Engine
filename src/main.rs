use iced::alignment::Horizontal;
use iced::widget::{button, column, container, row, text, text_input};
use iced::{Application, Color, Command, Element, Length, Settings, Theme};
use std::fs;
use std::path::PathBuf;

// Import our API client
mod api_client;

fn main() -> iced::Result {
    TextAnalyzerApp::run(Settings {
        window: iced::window::Settings {
            size: (900, 700),
            min_size: Some((600, 500)),
            ..Default::default()
        },
        ..Default::default()
    })
}

struct TextAnalyzerApp {
    // Content
    input_text: String,
    result_text: String,
    analyzing: bool,
    api_status: ApiStatus,

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

    // File handling messages
    SelectFilePressed,
    FileSelected(Option<PathBuf>),
    FileDialogClosed,
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
            Message::FileDialogClosed => {
                self.file_selector_open = false;
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

        // Results section
        let results_section = column![
            text("Analysis Results:").size(16),
            container(
                text(&self.result_text)
                    .size(14)
                    .horizontal_alignment(Horizontal::Left),
            )
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
        .padding(20);

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

        // Main layout
        let content = column![
            title,
            row![
                input_section.width(Length::FillPortion(1)),
                file_section.width(Length::FillPortion(1)),
            ],
            results_section.height(Length::Fill),
            footer,
        ]
        .spacing(15)
        .padding(20)
        .height(Length::Fill);

        // Main container with background color
        container(content)
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
