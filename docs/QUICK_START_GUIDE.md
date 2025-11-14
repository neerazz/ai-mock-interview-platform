# Quick Start Guide - AI Mock Interview Platform

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

### For Windows:

1. Visit [https://www.docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop)
2. Click "Download for Windows"
3. Run the installer file you downloaded
4. Follow the installation wizard (keep all default settings)
5. Restart your computer when prompted
6. Open Docker Desktop from your Start menu
7. Wait for Docker Desktop to start (you'll see a whale icon in your system tray)

### For macOS:

1. Visit [https://www.docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop)
2. Click "Download for Mac" (choose Intel or Apple Silicon based on your Mac)
3. Open the downloaded .dmg file
4. Drag Docker to your Applications folder
5. Open Docker from Applications
6. Click "Open" when macOS asks for permission
7. Wait for Docker Desktop to start (you'll see a whale icon in your menu bar)

### For Linux:

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
5. You'll see something like this:

```
# Database Configuration
DB_PASSWORD=your_secure_password_here

# AI Provider API Keys
OPENAI_API_KEY=sk-your-openai-key-here
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key-here
```

6. Replace `your_secure_password_here` with any password you want (this is just for your local database)
7. Replace `sk-your-openai-key-here` with the OpenAI API key you copied in Step 2
8. You can leave the `ANTHROPIC_API_KEY` line as-is (it's optional)
9. Save the file and close it

**Example of what it should look like:**
```
DB_PASSWORD=MySecurePassword123
OPENAI_API_KEY=sk-proj-abc123xyz789...
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key-here
```

## Step 5: Start the Platform

**Estimated Time: 2-3 minutes**

Now you're ready to start the interview platform!

### For Windows:

1. Open the "ai-mock-interview-platform" folder
2. Double-click the file named `startup.sh`
3. If Windows asks "How do you want to open this file?", select "Git Bash" or "Windows Subsystem for Linux"
4. Alternatively, open Command Prompt:
   - Press Windows key + R
   - Type `cmd` and press Enter
   - Type `cd` followed by the path to your folder
   - Type `startup.sh` and press Enter

### For macOS/Linux:

1. Open Terminal
2. Type `cd` followed by a space
3. Drag the "ai-mock-interview-platform" folder into the Terminal window
4. Press Enter
5. Type `chmod +x startup.sh` and press Enter (this makes the script runnable)
6. Type `./startup.sh` and press Enter

**What you'll see:**
```
Starting AI Mock Interview Platform...
Starting Docker services...
Waiting for PostgreSQL to be ready...
PostgreSQL is ready!
Database connection successful!

Services started successfully!
================================
PostgreSQL: http://localhost:5432
Streamlit App: http://localhost:8501
================================
```

**If you see this message, you're all set!**

## Step 6: Open the Interview Platform

**Estimated Time: 1 minute**

1. Open your web browser (Chrome, Firefox, Safari, or Edge)
2. Go to: `http://localhost:8501`
3. You should see the AI Mock Interview Platform welcome screen!

## Using the Platform

### Starting Your First Interview

1. **Upload Your Resume**
   - Click "Browse files" or drag your resume (PDF or text file)
   - The AI will analyze your experience level and expertise
   - This helps generate relevant interview questions

2. **Choose Your AI Provider**
   - Select "OpenAI GPT-4" (recommended for most users)
   - Or "Anthropic Claude" if you have an Anthropic API key

3. **Select Communication Modes**
   - **Audio**: Speak your answers (requires microphone)
   - **Video**: Record yourself (requires webcam)
   - **Whiteboard**: Draw system diagrams (recommended!)
   - **Screen Share**: Share your screen (optional)
   - You can enable multiple modes at once

4. **Click "Start Interview"**
   - The AI interviewer will greet you and present a problem
   - Take your time to think and respond

### During the Interview

- **Left Panel**: Chat with the AI interviewer
  - Type your responses in the text box
  - Or speak if you enabled audio mode

- **Center Panel**: Whiteboard for drawing
  - Use the drawing tools to create system diagrams
  - Click "Save Snapshot" to save your work
  - Click "Clear Canvas" to start over

- **Right Panel**: Live transcript
  - See everything that's been said
  - Search for specific topics
  - Export the transcript when done

- **Bottom Bar**: Recording controls
  - Toggle audio/video recording
  - Take whiteboard snapshots
  - End the interview when ready

### Ending the Interview

1. Click the "End Interview" button at the bottom
2. Confirm that you want to end the session
3. Wait a moment while the AI generates your feedback
4. Review your evaluation report with:
   - Overall score and competency breakdown
   - What went well
   - What needs improvement
   - Personalized improvement plan

### Viewing Past Interviews

1. Click "History" in the navigation menu
2. See all your completed interviews
3. Click on any session to review:
   - Full conversation transcript
   - Whiteboard snapshots
   - Evaluation report
   - Token usage and costs

## Stopping the Platform

When you're done using the platform:

### For Windows:
1. Open Command Prompt
2. Navigate to the platform folder
3. Type: `docker-compose down`
4. Press Enter

### For macOS/Linux:
1. Open Terminal
2. Navigate to the platform folder
3. Type: `docker-compose down`
4. Press Enter

This stops all services and frees up your computer's resources.

## Troubleshooting

### Problem: "Docker is not running"

**Solution:**
1. Open Docker Desktop
2. Wait for it to fully start (whale icon should be steady)
3. Try running `startup.sh` again

### Problem: "Port 8501 is already in use"

**Solution:**
1. Something else is using that port
2. Close other applications that might be using it
3. Or restart your computer and try again

### Problem: "Invalid API key"

**Solution:**
1. Check that you copied your OpenAI API key correctly
2. Make sure there are no extra spaces in the `.env` file
3. Verify your API key is active at [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)

### Problem: "Cannot connect to database"

**Solution:**
1. Make sure Docker Desktop is running
2. Wait 30 seconds and try again (database might still be starting)
3. Run `docker-compose down` then `./startup.sh` again

### Problem: "Resume upload failed"

**Solution:**
1. Make sure your resume is in PDF or TXT format
2. Check that the file size is under 10MB
3. Try converting your resume to a simpler format

### Problem: "AI is not responding"

**Solution:**
1. Check your internet connection
2. Verify your OpenAI API key is valid
3. Check if you have sufficient credits in your OpenAI account
4. Look at the error message for specific details

### Still Having Issues?

1. Check the logs:
   - Open the `logs` folder in your platform directory
   - Look at `interview_platform.log` for error messages

2. Restart everything:
   ```
   docker-compose down
   ./startup.sh
   ```

3. Check Docker logs:
   ```
   docker-compose logs
   ```

## Tips for a Great Interview Experience

1. **Prepare Your Environment**
   - Find a quiet space
   - Test your microphone and camera before starting
   - Have a notepad handy for quick notes

2. **Use the Whiteboard**
   - Draw system diagrams as you explain
   - Use different colors for different components
   - Save snapshots at key points in your design

3. **Think Out Loud**
   - Explain your reasoning as you work
   - Discuss trade-offs and alternatives
   - Ask clarifying questions

4. **Take Your Time**
   - There's no time limit (though 45-60 minutes is typical)
   - Pause to think before responding
   - It's okay to revise your design

5. **Review Your Feedback**
   - Read the evaluation carefully
   - Focus on the improvement plan
   - Practice the areas that need work
   - Do another interview to track progress

## What's Next?

- **Practice Regularly**: Try to do at least one interview per week
- **Track Progress**: Review your history to see improvement over time
- **Focus on Weaknesses**: Use the improvement plans to guide your study
- **Experiment**: Try different communication modes to find what works best
- **Stay Updated**: Check for platform updates and new features

## Getting Help

If you need assistance:
- Check the troubleshooting section above
- Review the logs in the `logs` folder
- Consult the Developer Setup Guide for more technical details
- Contact support at [support email]

---

**Congratulations!** You're now ready to practice system design interviews with AI. Good luck! 🚀
