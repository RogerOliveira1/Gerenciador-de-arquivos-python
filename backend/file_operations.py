import shutil
import os
from backend.logger import AppLogger

class FileOperations:
    def __init__(self):
        self.logger = AppLogger()

    def copy_file(self, source_path, destination_path):
        try:
            shutil.copy2(source_path, destination_path)
            message = f"Arquivo copiado de \'{source_path}\' para \'{destination_path}\'"
            self.logger.info(message)
            return True, message
        except FileNotFoundError:
            message = f"Erro: Arquivo de origem \'{source_path}\' não encontrado."
            self.logger.error(message)
            return False, message
        except PermissionError:
            message = f"Erro: Permissão negada ao copiar para \'{destination_path}\'"
            self.logger.error(message)
            return False, message
        except Exception as e:
            message = f"Erro ao copiar arquivo: {e}"
            self.logger.error(message)
            return False, message

    def move_file(self, source_path, destination_path):
        try:
            shutil.move(source_path, destination_path)
            message = f"Arquivo movido de \'{source_path}\' para \'{destination_path}\'"
            self.logger.info(message)
            return True, message
        except FileNotFoundError:
            message = f"Erro: Arquivo de origem \'{source_path}\' não encontrado."
            self.logger.error(message)
            return False, message
        except PermissionError:
            message = f"Erro: Permissão negada ao mover para \'{destination_path}\'"
            self.logger.error(message)
            return False, message
        except Exception as e:
            message = f"Erro ao mover arquivo: {e}"
            self.logger.error(message)
            return False, message

    def rename_file(self, current_path, new_name):
        try:
            new_path = os.path.join(os.path.dirname(current_path), new_name)
            os.rename(current_path, new_path)
            message = f"Arquivo renomeado de \'{current_path}\' para \'{new_path}\'"
            self.logger.info(message)
            return True, message
        except FileNotFoundError:
            message = f"Erro: Arquivo \'{current_path}\' não encontrado."
            self.logger.error(message)
            return False, message
        except PermissionError:
            message = f"Erro: Permissão negada ao renomear \'{current_path}\'"
            self.logger.error(message)
            return False, message
        except Exception as e:
            message = f"Erro ao renomear arquivo: {e}"
            self.logger.error(message)
            return False, message

    def delete_file(self, path):
        try:
            if os.path.isfile(path):
                os.remove(path)
                message = f"Arquivo \'{path}\' excluído com sucesso."
                self.logger.info(message)
                return True, message
            elif os.path.isdir(path):
                shutil.rmtree(path)
                message = f"Diretório \'{path}\' excluído com sucesso."
                self.logger.info(message)
                return True, message
            else:
                message = f"Erro: \'{path}\' não é um arquivo ou diretório válido."
                self.logger.error(message)
                return False, message
        except FileNotFoundError:
            message = f"Erro: Arquivo ou diretório \'{path}\' não encontrado."
            self.logger.error(message)
            return False, message
        except PermissionError:
            message = f"Erro: Permissão negada ao excluir \'{path}\'"
            self.logger.error(message)
            return False, message
        except Exception as e:
            message = f"Erro ao excluir arquivo/diretório: {e}"
            self.logger.error(message)
            return False, message


