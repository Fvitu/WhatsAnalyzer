# 📱 WhatsAnalyzer

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)
![Status](https://img.shields.io/badge/Status-Cooking-orange.svg)

**WhatsAnalyzer** is a powerful Python web application built with Flask that turns your WhatsApp chat history into beautiful, interactive insights. Curious about who talks the most? Which emojis are your favorites? Or when your group is most active? WhatsAnalyzer cooks up the data for you! 🍳

> **Note:** This project is part of a personal coding challenge!

## ✨ Features

-   **📊 Comprehensive Statistics:** Visualize total messages, active days, and engagement metrics.
-   **👥 User Analysis:** See who dominates the conversation and who is the silent observer.
-   **😀 Emoji & Link Tracking:** Discover the most used emojis and shared links within your chats.
-   **📅 Temporal Trends:** Analyze activity over time (daily, monthly) to see how your conversations evolve.
-   **🔒 Secure & Private:** Authenticated access ensures your data remains private during the session. (Runs locally or self-hosted).
-   **📂 Easy Upload:** Simple drag-and-drop interface for WhatsApp `.txt` export files.

## 🚀 Tech Stack

-   **Backend:** Python, Flask
-   **Authentication:** Flask-Login, Flask-WTF
-   **Database:** MySQL (via PyMySQL)
-   **Frontend:** HTML5, CSS3, JavaScript (Chart.js for visualizations)
-   **Processing:** Python Regex (`re`) for parsing raw chat logs.

## 🛠️ Installation & Setup

Follow these steps to get the kitchen running on your local machine:

### Prerequisites

-   Python 3.8 or higher
-   MySQL Server installed and running

### 1. Clone the Repository

```bash
git clone https://github.com/Fvitu/WhatsAnalyzer
cd WhatsAnalyzer
```

### 2. Set up Virtual Environment

It's recommended to use a virtual environment.

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Database Configuration

1.  Create a MySQL database (e.g., `whatsanalyzer_db`).
2.  Import the database schema (if provided in `sql/` or via migrations).
3.  Configure your environment variables or `config.py` with your database credentials.

### 5. Run the Application

```bash
python app.py
```

Visit `http://localhost:5000` in your browser.

## 📖 How to Use

1.  **Export Chat:** Open a WhatsApp chat (Individual or Group) > Tap the three dots (⋮) > More > Export chat > Without Media.
2.  **Register/Login:** Create an account on the WhatsAnalyzer platform.
3.  **Upload:** Upload the exported `.txt` file via the upload interface.
4.  **Explore:** View the generated dashboard with all your stats!

## 📸 Screenshots

![WhatsAnalyzer Dashboard](screenshots/dashboard.png)

## 🤝 Contributing

Contributions are welcome! If you have ideas for new metrics or improvements:

1.  Fork the repository.
2.  Create a new branch (`git checkout -b feature/AmazingFeature`).
3.  Commit your changes (`git commit -m 'Add some AmazingFeature'`).
4.  Push to the branch (`git push origin feature/AmazingFeature`).
5.  Open a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

_Built by Fvitu with ❤️ and Python._
