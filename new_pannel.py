from re import T
import pygame
import sounddevice as sd
import soundfile as sf
import tkinter
import threading
import numpy
import time
from tkinter import filedialog
from scipy.io.wavfile import write

def play_sound(file_name):
    global frame, sample_rate, frames_num, f, outdata, stream

    frame = 0
    f = sf.SoundFile(file_name)
    sample_rate = f.samplerate
    frames_num = f.frames
    stream = sd.OutputStream(dtype=numpy.float32, samplerate=f.samplerate, blocksize=1024, channels=f.channels)
    stream.start()

    if f.channels > 1:
        outdata = numpy.zeros((1024, f.channels), numpy.float32)
    else:
        outdata = numpy.zeros(1024, numpy.float32)

    while run and play:
        data = f.read(1024)
        outdata[:] = data
        stream.write(outdata)
        frame += 1024
    
    f.close()
        

def new_pannel():
    global run, play, frame, ra, f

    run = True
    id_icon = pygame.image.load("images\\id.png")
    play_icon = pygame.image.load("images\\play.png")
    stop_icon = pygame.image.load("images\\stop.png")
    pos1, pos2 = (15, 475)
    play = False
    changing_pos1 = False
    changing_pos2 = False
    name = ""
    text_selected = False

    top = tkinter.Tk()
    top.withdraw()
    file_name = filedialog.askopenfilename(parent=top)

    if file_name:
        pygame.init()
        pygame.font.init()
        font = pygame.font.SysFont('Verdana', 25)
        font2 = pygame.font.SysFont('Verdana', 15)
        pannel_screen = pygame.display.set_mode((500, 170))
        threading.Thread(target=play_sound, args=(file_name, )).start()
        time.sleep(0.1)
        pygame.display.set_caption("Crop")
        ti = int(frames_num / sample_rate)

        while run:
            pannel_screen.fill((255, 255, 255))
            pos = pygame.mouse.get_pos()

            pygame.draw.rect(pannel_screen, (120, 120, 120), (20, 20, 460, 30))
            pygame.draw.rect(pannel_screen, (200, 200, 200), (440, 135, 40, 20))
            pygame.draw.line(pannel_screen, (0, 0, 0), (pos1 + 5, 20), (pos1 + 5, 50), 1)
            pygame.draw.line(pannel_screen, (0, 0, 0), (pos2 + 5, 20), (pos2 + 5, 50), 1)
            if play:
                pygame.draw.line(pannel_screen, (255, 0, 0), (frame / frames_num * 460 + 20, 20), (frame / frames_num * 460 + 20, 50), 1)
            else:
                pygame.draw.line(pannel_screen, (255, 0, 0), (pos1 + 5, 20), (pos1 + 5, 50), 1)

            img = font2.render("OK", True, (0, 0, 0))
            pannel_screen.blit(img, (448, 135))

            img = font.render("Name: " + name, True, (0, 0, 0))
            pannel_screen.blit(img, (20, 120))

            pannel_screen.blit(id_icon, (pos1, 52))
            pannel_screen.blit(id_icon, (pos2, 52))
            ra = ((pos1 - 15) / 460, (pos2 - 15) / 460)
            img = font.render(str(int(ra[0] * ti)) + "-" + str(int(ra[1] * ti)) + "  " + str(int(frame / sample_rate)) + "/" + str(ti), True, (0, 0, 0))
            pannel_screen.blit(img, (20, 80))
            text_rect = img.get_rect()
            if play:
                pannel_screen.blit(stop_icon, (text_rect[2] + 40, 88))
            else:
                pannel_screen.blit(play_icon, (text_rect[2] + 40, 88))

            if frame + 2048 >= ra[1] * frames_num:
                play = False

            if changing_pos1:
                pos1 = pos[0]
                if pos1 < 15:pos1 = 15
                if pos1 > pos2 - 12:pos1 = pos2 - 12
            if changing_pos2:
                pos2 = pos[0]
                if pos2 < pos1 + 12:pos2 = pos1 + 12
                if pos2 > 475:pos2 = 475

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                    
                if event.type == pygame.KEYDOWN:
                    try:
                        if event.key != pygame.K_BACKSPACE:
                            name += chr(event.key)
                        else:
                            name = name[:-1]
                    except:
                        pass

                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        changing_pos1 = False
                        changing_pos2 = False
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if 15 < pos[0] < 490 and 50 < pos[1] < 75:
                            if abs(pos1 - pos[0]) < abs(pos2 -pos[0]):
                                changing_pos1 = True
                            else:
                                changing_pos2 = True
                        
                        if text_rect[2] + 40 < pos[0] < text_rect[2] + 55 and 88 < pos[1] < 105:
                            if play:
                                play = False
                            else:
                                play = False
                                threading.Thread(target=play_sound, args=(file_name, )).start()
                                play = True
                                time.sleep(0.01)
                                f.seek(int(ra[0] * frames_num))
                                frame = int(ra[0] * frames_num)
                        
                        if 440 < pos[0] < 480 and 135 < pos[1] < 155:
                            run = False
                
            pygame.display.update()
        
        f.close()
        f = sf.SoundFile(file_name)
        f.seek(int(ra[0] * frames_num))
        frames = numpy.zeros(int((ra[1] - ra[0]) * frames_num), numpy.float32)
        data = f.read(1024)
        fr = 0
        if f.channels > 1:
            while True:
                outdata[:] = data
                for i in range(len(outdata)):
                    frames[fr + i] = outdata[i][0]
                fr += 1024
                data = f.read(1024)
                if fr + 1024 > int((ra[1] - ra[0]) * frames_num):
                    break

        else:
            while True:
                outdata[:] = data
                for i in range(len(outdata)):
                    frames[i] = outdata[i]
                fr += 1024
                data = f.read(1024)
                if fr + 1024 > int((ra[1] - ra[0]) * frames_num):
                    break

        write("audios\\" + file_name[file_name.rindex("/") + 1:], sample_rate, frames)

        return name, file_name
    return False, False