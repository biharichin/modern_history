import os
import telegram

def parse_questions(file_path):
    questions = []
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue

        if 'Answer:' in line:
            i += 1
            continue

        # Found a question
        question_text = line
        options = []
        # The next 4 lines should be options
        for j in range(1, 5):
            if i + j < len(lines):
                option_line = lines[i + j].strip()
                if option_line.startswith(('A ', 'B ', 'C ', 'D ')):
                     options.append(option_line[2:])
                else: # handle if options are not in A,B,C,D format
                    options.append(option_line)


        # Find the answer line
        answer_line_index = -1
        for j in range(1, 10): # Search for answer in the next few lines
            if i + j < len(lines) and lines[i + j].strip().startswith('Answer:'):
                answer_line_index = i + j
                break

        if answer_line_index != -1:
            correct_option_letter = lines[answer_line_index].strip().split('Answer: ')[1]
            correct_option_index = ord(correct_option_letter) - ord('A')
            
            questions.append({
                "question": question_text,
                "options": options,
                "correct_option_index": correct_option_index,
            })
            i = answer_line_index + 1
        else:
            i += 1
            
    return questions

def main():
    try:
        token = os.environ["TELEGRAM_TOKEN"]
        chat_ids_str = os.environ["CHAT_IDS"]
        chat_ids = [chat_id.strip() for chat_id in chat_ids_str.split(',')]
    except KeyError as e:
        print(f"Error: Missing environment variable {e}")
        return

    bot = telegram.Bot(token=token)
    questions = parse_questions('moder_history.txt')
    
    try:
        with open('state.txt', 'r') as f:
            last_question_index = int(f.read().strip())
    except (FileNotFoundError, ValueError):
        last_question_index = 0

    if last_question_index >= len(questions):
        for chat_id in chat_ids:
            bot.send_message(chat_id=chat_id, text="no question, we done")
        return

    end_index = min(last_question_index + 30, len(questions))

    for i in range(last_question_index, end_index):
        q = questions[i]
        for chat_id in chat_ids:
            try:
                bot.send_poll(
                    chat_id=chat_id,
                    question=q['question'],
                    options=q['options'],
                    type='quiz',
                    correct_option_id=q['correct_option_index'],
                    is_anonymous=False
                )
            except Exception as e:
                print(f"Failed to send poll to {chat_id}: {e}")

    with open('state.txt', 'w') as f:
        f.write(str(end_index))

if __name__ == "__main__":
    main()
