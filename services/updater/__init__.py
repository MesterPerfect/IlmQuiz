
"""
Updater Package
Handles checking for updates, downloading assets, and triggering the external installer.
"""
from .checker import UpdateChecker
from .downloader import UpdateDownloader
from .installer import trigger_update_installation
