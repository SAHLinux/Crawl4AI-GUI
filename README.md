# Crawl4AI-GUI

A powerful graphical user interface with multi-threading support for the popular web scraper [Crawl4AI](https://github.com/seyyed/crawl4ai). This application provides an intuitive interface to crawl multiple websites simultaneously and save the content as markdown files.

## Features

1. **Multi-URL Processing**: Enter multiple URLs directly in the interface or load them from a text file.
2. **Batch Processing**: Process multiple URLs simultaneously with configurable concurrency.
3. **Customizable Output**: Select where to save the generated markdown files.
4. **Progress Tracking**: Real-time progress bar and status updates during crawling.
5. **Error Handling**: Comprehensive error reporting and logging.
6. **User-Friendly Interface**: Intuitive PyQt6-based GUI for easy interaction.

## Screenshots

(Add screenshots here)

## Requirements

- Python 3.8 or higher
- PyQt6
- Crawl4AI
- Playwright

## Installation

### Windows

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/Crawl4AI-GUI.git
   cd Crawl4AI-GUI
   ```

2. Create a virtual environment:
   ```
   python -m venv .venv
   ```

3. Activate the virtual environment:
   ```
   .\.venv\Scripts\activate
   ```

4. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

5. Install Playwright browsers:
   ```
   playwright install
   ```

6. Run the application:
   ```
   python crawler_gui.py
   ```

   Or use the provided batch file:
   ```
   run.bat
   ```

### macOS/Linux

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/Crawl4AI-GUI.git
   cd Crawl4AI-GUI
   ```

2. Create a virtual environment:
   ```
   python -m venv .venv
   ```

3. Activate the virtual environment:
   ```
   source .venv/bin/activate
   ```

4. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

5. Install Playwright browsers:
   ```
   playwright install
   ```

6. Run the application:
   ```
   python crawler_gui.py
   ```

## Usage

1. **Enter URLs**: Type or paste URLs in the text area (one URL per line).
2. **Load URLs from File**: Click "Load URLs from File" to import URLs from a text file.
3. **Select Output Directory**: Choose where to save the generated markdown files.
4. **Set Concurrency**: Adjust the "Max Concurrent Crawls" value to control how many URLs are processed simultaneously.
5. **Start Crawling**: Click "Start Crawling" to begin the process.
6. **Monitor Progress**: Watch the progress bar and status messages.
7. **Cancel if Needed**: Click "Cancel" to stop the crawling process.

## Troubleshooting

### Common Issues

- **Playwright Installation Errors**: If you encounter issues with Playwright, try reinstalling it with:
  ```
  playwright install --force
  ```

- **URL Errors**: Ensure all URLs include the protocol (http:// or https://).

- **Permission Errors**: Make sure you have write permissions for the selected output directory.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
