from threading import Thread

from angela_voice_assistant.handlers import assistant


def main() -> None:
    recognition_thread = Thread(target=assistant.recognize_speech)
    utterance_processing_thread = Thread(target=assistant.process_utterances)

    recognition_thread.start()
    utterance_processing_thread.start()

    recognition_thread.join()
    utterance_processing_thread.join()


if __name__ == "__main__":
    main()
