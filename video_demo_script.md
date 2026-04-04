# Hackathon Video Demo Guide: Call Center Compliance API

Since I am an AI, I cannot directly record my screen, narrate audio, or upload a video to YouTube for you. However, I have generated a **complete step-by-step recording plan and voiceover script** based exactly on your codebase and the hackathon's "Track 3" evaluation criteria. 

You can use a free tool like **Loom**, **OBS Studio**, or **Zoom** to record your screen while reading the script below.

---

## 🎬 Recording Checklist & Setup
Before you hit record, have the following windows open and ready:
1. **Your IDE (VS Code)**: Open `src/main.py` and `README.md` to show the clean code structure and approach.
2. **Terminal**: Showing your FastAPI server running (`uvicorn src.main:app --reload`) or your deployment environment logs.
3. **Postman or cURL Terminal**: A ready-to-send POST request targeting your connected endpoint with the proper `x-api-key` header and a sample Base64 payload (Hinglish or Tanglish).

---

## 🗣️ Voiceover Script & Visual Actions

**Target Time:** ~3 minutes

### 1. Introduction (0:00 - 0:30)
* **Visual**: Camera showing your face (optional, via Loom) or showing the GitHub `README.md` and architecture diagram.
* **Audio**: 
> "Hello everyone, and welcome to our demo for Track 3: Call Center Compliance. Our team has built a highly optimized, single-stage AI processing pipeline that analyzes native Hinglish and Tanglish audio to ensure call center agents are strictly following SOPs. Our primary goal was to maximize evaluation accuracy while completely eliminating the common API timeout issues associated with heavy audio processing."

### 2. Architecture & Code Quality (0:30 - 1:15)
* **Visual**: Switch to VS Code. Briefly show the clean structure (`src/main.py`, `.env.example`, `requirements.txt`). Highlight the section where Gemini 2.5 Flash is called.
* **Audio**: 
> "Taking a quick look at our codebase architecture, we built the backend using FastAPI for maximum async performance. The core innovation of our approach is using **Google Gemini 2.5 Flash** as a single multimodal engine. Instead of chaining separate Speech-to-Text and NLP models—which introduces high latency—we pass the Base64 audio directly to Gemini along with a highly tuned system prompt. This guarantees lightning-fast execution and strict Pydantic-validated JSON responses."

### 3. Live Demonstration - Success Case (1:15 - 2:45)
* **Visual**: Open Postman (or terminal for cURL). Emphasize the Headers tab showing `x-api-key`. Then, click **Send** on a request containing a Tanglish/Hinglish base64 audio string.
* **Audio**: 
> "Let's see it in action. Here we have a request hitting our `/api/call-analytics` endpoint. Notice that the `x-api-key` header is strictly enforced, fulfilling the security requirement. In the body, we are passing a Base64-encoded MP3 file as required, so there’s no local file saving involved. I'll hit send."
* **Visual**: Point the cursor specifically to the response JSON fields as you mention them.
* **Audio**: 
> "As you can see, the API returns a structured JSON response. We get a highly accurate **Transcript** in the detected language, and a concise **Summary**. 
> Next, let's look at the **SOP Validation** object. It strictly evaluates the five required stages: greeting, identification, problem statement, solution offering, and closing. It outputs exact boolean values and computes a compliance score. In this example, the agent missed the identification step, so the status is flagged as 'NOT_FOLLOWED'.
> Under **Analytics**, the system accurately classified the payment preference—such as EMI or Partial Payment—and detected the rejection reason if the sale didn't go through. Finally, we have an array of relevant **Keywords** directly traceable to the transcript."

### 4. Edge Cases & Wrap Up (2:45 - 3:30)
* **Visual**: Show a quick test where the `x-api-key` is disabled or missing. Hit send and show the `401 Unauthorized` error.
* **Audio**: 
> "We've also handled core edge cases. For instance, if an unauthorized user pings the API without the correct secret key, it instantly returns a 401 Unauthorized JSON response. 
> To summarize, our API meets all hackathon criteria: It processes base64 audio directly, safely validates JSON schemas for analytical extraction, accurately scores agent compliance in multiple languages, and is ready for production. Thank you!"

---

## 📤 Next Steps
1. **Record the Video**: Use Loom, OBS, or Microsoft Clipchamp (built into Windows 11).
2. **Upload**: Save the `.mp4` and upload it to Google Drive or YouTube.
3. **Permissions**: If using Google Drive, make sure the sharing settings are set to **"Anyone with the link can view."**
4. **Submit**: Paste the URL into the hackathon submission form.
