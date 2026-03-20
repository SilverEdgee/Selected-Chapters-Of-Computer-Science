"""
Lab Work #3: Standard Data Types, Collections, Functions, Modules
Module: string_tasks.py
Description: String analysis tasks — binary check (Task 3) and text analysis (Task 4)
Version: 1.0
Developer: Pometko D.I., Variant 22
Date: 20-03-2026
"""

import string

_TEXT = (
    "So she was considering in her own mind, as well as she could, "
    "for the hot day made her feel very sleepy and stupid, whether "
    "the pleasure of making a daisy-chain would be worth the trouble "
    "of getting up and picking the daisies, when suddenly a White "
    "Rabbit with pink eyes ran close by her."
)



def _is_binary(s: str) -> bool:
    """
    Check whether a string is a valid binary number (only '0' and '1').

    Args:
        s (str): The string to check.

    Returns:
        bool: True if the string is binary, False otherwise.
    """
    s = s.strip()
    if not s:
        return False
    for ch in s:
        if ch not in ('0', '1'):
            return False
    return True


def task3_binary_check() -> None:
    """
    Task 3 (Variant 22): Read a string from the keyboard and determine
    whether it represents a binary number. No regex used.
    """
    text = input("\n  Enter a string: ")
    if _is_binary(text):
        print(f"  '{text.strip()}' IS a binary number.")
    else:
        print(f"  '{text.strip()}' is NOT a binary number.")


def _get_words(text: str) -> list:
    """
    Split text into words, stripping punctuation from each token.

    Args:
        text (str): Source text.

    Returns:
        list of str: Tokens with surrounding punctuation removed.
    """
    return [token.strip(string.punctuation) for token in text.split() if token.strip(string.punctuation)]


def task4a_count_lowercase(text: str = _TEXT) -> int:
    """
    Count lowercase letters in the text.

    Args:
        text (str): Source text.

    Returns:
        int: Number of lowercase characters.
    """
    return sum(1 for ch in text if ch.islower())


def task4b_last_word_with_i(text: str = _TEXT):
    """
    Find the last word containing the letter 'i'
    and its 1-based position in the word list.

    Args:
        text (str): Source text.

    Returns:
        tuple: (word: str, position: int) or (None, None) if not found.
    """
    words = _get_words(text)
    result_word, result_pos = None, None
    for idx, word in enumerate(words, start=1):
        if 'i' in word.lower():
            result_word, result_pos = word, idx
    return result_word, result_pos


def task4c_exclude_i_words(text: str = _TEXT) -> str:
    """
    Return the text with all words starting with 'i'
    Args:
        text (str): Source text.

    Returns:
        str: Space-joined filtered text.
    """
    tokens = text.split()
    filtered = [t for t in tokens if not t.strip(string.punctuation).lower().startswith('i')]
    return ' '.join(filtered)


def task4_text_analysis() -> None:
    """
    Task 4 (Variant 22): Run all three sub-tasks on the fixed text and
    print results.
    """
    print(f"\n  Text:\n  \"{_TEXT}\"\n")

    lc = task4a_count_lowercase()
    print(f"  a) Lowercase letters: {lc}")

    word, pos = task4b_last_word_with_i()
    if word:
        print(f"  b) Last word with 'i': '{word}' (position #{pos})")
    else:
        print("  b) No word with 'i' found.")

    filtered = task4c_exclude_i_words()
    print(f"  c) Without words starting with 'i':\n     \"{filtered}\"")