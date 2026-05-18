#!/usr/bin/env python3
"""语音转文字 - 使用 SiliconFlow SenseVoice API"""
import sys, subprocess, tempfile, os, json, urllib.request

API_KEY = "sk-kgsuhpdtuiwbyfjfsdvlkyffbfubvlbapkdnulvbobpoftmp"
API_URL = "https://api.siliconflow.cn/v1/audio/transcriptions"

def transcribe(audio_path):
    # Convert to wav if needed
    ext = os.path.splitext(audio_path)[1].lower()
    if ext != '.wav':
        wav_path = tempfile.mktemp(suffix='.wav')
        subprocess.run(['ffmpeg', '-i', audio_path, wav_path, '-y'], 
                      capture_output=True, timeout=30)
    else:
        wav_path = audio_path
    
    # Call SiliconFlow API
    import subprocess as sp
    result = sp.run([
        'curl', '-s', '-X', 'POST', API_URL,
        '-H', f'Authorization: Bearer {API_KEY}',
        '-F', 'model=FunAudioLLM/SenseVoiceSmall',
        '-F', f'file=@{wav_path}'
    ], capture_output=True, text=True, timeout=30)
    
    # Clean up
    if ext != '.wav' and os.path.exists(wav_path):
        os.remove(wav_path)
    
    data = json.loads(result.stdout)
    return data.get('text', '')

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法: python3 stt.py <audio_file>")
        sys.exit(1)
    text = transcribe(sys.argv[1])
    print(text)
