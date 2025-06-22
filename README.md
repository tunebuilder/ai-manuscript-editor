# 📝 AI Manuscript Editor

Transform your manuscript with AI-powered stylistic editing.

## ✨ Features

- **Document Ingestion**: Upload PDF or DOCX files with journal entries
- **Smart Parsing**: Automatically detects and extracts "Day X" entries
- **AI Enhancement**: Uses OpenAI's GPT-4.5-preview for professional editing
- **Custom Prompts**: Editable system prompts for personalized editing styles
- **Batch Processing**: Efficient processing of multiple entries
- **PDF Export**: Professional PDF generation with ReportLab
- **Error Handling**: Robust error recovery with retry capabilities

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ai-editor
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv env
   source env/bin/activate  # On Windows: env\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
   *Note: This installs the latest version of OpenAI for optimal performance and features*

4. **Run the application**
   ```bash
   streamlit run app.py
   ```

5. **Open your browser**
   - The app will automatically open at `http://localhost:8501`

## 📖 Usage Guide

### Step 1: Setup
1. Enter your OpenAI API key in the sidebar
2. Optionally customize the AI editing instructions

### Step 2: Upload Document
1. Upload a PDF or DOCX file containing journal entries
2. Ensure entries follow the format: "Day 1", "Day 2", etc.

### Step 3: Process & Edit
1. Click "Begin Processing" to extract and parse entries
2. Review the parsed entries in the sidebar
3. Click "✨ Edit with AI" to enhance your writing

### Step 4: Download
1. Review the AI-enhanced entries
2. Click "📥 Download PDF" to get your polished manuscript

## 📄 Document Format Requirements

Your journal document should contain entries formatted like:

```
Day 1

Today I woke up feeling energized and ready to tackle the world...

Day 2

Had an interesting conversation with my neighbor today...
```

**Supported formats:**
- `Day 1`, `Day 2`, etc.
- `Day 1 - A Great Start` (with additional text)
- Case insensitive: `day 1`, `DAY 1`

## 🎨 Customization

### Editing Instructions
The default AI prompt focuses on:
- Enhancing rhythm and narrative flow
- Strengthening verbs and imagery
- Eliminating passive voice and unnecessary adverbs
- Maintaining your authentic voice

You can customize these instructions in the sidebar before processing.

### System Requirements
- **Model**: OpenAI GPT-4.5-preview
- **Batch Size**: 4 entries per batch
- **Rate Limiting**: Built-in exponential backoff
- **Memory**: In-memory processing (no disk I/O)

## 🔧 Technical Architecture

### Core Components

- **`app.py`**: Main Streamlit application
- **`document_ingestion.py`**: PDF/DOCX text extraction
- **`chunking_engine.py`**: Journal entry parsing
- **`openai_editor.py`**: AI editing with GPT-4.5
- **`pdf_generator.py`**: ReportLab PDF creation

### Dependencies

- **Streamlit**: Web interface
- **OpenAI**: AI text enhancement
- **PyPDF2**: PDF text extraction  
- **python-docx**: DOCX text extraction
- **ReportLab**: PDF generation

## 🛠️ Development

### Project Structure
```
ai-editor/
├── app.py                    # Main Streamlit app
├── document_ingestion.py     # Text extraction
├── chunking_engine.py        # Entry parsing
├── openai_editor.py          # AI editing
├── pdf_generator.py          # PDF generation
├── requirements.txt          # Dependencies
├── docs/                     # Documentation
│   ├── project-plan.md       # Development plan
│   ├── changes-made.md       # Change tracking
│   ├── chunk-logic.md        # Parsing logic
│   └── openai-api.md         # API configuration
└── test_fixtures/            # Test files
    └── sample_journal.txt    # Test data
```

### Running Tests
```bash
# Test document ingestion
python document_ingestion.py

# Test chunking engine  
python chunking_engine.py

# Test AI editing (requires API key)
python openai_editor.py

# Test PDF generation
python pdf_generator.py
```

## 🚨 Troubleshooting

### Common Issues

**"No journal entries found"**
- Ensure entries start with "Day 1", "Day 2", etc.
- Check that the document text is readable (not scanned images)

**"AI editing failed"**
- Verify your OpenAI API key is valid
- Check you have sufficient API credits
- Wait a few minutes if rate limited

**"PDF generation failed"**
- Try refreshing and clicking download again
- Check for special characters in your text

### Getting Help

1. Check the error messages in the app (they include solutions)
2. Review the troubleshooting guides in error dialogs
3. Verify your document format matches the requirements

## 📊 Performance

- **Document Size**: Handles documents up to several hundred pages
- **Processing Speed**: ~30 seconds per 10 journal entries
- **Memory Usage**: Minimal (in-memory processing)
- **API Costs**: ~$0.10-0.50 per 10 entries (varies by length)

## 🔒 Privacy & Security

- **No Data Storage**: All processing is in-memory
- **API Security**: OpenAI API key required (not stored)
- **Local Processing**: Document extraction happens locally
- **No Telemetry**: No usage data collected

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📞 Support

For support, please open an issue on the GitHub repository or contact the development team.

---

**Made with ❤️ using Streamlit and OpenAI** 