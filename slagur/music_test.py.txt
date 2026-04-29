import pygame
import os
import time

print("Current folder:", os.getcwd())
print("Files here:", os.listdir())

pygame.init()
pygame.mixer.init()

music_file = "bg_music.wav"

print("Exists?", os.path.exists(music_file))

pygame.mixer.music.load(music_file)
pygame.mixer.music.set_volume(1.0)
pygame.mixer.music.play(-1)

print("Playing for 10 seconds...")
time.sleep(10)

pygame.mixer.music.stop()
print("Done")