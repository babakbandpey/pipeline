"""
This script is used to download the captions of a YouTube video and convert it to a podcast.
Using the Pipline txt_rag module, the captions are converted to a podcast.
"""

from pipeline import YTCaptionDownloader
from pipeline import logger
from pipeline import FileUtils


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


def main():
    """
    Main function to download the captions of a YouTube video and convert it to a podcast
    """

    yt_url = "https://www.youtube.com/watch?v=hEInetWQXD8"

    # first, download the captions
    caption_downloader = YTCaptionDownloader('./yt')
    download_path = caption_downloader.download_captions(yt_url)

    # Read the downloaded captions
    # captions = FileUtils.read_file(download_path)
    # FileUtils.write_to_file(restored_caption_path, restored_captions)

    logger.info("Captions downloaded to: %s", download_path)


if __name__ == "__main__":
    main()
