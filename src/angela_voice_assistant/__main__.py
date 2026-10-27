from threading import Thread

from angela_voice_assistant.handlers import assistant
from angela_voice_assistant.answers import frazes


def main() -> None:
    assistant.set_answers(frazes)

    recognition_thread = Thread(target=assistant.recognize_speech)
    utterance_processing_thread = Thread(target=assistant.process_utterances)
    utterance_server_thread = Thread(target=assistant.process_server_modules)

    recognition_thread.start()
    utterance_processing_thread.start()
    utterance_server_thread.start()

    recognition_thread.join()
    utterance_processing_thread.join()
    utterance_server_thread.join()


if __name__ == "__main__":
    main()
