import pygame
import tkinter
import threading
import time
import numpy
import json
import shutil
import os
import sounddevice as sd
import soundfile as sf
from tkinter import filedialog
from tkinter import simpledialog
from scipy.io.wavfile import write
from datetime import datetime
from pygame import gfxdraw

pygame.init()
pygame.font.init()
pygame.display.set_caption("Time machine")

f = open("file.json", "r")
json_data = json.load(f)
f.close()

##################
names = ["allah o", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14","15", "16"]
font = pygame.font.SysFont('Verdana', 25)
font2 = pygame.font.SysFont('Verdana', 20)
font3 = pygame.font.SysFont('Verdana', 15)
screen_size = (450, 640)
chunk = 1024
sample_format = numpy.float32
channels = 2
fs = 44100
seconds = 300
frames = []
frames_size = fs / chunk * seconds
run = True
is_playing = True
un_mute_icon = pygame.image.load("images\\un_mute.png")
mute_icon = pygame.image.load("images\\mute.png")
un_deafen_icon = pygame.image.load("images\\un_deafen.png")
deafen_icon = pygame.image.load("images\\deafen.png")
plus_icon = pygame.image.load("images\\plus.png")
plus_selected_icon = pygame.image.load("images\\plus_selected.png")
delete_icon = pygame.image.load("images\\delete.png")
key = 18
mute = json_data["data"]["mute"]
deafen = json_data["data"]["deafen"]
max_time = 0
is_setting = False
sound_level = 5
frame_num = 0
hear_my_self = json_data["data"]["hear_my_self"]
hear_my_self_anim = 5
voice_changer = json_data["data"]["voice_changer"]
voice_changer_anim = 5
input_volume = json_data["data"]["input_volume"]
play_volume = json_data["data"]["output_volume"]
changing_input_volume = False
changing_play_volume = False
y_offset = 0
volume_editing_num = -1
playing_num = -1
##################

if hear_my_self:hear_my_self_anim = 0
if voice_changer:voice_changer_anim = 0

def play_back():
    global frames, mic_buffer

    speaker_stream = sd.OutputStream(dtype=numpy.float32, samplerate=44100, blocksize=chunk, channels=2)
    speaker_stream.start()

    while run:
        if not mute:
            mic_data = input_stream.read(chunk)
            output_stream.write(mic_data[0] * input_volume * 4)
            if hear_my_self:
                speaker_stream.write(mic_data[0] * input_volume * 4)
        if len(frames) <= frames_size:
            data = record_stream.read(chunk)[0]
            frames.append(data)
        else:
            data = record_stream.read(chunk)[0]
            frames.pop(0)
            frames.append(data)

def play_audio(name):
    global max_time, f, frame_num

    filename = "audios\\" + name
    f = sf.SoundFile(filename)

    max_time = int(f.frames / f.samplerate)

    stream = sd.OutputStream(dtype=numpy.float32, samplerate=f.samplerate, blocksize=chunk, device=9, channels=f.channels)
    speaker_stream = sd.OutputStream(dtype=numpy.float32, samplerate=f.samplerate, blocksize=chunk, channels=f.channels)
    stream.start()
    speaker_stream.start()
    outdata = numpy.zeros((chunk, 2), numpy.float32)
    
    data = f.read(chunk)
    frame_num = 0
    while len(data) and is_playing and run:
        vl = json_data["audios"][playing_num]["volume"]
        outdata[:] = data
        if not is_setting:
            stream.write(outdata * vl * 2)
            if not deafen:
                speaker_stream.write(outdata * play_volume * vl * 4)
            data = f.read(chunk)
            frame_num += 1
        
    max_time = 0

    stream.stop()
    speaker_stream.stop()
    f.close()

screen = pygame.display.set_mode(screen_size)

clock = pygame.time.Clock()

record_stream = sd.InputStream(dtype=numpy.float32, samplerate=fs, blocksize=chunk, device=2, channels=1)
input_stream = sd.InputStream(dtype=numpy.float32, samplerate=fs, blocksize=chunk, device=4, channels=2)
output_stream = sd.OutputStream(dtype=numpy.float32, samplerate=fs, blocksize=chunk, device=9, channels=2)
record_stream.start()
input_stream.start()
output_stream.start()

threading.Thread(target=play_back).start()

while run:
    clock.tick(60)

    screen.fill((187, 173, 160))

    pos = pygame.mouse.get_pos()

    num = -1
    for audio in json_data["audios"]:
        num = audio["num"]
        x_num = num % 4
        y_num = num // 4
        draw_pos = (10 * (x_num + 1) + 100 * x_num, 10 * (y_num + 1) + 100 * y_num - y_offset)
        if volume_editing_num == num:
            audio["volume"] = (pos[0] - draw_pos[0] - 10) / 80
            if audio["volume"] < 0:audio["volume"] = 0
            if audio["volume"] > 1:audio["volume"] = 1
        if draw_pos[0] < pos[0] < draw_pos[0] + 100 and draw_pos[1] < pos[1] < draw_pos[1] + 90 and not (draw_pos[0] + 85 < pos[0] < draw_pos[0] + 100 and draw_pos[1] < pos[1] < draw_pos[1] + 17):
            pygame.draw.rect(screen, (225, 213, 200), (draw_pos[0], draw_pos[1], 100, 100))
        else:
            pygame.draw.rect(screen, (205, 193, 180), (draw_pos[0], draw_pos[1], 100, 100))
        pygame.draw.line(screen, (0, 175, 244), (draw_pos[0] + 10, draw_pos[1] + 93), (draw_pos[0] + 10 + int(80 * audio["volume"]), draw_pos[1] + 93), 3)
        pygame.draw.line(screen, (237, 27, 36), (draw_pos[0] + 10 + int(80 * audio["volume"]), draw_pos[1] + 93), (draw_pos[0] + 90, draw_pos[1] + 93), 3)
        gfxdraw.filled_circle(screen, draw_pos[0] + 10 + int(80 * audio["volume"]), draw_pos[1] + 93, 4, (255, 255, 255))
        img = font2.render(audio["inname"], True, (0, 0, 0))
        text_rect = img.get_rect()
        screen.blit(img, (draw_pos[0] + (50 - text_rect[2] / 2), draw_pos[1] + (50 - text_rect[3] / 2)))
        screen.blit(delete_icon, (draw_pos[0] + 85, draw_pos[1] + 5))

    num += 1
    x_num = num % 4
    y_num = num // 4
    draw_pos = (10 * (x_num + 1) + 100 * x_num, 10 * (y_num + 1) + 100 * y_num - y_offset)
    if draw_pos[0] < pos[0] < draw_pos[0] + 100 and draw_pos[1] < pos[1] < draw_pos[1] + 100:
        pygame.draw.rect(screen, (225, 213, 200), (draw_pos[0], draw_pos[1], 100, 100))
        screen.blit(plus_selected_icon, (draw_pos[0] + 25, draw_pos[1] + 25))
    else:
        pygame.draw.rect(screen, (205, 193, 180), (draw_pos[0], draw_pos[1], 100, 100))
        screen.blit(plus_icon, (draw_pos[0] + 25, draw_pos[1] + 25))

    pygame.draw.rect(screen, (187, 173, 160), (0, 440, 450, 180))

    pygame.draw.line(screen, (0, 175, 244), (105, 620), (105 + int(150 * input_volume), 620), 3)
    pygame.draw.line(screen, (0, 175, 244), (270, 620), (270 + int(150 * play_volume), 620), 3)
    pygame.draw.line(screen, (237, 27, 36), (105 + int(150 * input_volume), 620), (255, 620), 3)
    pygame.draw.line(screen, (237, 27, 36), (270 + int(150 * play_volume), 620), (420, 620), 3)
    gfxdraw.filled_circle(screen, 105 + int(150 * input_volume), 620, 4, (255, 255, 255))
    gfxdraw.filled_circle(screen, 270 + int(150 * play_volume), 620, 4, (255, 255, 255))
    
    if not ((hear_my_self_anim > 1 and hear_my_self) or (hear_my_self_anim < 4 and not hear_my_self)):
        if hear_my_self:
            pygame.draw.rect(screen, (0, 175, 244), (10, 610, 40, 20), 0, 10)
            gfxdraw.filled_circle(screen, 21, 620, 6, (255, 255, 255))
        else:
            pygame.draw.rect(screen, (237, 27, 36), (10, 610, 40, 20), 0, 10)
            gfxdraw.filled_circle(screen, 38, 620, 6, (255, 255, 255))
    else:
        pygame.draw.rect(screen, (int(59 * hear_my_self_anim), 175 - int(37 * hear_my_self_anim), 244 - int(52 * hear_my_self_anim)), (10, 610, 40, 20), 0, 10)
        gfxdraw.filled_circle(screen, 21 + int(4 * hear_my_self_anim), 620, 6, (255, 255, 255))
        if hear_my_self:
            hear_my_self_anim -= 1
        else:
            hear_my_self_anim += 1
    
    if not ((voice_changer_anim > 1 and voice_changer) or (voice_changer_anim < 4 and not voice_changer)):
        if voice_changer:
            pygame.draw.rect(screen, (0, 175, 244), (55, 610, 40, 20), 0, 10)
            gfxdraw.filled_circle(screen, 66, 620, 6, (255, 255, 255))
        else:
            pygame.draw.rect(screen, (237, 27, 36), (55, 610, 40, 20), 0, 10)
            gfxdraw.filled_circle(screen, 83, 620, 6, (255, 255, 255))
    else:
        pygame.draw.rect(screen, (int(59 * voice_changer_anim), 175 - int(37 * voice_changer_anim), 244 - int(52 * voice_changer_anim)), (55, 610, 40, 20), 0, 10)
        gfxdraw.filled_circle(screen, 66 + int(4 * voice_changer_anim), 620, 6, (255, 255, 255))
        if voice_changer:
            voice_changer_anim -= 1
        else:
            voice_changer_anim += 1

    pygame.draw.rect(screen, (0, 0, 0), (10, 610, 40, 20), 2, 10)
    pygame.draw.rect(screen, (0, 0, 0), (55, 610, 40, 20), 2, 10)

    pygame.draw.rect(screen, (0, 0, 0), (110, 560, 200, 40))
    if max_time:
        img = font.render(str(int(frame_num * chunk / f.samplerate)) + "/" + str(max_time), True, (0, 0, 0))
        screen.blit(img, (320, 563))
        pygame.draw.rect(screen, (255, 0, 0), (115, 565, int(frame_num * chunk / f.frames * 190), 30))
    
        if frame_num * chunk + 2 * chunk >= f.frames:
            is_playing = False

    if mute:
        screen.blit(mute_icon, (10, 560))
    else:
        screen.blit(un_mute_icon, (10, 560))

    if deafen:
        screen.blit(deafen_icon, (60, 560))
    else:
        screen.blit(un_deafen_icon, (60, 560))

    if 10 < pos[0] < 220 and 450 < pos[1] < 550:
        pygame.draw.rect(screen, (225, 213, 200), (10, 450, 210, 100))
    else:
        pygame.draw.rect(screen, (205, 193, 180), (10, 450, 210, 100))
    
    if 230 < pos[0] < 440 and 450 < pos[1] < 550:
        pygame.draw.rect(screen, (225, 213, 200), (230, 450, 210, 100))
    else:
        pygame.draw.rect(screen, (205, 193, 180), (230, 450, 210, 100))
    
    img = font2.render("Record last 5 min", True, (0, 0, 0))
    text_rect = img.get_rect()
    screen.blit(img, (10 + (105 - text_rect[2] / 2), 450 + (50 - text_rect[3] / 2)))
    img = font2.render("Stop all sounds", True, (0, 0, 0))
    text_rect = img.get_rect()
    screen.blit(img, (230 + (105 - text_rect[2] / 2), 450 + (50 - text_rect[3] / 2)))
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONUP:
            changing_input_volume = False
            changing_play_volume = False
            is_setting = False
            volume_editing_num = -1

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4:
                y_offset -= 10
                if y_offset < 0:y_offset = 0

            if event.button == 5:
                max_offset = 10 * ((len(json_data["audios"]) + 0) // 4 + 2) + 100 * ((len(json_data["audios"]) + 0) // 4 + 1)
                y_offset += 10
                if max_offset - y_offset < 450:y_offset = max_offset - 450
                if len(json_data["audios"]) < 15:y_offset = 0

            if event.button == 1:
                if 10 < pos[0] < 50 and 560 < pos[1] < 600:
                    if mute:
                        mute = False
                    else:
                        mute = True
                
                if 60 < pos[0] < 100 and 560 < pos[1] < 600:
                    if deafen:
                        deafen = False
                    else:
                        deafen = True

                if 10 < pos[0] < 50 and 610 < pos[1] < 630:
                    if hear_my_self:
                        hear_my_self = False
                        hear_my_self_anim = 1
                    else:
                        hear_my_self = True
                        hear_my_self_anim = 4
                
                if 55 < pos[0] < 95 and 610 < pos[1] < 630:
                    if voice_changer:
                        voice_changer = False
                        voice_changer_anim = 1
                    else:
                        voice_changer = True
                        voice_changer_anim = 4
                
                if 105 < pos[0] < 255 and 615 < pos[1] < 625:
                    if changing_input_volume:
                        changing_input_volume = False
                    else:
                        changing_input_volume = True
                    input_volume = (pos[0] - 105) / 150

                if 270 < pos[0] < 420 and 615 < pos[1] < 625:
                    if changing_play_volume:
                        changing_play_volume = False
                    else:
                        changing_play_volume = True
                    play_volume = (pos[0] - 270) / 150

                num = -1
                for audio in json_data["audios"]:
                    num = audio["num"]
                    x_num = num % 4
                    y_num = num // 4
                    draw_pos = (10 * (x_num + 1) + 100 * x_num, 10 * (y_num + 1) + 100 * y_num - y_offset)
                    if draw_pos[0] + 85 < pos[0] < draw_pos[0] + 100 and draw_pos[1] < pos[1] < draw_pos[1] + 17:
                        if playing_num == num:
                            is_playing = False
                        time.sleep(0.5)
                        audios = json_data["audios"]
                        os.remove("audios\\" + audio["filename"])
                        audios.pop(num)
                        for i in range(len(audios)):
                            audios[i]["num"] = i
                        json_data["audios"] = audios
                    elif draw_pos[0] < pos[0] < draw_pos[0] + 100 and draw_pos[1] < pos[1] < draw_pos[1] + 90:
                        is_playing = False
                        time.sleep(0.3)
                        is_playing = True
                        threading.Thread(target=play_audio, args=(audio["filename"], )).start()
                        playing_num = num
                    elif draw_pos[0] < pos[0] < draw_pos[0] + 100 and draw_pos[1] + 90 < pos[1] < draw_pos[1] + 100:
                        audio["volume"] = (pos[0] - draw_pos[0] - 10) / 80
                        if audio["volume"] < 0:audio["volume"] = 0
                        if audio["volume"] > 1:audio["volume"] = 1
                        volume_editing_num = num
                
                num += 1
                x_num = num % 4
                y_num = num // 4
                draw_pos = (10 * (x_num + 1) + 100 * x_num, 10 * (y_num + 1) + 100 * y_num - y_offset)
                    
                if draw_pos[0] < pos[0] < draw_pos[0] + 100 and draw_pos[1] < pos[1] < draw_pos[1] + 100:
                    top = tkinter.Tk()
                    top.withdraw()
                    file_name = filedialog.askopenfilename(parent=top)
                    if file_name:
                        shutil.copyfile(file_name, "audios\\" + file_name[file_name.rindex("/") + 1:])
                        inname = simpledialog.askstring("Name:", "Enter the in name:")
                        audios = json_data["audios"]
                        audios.append({"num" : len(audios), "inname" : inname, "filename" : file_name[file_name.rindex("/") + 1:], "volume" : 0.5})
                        json_data["audios"] = audios

                if 10 < pos[0] < 220 and 450 < pos[1] < 550:
                    t = str(datetime.now())
                    filename = t[:t.rindex(".")].replace(":", "") + ".wav"
                    write("audios\\" + filename, fs, numpy.append([*frames[:-1]], frames[-1]))
                if 230 < pos[0] < 440 and 450 < pos[1] < 550:
                    is_playing = False

                if max_time:
                    if 115 < pos[0] < 305 and 565 < pos[1] < 595:
                        is_setting = True
                        f.seek(int((pos[0] - 115) / 190 * f.frames))
                        frame_num = int((pos[0] - 115) / 190 * f.frames / chunk)
        
        if is_setting:
            if 115 < pos[0] < 305:
                f.seek(int((pos[0] - 115) / 190 * f.frames))
                frame_num = int((pos[0] - 115) / 190 * f.frames / chunk)
        
        if changing_input_volume:
            input_volume = (pos[0] - 100) / 150
            if input_volume >= 1:input_volume = 1
            if input_volume <= 0:input_volume = 0
        
        if changing_play_volume:
            play_volume = (pos[0] - 260) / 150
            if play_volume >= 1:play_volume = 1
            if play_volume <= 0:play_volume = 0
                
    pygame.display.update()

time.sleep(0.1)
json_data["data"]["mute"] = mute
json_data["data"]["deafen"] = deafen
json_data["data"]["hear_my_self"] = hear_my_self
json_data["data"]["voice_changer"] = voice_changer
json_data["data"]["input_volume"] = input_volume
json_data["data"]["output_volume"] = play_volume
f = open("file.json", "w")
json.dump(json_data, f)
f.close()