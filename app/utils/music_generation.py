from ast import Bytes
import io
from pathlib import Path
import base64
import torch.cuda

# from Riffusion.Riffusion_generate import RiffusionGenerator
# from MusicGen.Music_gen import MusicGenGenerator
app_path = Path(__file__).resolve().parent.parent

from abc import ABCMeta, abstractmethod

class MusicGenerator(metaclass=ABCMeta):
    @abstractmethod
    def generate(self, text: str, time: int) ->io.BytesIO:
        pass

class MusicGeneratorFactory:
    def create_generator(self, mode) -> MusicGenerator:
        generator_dict={
            0: TestGenerator,
            1: MusicGenGenerator
        }
        return generator_dict[mode]()

class TestGenerator(MusicGenerator):
    def generate(self, text: str, time: int) -> io.BytesIO:
        print("音乐生成提示词：" + text.encode('gbk', errors='replace').decode('gbk'))
        test_path = app_path/"static"/"BONK.mp3"
        test_mp3 = open(test_path,"rb").read()
        return test_mp3

from transformers import AutoProcessor, MusicgenForConditionalGeneration
import scipy

device = 'cuda' if torch.cuda.is_available() else 'cpu'

class MusicGenGenerator(MusicGenerator):
    def __init__(self) -> None:
        
        self.processor = AutoProcessor.from_pretrained("./app/facebook/musicgen-small")
        self.model = MusicgenForConditionalGeneration.from_pretrained("./app/facebook/musicgen-small")
        self.sampling_rate = self.model.config.audio_encoder.sampling_rate
        self.model.to(device)

    def generate(self, text: str, time: int) -> io.BytesIO:
        inputs = self.processor(
            text=[text],
            padding=True,
            return_tensors="pt",
        ).to(device)
        wav_file_data = io.BytesIO()
        audio_values = self.model.generate(**inputs, max_new_tokens=int(time*256/5)) #time为秒数，256token = 5s 
        scipy.io.wavfile.write(wav_file_data, rate=self.sampling_rate, data=audio_values[0, 0].cpu().numpy())
        with open('musicgen.wav', 'wb') as f:
            f.write(wav_file_data.getvalue())
        return wav_file_data

class MubertGenerator(MusicGenerator):
    def generate(self, text: str, time: int) -> io.BytesIO:
        pass

class MousaiGenerator(MusicGenerator):
    def generate(self, text: str, time: int) -> io.BytesIO:
        pass


if __name__=="__main__":
    mgfactory = MusicGeneratorFactory()
    mg = mgfactory.create_generator(1)
    print(mg.generate("cyberpunk electronic dancing music"))