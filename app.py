import pytube
import ffmpeg
from pytube import YouTube
import os
import subprocess
import json
from flask import request, jsonify
from flask import Flask, render_template
from flask import Flask
from flask_cors import CORS
from flask import Flask, send_from_directory
from flask import send_from_directory, make_response
import re
import time
from datetime import datetime, timedelta
from flask_apscheduler import APScheduler
import subprocess



application = Flask(__name__)
scheduler = APScheduler()

CORS(application)
application.static_folder = 'static'



def delete30minutesOldFiles():

    print("In delete30minutesOldFiles")

    current_dir = os.getcwd()
    max_age = 30 * 60

    now = time.time()
    for filename in os.listdir(current_dir):
        file_path = os.path.join(current_dir, filename)
        if filename.endswith(".mp4"):
            file_creation_time = os.path.getctime(file_path)
            file_age = now - file_creation_time
            if file_age > max_age:
                os.remove(file_path)
                print(f"Deleted {filename}")

delete30minutesOldFiles()
def download_video(url, video_filename, quality):
    yt = YouTube(url)
    video_stream = yt.streams.filter(res=quality, mime_type="video/mp4", progressive=False).first()
    video_stream.download(filename=video_filename)
    return video_filename
    
def download_video2(url, filename):
    if os.path.exists(filename):
        os.remove(filename)  # Remove the file if it already exists
    yt = YouTube(url)
    video = yt.streams.filter(file_extension='mp4').first()
    video.download(filename=filename) 


def bytes_to_mb(size_in_bytes):
    try:
        if isinstance(size_in_bytes, (int, float)):
            size_in_mb = size_in_bytes / (1024 * 1024)
            return str(round(size_in_mb, 2)) + "MB"
        else:
            return "Null"
    except Exception as e:
        return "Null"
    
def list_available_resolutions(url):
    try:      
        yt = YouTube(url)
    # Fetch all streams with file extension 'mp4'
        streams = yt.streams.filter(file_extension='mp4').order_by('resolution')
        # Initialize an empty dictionary to store resolution details
        resolution_details = {}
        
        for stream in streams:
            if stream.resolution not in resolution_details:
                resolution_details[stream.resolution] = {
                    "filesize": stream.filesize,
                    "has_audio": stream.includes_audio_track,  # Check if the stream includes an audio track
                    "format_id": stream.itag  # Include format id
                }
        
        # Sort the resolutions in descending order
        sorted_resolutions = sorted(resolution_details.items(), key=lambda x: int(x[0][:-1]), reverse=True)
        
        title = yt.title
        thumbnail_url = yt.thumbnail_url
        video_details = [{
            "resolution": resolution,
            "filesize": bytes_to_mb(details["filesize"]),
            "has_audio": details["has_audio"],
            "format_id": None,
            "title": title,
            "thumbnail": thumbnail_url,
            "icon": "/Videos/images/mp4.png",
            "need_format_id": False
        } for resolution, details in sorted_resolutions]
        
        json_string = json.dumps(video_details, indent=4)
        return json_string
    except Exception as e:
        try:
            print("Hbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb")
            return list_available_resolutions_for_restricted_content(url)
        except Exception as e:
            return {
              "status" : False,
              "message": str(e)

            }



def list_available_resolutions_for_restricted_content(url):
    desired_format_notes = ["240p", "360p", "720p", "1080p"]
    process = subprocess.run(['yt-dlp', '-j', url], capture_output=True, text=True)
    if process.returncode == 0:
        try:
            video_info = json.loads(process.stdout)
            formats = video_info.get('formats', [])
            thumbnail_url = video_info.get('thumbnail', '')
            title  = video_info.get('title', '')

            format_details = []

            filtered_formats = [format for format in formats if (format.get("format_note") in desired_format_notes and format.get("acodec") != 'none')]

            for format in filtered_formats:
                detail = {
                    "format_id": format.get("format_id"),
                    "resolution": format.get("format_note"),
                    "filesize": bytes_to_mb(format.get("filesize")),
                    "thumbnail": thumbnail_url,
                    "title": title,
                    "icon": "/Videos/images/mp4.png",

                    "need_format_id": True,
                    "has_audio": True,
                }
                format_details.append(detail)
            formats_json = json.dumps(format_details, indent=4)
            print(formats_json)
            return str(formats_json)
        except json.JSONDecodeError as e:
            return str(e)
    else:
        return {
              "status" : False,
              "message": "Something went wrong"

            }

def get_title_and_thumbnail(video_url):
    yt = YouTube(video_url)
    title = yt.title
    thumbnail_url = yt.thumbnail_url
    print("Title:", title)
    print("Thumbnail URL:", thumbnail_url)

def download_video3(url, filename, resolution):
    if os.path.exists(filename):
        os.remove(filename)  

    yt = YouTube(url)

    video = yt.streams.filter(progressive=True, file_extension='mp4', resolution=resolution).first()
    if video:
        video.download(filename=filename)
        print(f"Video downloaded successfully")
    else:
        print(f"Failed to download video: No stream available for resolution {resolution}.")

def dowload_ag_restrcited_videos(url):
    print("g")


def download_video_which_doesnt_have_audio(url, filename, quality):
    try:
        yt = YouTube(url)
        #video_stream = yt.streams.filter(res="1080p", mime_type="video/mp4", progressive=False).first()
        video_stream = yt.streams.filter(res=quality, mime_type="video/mp4", progressive=False).first()
        video_filename = f"{filename}_video.mp4"
        video_stream.download(filename=video_filename)
        audio_stream = yt.streams.filter(only_audio=True).first()
        audio_filename = f"{filename}_audio.mp4"
        audio_stream.download(filename=audio_filename)
        output_filename = f"{filename}_{quality}.mp4"
        ffmpeg_command = f"ffmpeg -i ~/{video_filename} -i ~/{audio_filename} -c:v copy -c:a aac ~/{output_filename}"
        subprocess.run(ffmpeg_command, shell=True)
        #os.remove(video_filename)
        os.remove(audio_filename)
        
        print(f"Full HD video downloaded and merged successfully: {output_filename}")

        return output_filename
    except Exception as e:
        print(e)
        return ""

# Example usage
#url = "https://www.youtube.com/watch?v=RFcZoDqJPvY"
#print(list_available_resolutions(url))
#print("Available resolutions:", resolutions)
#download_full_hd("https://www.youtube.com/watch?v=RFcZoDqJPvY", "kasb.mp4")
# Let's assume the user selects a resolution, for example, the highest one
#selected_resolution = resolutions[-1]  # highest resolution
#print(f"Downloading video in {selected_resolution} resolution...")
#download_video3(url, "my_video.mp4", selected_resolution)

#get_title_and_thumbnail(url)

import subprocess

def clean_string(input_string):
    # Trim leading and trailing spaces
    trimmed_string = input_string.strip()
    
    # Remove special characters, except for spaces and alphanumeric characters
    cleaned_string = re.sub('[^A-Za-z0-9 ]+', '', trimmed_string)
    
    return cleaned_string.replace(" ", "_")

def dowload_age_restricted_videos(url, format_id, output_filename):
    command = ['yt-dlp', '-f', str(format_id), url]
    if output_filename:
        command += ['-o', output_filename]
    result = subprocess.run(command, capture_output=True, text=True)

    if result.returncode == 0:
        print("Download successful")
        return output_filename
    else:
        print("Download failed:", result.stderr)
        return ""


# Run yt-dlp with the specified format option
#result = subprocess.run(['yt-dlp', '-f', format_option, url], capture_output=True, text=True)

# Check the output and error
#if result.returncode == 0:
#    print("Download successful")
#else:
#   print("Error downloading video:", result.stderr)



#subprocess.run(['yt-dlp', url])
#download_video(url, "kgf.mp4")



def dowloadTrimmedVideo(start_time, end_time, filename):
    start_time = start_time  # For example, starting at 30 seconds
    duration = end_time   # For a duration of 10 seconds

    # Use ffmpeg to trim the video
    subprocess.run([
        'ffmpeg',
        '-i', filename,  # Input file
        '-ss', start_time,             # Start time
        '-t', duration,                # Duration
        '-c', 'copy',                  # Copy the stream to avoid re-encoding
        'trimmed' + str(filename)            # Output file
    ])

    return 'trimmed' + str(filename)  

def getAllResolutionsUsingYbdl(url):
    subprocess.run(['yt-dlp', '-F', url])

@application.route("/download/fullhd", methods=[ 'GET', 'POST'])
def dowloadFullHd():
    current_epoch_time = time.time()
    decoded_token = ""
    token = request.headers.get('url')
    name = request.headers.get('filename')
    name = name + "_"+ str(current_epoch_time)
    res = request.headers.get('resolution')
    format_id = request.headers.get('formatid')
    hasAudio = request.headers.get('hasAudio')
    print("format_id :::::::::::" + str(format_id))
    fileLink = ""
    if(format_id == None or format_id == 'null'):
        if(str(hasAudio) == "true"):
            print("has audio" + str(hasAudio))
            fileLink = download_video(token, name + ".mp4", res)
        else:
            fileLink = download_video_which_doesnt_have_audio(token, clean_string(name), str(res))
    else:
        fileLink = dowload_age_restricted_videos(token, int(format_id), name + ".mp4")

    return {
      "videolink" : fileLink
    }

@application.route("/download/trimmed", methods=[ 'GET', 'POST'])
def downloadtrimmed():
    start_time = request.headers.get('starttime')
    end_time = request.headers.get('endtime')
    hasAudio = request.headers.get('filename')
    fileLink = dowloadTrimmedVideo(start_time, end_time, filename)
    return {
      "videolink" : fileLink
    }

@application.route("/get/download/options", methods=[ 'GET', 'POST'])
def getLatestMoviesroute():
    try:
        
        decoded_token = ""
        token = request.headers.get('url')
        print("Received Token:", token)
        return list_available_resolutions(token)
    except Exception as e:
        return {'status': 'error', 'message': 'Something went wrong', 'error': str(e)}, 500

@application.route('/Videos/<filename>')
def get_video(filename):
    response = send_from_directory('videos', filename)
    return response

@application.route('/Videos/images/<filename>')
def get_image(filename):
    directory = ''
    response = send_from_directory(directory, filename)
    
    # Modify the response to add the Content-Disposition header
    response.headers['Content-Disposition'] = 'attachment; filename={}'.format(filename)
    
    return response

@application.route("/", methods=['GET'])
def main():
    return render_template('youtubedowloader1.html')


if __name__ == "__main__":
    scheduler.add_job(id='Scheduled Task', func=delete30minutesOldFiles, trigger='interval', minutes=30)
    scheduler.start()
    application.debug = True
    application.run()