import os
import wget
import subprocess
import colorama
import shutil

from zipfile import ZipFile
from termcolor import colored
from gtts import gTTS
from pydub import AudioSegment
from moviepy.editor import AudioFileClip, ImageClip, concatenate_videoclips

colorama.init()

default_audio_path = 'audio/default_audio.wav'
rhub_output = 'temp/rhub_output.txt'
face_path = 'face/'
rhub_list = []

ffmpeg_zip = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"

if 'temp' not in os.listdir():
    os.mkdir('temp')

## Rhubarb installer
rhubarb_exe_link = 'https://github.com/DanielSWolf/rhubarb-lip-sync/releases/download/v1.13.0/Rhubarb-Lip-Sync-1.13.0-Windows.zip'
rhubarb_exe_zip = 'Rhubarb-Lip-Sync-1.13.0-Windows.zip'
rhubarb_exe_folder = 'Rhubarb-Lip-Sync-1.13.0-Windows'

if rhubarb_exe_folder not in os.listdir():
    print(colored("'Rhubarb-Lip-Sync-1.13.0-Windows' not found, downloading 'Rhubarb-Lip-Sync-1.13.0-Windows'...", 'red'))
    wget.download(rhubarb_exe_link)
    with ZipFile(rhubarb_exe_zip, 'r') as zip:
        zip.printdir()

        print('Extracting all the files now...')
        zip.extractall()
        print('Done!')
   
    os.remove(rhubarb_exe_zip)


audio_path = input(colored("Audio file (.wav) or press enter to use default audio file or press enter to use text input: ", 'yellow'))
text_input = input(colored("Enter speech text (enter to skip): ", 'yellow'))


def rhubarbRunExe(audio_path):

    dialog = None

    if text_input != "":
        txt_audio = "temp/audio.mp3"
        audio_path = "temp/audio.wav"
        
        myobj = gTTS(text=text_input, lang='en', slow=False)
        myobj.save(txt_audio)

        try:
            conv_snd = AudioSegment.from_mp3(txt_audio)
            conv_snd.export(audio_path, format='wav')
        except Exception as e:
            print(colored(f"'ffmpeg' path is not defined in your envioment variable path, please extract '{ffmpeg_zip}' in 'C:\\ffmpeg' directory and add it's bin path in envioment variables", 'red'))
            exit()

        dialog = open("temp/input_dialog.txt",'w')
        dialog.write(text_input)
        dialog.close
        d = "-d temp/input_dialog.txt"

    elif '.wav' not in audio_path:
        audio_path = default_audio_path
        print(colored("'.wav' file not found using default audio file.", 'red'))
        d = "-d audio/default_dialog.txt"
        
    else:
        print(colored("'.wav' file found in given audio path", 'green'))
        d = ""

    subprocess.run(f"{rhubarb_exe_folder}\\rhubarb.exe -o {rhub_output} {d} {audio_path}", shell=True)

    return audio_path

def videoProcess(audio_path):
    if 'output' not in os.listdir():
        os.mkdir('output')
    audio_path = rhubarbRunExe(audio_path)
    print('')
    try:
        rhub_raw_list = list(open(rhub_output))
    except Exception as e:
        rhub_raw_list = list(open('audio/default_rhub_output.txt'))

    for r in rhub_raw_list:
        r = r.replace('\t',':')
        r = r.replace('\n','')
        rhub_list.append(r)

    imageclips = []

    for data in range(len(rhub_list)):
        if data == len(rhub_list)-1:
            break
        imageclips.append(videoImage(rhub_list[data],rhub_list[data+1]))

    final = concatenate_videoclips(imageclips, method="compose")

    final = final.set_audio(AudioFileClip(audio_path))
    final.write_videofile('output/output.mp4', fps=60)

def videoImage(data, data_p1):
    return ImageClip(img=f"{face_path}{data.split(':')[1]}.png", transparent=True, duration=float(data_p1.split(':')[0]) - float(data.split(':')[0]))


if __name__ == "__main__":
    videoProcess(audio_path)

if 'temp' in os.listdir():  
    shutil.rmtree('temp')