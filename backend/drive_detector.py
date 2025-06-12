import psutil
import os
from backend.logger import AppLogger

class DriveDetector:
    def __init__(self):
        self.logger = AppLogger()

    def get_mounted_drives(self):
        drives = []
        partitions = psutil.disk_partitions()
        for p in partitions:
            is_removable = False
            if 'removable' in p.opts:
                is_removable = True
            elif os.name == 'posix' and (p.mountpoint.startswith('/media') or p.mountpoint.startswith('/mnt')):
                is_removable = True

            drives.append({
                'device': p.device,
                'mountpoint': p.mountpoint,
                'fstype': p.fstype,
                'opts': p.opts,
                'is_removable': is_removable
            })
            self.logger.debug(f"Drive detectado: {p.mountpoint}, Removível: {is_removable}")
        return drives

    def is_usb_drive(self, mountpoint):
        if os.name == 'posix': # Linux/macOS
            return mountpoint.startswith('/media') or mountpoint.startswith('/mnt')
        elif os.name == 'nt': # Windows
            self.logger.warning("Detecção de pendrive em Windows é limitada sem APIs específicas.")
            return False
        return False


