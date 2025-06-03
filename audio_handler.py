import pyaudio
import speech_recognition as sr
import threading
import time
import asyncio
from typing import Callable, Optional
from config import Config

class AudioHandler:
    def __init__(self, on_transcription: Callable[[str], None]):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone(sample_rate=Config.AUDIO_RATE)
        self.on_transcription = on_transcription
        self.is_listening = False
        self.audio_thread = None

        # Calibrate for ambient noise
        print("Calibrating microphone for ambient noise...")
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=2)
        print("Microphone calibrated!")

    def start_listening(self):
        """Start continuous audio listening in a separate thread"""
        if not self.is_listening:
            self.is_listening = True
            self.audio_thread = threading.Thread(target=self._listen_continuously)
            self.audio_thread.daemon = True
            self.audio_thread.start()
            print("Started listening...")

    def stop_listening(self):
        """Stop audio listening"""
        self.is_listening = False
        if self.audio_thread:
            self.audio_thread.join(timeout=1)
        print("Stopped listening.")

    def _listen_continuously(self):
        """Continuously listen for audio and transcribe"""
        while self.is_listening:
            try:
                # Listen for audio with timeout
                with self.microphone as source:
                    print("Listening for audio...")
                    audio = self.recognizer.listen(
                        source,
                        timeout=1,
                        phrase_time_limit=5
                    )

                # Transcribe audio in a separate thread to avoid blocking
                threading.Thread(
                    target=self._transcribe_audio,
                    args=(audio,)
                ).start()

            except sr.WaitTimeoutError:
                # No audio detected, continue listening
                continue
            except Exception as e:
                print(f"Error in audio listening: {e}")
                time.sleep(0.1)

    def _transcribe_audio(self, audio):
        """Transcribe audio to text"""
        try:
            # Use Google Web Speech API (free tier)
            text = self.recognizer.recognize_google(audio)
            if text.strip():
                print(f"Transcribed: {text}")
                # Call the callback with transcribed text
                self.on_transcription(text)
        except sr.UnknownValueError:
            print("Could not understand audio")
        except sr.RequestError as e:
            print(f"Speech recognition error: {e}")
        except Exception as e:
            print(f"Transcription error: {e}")

class AudioRecorder:
    """Alternative recorder for more control over audio processing"""
    def __init__(self, on_audio_chunk: Callable[[bytes], None]):
        self.on_audio_chunk = on_audio_chunk
        self.is_recording = False
        self.audio = pyaudio.PyAudio()
        self.stream = None

    def start_recording(self):
        """Start recording audio"""
        if not self.is_recording:
            self.is_recording = True
            self.stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=Config.AUDIO_CHANNELS,
                rate=Config.AUDIO_RATE,
                input=True,
                frames_per_buffer=Config.AUDIO_CHUNK_SIZE,
                stream_callback=self._audio_callback
            )
            self.stream.start_stream()
            print("Started recording...")

    def stop_recording(self):
        """Stop recording audio"""
        if self.is_recording:
            self.is_recording = False
            if self.stream:
                self.stream.stop_stream()
                self.stream.close()
            print("Stopped recording.")

    def _audio_callback(self, in_data, frame_count, time_info, status):
        """Callback for audio stream"""
        if self.is_recording:
            self.on_audio_chunk(in_data)
        return (in_data, pyaudio.paContinue)

    def __del__(self):
        if hasattr(self, 'audio'):
            self.audio.terminate()