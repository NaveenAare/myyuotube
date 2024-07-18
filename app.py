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
import requests
import threading


application = Flask(__name__)
scheduler = APScheduler()

CORS(application)
application.static_folder = 'static'




def delete30minutesOldFiles():
    try:
        print("In delete_mp4_files_in_current_directory")

        current_directory = os.getcwd()
        max_age = 5 * 60  # 30 minutes in seconds

        now = time.time()
        for filename in os.listdir(current_directory):
            if filename.endswith(".mp4"):
                file_path = os.path.join(current_directory, filename)
                if os.path.isfile(file_path):
                    file_creation_time = os.path.getctime(file_path)
                    file_age = now - file_creation_time
                    if file_age > max_age:
                        os.remove(file_path)
                        print(f"Deleted {filename}")
    except Exception as e:
        print(f"Exception: {e}")

#delete30minutesOldFiles()
def download_video(url, video_filename, quality):
    yt = YouTube(url)
    video_stream = yt.streams.filter(res=quality, mime_type="video/mp4", progressive=False).first()
    video_stream.download(filename=video_filename)
    return video_filename
    

def checkFileExistence(filename):
    if os.path.exists(filename):
        os.remove(filename)


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
        streams = yt.streams.filter(file_extension='mp4').order_by('resolution')
        resolution_details = {}
        
        for stream in streams:
            if stream.resolution not in resolution_details:
                resolution_details[stream.resolution] = {
                    "filesize": stream.filesize,
                    "has_audio": stream.includes_audio_track,  # Check if the stream includes an audio track
                    "format_id": stream.itag  # Include format id
                }
        
        sorted_resolutions = []
        sorted_resolutions = sorted(resolution_details.items(), key=lambda x: int(x[0][:-1]), reverse=True)
        
        title = yt.title
        thumbnail_url = yt.thumbnail_url

        duration_seconds = yt.length

        if(duration_seconds > 300):
            filtered_formatsss = []
            for resolution, format in sorted_resolutions:
                print(format)
                if(format["has_audio"]):
                    filtered_formatsss.append((resolution, format))
                sorted_resolutions = filtered_formatsss
            #sorted_resolutions = [format for format in sorted_resolutions if (format["has_audio"])]




        print(f"The duration of the video is {duration_seconds} seconds.")


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
        sorted_video_details = sorted(video_details, key=lambda x: not x['has_audio'])

        json_string = json.dumps(sorted_video_details, indent=4)
        return json_string
    except Exception as e:
        try:
            print(f"Hbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb  {e}")
            return list_available_resolutions_for_restricted_content(url)
        except Exception as e:
            return {
              "status" : False,
              "message": str(e)

            }



def getAudioStatus(value):
    return value != "none"

def filter_unique_resolutionssss(formats):
    seen_resolutions = set()
    unique_formats = []
    for format in formats:
        resolution = format.get("resolution")
        if resolution not in seen_resolutions:
            seen_resolutions.add(resolution)
            unique_formats.append(format)
    return unique_formats

def filter_unique_resolutions(formats):
    seen_resolutions = set()
    unique_formats = []
    
    for format in formats:
        resolution = format.get("resolution")
        has_audio = format.get("has_audio")
        
        if resolution not in seen_resolutions or has_audio:
            if not has_audio:
                seen_resolutions.add(resolution)
            unique_formats.append(format)
    print(formats)
    
    return unique_formats



def list_available_resolutions_for_restricted_content(url):
    print("in age res")
    desired_format_notes = ["240p", "360p", "480p", "720p", "1080p"]
    cookies_file = 'cookises.txt'
    if os.path.exists(cookies_file):
        print(f"Cookies file '{cookies_file}' exists.")
    
        with open(cookies_file, 'r') as file:
            lines = file.readlines()
            print("Cookies file content preview (first 10 lines):")
            for line in lines[:10]:  # Print only the first 10 lines for preview
                print(line.strip())
    else:
        print(f"Cookies file '{cookies_file}' does not exist or is not accessible.")
        return {
              "status" : False,
              "message": "No file"

            }
    process = subprocess.run(['yt-dlp','--cookies', cookies_file, '-j', url], capture_output=True, text=True)
    print(process.stderr)
    errror = ""
    if process.returncode == 0:
        try:
            video_info = json.loads(process.stdout)
            formats = video_info.get('formats', [])
            thumbnail_url = video_info.get('thumbnail', '')
            title  = video_info.get('title', '')


            duration = video_info.get('duration', '')

            print(f"The duration of the video is {duration} seconds.")


            format_details = []

            if(duration > 900):
                filtered_formats = [format for format in formats if (format.get("format_note") in desired_format_notes and getAudioStatus(format.get("acodec")))]
                filtered_formats = filtered_formats[::-1]
            else:
                filtered_formats = [format for format in formats if (format.get("format_note") in desired_format_notes)]



            for format in filtered_formats:
                detail = {
                    "format_id": format.get("format_id"),
                    "resolution": format.get("format_note"),
                    "filesize": bytes_to_mb(format.get("filesize")),
                    "thumbnail": thumbnail_url,
                    "title": title,
                    "icon": "/Videos/images/mp4.png",
                    "need_format_id": True,
                    "has_audio": getAudioStatus(format.get("acodec")),
                }
                format_details.append(detail)
            reversed_unique_formats = sorted(filter_unique_resolutions(format_details), key=lambda x: not x['has_audio'])
            reversed_unique_formats1 = sorted(format_details, key=lambda x: not x['has_audio'])

            formats_json = json.dumps(reversed_unique_formats, indent=4)
            print(formats_json)
            return str(formats_json)
        except json.JSONDecodeError as e:
            errror = str(e)
            return str(e)
    else:
        return {
              "status" : False,
              "message": str(process.stderr)

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


def download_audio(url, filename):
    try:
        yt = YouTube(url)
        audio_stream = yt.streams.filter(only_audio=True).first()
        audio_filename = f"{filename}_audio.mp3"
        audio_stream.download(filename=audio_filename)
        return audio_filename
    except:
        return ""

def download_video_which_doesnt_have_audio(url, filename, quality):
    try:
        print("in without audio")
        yt = YouTube(url)
        #video_stream = yt.streams.filter(res="1080p", mime_type="video/mp4", progressive=False).first()
        video_stream = yt.streams.filter(res=quality, mime_type="video/mp4", progressive=False).first()
        video_filename = f"{filename}_video.mp4"
        video_stream.download(filename=video_filename)
        audio_stream = yt.streams.filter(only_audio=True).first()
        audio_filename = f"{filename}_audio.mp4"
        audio_stream.download(filename=audio_filename)
        output_filename = f"{filename}_{quality}.mp4"
        checkFileExistence(output_filename)
        ffmpeg_command = f"ffmpeg -i {video_filename} -i {audio_filename} -c:v copy -c:a aac {output_filename}"

        #video_clip = VideoFileClip(video_filename)
        #audio_clip = AudioFileClip(audio_filename)

        #final_clip = video_clip.set_audio(audio_clip)

        #final_clip.write_videofile(output_filename, codec="libx264", audio_codec="aac")
        #os.remove(video_filename)
        #os.remove(audio_filename)

          
        result = subprocess.run(ffmpeg_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        if result.returncode == 0:
            print("FFmpeg command executed successfully")
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

def audioForallVideos(url, output_filename):
    try:
        commandToDownloadAudio = ['yt-dlp', '-f', 'bestaudio', '--extract-audio', '--audio-format', 'mp3', url]
        if output_filename:
            commandToDownloadAudio += ['-o', output_filename.replace(".mp4", "audio_")]
        result = subprocess.run(commandToDownloadAudio, capture_output=True, text=True)

        print(f"Download successful  ${output_filename}")
        audifilename = output_filename.replace(".mp4", "audio_.mp3")
        return audifilename+ ".mp3"
    except Exception as e:
        print(str(e))
        return ""

    

def dowload_age_restricted_videos_having_without_audio(url, format_id, output_filename):
    print("In age rest without audio")
    command = ['yt-dlp', '-f', str(format_id), url]
    commandToDownloadAudio = ['yt-dlp', '-f', 'bestaudio', '--extract-audio', '--audio-format', 'mp3', url]

    if output_filename:
        command += ['-o', output_filename]
        commandToDownloadAudio += ['-o', output_filename.replace(".mp4", "audio_")]
    result = subprocess.run(command, capture_output=True, text=True)
    result = subprocess.run(commandToDownloadAudio, capture_output=True, text=True)

    print(f"Download successful  ${output_filename}")
    audifilename = output_filename.replace(".mp4", "audio_.mp3")
    ooutputfilename = output_filename.replace(".mp4", "_1.mp4")
    ffmpeg_command = f"ffmpeg -i {output_filename} -i {audifilename} -c:v copy -c:a aac {ooutputfilename}"

    result = subprocess.run(ffmpeg_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    if result.returncode == 0:
        

        #video_clip = VideoFileClip(output_filename)
        #audio_clip = AudioFileClip()

        #final_clip = video_clip.set_audio(audio_clip)

        #final_clip.write_videofile(output_filename.replace(".mp4", "_1.mp4"), codec="libx264", audio_codec="aac")
        print("FFmpeg command executed successfully")
        return ooutputfilename
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



def increment_counter_error_byDate():
    # Get the current date in YYYY-MM-DD format
    current_date = datetime.now().strftime('%Y-%m-%d')
    url = f"https://videos-downloader-13024-default-rtdb.asia-southeast1.firebasedatabase.app/Error_Count/{current_date}.json"

    try:
        # GET request to check the current value of the counter
        response = requests.get(url, timeout=0.1)  # Timeout set to 100 milliseconds
        if response.status_code == 200:
            count = response.json()
            if count is None:
                count = 0
            new_count = count + 1

            # PUT request to update the counter value
            put_response = requests.put(url, json=new_count, timeout=0.5)  # Timeout for PUT request as well
            if put_response.status_code == 200:
                print(f"Counter updated successfully: {new_count}")
            else:
                print(f"Failed to update counter: {put_response.status_code}")
        else:
            print(f"Failed to get current count: {response.status_code}")
    except requests.exceptions.Timeout:
        print("The request timed out")
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")

def increment_counter_Success_rate_byDate():
    # Get the current date in YYYY-MM-DD format
    current_date = datetime.now().strftime('%Y-%m-%d')
    url = f"https://videos-downloader-13024-default-rtdb.asia-southeast1.firebasedatabase.app/Success_downloads/{current_date}.json"

    try:
        # GET request to check the current value of the counter
        response = requests.get(url, timeout=0.2)  # Timeout set to 100 milliseconds
        if response.status_code == 200:
            count = response.json()
            if count is None:
                count = 0
            new_count = count + 1

            # PUT request to update the counter value
            put_response = requests.put(url, json=new_count, timeout=0.5)  # Timeout for PUT request as well
            if put_response.status_code == 200:
                print(f"Counter updated successfully: {new_count}")
            else:
                print(f"Failed to update counter: {put_response.status_code}")
        else:
            print(f"Failed to get current count: {response.status_code}")
    except requests.exceptions.Timeout:
        print("The request timed out")
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")



def increment_counter_byDate():
    # Get the current date in YYYY-MM-DD format
    current_date = datetime.now().strftime('%Y-%m-%d')
    url = f"https://videos-downloader-13024-default-rtdb.asia-southeast1.firebasedatabase.app/Count/{current_date}.json"

    try:
        # GET request to check the current value of the counter
        response = requests.get(url, timeout=0.1)  # Timeout set to 100 milliseconds
        if response.status_code == 200:
            count = response.json()
            if count is None:
                count = 0
            new_count = count + 1

            # PUT request to update the counter value
            put_response = requests.put(url, json=new_count, timeout=0.5)  # Timeout for PUT request as well
            if put_response.status_code == 200:
                print(f"Counter updated successfully: {new_count}")
            else:
                print(f"Failed to update counter: {put_response.status_code}")
        else:
            print(f"Failed to get current count: {response.status_code}")
    except requests.exceptions.Timeout:
        print("The request timed out")
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")

def increment_counter_forAudio_byDate():
    # Get the current date in YYYY-MM-DD format
    current_date = datetime.now().strftime('%Y-%m-%d')
    url = f"https://videos-downloader-13024-default-rtdb.asia-southeast1.firebasedatabase.app/Count_audio/{current_date}.json"

    try:
        # GET request to check the current value of the counter
        response = requests.get(url, timeout=0.1)  # Timeout set to 100 milliseconds
        if response.status_code == 200:
            count = response.json()
            if count is None:
                count = 0
            new_count = count + 1

            # PUT request to update the counter value
            put_response = requests.put(url, json=new_count, timeout=0.5)  # Timeout for PUT request as well
            if put_response.status_code == 200:
                print(f"Counter updated successfully: {new_count}")
            else:
                print(f"Failed to update counter: {put_response.status_code}")
        else:
            print(f"Failed to get current count: {response.status_code}")
    except requests.exceptions.Timeout:
        print("The request timed out")
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")


def increment_counter():
    url = "https://videos-downloader-13024-default-rtdb.asia-southeast1.firebasedatabase.app/Count.json"
    try:
        response = requests.get(url, timeout=0.1)  # Timeout set to 100 milliseconds
        if response.status_code == 200:
            count = response.json()
            if count is None:
                count = 0
            new_count = count + 1
            put_response = requests.put(url, json=new_count, timeout=0.5)  # Timeout for PUT request as well
            if put_response.status_code == 200:
                print(f"Counter updated successfully: {new_count}")
            else:
                print(f"Failed to update counter: {put_response.status_code}")
        else:
            print(f"Failed to get current count: {response.status_code}")
    except requests.exceptions.Timeout:
        print("The request timed out")
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")


def increment_counter_audio():
    url = "https://videos-downloader-13024-default-rtdb.asia-southeast1.firebasedatabase.app/Count_audio.json"
    try:
        response = requests.get(url, timeout=0.1)  # Timeout set to 100 milliseconds
        if response.status_code == 200:
            count = response.json()
            if count is None:
                count = 0
            new_count = count + 1
            put_response = requests.put(url, json=new_count, timeout=0.5)  # Timeout for PUT request as well
            if put_response.status_code == 200:
                print(f"Counter updated successfully: {new_count}")
            else:
                print(f"Failed to update counter: {put_response.status_code}")
        else:
            print(f"Failed to get current count: {response.status_code}")
    except requests.exceptions.Timeout:
        print("The request timed out")
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")




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

@application.route("/download/audio", methods=[ 'GET', 'POST'])
def dowloadAudio():
    try:
        increment_counter_forAudio_byDate()
    except:
        print("except audio")
    current_epoch_time = time.time()
    decoded_token = ""
    token = request.headers.get('url')
    token = token.split("&")[0]
    name = request.headers.get('filename')
    name = name + "_"+ str(current_epoch_time)
    fileLink = download_audio(token, clean_string(name))
    if(fileLink == ""):
        fileLink = audioForallVideos(token, clean_string(name))
    return {
      "videolink" : fileLink
    }

@application.route("/download/fullhd", methods=[ 'GET', 'POST'])
def downloadFullHd():
    lock = threading.Lock()
    
    def download_and_return():
        try:
            increment_counter_byDate()
        except Exception as e:
            print("Exception:", e)
    
        current_epoch_time = time.time()
        decoded_token = ""
        token = request.headers.get('url')
        token = token.split("&")[0]
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
                fileLink = download_video(token, clean_string(name) + ".mp4", res)
            else:
                fileLink = download_video_which_doesnt_have_audio(token, clean_string(name), str(res))
        else:
            if(str(hasAudio) == "true"):
                fileLink = dowload_age_restricted_videos(token, int(format_id), clean_string(name) + ".mp4")
            else:
                fileLink = dowload_age_restricted_videos_having_without_audio(token, int(format_id), clean_string(name) + ".mp4")
        
        with lock:
            return {
              "videolink" : fileLink
            }
    
    # Run the function synchronously
    result = download_and_return()
    
    return result




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
        token = token.split("&")[0]
        print("Received Token:", token)
        #return list_available_resolutions(token)
        return list_available_resolutions_for_restricted_content(token)
    except Exception as e:
        try:
            increment_counter_error_byDate()
        except Exception as e:
            print("Exception:", e)
        return {'status': 'error', 'message': 'Something went wrong', 'error': str(e)}, 500

@application.route("/get/download/options/audio", methods=[ 'GET', 'POST'])
def getLatestMoviesAudioroute():
    try:
        decoded_token = ""
        token = request.headers.get('url')
        token = token.split("&")[0]
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
    try:
        increment_counter_Success_rate_byDate()
    except Exception as e:
        print("Exception:", e)
    directory = ''
    response = send_from_directory(directory, filename)
    
    # Modify the response to add the Content-Disposition header
    response.headers['Content-Disposition'] = 'attachment; filename={}'.format(filename)
    
    return response


@application.route('/sitemap.xml')
def getSitemap():
    response = send_from_directory('static', "sitemap.xml")
    return response

@application.route("/", methods=['GET'])
def main():
    return render_template('youtubedowloader1.html')

@application.route("/download-mp3", methods=['GET'])
def mainaudio():
    return render_template('audio_3.html')

@application.route("/youtube-audio-downloader", methods=['GET'])
def mainaudiotest():
    return render_template('audio_2.html')

@application.route("/download-mp3-es", methods=['GET'])
def mainaudioes():
    return render_template('audio_es.html')


@application.route("/download-mp3-de", methods=['GET'])
def mainaudiode():
    return render_template('audio_de.html')

@application.route("/lang/en/youtube-video-downloader", methods=['GET'])
def main2():
    return render_template('ytttt.html')

@application.route("/es", methods=['GET'])
def mainspanish():
    return render_template('yt_spanish.html')

@application.route("/de", methods=['GET'])
def maingerman():
    return render_template('german_yt.html')

@application.route("/pt", methods=['GET'])
def mainportugese():
    return render_template('portuguese.html')



@application.route("/shorts-downloader", methods=['GET'])
def mainshorts():
    return render_template('shorts.html')

@application.route("/privacypolicy", methods=['GET'])
def mainprivacy():
    return render_template('privacypolicy.html')

@application.route("/termsandconditions", methods=['GET'])
def mainterms():
    return render_template('termsandconditions.html')

@application.route("/contactus", methods=['GET'])
def contactus():
    return render_template('contactus.html')


if __name__ == "__main__":
    scheduler.add_job(id='Scheduled Task', func=delete30minutesOldFiles, trigger='interval', minutes=30)
    scheduler.start()
    application.debug = True
    application.run()