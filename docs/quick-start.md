# Quick Start Guide

Welcome! This guide will help you set up and start using the AI Mock Interview Platform in just a few simple steps. No technical experience required!

## What You'll Need

Before you begin, make sure you have:

- A computer running Windows, macOS, or Linux
- An internet connection
- An OpenAI API key (we'll show you how to get one)
- About 15-20 minutes for setup

## Step 1: Install Docker Desktop

**Estimated Time: 5-10 minutes**

Docker Desktop lets you run the interview platform on your computer without complicated setup.

### For Windows

1. Visit [https://www.docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop)
2. Click "Download for Windows"
3. Run the installer file you downloaded
4. Follow the installation wizard (keep all default settings)
5. Restart your computer when prompted
6. Open Docker Desktop from your Start menu
7. Wait for Docker Desktop to start (you'll see a whale icon in your system tray)

### For macOS

1. Visit [https://www.docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop)
2. Click "Download for Mac" (choose Intel or Apple Silicon based on your Mac)
3. Open the downloaded .dmg file
4. Drag Docker to your Applications folder
5. Open Docker from Applications
6. Click "Open" when macOS asks for permission
7. Wait for Docker Desktop to start (you'll see a whale icon in your menu bar)

### For Linux

1. Visit [https://docs.docker.com/desktop/install/linux-install/](https://docs.docker.com/desktop/install/linux-install/)
2. Follow the instructions for your Linux distribution
3. Start Docker Desktop after installation

**How to verify Docker is working:**

- Look for the Docker whale icon in your system tray (Windows) or menu bar (macOS)
- The icon should be steady, not animated
- If you see the whale icon, Docker is ready!

## Step 2: Get Your OpenAI API Key

**Estimated Time: 3-5 minutes**

The AI interviewer uses OpenAI's technology to conduct interviews. You'll need an API key to use it.

1. Go to [https://platform.openai.com/signup](https://platform.openai.com/signup)
2. Create an account or sign in if you already have one
3. Click on your profile icon in the top-right corner
4. Select "View API keys" from the menu
5. Click "Create new secret key"
6. Give it a name like "Interview Platform"
7. **IMPORTANT**: Copy the key that appears (it starts with "sk-")
8. Save this key somewhere safe - you won't be able to see it again!

**Cost Information:**

- OpenAI charges based on usage (typically $0.50-$2.00 per interview)
- You'll need to add a payment method to your OpenAI account
- You can set spending limits in your OpenAI account settings

## Step 3: Download the Interview Platform

**Estimated Time: 2 minutes**

1. Download the platform from [GitHub Release Link]
2. Extract the ZIP file to a location you'll remember (like your Documents folder)
3. You should now have a folder called "ai-mock-interview-platform"

## Step 4: Configure Your Settings

**Estimated Time: 2 minutes**

1. Open the "ai-mock-interview-platform" folder
2. Find the file named `.env.template` in the `config` folder
3. Make a copy of this file and rename it to `.env` in the root folder
4. Open the `.env` file with Notepad (Windows) or TextEdit (macOS)
5. Replace the placeholder values with your actual configuration

Example:
```bash
DB_PASSWORD=MySecurePassword123
OPENAI_API_KEY=sk-proj-abc123xyz789...
```

## Step 5: Start the Platform

**Estimated Time: 2-3 minutes**

### For Windows

Open Command Prompt in the platform folder and run:
```cmd
startup.sh
```

### For macOS/Linux

Open Terminal, navigate to the platform folder, and run:
```bash
chmod +x startup.sh
./startup.sh
```

## Step 6: Open the Interview Platform

1. Open your web browser (Chrome, Firefox, Safari, or Edge)
2. Go to: `http://localhost:8501`
3. You should see the AI Mock Interview Platform welcome screen!

## Using the Platform

### Starting Your First Interview

1. **Upload Your Resume** - The AI will analyze your experience level
2. **Choose Your AI Provider** - Select OpenAI GPT-4 (recommended)
3. **Select Communication Modes** - Enable audio, video, whiteboard as needed
4. **Click "Start Interview"** - The AI interviewer will present a problem

### During the Interview

- **Left Panel**: Chat with the AI interviewer
- **Center Panel**: Whiteboard for drawing system diagrams
- **Right Panel**: Live transcript
- **Bottom Bar**: Recording controls

### Ending the Interview

1. Click the "End Interview" button
2. Wait for the AI to generate your feedback
3. Review your evaluation report

## Troubleshooting

### Docker is not running

**Solution:** Open Docker Desktop and wait for it to fully start

### Port 8501 is already in use

**Solution:** Close other applications using that port or restart your computer

### Invalid API key

**Solution:** Verify your OpenAI API key is correct in the `.env` file

### Cannot connect to database

**Solution:** Wait 30 seconds for the database to start, or run `docker-compose down` then `./startup.sh` again

## What's Next?

- Practice regularly (at least one interview per week)
- Track your progress in the History section
- Focus on areas identified in your improvement plans
- Experiment with different communication modes

For more detailed information, see the [Developer Setup Guide](developer-setup.md).

---

**Congratulations!** You're now ready to practice system design interviews with AI. Good luck! 🚀
