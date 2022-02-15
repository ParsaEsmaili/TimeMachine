from matplotlib.pyplot import text
import pygame
import sounddevice as sd
import soundfile as sf
import tkinter
import threading
import numpy
from tkinter import filedialog

def play_sound(file_name):
    global frame, sample_rate, frames_num

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

    while run:
        if not play:
            continue
        data = f.read(1024)
        outdata[:] = data
        stream.write(outdata)
        frame += 1024
        

def new_pannel():
    global run, play

    run = True
    id_icon = pygame.image.load("images\\id.png")
    play_icon = pygame.image.load("images\\play.png")
    pos1, pos2 = (15, 475)
    play = False
    changing_pos1 = False
    changing_pos2 = False

    top = tkinter.Tk()
    top.withdraw()
    file_name = filedialog.askopenfilename(parent=top)

    if file_name:
        threading.Thread(target=play_sound, args=(file_name, )).start()

        pygame.init()
        pygame.font.init()
        font = pygame.font.SysFont('Verdana', 25)
        screen = pygame.display.set_mode((500, 300))
        pygame.display.set_caption("Crop")
        time = int(frames_num / sample_rate)

        while run:
            screen.fill((255, 255, 255))
            pos = pygame.mouse.get_pos()

            pygame.draw.rect(screen, (120, 120, 120), (20, 20, 460, 30))
            pygame.draw.line(screen, (0, 0, 0), (pos1 + 5, 20), (pos1 + 5, 50), 1)
            pygame.draw.line(screen, (0, 0, 0), (pos2 + 5, 20), (pos2 + 5, 50), 1)
            pygame.draw.line(screen, (255, 0, 0), (frame / frames_num * 460 + 20, 20), (frame / frames_num * 460 + 20, 50), 1)
            screen.blit(id_icon, (pos1, 52))
            screen.blit(id_icon, (pos2, 52))
            ra = ((pos1 - 15) / 460, (pos2 - 15) / 460)
            img = font.render(str(int(ra[0] * time)) + "-" + str(int(ra[1] * time)) + "  " + str(int(frame / sample_rate)) + "/" + str(time), True, (0, 0, 0))
            screen.blit(img, (20, 80))
            text_rect = img.get_rect()
            screen.blit(play_icon, (text_rect[2] + 20, 80))

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


            
            pygame.display.update()

new_pannel()