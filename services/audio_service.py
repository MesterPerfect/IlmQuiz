"""
Unified Audio Service for IlmQuiz powered by the BASS audio library via ctypes.
Cross-platform support for Windows, macOS, and Linux with zero external pip dependencies.
Replaces QtMultimedia with ultra-low latency, crystal-clear BASS audio playback.
"""

import os
import sys
import platform
import logging
import ctypes
from pathlib import Path
from typing import Optional, Dict, Any

from core.constants import BASE_DIR, SOUNDS_DIR

logger = logging.getLogger(__name__)

# BASS Constants
BASS_UNICODE = 0x80000000
BASS_SAMPLE_OVER_POS = 0x20000  # Override oldest instance if maximum simultaneous playbacks reached
BASS_ATTRIB_VOL = 2            # Volume attribute (0.0 to 1.0)
BASS_ERROR_ALREADY = 32        # BASS is already initialized in this process


class AudioService:
    """
    Unified cross-platform audio manager for game sound effects using BASS library.
    Provides drop-in compatibility with legacy PySide audio calls while delivering
    superior performance and low latency.
    """

    def __init__(self, sounds_dir: str = SOUNDS_DIR):
        self.sounds_dir = Path(sounds_dir)
        self.bass: Any = None
        self.available = False
        self.muted = False
        self.volume: float = 0.8  # Default volume 80% (0.0 to 1.0)
        self.samples: Dict[str, int] = {}
        self.active_channels: Dict[str, int] = {}

        self._init_bass()
        if self.available:
            self._load_default_sounds()

    def _find_bass_library(self) -> Optional[Path]:
        """Locates the platform- and architecture-appropriate BASS dynamic library."""
        system = platform.system()
        is_64bit = sys.maxsize > 2**32
        machine = platform.machine().lower()
        base_path = Path(BASE_DIR)

        candidates = []

        if system == "Windows":
            arch_dir = "x64" if is_64bit else "x86"
            candidates = [
                base_path / "assets" / "bass" / "windows" / arch_dir / "bass.dll",
                base_path / "assets" / "bass" / "bass.dll",
                base_path / "bass.dll",
                base_path / "lib" / "bass.dll",
            ]
        elif system == "Darwin":  # macOS
            candidates = [
                base_path / "assets" / "bass" / "macos" / "libbass.dylib",
                base_path / "assets" / "bass" / "libbass.dylib",
                base_path / "libbass.dylib",
                base_path / "lib" / "libbass.dylib",
            ]
        else:  # Linux
            arch_dir = "aarch64" if ("arm" in machine or "aarch64" in machine) else "x86_64"
            candidates = [
                base_path / "assets" / "bass" / "linux" / arch_dir / "libbass.so",
                base_path / "assets" / "bass" / "libbass.so",
                base_path / "libbass.so",
                base_path / "lib" / "libbass.so",
            ]

        for p in candidates:
            if p.exists():
                return p
        return None

    def _init_bass(self):
        """Loads BASS shared library via ctypes and initializes audio output device."""
        lib_path = self._find_bass_library()
        if not lib_path:
            logger.warning("BASS audio library binary not found. Audio effects will run in silent mode.")
            return

        try:
            self.bass = ctypes.CDLL(str(lib_path.resolve()))

            # BASS_Init(int device, DWORD freq, DWORD flags, void *win, void *clsid)
            self.bass.BASS_Init.argtypes = [
                ctypes.c_int,
                ctypes.c_ulong,
                ctypes.c_ulong,
                ctypes.c_void_p,
                ctypes.c_void_p,
            ]
            self.bass.BASS_Init.restype = ctypes.c_bool

            # BASS_SampleLoad(BOOL mem, void *file, QWORD offset, DWORD length, DWORD max, DWORD flags)
            self.bass.BASS_SampleLoad.argtypes = [
                ctypes.c_bool,
                ctypes.c_void_p,
                ctypes.c_uint64,
                ctypes.c_ulong,
                ctypes.c_ulong,
                ctypes.c_ulong,
            ]
            self.bass.BASS_SampleLoad.restype = ctypes.c_ulong

            # BASS_SampleGetChannel(HSAMPLE handle, BOOL onlynew)
            self.bass.BASS_SampleGetChannel.argtypes = [ctypes.c_ulong, ctypes.c_bool]
            self.bass.BASS_SampleGetChannel.restype = ctypes.c_ulong

            # BASS_ChannelSetAttribute(DWORD handle, DWORD attrib, float value)
            self.bass.BASS_ChannelSetAttribute.argtypes = [ctypes.c_ulong, ctypes.c_ulong, ctypes.c_float]
            self.bass.BASS_ChannelSetAttribute.restype = ctypes.c_bool

            # BASS_ChannelPlay(DWORD handle, BOOL restart)
            self.bass.BASS_ChannelPlay.argtypes = [ctypes.c_ulong, ctypes.c_bool]
            self.bass.BASS_ChannelPlay.restype = ctypes.c_bool

            # BASS_ChannelStop(DWORD handle)
            self.bass.BASS_ChannelStop.argtypes = [ctypes.c_ulong]
            self.bass.BASS_ChannelStop.restype = ctypes.c_bool

            # BASS_SampleFree(HSAMPLE handle)
            self.bass.BASS_SampleFree.argtypes = [ctypes.c_ulong]
            self.bass.BASS_SampleFree.restype = ctypes.c_bool

            # BASS_Free()
            self.bass.BASS_Free.argtypes = []
            self.bass.BASS_Free.restype = ctypes.c_bool

            # Initialize default sound output device (-1) at 44100 Hz
            ok = self.bass.BASS_Init(-1, 44100, 0, None, None)
            if not ok:
                error_func = getattr(self.bass, "BASS_ErrorGetCode", None)
                error_code = error_func() if error_func else 0
                if error_code != BASS_ERROR_ALREADY:
                    logger.warning(f"BASS_Init failed with error code: {error_code}")
                    self.available = False
                    return

            self.available = True
            logger.info(f"BASS audio initialized successfully from {lib_path.name}")

        except Exception as e:
            logger.exception(f"Failed to load or initialize BASS library: {e}")
            self.available = False

    def load_sound(self, name: str, filepath: Path | str) -> bool:
        """Loads a sound file into memory as a BASS sample."""
        if not self.available:
            return False

        path_obj = Path(filepath)
        if not path_obj.exists():
            logger.warning(f"Sound file not found: {path_obj}")
            return False

        try:
            full_path = str(path_obj.resolve())
            if sys.platform == "win32":
                file_arg = ctypes.cast(ctypes.c_wchar_p(full_path), ctypes.c_void_p)
                flags = BASS_UNICODE | BASS_SAMPLE_OVER_POS
            else:
                file_arg = ctypes.cast(ctypes.c_char_p(full_path.encode("utf-8")), ctypes.c_void_p)
                flags = BASS_SAMPLE_OVER_POS

            # Allow up to 8 simultaneous playback instances per sample (low latency polyphony)
            sample_handle = self.bass.BASS_SampleLoad(False, file_arg, 0, 0, 8, flags)
            if sample_handle:
                # Free previously loaded sample with same name if any
                if name in self.samples:
                    self.bass.BASS_SampleFree(self.samples[name])
                self.samples[name] = sample_handle
                logger.debug(f"Loaded BASS sample '{name}' from {path_obj.name}")
                return True
            else:
                logger.warning(f"Failed to load BASS sample '{name}' from {filepath}")
                return False
        except Exception as e:
            logger.error(f"Error loading sound '{name}': {e}")
            return False

    def _load_default_sounds(self):
        """Loads default game sound effects."""
        default_sounds = {
            "correct": "correct.wav",
            "wrong": "wrong.wav",
            "beep": "beep.wav",
            "time_up": "time_up.wav",
        }
        for name, filename in default_sounds.items():
            sound_file = self.sounds_dir / filename
            self.load_sound(name, sound_file)

    def play_sound(self, name: str):
        """Plays a loaded sound effect by its registered name."""
        if not self.available or self.muted:
            return

        sample_handle = self.samples.get(name)
        if not sample_handle:
            logger.debug(f"Attempted to play unknown or unloaded sound: {name}")
            return

        try:
            channel = self.bass.BASS_SampleGetChannel(sample_handle, False)
            if channel:
                self.bass.BASS_ChannelSetAttribute(channel, BASS_ATTRIB_VOL, float(self.volume))
                self.bass.BASS_ChannelPlay(channel, True)
                self.active_channels[name] = channel
                logger.debug(f"Playing BASS sound '{name}' at volume {self.volume:.2f}")
            else:
                logger.warning(f"Could not allocate channel for sound: {name}")
        except Exception as e:
            logger.error(f"Error playing sound '{name}': {e}")

    def play(self, name: str):
        """Convenience alias for play_sound."""
        self.play_sound(name)

    def stop_sound(self, name: str):
        """Stops an actively playing sound channel if running."""
        if not self.available:
            return
        channel = self.active_channels.get(name)
        if channel:
            try:
                self.bass.BASS_ChannelStop(channel)
            except Exception:
                pass

    def stop_all(self):
        """Stops all active sound channels."""
        if not self.available:
            return
        for channel in list(self.active_channels.values()):
            try:
                self.bass.BASS_ChannelStop(channel)
            except Exception:
                pass
        self.active_channels.clear()

    def set_volume(self, volume: float):
        """Sets the master volume for sound effects (normalized to 0.0 - 1.0)."""
        # Support both 0-1 and 0-100 ranges
        if volume > 1.0:
            volume = volume / 100.0
        self.volume = max(0.0, min(1.0, float(volume)))

        # Update currently active channels
        if self.available and self.bass:
            for channel in self.active_channels.values():
                try:
                    self.bass.BASS_ChannelSetAttribute(channel, BASS_ATTRIB_VOL, self.volume)
                except Exception:
                    pass

    def get_volume(self) -> float:
        """Returns the current master volume (0.0 to 1.0)."""
        return self.volume

    def toggle_mute(self) -> bool:
        """Toggles the mute state and returns the new state."""
        self.muted = not self.muted
        if self.muted:
            self.stop_all()
        return self.muted

    def cleanup(self):
        """Frees all allocated BASS samples and releases audio device."""
        if self.available and self.bass:
            try:
                self.stop_all()
                for sample in self.samples.values():
                    self.bass.BASS_SampleFree(sample)
                self.samples.clear()
                self.bass.BASS_Free()
            except Exception:
                pass
            finally:
                self.available = False

    def __del__(self):
        self.cleanup()
