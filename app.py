import streamlit as st
from auth import (
    signup_user,
    login_user,
    save_history,
    get_history,
    get_single_history
)

import tempfile
import os
import glob
import subprocess
import whisper
import yt_dlp
import subprocess

from moviepy.editor import VideoFileClip
from transformers import pipeline


st.set_page_config(
    page_title="AI Video Summarizer Pro",
    page_icon="🎬",
    layout="wide"
)


if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""


# ================= LOGIN PAGE =================

if not st.session_state.logged_in:

    st.markdown("""
    <style>

    .login-container{
    max-width:450px;
    margin:auto;
    margin-top:60px;
    background:white;
    padding:40px;
    border-radius:25px;
    box-shadow:0px 4px 20px rgba(0,0,0,0.08);
    border:1px solid #dbeafe;
    }

    .login-title{
    text-align:center;
    font-size:45px;
    font-weight:800;
    color:#2563eb;
    margin-bottom:10px;
    }

    .login-subtitle{
    text-align:center;
    color:#444444;
    font-size:18px;
    margin-bottom:30px;
    }

    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="login-container">

    <div class="login-title">
    🎬 AI Video Summarizer Pro
    </div>

    <div class="login-subtitle">
    Secure Login Portal
    </div>

    </div>
    """, unsafe_allow_html=True)

    menu = st.selectbox(
        "🔐 Choose Option",
        ["Login", "Signup"]
    )

    username = st.text_input("👤 Username")

    password = st.text_input(
        "🔑 Password",
        type="password"
    )

    if menu == "Signup":

        if st.button("Create Account"):

            success = signup_user(
                username,
                password
            )

            if success:

                st.success(
                    "✅ Account Created Successfully"
                )

            else:

                st.error(
                    "⚠ Username Already Exists"
                )

    else:

        if st.button("Login"):

            user = login_user(
                username,
                password
            )

            if user:

                st.session_state.logged_in = True
                st.session_state.username = username

                st.rerun()

            else:

                st.error(
                    "❌ Invalid Username or Password"
                )

    st.stop()


# ================= MAIN UI =================

st.markdown("""
<style>

.stApp{
background: linear-gradient(to bottom right,#f8fbff,#e3f2fd);
}

h1,h2,h3,h4,p,label{
color:#111111 !important;
}

.main-title{
text-align:center;
font-size:55px;
font-weight:800;
color:#111111;
margin-top:10px;
}

.sub-title{
text-align:center;
font-size:20px;
color:#444444;
margin-bottom:30px;
}

.card{
background:white;
padding:25px;
border-radius:18px;
text-align:center;
box-shadow:0px 4px 15px rgba(0,0,0,0.08);
transition:0.3s;
border:1px solid #dbeafe;
cursor:pointer;
}

.card:hover{
transform:scale(1.03);
background:#dbeafe;
}

.box{
background:white;
padding:20px;
border-radius:18px;
margin-top:20px;
box-shadow:0px 4px 12px rgba(0,0,0,0.08);
border:1px solid #dbeafe;
}

.stButton>button{
width:100%;
background:#2563eb;
color:white;
border:none;
border-radius:12px;
height:50px;
font-size:18px;
font-weight:bold;
}

.stDownloadButton>button{
background:#2563eb !important;
color:white !important;
border-radius:10px;
}

input, textarea{
background:white !important;
color:black !important;
}

video{
border-radius:15px !important;
max-height:300px !important;
object-fit:contain !important;
background:#dbeafe !important;
}

</style>
""", unsafe_allow_html=True)


# ================= SIDEBAR =================

with st.sidebar:

    st.markdown("## 👤 User Panel")

    st.success(
        f"Welcome {st.session_state.username}"
    )

    st.write("")

    st.markdown("## 📜 History")

    history = get_history(
        st.session_state.username
    )

    if history:

        for item in history:

            history_id = item[0]
            video_name = item[2]

            if st.button(
                f"🎥 {video_name}",
                key=f"history_{history_id}"
            ):

                selected_history = get_single_history(
                    history_id
                )

                st.session_state.old_transcript = selected_history[3]
                st.session_state.old_summary = selected_history[4]

    else:

        st.write("No History Found")

    st.write("")

    if st.button("🚪 Logout"):

        st.session_state.logged_in = False
        st.session_state.username = ""

        st.rerun()


# ================= OLD HISTORY =================

if "old_summary" in st.session_state:

    st.markdown("""
    <div class="box">
    <h1>📜 Previous History</h1>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("## 📄 Transcript")

    st.write(
        st.session_state.old_transcript
    )

    st.markdown("## 🤖 Summary")

    st.success(
        st.session_state.old_summary
    )


# ================= HEADER =================

st.markdown("""
<div class="main-title">🎬 AI Video Summarizer Pro</div>

<div class="sub-title">
Smart AI Powered Video Summary Generator with Transcript, AI Summary & Chat
</div>
""", unsafe_allow_html=True)


# ================= OPTIONS =================

col1, col2 = st.columns(2)

with col1:

    language = st.selectbox(
        "🌍 Choose Language",
        ["English", "Hindi", "Hinglish"]
    )

with col2:

    summary_type = st.selectbox(
        "📝 Choose Summary Type",
        ["Short", "Detailed", "Bullet Points"]
    )


input_type = st.radio(
    "📥 Choose Input Type",
    ["Upload Video", "Paste YouTube URL"],
    horizontal=True
)

uploaded_file = None
youtube_url = ""


if input_type == "Upload Video":

    uploaded_file = st.file_uploader(
        "📤 Upload Your Video",
        type=["mp4", "mov", "avi"]
    )

else:

    youtube_url = st.text_input(
        "📎 Paste YouTube URL"
    )


generate = st.button(
    "✨ Generate AI Summary"
)


# ================= MODELS =================

@st.cache_resource
def load_whisper():

    return whisper.load_model("base")


@st.cache_resource
def load_summary_model():

    return pipeline(
        "summarization",
        model="facebook/bart-large-cnn"
    )


@st.cache_resource
def load_qa_model():

    return pipeline(
        "question-answering",
        model="distilbert-base-uncased-distilled-squad"
    )


whisper_model = load_whisper()

summarizer = load_summary_model()


# ================= MAIN PROCESS =================

if generate:

    video_path = ""
    audio_path = "audio.wav"
    is_youtube = False

    # ===== YOUTUBE URL =====

    if input_type == "Paste YouTube URL":

        if youtube_url.strip() == "":

            st.warning(
                "⚠ Please Enter YouTube URL"
            )

            st.stop()

        is_youtube = True

        with st.spinner(
            "📥 Downloading Audio from YouTube..."
        ):

            ydl_opts = {
                "format": "bestaudio/best",
                "outtmpl": "youtube_audio.%(ext)s",
                "quiet": False,
                "no_warnings": False,
                "postprocessors": [{
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "wav",
                    "preferredquality": "192",
                }]
            }

            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:

                    st.write("📍 Extracting audio track...")
                    info = ydl.extract_info(
                        youtube_url,
                        download=True
                    )

                    uploaded_name = info.get("title", "youtube_audio") + ".wav"
                    
                    # Find the downloaded audio file
                    audio_files = glob.glob("youtube_audio*")
                    
                    if audio_files:
                        audio_path = audio_files[0]
                        st.write(f"✅ Audio extracted: {audio_path}")
                        st.write(f"📍 Audio file size: {os.path.getsize(audio_path) / (1024*1024):.2f} MB")
                    else:
                        st.error("⚠ Audio extraction failed: no audio file found")
                        st.stop()
                            
            except Exception as e:
                st.error(f"⚠ YouTube download error: {str(e)}")
                st.stop()

    # ===== FILE UPLOAD =====

    elif uploaded_file is not None:

        uploaded_name = uploaded_file.name

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".mp4"
        ) as temp_video:

            temp_video.write(
                uploaded_file.read()
            )

            video_path = temp_video.name

    else:

        st.warning(
            "⚠ Please Upload Video First"
        )

        st.stop()

    # ================= VIDEO PREVIEW =================

    if not is_youtube:
        st.success(
            "✅ Video Ready Successfully"
        )

        st.markdown("""
        <div class="box">
        <h3>🎥 Video Preview</h3>
        </div>
        """, unsafe_allow_html=True)

        st.video(video_path)
    else:
        st.success(
            "✅ Audio Ready Successfully"
        )

    # ================= AUDIO EXTRACTION =================

    if not is_youtube:
        audio_path = "audio.wav"

        with st.spinner(
            "🎙 Extracting Transcript..."
        ):

            try:
                st.write("📍 Loading video file...")
                video = VideoFileClip(
                    video_path
                )
                st.write("✅ Video loaded successfully")
            except OSError as e:
                st.warning("⚠ MoviePy cannot read the file, attempting ffmpeg conversion...")
                
                converted_video = "youtube_video_converted.mp4"
                
                try:
                    st.write("📍 Converting video with ffmpeg...")
                    result = subprocess.run(
                        ["ffmpeg", "-i", video_path, "-c:v", "libx264", "-c:a", "aac", "-y", converted_video],
                        capture_output=True,
                        text=True,
                        timeout=300
                    )
                    
                    if result.returncode == 0 and os.path.exists(converted_video):
                        st.write("✅ Conversion successful")
                        video_path = converted_video
                        video = VideoFileClip(video_path)
                    else:
                        st.error(f"⚠ Conversion failed: {result.stderr}")
                        st.stop()
                        
                except subprocess.TimeoutExpired:
                    st.error("⚠ Conversion timed out")
                    st.stop()
                except Exception as convert_err:
                    st.error(f"⚠ Conversion error: {str(convert_err)}")
                    st.stop()

            try:
                st.write("📍 Extracting audio...")
                video.audio.write_audiofile(
                    audio_path,
                    logger=None,
                    verbose=False
                )
                st.write("✅ Audio extracted successfully")
            except Exception as e:
                st.error(f"⚠ Audio extraction failed: {str(e)}")
                st.stop()

    # ================= TRANSCRIPTION =================

    with st.spinner(
        "🎙 Transcribing Audio..."
    ):

        try:
            st.write("📍 Transcribing audio with Whisper...")
            result = whisper_model.transcribe(
                audio_path
            )
            transcript = result["text"]
            st.write("✅ Transcription completed")
        except Exception as e:
            st.error(f"⚠ Transcription failed: {str(e)}")
            st.stop()

    # ================= SUMMARY =================

    with st.spinner(
        "🤖 Generating AI Summary..."
    ):

        try:
            st.write("📍 Preparing text for summarization...")
            transcript_short = transcript[:2000]
            
            st.write("📍 Generating summary...")
            summary = summarizer(
                transcript_short,
                max_length=80,
                min_length=20,
                do_sample=False
            )
            st.write("✅ Summary generated")
            
            final_summary = summary[0]["summary_text"]
        except Exception as e:
            st.error(f"⚠ Summary generation failed: {str(e)}")
            st.stop()

    # ================= SAVE HISTORY =================

    save_history(
        st.session_state.username,
        uploaded_name,
        transcript,
        final_summary
    )

    # ================= LANGUAGE =================

    if language == "Hindi":

        final_summary = (
            "Hindi Summary:\n\n"
            + final_summary
        )

    elif language == "Hinglish":

        final_summary = (
            "Hinglish Summary:\n\n"
            + final_summary
        )

    else:

        final_summary = (
            "English Summary:\n\n"
            + final_summary
        )

    # ================= TRANSCRIPT =================

    st.markdown("""
    <div class="box">
    <h1>📄 Transcript</h1>
    </div>
    """, unsafe_allow_html=True)

    st.write(transcript)

    # ================= SUMMARY =================

    st.markdown("""
    <div class="box">
    <h1>🤖 AI Summary</h1>
    </div>
    """, unsafe_allow_html=True)

    st.success(final_summary)

    # ================= KEY POINTS =================

    st.markdown("""
    <div class="box">
    <h1>🔥 Key Moments</h1>
    </div>
    """, unsafe_allow_html=True)

    points = final_summary.split(".")

    for point in points[:5]:

        if point.strip() != "":

            st.write(
                "✅",
                point
            )

    # ================= DOWNLOAD =================

    col1, col2 = st.columns(2)

    with col1:

        st.download_button(
            "📄 Download Summary",
            final_summary,
            file_name="summary.txt"
        )

    with col2:

        st.download_button(
            "📥 Download Transcript",
            transcript,
            file_name="transcript.txt"
        )

    # ================= CHAT =================

    st.markdown("""
    <div class="box">
    <h1>💬 Chat With Video</h1>
    </div>
    """, unsafe_allow_html=True)

    question = st.text_input(
        "Ask Question From Video"
    )

    if question:

        try:
            with st.spinner("🔄 Loading QA Model..."):
                qa_model = load_qa_model()
            
            st.write("📍 Searching for answer in transcript...")
            
            # Truncate transcript if too long (QA model has token limit)
            context = transcript[:1024]
            
            answer = qa_model(
                question=question,
                context=context
            )
            
            st.success("✅ Answer Found")
            st.info(
                f"**Answer:** {answer['answer']}\n\n**Confidence:** {answer['score']*100:.1f}%"
            )
        except Exception as e:
            st.error(f"⚠ Could not find answer: {str(e)}")

    # ================= CLEANUP =================

    try:

        os.remove(video_path)

        os.remove(audio_path)

    except:

        pass