use iced::alignment::{Horizontal, Vertical};
use iced::widget::{button, column, container, row, slider, text, text_input};
use iced::{Application, Color, Command, Element, Length, Settings, Theme};

fn main() -> iced::Result {
    AestheticApp::run(Settings {
        window: iced::window::Settings {
            size: (500, 600),
            min_size: Some((320, 400)),
            ..Default::default()
        },
        ..Default::default()
    })
}

struct AestheticApp {
    bg_color: Color,
    accent_color: Color,
    slider_r: f32,
    slider_g: f32,
    slider_b: f32,
    accent_r: f32,
    accent_g: f32,
    accent_b: f32,
    text_input: String,
    slider_value: f32,
}

#[derive(Debug, Clone)]
enum Message {
    BackgroundRedChanged(f32),
    BackgroundGreenChanged(f32),
    BackgroundBlueChanged(f32),
    AccentRedChanged(f32),
    AccentGreenChanged(f32),
    AccentBlueChanged(f32),
    TextInputChanged(String),
    SliderChanged(f32),
    ButtonPressed,
}

impl Application for AestheticApp {
    type Message = Message;
    type Theme = Theme;
    type Executor = iced::executor::Default;
    type Flags = ();

    fn new(_flags: ()) -> (Self, Command<Message>) {
        (
            Self {
                bg_color: Color::from_rgb(0.12, 0.12, 0.18),
                accent_color: Color::from_rgb(0.5, 0.3, 0.8),
                slider_r: 0.12,
                slider_g: 0.12,
                slider_b: 0.18,
                accent_r: 0.5,
                accent_g: 0.3,
                accent_b: 0.8,
                text_input: "Welcome to Rust!".to_string(),
                slider_value: 0.5,
            },
            Command::none(),
        )
    }

    fn title(&self) -> String {
        String::from("Aesthetic Rust Window")
    }

    fn update(&mut self, message: Message) -> Command<Message> {
        match message {
            Message::BackgroundRedChanged(value) => {
                self.slider_r = value;
                self.bg_color = Color::from_rgb(self.slider_r, self.slider_g, self.slider_b);
            }
            Message::BackgroundGreenChanged(value) => {
                self.slider_g = value;
                self.bg_color = Color::from_rgb(self.slider_r, self.slider_g, self.slider_b);
            }
            Message::BackgroundBlueChanged(value) => {
                self.slider_b = value;
                self.bg_color = Color::from_rgb(self.slider_r, self.slider_g, self.slider_b);
            }
            Message::AccentRedChanged(value) => {
                self.accent_r = value;
                self.accent_color = Color::from_rgb(self.accent_r, self.accent_g, self.accent_b);
            }
            Message::AccentGreenChanged(value) => {
                self.accent_g = value;
                self.accent_color = Color::from_rgb(self.accent_r, self.accent_g, self.accent_b);
            }
            Message::AccentBlueChanged(value) => {
                self.accent_b = value;
                self.accent_color = Color::from_rgb(self.accent_r, self.accent_g, self.accent_b);
            }
            Message::TextInputChanged(value) => {
                self.text_input = value;
            }
            Message::SliderChanged(value) => {
                self.slider_value = value;
            }
            Message::ButtonPressed => {
                self.text_input = "Button was clicked!".to_string();
            }
        }
        Command::none()
    }

    fn view(&self) -> Element<Message> {
        // Title
        let title = text("✨ Aesthetic Rust Window ✨")
            .size(28)
            .style(iced::theme::Text::Color(Color::WHITE))
            .horizontal_alignment(Horizontal::Center);

        // Background color controls
        let bg_color_controls = column![
            text("Background Color:").size(16),
            row![
                text("R:"),
                slider(0.0..=1.0, self.slider_r, Message::BackgroundRedChanged).step(0.01),
            ]
            .spacing(10),
            row![
                text("G:"),
                slider(0.0..=1.0, self.slider_g, Message::BackgroundGreenChanged).step(0.01),
            ]
            .spacing(10),
            row![
                text("B:"),
                slider(0.0..=1.0, self.slider_b, Message::BackgroundBlueChanged).step(0.01),
            ]
            .spacing(10),
        ]
        .spacing(10)
        .padding(20);

        // Accent color controls
        let accent_color_controls = column![
            text("Accent Color:").size(16),
            row![
                text("R:"),
                slider(0.0..=1.0, self.accent_r, Message::AccentRedChanged).step(0.01),
            ]
            .spacing(10),
            row![
                text("G:"),
                slider(0.0..=1.0, self.accent_g, Message::AccentGreenChanged).step(0.01),
            ]
            .spacing(10),
            row![
                text("B:"),
                slider(0.0..=1.0, self.accent_b, Message::AccentBlueChanged).step(0.01),
            ]
            .spacing(10),
        ]
        .spacing(10)
        .padding(20);

        // Interactive elements
        let interaction = column![
            row![
                text("Slider:"),
                slider(0.0..=1.0, self.slider_value, Message::SliderChanged).step(0.01),
            ]
            .spacing(10),
            row![
                text("Text:"),
                text_input("Type something...", &self.text_input).on_input(Message::TextInputChanged),
            ]
            .spacing(10),
            button("Click Me!")
                .on_press(Message::ButtonPressed)
                .style(iced::theme::Button::Custom(Box::new(CustomButtonStyle {
                    accent_color: self.accent_color,
                }))),
        ]
        .spacing(15)
        .padding(20);

        // Footer
        let footer = text("Made with Rust and iced")
            .size(14)
            .horizontal_alignment(Horizontal::Center);

        // Main content
        let content = column![
            title,
            iced::widget::horizontal_rule(10),
            bg_color_controls,
            accent_color_controls,
            interaction,
            iced::widget::horizontal_rule(10),
            footer,
        ]
        .spacing(20)
        .padding(20)
        .width(Length::Fill)
        .height(Length::Fill)
        .align_items(iced::Alignment::Center);

        // Main container with background color
        container(content)
            .width(Length::Fill)
            .height(Length::Fill)
            .style(iced::theme::Container::Custom(Box::new(
                CustomContainerStyle {
                    bg_color: self.bg_color,
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

struct CustomButtonStyle {
    accent_color: Color,
}

impl iced::widget::button::StyleSheet for CustomButtonStyle {
    type Style = iced::Theme;

    fn active(&self, _style: &Self::Style) -> iced::widget::button::Appearance {
        iced::widget::button::Appearance {
            background: Some(iced::Background::Color(self.accent_color)),
            text_color: Color::WHITE,
            border_radius: 4.0.into(),
            shadow_offset: iced::Vector::new(1.0, 1.0),
            ..Default::default()
        }
    }
}