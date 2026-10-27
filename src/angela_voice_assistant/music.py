import os
from random import choice

from pygame import mixer


class LocalMusic:
    def __init__(self, music_path="/home/stmac/Музыка/", end_music=(".mp3")) -> None:
        """
            Class for playing local music from your path

            Args:
                music_path - path with your music

                end_music - end of file name
            
            return:
                None
        """
        self.music_path = music_path
        self.end_music = end_music
        
    def play_music(self, music) -> None:
        """
        Playing your music file

        Args:
            music - full name your file
        """
        mixer.music.load(music)
        mixer.music.play()
    
    def run(self) -> None:
        """
        Run process working to music
        """
        self.q = Queue()
        self.list_music = [self.music_path+music for music in os.listdir(self.music_path) if any([music.endswith(end) for end in self.end_music])]
        self.play_ = False
        mixer.init()
        
        while True:
            command = self.q.get()
            
            if command == "play":
                if self.play_:self.stop_music()
                else: self.play_ = True
            elif command == "pause":
                mixer.music.pause()
                self.play_ = False
            elif command == "unpause":
                mixer.music.unpause()
                self.play_ = True
            elif command == "next":
                mixer.music.stop()
            elif command == "stop":
                mixer.music.stop()
                self.play_ = False
            elif command == "-1":
                break

            if self.play_ and not mixer.music.get_busy():
                self.play_music(choice(self.list_music))
    
    def pause(self):
        """
        Pause the music playing
        """
        self.q.put("pause")
    
    def unpause(self):
        """
        Unpause the music playing
        """
        self.q.put("unpause")
    
    def play(self):
        self.q.put("play")

    def off_music(self):
        self.q.put("-1")
    
    def next(self):
        self.q.put("next")

    def stop_music(self):
        self.q.put("stop")


