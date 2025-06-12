import logging
import os

class AppLogger:
    def __init__(self, log_file="file_manager.log", level=logging.INFO):
        self.log_file = log_file
        self.logger = logging.getLogger("FileManager")
        self.logger.setLevel(level)

        # Evita adicionar múltiplos handlers se já existirem
        if not self.logger.handlers:
            # Handler para arquivo
            file_handler = logging.FileHandler(self.log_file)
            file_handler.setLevel(level)

            # Handler para console (opcional)
            console_handler = logging.StreamHandler()
            console_handler.setLevel(level)

            # Formatter
            formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)

            # Adiciona handlers ao logger
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)

    def info(self, message):
        self.logger.info(message)

    def warning(self, message):
        self.logger.warning(message)

    def error(self, message):
        self.logger.error(message)

    def debug(self, message):
        self.logger.debug(message)

    def critical(self, message):
        self.logger.critical(message)


