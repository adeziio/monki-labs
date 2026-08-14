from core.pipeline import MonkiPipeline


def main():
    print(r"""
              __,__
     .--.  .-"     "-.  .--.
    / .. \/  .-. .-.  \/ .. \
   | |  '|  /   Y   \  |'  | |
   | \   \  \ 0 | 0 /  /   / |
    \ '- ,\.-"`` ``"-./, -' /
     `'-' /_   ^ ^   _\ '-'`
         |  \._   _./  |
         \   \`-.-`/   /
          `\  '---'  /`
            `-.___.-`

            MONKI LABS
         AI VIDEO STUDIO
""")

    pipeline = MonkiPipeline()

    pipeline.create_episode()


if __name__ == "__main__":

    main()