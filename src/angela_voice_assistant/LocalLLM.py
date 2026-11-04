from ollama import chat

from angela_voice_assistant.MyLogging import logging

log = logging('log')

@log.log_class()
class LocalLLM():
    def __init__(self, model_name:str) -> None:
        '''
        Initialize the model with the given name and set up the rules for interaction.
        
        Args:
            model_name (str): The name of the model to be used for generating responses.
        '''
        self.work:bool = True
        self.model_name: str = model_name
        self.rule: str = """Ты - Анджела, голосовой помощник. 
                                        Правила: 
                                        - Отвечай максимально кратко
                                        - Только на русском
                                        - Без кода
                                        - Дружелюбно"""
        print("Initialize model:")
        init_response = chat(
                            model=model_name,
                            messages=[{'role': 'user', 'content': 'init'}],
                            keep_alive=-1
                            )
        print("End of initialization")
            

    def generate(self, prompt:str) -> str:
        '''
        Generate a response from the model based on the provided prompt.

        Args:
            prompt (str): The input text for which the model will generate a response.
        '''
        response = chat(
            model=self.model_name,
            messages=[
                {'role': 'system', 'content': self.rule},
                {'role': 'user', 'content': prompt}
            ],
            keep_alive=-1
        )
        return response['message']['content']

    
    def close_model(self) -> None:
        '''
        Close the model session by sending an exit command to the model.
        '''
        chat(
                model=self.model_name,
                messages=[{'role': 'user', 'content': 'exit'}],
                keep_alive=0
            )

