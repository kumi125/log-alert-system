# 🔔 Log Alert System 📜

A **real-time log monitoring and alert system** built with **Python** and **PyQt5**.  
This tool continuously watches log files for specific keywords and generates popup notifications  
(with sound alerts) whenever suspicious or critical events occur.

---

## 🚀 Features

- 📖 **Live Log Monitoring:** Continuously reads from a `.log` file and displays the latest entries.  
- 🧠 **Keyword Detection:** Detects and alerts for predefined terms like `unauthorized`, `error`, `attack`, etc.  
- 🔔 **Beep + Popup Alerts:** Plays a sound and shows a styled popup for each detected event.  
- 🕒 **Alert History:** Saves all triggered alerts in `alerts.txt` for future review.  
- ✅ **Simple GUI:** Clean PyQt5 interface with real-time updates.

---

## 🖼️ Screenshots

| Alert GUI | Detected Log | Alert Example |
|------------|---------------|----------------|
| ![Alert GUI](docs/Screenshot1.png) | ![Detected Log](docs/Screenshot2.png) | ![Alert Example](docs/Screenshot3.png) |

> 💡 Screenshots are stored in the `docs/` folder.

---

## 📂 Project Structure

log-alert-system/
├── src/
│ ├── init.py # Makes src a Python package
│ └── log_alert_gui.py # Main GUI script
├── data/
│ └── sample.txt # Sample log file
├── output/
│ └── alerts.txt # Generated alert history
├── docs/
│ ├── Screenshot1.png
│ ├── Screenshot2.png
│ └── Screenshot3.png
├── README.md
└── requirements.txt


---

## 🔧 How to Run

1. **Clone the repository:**
   ```bash
   git clone https://github.com/kumi125/log-alert-system.git
   cd log-alert-system

    Install dependencies:

pip install PyQt5

Run the script:

    python src/log_alert_gui.py

    📌 Make sure data/sample.txt exists and contains log entries,
    or replace it with your own .log file.

⚙️ Customization

    To modify alert keywords: open src/log_alert_gui.py and edit the keyword list.

    You can adjust popup styles, alert sounds, or monitoring intervals in the code.

🛡️ Use Cases

    🔍 Monitoring firewall or server logs

    🧑‍💻 Detecting intrusion attempts

    📊 Log analysis for training/demo in cybersecurity labs

    🧠 Learning Python GUI & alerting mechanisms

👨‍💻 Author

Kumail Hussain
🎓 Cybersecurity Student | Islamabad, Pakistan
🌐 GitHub: @kumi125
📜 License

This project is open-source and available under the MIT License.

⭐ If you like this project, consider giving it a star on GitHub!


---

## ✨ Why this version is better

✅ Professional layout — clear headings, spacing, and emoji use  
✅ Adds code formatting + folder tree block  
✅ Screenshot table looks organized  
✅ Easy-to-follow setup steps  
✅ Includes license and star note (looks polished!)  

---

Would you like me to **create a version that auto-links your screenshots** (based on your actual file names in `/docs`)?  
That way, you can paste it and the images will show properly on GitHub immediately.
