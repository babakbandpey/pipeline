"""
This script is used to download the captions of a YouTube video and convert it to a podcast.
Using the Pipline txt_rag module, the captions are converted to a podcast.
"""

import os
from transformers import AutoTokenizer, AutoModelForTokenClassification
import torch
import language_tool_python
from pipeline import YTCaptionDownloader
from pipeline import logger
from pipeline import FileUtils


# Load a pre-trained punctuation restoration model
tokenizer = AutoTokenizer.from_pretrained("oliverguhr/fullstop-punctuation-multilang-large")
model = AutoModelForTokenClassification.from_pretrained("oliverguhr/fullstop-punctuation-multilang-large")

# Function to add punctuation
def restore_punctuation(text):
    """
    Restore punctuation to the input text.
    Args:
        text (str): The input text without punctuation.
    Returns:
        str: The input text with restored punctuation.
    """

    # Tokenize input
    # Tokenize input
    inputs = tokenizer.encode_plus(
        text,
        return_tensors="pt",
        add_special_tokens=True,
        truncation=True,
        max_length=512  # Adjust if your model allows longer sequences
    )
    input_ids = inputs['input_ids']
    attention_mask = inputs['attention_mask']

    # Get predictions
    with torch.no_grad():
        outputs = model(input_ids, attention_mask=attention_mask)
    logits = outputs.logits

    # Get the predicted punctuation labels
    predictions = torch.argmax(logits, dim=2)

    # Map label IDs to punctuation symbols
    label2punct = {
        0: '',   # No punctuation
        1: '.',  # Period
        2: ',',  # Comma
        3: '?'   # Question mark
    }

    # Get the tokens
    tokens = tokenizer.convert_ids_to_tokens(input_ids[0])
    predicted_labels = predictions[0]

    # Reconstruct the text
    words = []
    current_word = ''
    for token, label_id in zip(tokens, predicted_labels):
        if token in tokenizer.all_special_tokens:
            continue
        # Handle subword tokens
        if token.startswith('##'):
            current_word += token[2:]
        else:
            if current_word:
                words.append(current_word)
            current_word = token
        # Add punctuation if predicted
        punct = label2punct.get(label_id.item(), '')
        if punct:
            current_word += punct

    # Append the last word
    if current_word:
        words.append(current_word)

    # Join words with spaces
    punctuated_text = ' '.join(words)

    replace_dict = {
        ' .': '.',
        ' ,': ',',
        ' ?': '?',
        ' !': '!',
        ' :': ':',
        ' ;': ';',
        ' )': ')',
        '( ': '(',
        ' /': '/',
        ' %': '%',
        ' - ': '-',
        ' \'': '\'',
        ' "': '"',
        '  ': ' ',
        ' e ': 'e ',
        ' s ': 's ',
        ' \' ll': '\'ll',
        ' \' re': '\'re',
        ' \' ve': '\'ve',
    }

    # Replace punctuation with spaces
    for key, value in replace_dict.items():
        punctuated_text = punctuated_text.replace(key, value)

    return punctuated_text


def split_text_into_chunks(text, max_chunk_length=500):
    """
    Split the input text into chunks of a maximum length.
    Args:
        text (str): The input text to split.
        max_chunk_length (int): The maximum length of each chunk.
    Returns:
        list: A list of text chunks.
    """

    words = text.strip().split()
    chunks = []
    current_chunk = ''
    for word in words:
        if len(current_chunk.split()) + 1 > max_chunk_length:
            chunks.append(current_chunk.strip())
            current_chunk = ''
        current_chunk += ' ' + word
    if current_chunk:
        chunks.append(current_chunk.strip())
    return chunks


def restore_punctuation_full(text):
    """
    Restore punctuation to the input text.
    Args:
        text (str): The input text without punctuation.
    Returns:
        str: The input text with restored punctuation.
    """

    chunks = split_text_into_chunks(text)
    restored_text = ''
    for chunk in chunks:
        restored_chunk = restore_punctuation(chunk)
        restored_text += restored_chunk + ' '
    return restored_text.strip()


def main():
    """
    Main function to download the captions of a YouTube video and convert it to a podcast
    """

    yt_url = "https://www.youtube.com/watch?v=hYxNprRHMx0"

    # first, download the captions
    caption_downloader = YTCaptionDownloader('./yt')
    download_path = caption_downloader.download_captions(yt_url)

    # Read the downloaded captions
    captions = FileUtils.read_file(download_path)

    # Restore punctuation
    restored_captions = restore_punctuation_full(captions)

    restored_caption_path = os.path.join(caption_downloader.output_dir, "restored_captions.txt")

    # Save the restored captions
    FileUtils.write_to_file(restored_caption_path, restored_captions)

    logger.info("Captions downloaded to: %s", download_path)


if __name__ == "__main__":
    main()
