# Local Installation Guide

This guide provides step-by-step instructions for setting up the AI Welding Defect Detection System on your local machine.

## Prerequisites

Before starting, make sure you have the following installed:

- **Node.js** (version 18 or higher) - [Download here](https://nodejs.org/)
- **Python** (version 3.11 or higher) - [Download here](https://python.org/downloads/)
- **Git** - [Download here](https://git-scm.com/downloads)

## Quick Setup (5 minutes)

### 1. Clone the Repository

```bash
git clone <your-repository-url>
cd ai-welding-defect-detection
```

### 2. Install Dependencies

```bash
# Install Node.js dependencies
npm install

# Install Python dependencies  
pip install flask flask-cors pillow numpy python-multipart werkzeug
```

### 3. Start the Application

```bash
# Start the development server
npm run dev
```

The application will be available at `http://localhost:5000`

## Detailed Installation by Operating System

### Windows

#### Step 1: Install Prerequisites
1. **Download and install Node.js** from https://nodejs.org/
   - Choose the "LTS" version (recommended)
   - During installation, make sure to check "Add to PATH"

2. **Download and install Python** from https://python.org/downloads/
   - Choose Python 3.11 or newer
   - **Important**: Check "Add Python to PATH" during installation

3. **Download and install Git** from https://git-scm.com/downloads
   - Use default installation options

#### Step 2: Setup Project
Open **Command Prompt** or **PowerShell** and run:

```cmd
# Clone the repository
git clone <your-repository-url>
cd ai-welding-defect-detection

# Install Node.js dependencies
npm install

# Install Python dependencies
pip install flask flask-cors pillow numpy python-multipart werkzeug
```

#### Step 3: Run the Application
```cmd
npm run dev
```

### macOS

#### Step 1: Install Prerequisites
1. **Install Homebrew** (if not already installed):
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```

2. **Install Node.js, Python, and Git**:
   ```bash
   brew install node python@3.11 git
   ```

#### Step 2: Setup Project
```bash
# Clone the repository
git clone <your-repository-url>
cd ai-welding-defect-detection

# Install Node.js dependencies
npm install

# Install Python dependencies
pip3 install flask flask-cors pillow numpy python-multipart werkzeug
```

#### Step 3: Run the Application
```bash
npm run dev
```

### Linux (Ubuntu/Debian)

#### Step 1: Install Prerequisites
```bash
# Update package manager
sudo apt update

# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Install Python and Git
sudo apt install python3.11 python3-pip git
```

#### Step 2: Setup Project
```bash
# Clone the repository
git clone <your-repository-url>
cd ai-welding-defect-detection

# Install Node.js dependencies
npm install

# Install Python dependencies
pip3 install flask flask-cors pillow numpy python-multipart werkzeug
```

#### Step 3: Run the Application
```bash
npm run dev
```

## Verification

After installation, verify everything is working:

1. **Check if the server is running**: Open your browser and go to `http://localhost:5000`
2. **Test the application**: 
   - You should see the AI Welding Defect Detection interface
   - Try uploading a sample image to test the system

## Optional: Python Backend Setup

For enhanced AI processing, you can also run the dedicated Python backend:

```bash
# In a new terminal window, navigate to the backend folder
cd backend

# Start the Python Flask server
python app.py
```

The Python backend will run on `http://localhost:8000`

## Project Structure

```
ai-welding-defect-detection/
├── client/                 # React frontend
├── server/                 # Node.js backend
├── backend/               # Python AI backend
├── shared/                # Shared TypeScript types
├── package.json          # Node.js dependencies
└── backend/requirements.txt  # Python dependencies
```

## Troubleshooting

### Common Issues

**"npm: command not found"**
- Restart your terminal after installing Node.js
- Make sure Node.js is added to your PATH

**"pip: command not found"**
- Use `pip3` instead of `pip` on macOS/Linux
- On Windows, make sure Python is added to PATH

**"Port 5000 already in use"**
- Close any applications using port 5000
- Or kill the process: `npx kill-port 5000`

**Permission errors on Linux/macOS**
- Use `sudo` for global installations
- Or use `pip3 install --user` for user-only installation

### Getting Help

If you encounter issues:
1. Make sure all prerequisites are correctly installed
2. Check that you're in the correct directory
3. Try restarting your terminal
4. Check the main README.md for additional troubleshooting tips

## What's Next?

Once installed, you can:
- Upload X-ray images to detect welding defects
- Use the advanced settings to customize detection parameters
- Export detailed analysis reports
- Explore the training panel for custom AI models

---

**Need help?** Create an issue in the GitHub repository or refer to the main README.md for detailed documentation.