#!/bin/bash

echo "🚀 Setting up Real-Time AI Audio Assistant..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    echo "Please install Python 3.8 or higher and try again."
    exit 1
fi

# Check Python version
python_version=$(python3 -c "import sys; print('.'.join(map(str, sys.version_info[:2])))")
echo "✅ Python $python_version detected"

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "📥 Installing Python packages..."
pip install -r requirements.txt

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚙️ Creating .env file from template..."
    cp .env.example .env
    echo "📝 Please edit .env file and add your API keys:"
    echo "   - OPENAI_API_KEY (for OpenAI/ChatGPT)"
    echo "   - GEMINI_API_KEY (for Google Gemini - optional)"
else
    echo "✅ .env file already exists"
fi

# Check for system dependencies
echo "🔍 Checking system dependencies..."

# Check for PortAudio (required for PyAudio)
if ! pkg-config --exists portaudio-2.0; then
    echo "⚠️ PortAudio not found. This is required for audio input."
    echo "Please install it:"
    echo "  Ubuntu/Debian: sudo apt-get install portaudio19-dev"
    echo "  macOS: brew install portaudio"
    echo "  Windows: Usually included with PyAudio wheel"
fi

echo ""
echo "✅ Installation complete!"
echo ""
echo "📋 Next Steps:"
echo "1. Edit the .env file and add your API keys"
echo "2. Run the application with: python main.py"
echo "3. Open your browser to http://localhost:8000"
echo ""
echo "🎤 Make sure your microphone is working and permissions are granted!"
echo ""
echo "To activate the virtual environment later, run:"
echo "   source venv/bin/activate"