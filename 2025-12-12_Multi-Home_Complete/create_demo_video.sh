#!/bin/bash

# Crisis Friday Demo Video - Automated Production Script
# Uses macOS text-to-speech (British accent) + FFmpeg for video creation

set -e  # Exit on error

echo "🎬 Starting Crisis Friday Demo Video Production..."

# ============================================
# CONFIGURATION
# ============================================

OUTPUT_DIR="./demo_video_output"
AUDIO_DIR="$OUTPUT_DIR/audio"
VIDEO_DIR="$OUTPUT_DIR/video"
SCREENSHOTS_DIR="$OUTPUT_DIR/screenshots"
FINAL_VIDEO="$OUTPUT_DIR/crisis_friday_demo_FINAL.mp4"

# Create directories
mkdir -p "$AUDIO_DIR" "$VIDEO_DIR" "$SCREENSHOTS_DIR"

# British accent voice (macOS built-in)
# Options: Daniel (UK male), Kate (UK female), Serena (UK female)
VOICE="Daniel"

# ============================================
# CHECK DEPENDENCIES
# ============================================

echo "📦 Checking dependencies..."

if ! command -v ffmpeg &> /dev/null; then
    echo "❌ FFmpeg not found. Installing via Homebrew..."
    echo "Run: brew install ffmpeg"
    echo "Then re-run this script."
    exit 1
fi

if ! command -v say &> /dev/null; then
    echo "❌ macOS 'say' command not found (required for voiceover)"
    exit 1
fi

echo "✅ All dependencies installed"

# ============================================
# GENERATE VOICEOVER AUDIO FILES
# ============================================

echo "🎙️ Generating AI voiceover (British accent: $VOICE)..."

# Scene 2: The Problem (0:08 - 0:35)
say -v "$VOICE" -o "$AUDIO_DIR/scene2.aiff" --rate=160 \
"It's Friday afternoon. Our Early Warning System detected a critical shortage 14 days ago - tonight's night shift needs one additional Senior Support Care Worker. In the old system, a manager would spend 2 hours making phone calls. Watch what happens now with our executive platform."

# Scene 3: Automated Response (0:35 - 1:10)
say -v "$VOICE" -o "$AUDIO_DIR/scene3.aiff" --rate=160 \
"Here's what the system did automatically. 14 days ago, it sent OT offers to 12 qualified Senior Support Care Workers via email and SMS. Within 18 hours, 3 staff accepted. The shortage was resolved before any manager even knew about it. Zero manual intervention required."

# Scene 4: Budget Dashboard (1:10 - 1:55)
say -v "$VOICE" -o "$AUDIO_DIR/scene4.aiff" --rate=160 \
"Let's see the financial impact. Our Budget Dashboard shows we're £15,000 under budget year-to-date with an efficiency score of 87 out of 100. For tonight's shortage, the system chose OT at £180 instead of agency at £280 - saving £100 on just this one shift. And executives can export all this data to Excel with one click for board reports."

# Scene 5: Retention Predictor (1:55 - 2:35)
say -v "$VOICE" -o "$AUDIO_DIR/scene5.aiff" --rate=160 \
"But there's a problem. Our Retention Predictor shows Alice Smith is already at medium risk for leaving, with 16 OT hours this month. Tonight's shift pushes her to 24 hours - crossing into high-risk territory. The system automatically generates an intervention plan: block further OT requests for 2 weeks, offer a compensatory day off, and schedule a manager check-in. This is how we maintain our 18.5% turnover rate - below the industry benchmark of 20%."

# Scene 6: CI Performance Predictor (2:35 - 3:05)
say -v "$VOICE" -o "$AUDIO_DIR/scene6.aiff" --rate=160 \
"Here's why this matters to the Care Inspectorate. Our CI Performance Predictor forecasts a 'Very Good' rating - 82 out of 100. We rank 3rd out of 8 homes in our region and we're trending upward. Tonight's OT decision maintained our optimal skill mix ratio of 1 senior to 3.2 support staff. The system doesn't just fill shifts - it protects our CI rating."

# Scene 7: Training Compliance (3:05 - 3:35)
say -v "$VOICE" -o "$AUDIO_DIR/scene7.aiff" --rate=160 \
"Alice was eligible for tonight's OT because she's 100% training compliant. Our Training Dashboard tracks 47 certifications expiring in the next 6 months and provides a predictive booking calendar. We maintain 87% compliance - approaching our 95% target - and avoid costly CI penalties for expired certifications."

# Scene 8: Auto-Roster (3:35 - 4:05)
say -v "$VOICE" -o "$AUDIO_DIR/scene8.aiff" --rate=160 \
"And when it's time to build next week's roster, one click generates a complete draft using ML forecasts. Quality score: 94 out of 100. Fairness score: 91 - meaning shifts are distributed equitably. High confidence with no predicted shortages. Managers can review the color-coded preview and approve - cutting roster creation from 4 hours to 15 minutes."

# Scene 9: Results Summary (4:05 - 4:30)
say -v "$VOICE" -o "$AUDIO_DIR/scene9.aiff" --rate=160 \
"So what just happened? A Friday afternoon crisis was prevented 14 days in advance. We saved £100 on tonight's shift, managed retention risk, protected our CI rating, and the manager spent zero time on it. This is the executive platform - traffic light dashboards, automated decision-making, and one-click reporting to the board."

echo "✅ Voiceover audio generated (8 scenes)"

# Convert AIFF to MP3 for compatibility
echo "🔄 Converting audio files to MP3..."
for aiff in "$AUDIO_DIR"/*.aiff; do
    mp3="${aiff%.aiff}.mp3"
    ffmpeg -i "$aiff" -acodec libmp3lame -ab 192k "$mp3" -y -loglevel error
    rm "$aiff"  # Remove original AIFF
done

echo "✅ Audio conversion complete"

# ============================================
# CREATE TITLE CARDS (TEXT-BASED SCENES)
# ============================================

echo "🎨 Creating title cards..."

# Scene 1: Opening Title (0:00 - 0:08)
ffmpeg -f lavfi -i color=c=black:s=1920x1080:d=8 \
    -vf "drawtext=fontfile=/System/Library/Fonts/Supplemental/Arial.ttf:text='Staff Rota Management System':fontcolor=white:fontsize=72:x=(w-text_w)/2:y=(h-text_h)/2-100, \
         drawtext=fontfile=/System/Library/Fonts/Supplemental/Arial.ttf:text='Executive Platform Demo':fontcolor=white:fontsize=48:x=(w-text_w)/2:y=(h-text_h)/2, \
         drawtext=fontfile=/System/Library/Fonts/Supplemental/Arial.ttf:text='Crisis Friday Scenario':fontcolor=white:fontsize=36:x=(w-text_w)/2:y=(h-text_h)/2+100" \
    -pix_fmt yuv420p "$VIDEO_DIR/scene1_title.mp4" -y -loglevel error

# Scene 10: Closing Card (4:30 - 4:35)
ffmpeg -f lavfi -i color=c=black:s=1920x1080:d=5 \
    -vf "drawtext=fontfile=/System/Library/Fonts/Supplemental/Arial.ttf:text='Staff Rota Management System':fontcolor=white:fontsize=60:x=(w-text_w)/2:y=(h-text_h)/2-150, \
         drawtext=fontfile=/System/Library/Fonts/Supplemental/Arial.ttf:text='18 AI Features | £590K Annual ROI':fontcolor=white:fontsize=42:x=(w-text_w)/2:y=(h-text_h)/2-60, \
         drawtext=fontfile=/System/Library/Fonts/Supplemental/Arial.ttf:text='Executive Dashboards Included':fontcolor=white:fontsize=36:x=(w-text_w)/2:y=(h-text_h)/2+20, \
         drawtext=fontfile=/System/Library/Fonts/Supplemental/Arial.ttf:text='Ready for Scotland-Wide Rollout':fontcolor=limegreen:fontsize=48:x=(w-text_w)/2:y=(h-text_h)/2+120" \
    -pix_fmt yuv420p "$VIDEO_DIR/scene10_closing.mp4" -y -loglevel error

echo "✅ Title cards created"

# ============================================
# INSTRUCTIONS FOR SCREEN RECORDINGS
# ============================================

echo ""
echo "⚠️  MANUAL STEP REQUIRED: SCREEN RECORDINGS"
echo ""
echo "I've generated the voiceover audio. Now you need to record your screen:"
echo ""
echo "1. Start your Django server:"
echo "   cd /path/to/staff-rota-system"
echo "   python manage.py runserver"
echo ""
echo "2. Open QuickTime Player → File → New Screen Recording"
echo ""
echo "3. Record these 7 scenes (play the audio files to guide your timing):"
echo ""
echo "   Scene 2 (27 sec): Navigate to Early Warning Dashboard"
echo "   Audio: $AUDIO_DIR/scene2.mp3"
echo "   Save as: $SCREENSHOTS_DIR/scene2_screen.mov"
echo ""
echo "   Scene 3 (35 sec): Show Automated Mitigation Log"
echo "   Audio: $AUDIO_DIR/scene3.mp3"
echo "   Save as: $SCREENSHOTS_DIR/scene3_screen.mov"
echo ""
echo "   Scene 4 (45 sec): Budget Dashboard walkthrough"
echo "   Audio: $AUDIO_DIR/scene4.mp3"
echo "   Save as: $SCREENSHOTS_DIR/scene4_screen.mov"
echo ""
echo "   Scene 5 (40 sec): Retention Predictor + Alice Smith"
echo "   Audio: $AUDIO_DIR/scene5.mp3"
echo "   Save as: $SCREENSHOTS_DIR/scene5_screen.mov"
echo ""
echo "   Scene 6 (30 sec): CI Performance Dashboard"
echo "   Audio: $AUDIO_DIR/scene6.mp3"
echo "   Save as: $SCREENSHOTS_DIR/scene6_screen.mov"
echo ""
echo "   Scene 7 (30 sec): Training Compliance Dashboard"
echo "   Audio: $AUDIO_DIR/scene7.mp3"
echo "   Save as: $SCREENSHOTS_DIR/scene7_screen.mov"
echo ""
echo "   Scene 8 (30 sec): Auto-Roster Generator"
echo "   Audio: $AUDIO_DIR/scene8.mp3"
echo "   Save as: $SCREENSHOTS_DIR/scene8_screen.mov"
echo ""
echo "   Scene 9 (25 sec): Results Summary"
echo "   Audio: $AUDIO_DIR/scene9.mp3"
echo "   Save as: $SCREENSHOTS_DIR/scene9_screen.mov"
echo ""
echo "4. After recording all scenes, run:"
echo "   ./create_demo_video.sh --assemble"
echo ""
echo "Audio files ready in: $AUDIO_DIR/"
echo "Save screen recordings to: $SCREENSHOTS_DIR/"
echo ""

# ============================================
# ASSEMBLE FINAL VIDEO (run with --assemble)
# ============================================

if [ "$1" == "--assemble" ]; then
    echo ""
    echo "🎬 Assembling final video..."
    
    # Check if screen recordings exist
    MISSING_FILES=0
    for i in {2..9}; do
        if [ ! -f "$SCREENSHOTS_DIR/scene${i}_screen.mov" ]; then
            echo "❌ Missing: $SCREENSHOTS_DIR/scene${i}_screen.mov"
            MISSING_FILES=1
        fi
    done
    
    if [ $MISSING_FILES -eq 1 ]; then
        echo "❌ Please record all screen scenes first (see instructions above)"
        exit 1
    fi
    
    # Add audio to each screen recording
    echo "🔊 Adding voiceover to screen recordings..."
    for i in {2..9}; do
        ffmpeg -i "$SCREENSHOTS_DIR/scene${i}_screen.mov" \
               -i "$AUDIO_DIR/scene${i}.mp3" \
               -c:v copy -c:a aac -map 0:v:0 -map 1:a:0 \
               "$VIDEO_DIR/scene${i}_final.mp4" -y -loglevel error
        echo "✅ Scene $i processed"
    done
    
    # Create concat list
    echo "📝 Creating video sequence..."
    cat > "$OUTPUT_DIR/concat_list.txt" <<EOF
file 'video/scene1_title.mp4'
file 'video/scene2_final.mp4'
file 'video/scene3_final.mp4'
file 'video/scene4_final.mp4'
file 'video/scene5_final.mp4'
file 'video/scene6_final.mp4'
file 'video/scene7_final.mp4'
file 'video/scene8_final.mp4'
file 'video/scene9_final.mp4'
file 'video/scene10_closing.mp4'
EOF
    
    # Concatenate all scenes
    echo "🎞️ Concatenating all scenes..."
    ffmpeg -f concat -safe 0 -i "$OUTPUT_DIR/concat_list.txt" \
           -c copy "$FINAL_VIDEO" -y -loglevel error
    
    echo ""
    echo "✅ VIDEO COMPLETE!"
    echo ""
    echo "📹 Final video: $FINAL_VIDEO"
    echo "📊 File size: $(du -h "$FINAL_VIDEO" | cut -f1)"
    echo ""
    echo "🎉 Your Crisis Friday demo video is ready for presentation!"
    echo ""
    
    # Create compressed version for email
    echo "📦 Creating compressed version for email..."
    ffmpeg -i "$FINAL_VIDEO" \
           -vcodec libx264 -crf 28 -preset fast \
           "$OUTPUT_DIR/crisis_friday_demo_COMPRESSED.mp4" -y -loglevel error
    
    echo "✅ Compressed version: $OUTPUT_DIR/crisis_friday_demo_COMPRESSED.mp4"
    echo "   Size: $(du -h "$OUTPUT_DIR/crisis_friday_demo_COMPRESSED.mp4" | cut -f1)"
    echo ""
fi

echo "🎬 Script complete!"
