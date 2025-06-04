import pyaudio
import speech_recognition as sr
import threading
import time
import asyncio
import numpy as np
from typing import Callable, Optional
from config import Config
import concurrent.futures


class AudioHandler:
    def __init__(self, on_transcription: Callable[[str], None]):
        self.recognizer = sr.Recognizer()
        self.on_transcription = on_transcription
        self.is_listening = False
        self.audio_thread = None
        self.audio = pyaudio.PyAudio()
        self.system_audio_device = None
        self.loop = None
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=2)

        # Find system audio output device
        self._find_system_audio_device()

    def _find_system_audio_device(self):
        """Find the system audio output device (loopback/stereo mix)"""
        print("Searching for system audio devices...")

        for i in range(self.audio.get_device_count()):
            device_info = self.audio.get_device_info_by_index(i)
            device_name = device_info['name'].lower()

            # Look for common system audio device names
            system_audio_keywords = [
                'stereo mix', 'what u hear', 'loopback', 'wave out mix',
                'speakers', 'headphones', 'primary sound capture driver'
            ]

            # Check if this device can be used for input and matches system audio patterns
            if (device_info['maxInputChannels'] > 0 and
                    any(keyword in device_name for keyword in system_audio_keywords)):
                self.system_audio_device = i
                print(f"Found system audio device: {device_info['name']} (Index: {i})")
                break

        if self.system_audio_device is None:
            print("⚠️ No system audio device found. Available devices:")
            for i in range(self.audio.get_device_count()):
                device_info = self.audio.get_device_info_by_index(i)
                if device_info['maxInputChannels'] > 0:
                    print(f"  {i}: {device_info['name']} (Inputs: {device_info['maxInputChannels']})")

            # Fallback to default input device
            try:
                self.system_audio_device = self.audio.get_default_input_device_info()['index']
                print(f"Using default input device as fallback: {self.system_audio_device}")
            except:
                print("❌ No audio input devices available")
                raise Exception("No audio input devices available")

    def start_listening(self):
        """Start continuous audio listening in a separate thread"""
        if not self.is_listening:
            self.is_listening = True
            self.audio_thread = threading.Thread(target=self._listen_continuously)
            self.audio_thread.daemon = True
            self.audio_thread.start()
            print("Started listening to system audio...")

    def stop_listening(self):
        """Stop audio listening"""
        self.is_listening = False
        if self.audio_thread:
            self.audio_thread.join(timeout=1)
        print("Stopped listening.")

    def _listen_continuously(self):
        """Continuously listen for system audio and transcribe"""
        stream = None
        try:
            # Open audio stream for system audio capture
            stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=Config.AUDIO_RATE,
                input=True,
                input_device_index=self.system_audio_device,
                frames_per_buffer=Config.AUDIO_CHUNK_SIZE
            )

            print(f"Listening to system audio on device {self.system_audio_device}...")

            audio_buffer = []
            silence_counter = 0
            silence_threshold = int(Config.SILENCE_DURATION * Config.AUDIO_RATE / Config.AUDIO_CHUNK_SIZE)

            while self.is_listening:
                try:
                    # Read audio data
                    data = stream.read(Config.AUDIO_CHUNK_SIZE, exception_on_overflow=False)
                    audio_buffer.append(data)

                    # Convert to numpy array for analysis
                    audio_array = np.frombuffer(data, dtype=np.int16)
                    audio_level = np.abs(audio_array).mean()

                    # Check for silence
                    if audio_level < Config.SILENCE_THRESHOLD:
                        silence_counter += 1
                    else:
                        silence_counter = 0

                    # Process audio when we have enough data and detect silence
                    if len(audio_buffer) > 20 and silence_counter > silence_threshold:
                        # Combine audio buffer
                        combined_audio = b''.join(audio_buffer)

                        # Process in separate thread to avoid blocking
                        self.executor.submit(self._process_audio_buffer, combined_audio)

                        # Reset buffer
                        audio_buffer = []
                        silence_counter = 0

                    # Prevent buffer from growing too large
                    if len(audio_buffer) > 100:
                        audio_buffer = audio_buffer[-50:]

                except Exception as e:
                    print(f"Error reading audio: {e}")
                    time.sleep(0.1)

        except Exception as e:
            print(f"Error in audio stream: {e}")
        finally:
            if stream:
                stream.stop_stream()
                stream.close()

    def _process_audio_buffer(self, audio_data):
        """Process audio buffer and transcribe"""
        try:
            # Create AudioData object for speech recognition
            audio_data_obj = sr.AudioData(
                audio_data,
                Config.AUDIO_RATE,
                2  # 2 bytes per sample for 16-bit audio
            )

            # Transcribe using Google Speech Recognition
            text = self.recognizer.recognize_google(audio_data_obj)
            if text.strip():
                print(f"Transcribed system audio: {text}")
                # Use thread-safe callback
                self._safe_callback(text)

        except sr.UnknownValueError:
            # No speech detected - this is normal
            pass
        except sr.RequestError as e:
            print(f"Speech recognition error: {e}")
        except Exception as e:
            print(f"Transcription error: {e}")

    def _safe_callback(self, text: str):
        """Thread-safe callback that handles async functions properly"""
        try:
            # Check if we're in an async context
            try:
                loop = asyncio.get_running_loop()
                # If we have a running loop, schedule the callback
                if asyncio.iscoroutinefunction(self.on_transcription):
                    asyncio.run_coroutine_threadsafe(self.on_transcription(text), loop)
                else:
                    loop.call_soon_threadsafe(self.on_transcription, text)
            except RuntimeError:
                # No running loop, call directly if it's not a coroutine
                if not asyncio.iscoroutinefunction(self.on_transcription):
                    self.on_transcription(text)
                else:
                    # Need to run in new event loop
                    try:
                        asyncio.run(self.on_transcription(text))
                    except Exception as e:
                        print(f"Error in async callback: {e}")
        except Exception as e:
            print(f"Error in callback: {e}")

    def __del__(self):
        """Cleanup audio resources"""
        if hasattr(self, 'audio'):
            self.audio.terminate()
        if hasattr(self, 'executor'):
            self.executor.shutdown(wait=False)


class AudioRecorder:
    """Enhanced recorder for system audio capture with more control"""

    def __init__(self, on_audio_chunk: Callable[[bytes], None]):
        self.on_audio_chunk = on_audio_chunk
        self.is_recording = False
        self.audio = pyaudio.PyAudio()
        self.stream = None
        self.system_audio_device = None
        self._find_system_audio_device()

    def _find_system_audio_device(self):
        """Find the system audio output device"""
        for i in range(self.audio.get_device_count()):
            device_info = self.audio.get_device_info_by_index(i)
            device_name = device_info['name'].lower()

            if (device_info['maxInputChannels'] > 0 and
                    ('stereo mix' in device_name or 'loopback' in device_name or
                     'what u hear' in device_name)):
                self.system_audio_device = i
                break

        if self.system_audio_device is None:
            self.system_audio_device = self.audio.get_default_input_device_info()['index']

    def start_recording(self):
        """Start recording system audio"""
        if not self.is_recording:
            self.is_recording = True
            self.stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=Config.AUDIO_CHANNELS,
                rate=Config.AUDIO_RATE,
                input=True,
                input_device_index=self.system_audio_device,
                frames_per_buffer=Config.AUDIO_CHUNK_SIZE,
                stream_callback=self._audio_callback
            )
            self.stream.start_stream()
            print("Started recording system audio...")

    def stop_recording(self):
        """Stop recording system audio"""
        if self.is_recording:
            self.is_recording = False
            if self.stream:
                self.stream.stop_stream()
                self.stream.close()
            print("Stopped recording system audio.")

    def _audio_callback(self, in_data, frame_count, time_info, status):
        """Callback for audio stream"""
        if self.is_recording:
            self.on_audio_chunk(in_data)
        return (in_data, pyaudio.paContinue)

    def __del__(self):
        if hasattr(self, 'audio'):
            self.audio.terminate()