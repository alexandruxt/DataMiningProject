import time

from whoosh.qparser import QueryParser
from whoosh import index, scoring
import openai
import os

openai.api_key = "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"


def ask_chat_gpt(prompt):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": ""},
                {"role": "user", "content": prompt},
            ],
        )

        return response['choices'][0]['message']['content']

    except openai.error.RateLimitError:
        print(f"Rate limit exceeded. Waiting for reset.")
        time.sleep(100)
        return ask_chat_gpt(prompt)


def retrieve_wikipedia_page(question, searcher):
    query_parser = QueryParser("content", searcher.schema)
    query = query_parser.parse(question)
    results = searcher.search(query)
    result_from_chat_GPT = ""
    if results:
        top_results_titles = [result["title"] for result in results[:10]]
        input_gpt = (
            f"Please select one item from the list {top_results_titles}. "
            f"Use the following clue: \"{question}\". No additional text allowed!"
        )
        result_from_chat_GPT = ask_chat_gpt(input_gpt)
    if len(results) > 0:
        return result_from_chat_GPT
    else:
        return "No Wikipedia page found"


def check_answers(file_path, searcher):
    correct_answers = 0
    total_questions = 0
    with open(file_path, "r") as file:
        lines = file.readlines()
        i = 0
        while i < len(lines):
            category = lines[i].strip()
            clue = lines[i + 1].strip()
            correct_answer = lines[i + 2].strip()
            retrieved_answer = retrieve_wikipedia_page(clue, searcher)
            print("\nQuestion nr:", total_questions)
            print("CLUE:",clue)
            print("RETRIEVED ANSWER",retrieved_answer)
            print("CORRECT ANSWER:",correct_answer)
            if (retrieved_answer.lower() in correct_answer.lower()) or (
                    correct_answer.lower() in retrieved_answer.lower()):
                correct_answers += 1
            # Move to the next set of category, clue, and correct answer
            i += 4  # Skip the blank line
            total_questions += 1
    return correct_answers, total_questions


def main():
    # Open the index for searching
    ix = index.open_dir("index")
    searcher = ix.searcher(weighting=scoring.TF_IDF())

    # Path to the file containing questions and answers
    questions_file_path = "questions.txt"

    # Check correctness of answers
    correct_answers_count, total = check_answers(questions_file_path, searcher)
    print("Number of correctly answered questions: ", correct_answers_count)
    print("Total nr of questions:", total)
    print("Precision at 1: ", correct_answers_count/total)
    # Close the searcher
    searcher.close()


if __name__ == "__main__":
    main()
