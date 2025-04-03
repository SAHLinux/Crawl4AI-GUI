import sys
import os
import asyncio
import aiofiles
from typing import List, Optional
from urllib.parse import urlparse
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QTextEdit,
    QLabel,
    QFileDialog,
    QProgressBar,
    QLineEdit,
    QMessageBox,
    QSpinBox,
)
from PyQt6.QtCore import QThread, pyqtSignal
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator


class CrawlerWorker(QThread):
    progress = pyqtSignal(int, str)  # Progress value, status message
    finished = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, urls: List[str], output_dir: str, max_concurrent: int):
        super().__init__()
        self.urls = urls
        self.output_dir = output_dir
        self.max_concurrent = max_concurrent
        self.is_running = True

    def stop(self):
        self.is_running = False

    async def save_markdown(self, url: str, content: str) -> None:
        """Save markdown content to a file."""
        try:
            # Create a safe filename from the URL
            filename = urlparse(url).netloc + "_" + urlparse(url).path.replace("/", "_")
            if not filename.endswith(".md"):
                filename += ".md"

            filepath = os.path.join(self.output_dir, filename)

            async with aiofiles.open(filepath, "w", encoding="utf-8") as f:
                await f.write(content)

        except Exception as e:
            self.error.emit(f"Error saving {url}: {str(e)}")

    async def crawl_urls(self):
        """Crawl URLs in parallel batches."""
        try:
            browser_config = BrowserConfig(
                headless=True,
                extra_args=["--disable-gpu", "--disable-dev-shm-usage", "--no-sandbox"],
            )

            crawl_config = CrawlerRunConfig(
                markdown_generator=DefaultMarkdownGenerator(
                    options={"ignore_links": True, "body_width": 80}
                )
            )

            # Create crawler instance
            async with AsyncWebCrawler(config=browser_config) as crawler:
                total_urls = len(self.urls)
                completed = 0

                # Process URLs in batches
                for i in range(0, total_urls, self.max_concurrent):
                    if not self.is_running:
                        break

                    batch = self.urls[i : i + self.max_concurrent]
                    tasks = []

                    for url in batch:
                        session_id = f"session_{url}"
                        task = crawler.arun(
                            url=url, config=crawl_config, session_id=session_id
                        )
                        tasks.append(task)

                    # Wait for batch completion
                    results = await asyncio.gather(*tasks, return_exceptions=True)

                    # Process results and save markdown
                    for url, result in zip(batch, results):
                        if isinstance(result, Exception):
                            self.error.emit(f"Failed to crawl {url}: {str(result)}")
                        elif result.success:
                            if hasattr(result, "markdown") and result.markdown:
                                await self.save_markdown(
                                    url, result.markdown.raw_markdown
                                )
                            completed += 1
                            self.progress.emit(
                                int(completed * 100 / total_urls),
                                f"Processed {completed}/{total_urls} URLs",
                            )
                        else:
                            self.error.emit(
                                f"Failed to crawl {url}: {result.error_message}"
                            )
                            completed += 1

        except Exception as e:
            self.error.emit(f"Crawler error: {str(e)}")

    def run(self):
        """Run the crawler worker."""
        asyncio.run(self.crawl_urls())
        self.finished.emit()


class CrawlerGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.worker: Optional[CrawlerWorker] = None
        self.initUI()

    def initUI(self):
        """Initialize the GUI components."""
        self.setWindowTitle("Crawl4AI GUI")
        self.setGeometry(100, 100, 800, 600)

        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout()

        # URL input area
        url_layout = QVBoxLayout()
        url_label = QLabel("Enter URLs (one per line):")
        self.url_input = QTextEdit()
        url_layout.addWidget(url_label)
        url_layout.addWidget(self.url_input)

        # Buttons layout
        button_layout = QHBoxLayout()

        # Load URLs button
        self.load_btn = QPushButton("Load URLs from File")
        self.load_btn.clicked.connect(self.load_urls)

        # Output directory selection
        self.output_dir = QLineEdit()
        self.output_dir.setPlaceholderText("Select output directory...")
        self.output_dir_btn = QPushButton("Browse")
        self.output_dir_btn.clicked.connect(self.select_output_dir)

        # Concurrent crawls spinner
        concurrent_layout = QHBoxLayout()
        concurrent_label = QLabel("Max Concurrent Crawls:")
        self.concurrent_spin = QSpinBox()
        self.concurrent_spin.setRange(1, 10)
        self.concurrent_spin.setValue(3)
        concurrent_layout.addWidget(concurrent_label)
        concurrent_layout.addWidget(self.concurrent_spin)

        # Start and Cancel buttons
        self.start_btn = QPushButton("Start Crawling")
        self.start_btn.clicked.connect(self.start_crawling)
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.cancel_crawling)
        self.cancel_btn.setEnabled(False)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_label = QLabel("Ready")

        # Status text area
        self.status_text = QTextEdit()
        self.status_text.setReadOnly(True)

        # Add all widgets to layouts
        button_layout.addWidget(self.load_btn)
        button_layout.addWidget(self.output_dir)
        button_layout.addWidget(self.output_dir_btn)

        layout.addLayout(url_layout)
        layout.addLayout(button_layout)
        layout.addLayout(concurrent_layout)
        layout.addWidget(self.start_btn)
        layout.addWidget(self.cancel_btn)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.progress_label)
        layout.addWidget(self.status_text)

        main_widget.setLayout(layout)

    def load_urls(self):
        """Load URLs from a text file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select URLs File", "", "Text Files (*.txt);;All Files (*)"
        )

        if file_path:
            try:
                with open(file_path, "r") as f:
                    urls = f.read()
                self.url_input.setText(urls)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load URLs: {str(e)}")

    def select_output_dir(self):
        """Select output directory for markdown files."""
        dir_path = QFileDialog.getExistingDirectory(
            self, "Select Output Directory", "", QFileDialog.Option.ShowDirsOnly
        )
        if dir_path:
            self.output_dir.setText(dir_path)

    def validate_inputs(self) -> bool:
        """Validate user inputs before starting the crawler."""
        # Check URLs
        urls = self.url_input.toPlainText().strip().split("\n")
        urls = [url.strip() for url in urls if url.strip()]
        if not urls:
            QMessageBox.warning(
                self, "Validation Error", "Please enter at least one URL"
            )
            return False

        # Validate URLs
        for url in urls:
            try:
                result = urlparse(url)
                if not all([result.scheme, result.netloc]):
                    QMessageBox.warning(self, "Validation Error", f"Invalid URL: {url}")
                    return False
            except Exception:
                QMessageBox.warning(
                    self, "Validation Error", f"Invalid URL format: {url}"
                )
                return False

        # Check output directory
        output_dir = self.output_dir.text().strip()
        if not output_dir:
            QMessageBox.warning(
                self, "Validation Error", "Please select an output directory"
            )
            return False

        if not os.path.isdir(output_dir):
            try:
                os.makedirs(output_dir)
            except Exception as e:
                QMessageBox.critical(
                    self, "Error", f"Failed to create output directory: {str(e)}"
                )
                return False

        return True

    def start_crawling(self):
        """Start the crawling process."""
        if not self.validate_inputs():
            return

        # Disable inputs during crawling
        self.url_input.setEnabled(False)
        self.load_btn.setEnabled(False)
        self.output_dir.setEnabled(False)
        self.output_dir_btn.setEnabled(False)
        self.start_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)

        # Get URLs and create worker
        urls = [
            url.strip()
            for url in self.url_input.toPlainText().split("\n")
            if url.strip()
        ]
        self.worker = CrawlerWorker(
            urls=urls,
            output_dir=self.output_dir.text().strip(),
            max_concurrent=self.concurrent_spin.value(),
        )

        # Connect signals
        self.worker.progress.connect(self.update_progress)
        self.worker.error.connect(self.log_error)
        self.worker.finished.connect(self.crawling_finished)

        # Start crawling
        self.progress_bar.setValue(0)
        self.status_text.clear()
        self.worker.start()

    def cancel_crawling(self):
        """Cancel the ongoing crawling process."""
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.worker.wait()
            self.crawling_finished()
            self.log_message("Crawling cancelled by user")

    def update_progress(self, value: int, message: str):
        """Update progress bar and status message."""
        self.progress_bar.setValue(value)
        self.progress_label.setText(message)

    def log_error(self, message: str):
        """Log error messages to the status text area."""
        self.status_text.append(f"ERROR: {message}")

    def log_message(self, message: str):
        """Log general messages to the status text area."""
        self.status_text.append(message)

    def crawling_finished(self):
        """Clean up after crawling is finished."""
        # Re-enable inputs
        self.url_input.setEnabled(True)
        self.load_btn.setEnabled(True)
        self.output_dir.setEnabled(True)
        self.output_dir_btn.setEnabled(True)
        self.start_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)

        # Update status
        self.progress_label.setText("Crawling completed")
        self.log_message("Crawling process finished")


def main():
    app = QApplication(sys.argv)
    gui = CrawlerGUI()
    gui.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
