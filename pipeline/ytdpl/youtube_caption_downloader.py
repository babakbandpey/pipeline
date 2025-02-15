"""
bbalvl7: what does this class do?

The `YouTubeCaptionDownloader` class provides functionality to download subtitles from YouTube videos and clean them
for better readability. It uses the `yt-dlp` command-line tool to fetch video information and download auto-generated
subtitles in VTT format. The downloaded captions are cleaned by removing unwanted parts such as timestamp tags,
formatting tags, and metadata lines. The cleaned subtitles are saved as text files in the specified output directory.

1. **Initialization**:
   - Takes an output_dir parameter and sets it as an instance variable. This directory is where the downloaded captions will be saved.

2. **Cleaning Subtitles method**:
   - Takes subtitle_content as input, which is the raw subtitle text.
   - Splits the subtitle content into lines and processes each line to remove unwanted parts:
     - Skips lines that are either the 'WEBVTT' header, timestamp lines, or alignment information.
     - Removes timestamp tags and formatting tags (`<c>` and `</c>`).
     - Strips leading and trailing whitespace from each line.
     - Ensures no duplicate consecutive lines are added to the cleaned list.
   - Removes metadata lines if they exist at the beginning.
   - Joins the cleaned lines into a single string, ensuring no more than two consecutive newlines.
   - Returns the cleaned subtitle text.

3. **Downloading Captions**:
   - Takes a video_url as input.
   - Uses the `yt-dlp` command-line tool to fetch video information in JSON format.
   - Extracts the video ID and title from the fetched information.
   - Sanitizes the video title to create a safe filename.
   - Constructs an output template path using the video ID and sanitized title.
   - Uses `yt-dlp` again to download the auto-generated subtitles in VTT format, saving them to the specified output directory.

In summary, this class provides functionality to download subtitles from YouTube videos and clean them for better readability.
"""

import os
import subprocess
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
import re
from pipeline.logger import logger

class YouTubeCaptionDownloader:
    """
    A class to download and clean subtitles from YouTube videos.
    """
    def __init__(self, output_dir = "/app/yt"):
        self.output_dir = output_dir

    def clean_subtitle(self, subtitle_content):
        """
        Clean the subtitle content by removing unwanted parts.
        Args:
            subtitle_content (str): The raw subtitle text.
        Returns:
            str: The cleaned subtitle text.
        """
        lines = subtitle_content.split('\n')
        cleaned_lines = []
        for line in lines:
            if line == 'WEBVTT' or re.match(r'^\d{2}:\d{2}:\d{2}\.\d{3} --> \d{2}:\d{2}:\d{2}\.\d{3}', line) or 'align:start position:0%' in line:
                continue
            line = re.sub(r'<\d{2}:\d{2}:\d{2}\.\d{3}>', '', line)
            line = re.sub(r'</?c>', '', line)
            line = line.strip()
            if line and (not cleaned_lines or line != cleaned_lines[-1]):
                cleaned_lines.append(line)

        if cleaned_lines and cleaned_lines[0].startswith('Kind:'):
            cleaned_lines = cleaned_lines[2:]

        cleaned_text = re.sub(r'\n{3,}', '\n\n', '\n'.join(cleaned_lines)).strip()
        return cleaned_text

    def download_captions(self, video_url):
        """
        Download and clean the captions for a YouTube video.
        Args:
            video_url (str): The URL of the YouTube video.
        Returns:
            str: The path to the saved text file with cleaned captions, or None if captions were not downloaded.
        """

        try:
            # Get video info
            cmd = ['yt-dlp', '-J', '--no-playlist', video_url]
            result = subprocess.run(cmd, capture_output=True, text=True)
            video_info = json.loads(result.stdout)

            video_id = video_info['id']
            video_title = video_info['title']

            txt_path = self.get_txt_path(video_id, video_title)

            # **Modification starts here**
            # Check if the .txt caption file already exists
            if os.path.exists(txt_path):
                print(f"Captions already downloaded for: {video_title}")
                return txt_path
            # **Modification ends here**

            output_template = os.path.join(self.output_dir, f'{video_id}_{self.sanitize_title(video_title)}.%(ext)s')

            # Download captions
            cmd = ['yt-dlp',
                   '--skip-download',
                   '--write-auto-sub',
                    # "--write-sub",
                   '--sub-format',
                #    'vtt',
                    'none',
                   '--output', output_template,
                   video_url]

            result = subprocess.run(cmd, capture_output=True, text=True)

            # Check if captions were downloaded
            subtitle_file = next((f for f in os.listdir(self.output_dir) if f.startswith(f'{video_id}_{self.sanitize_title(video_title)}') and f.endswith('.vtt')), None)

            if subtitle_file is None:
                print(f"No captions found for: {video_title}")
                return None

            subtitle_path = os.path.join(self.output_dir, subtitle_file)

            with open(subtitle_path, 'r', encoding='utf-8') as f:
                subtitle_content = f.read()

            cleaned_subtitle = self.clean_subtitle(subtitle_content)

            with open(txt_path, 'w', encoding='utf-8') as f:
                f.write(cleaned_subtitle)

            os.remove(subtitle_path)

            print(f"Downloaded and cleaned captions for: {video_title}")
            return txt_path
        except subprocess.CalledProcessError as e:
            logger.error(f"Error downloading captions for {video_url}: {e}")
            return None
        except FileNotFoundError as e:
            logger.error(f"yt-dlp command not found: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding video information: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error processing captions for {video_url}: {str(e)}")
            return None


    def get_txt_path(self, video_id, video_title):
        """
        Get the path for the text file to save the cleaned captions.
        Args:
            video_id (str): The ID of the YouTube video.
            video_title (str): The title of the YouTube video.
        Returns:
            str: The path to save the text file.
        """

        safe_title = self.sanitize_title(video_title)
        txt_path = os.path.join(self.output_dir, f'{video_id}_{safe_title}.txt')
        return txt_path


    def sanitize_title(self, title):
        """
        Sanitize the video title to create a safe filename.
        Args:
            title (str): The title of the YouTube video.
        Returns:
            str: The sanitized title.
        """
        return "".join([c for c in title if c.isalpha() or c.isdigit() or c==' ']).rstrip()


    def get_playlist_videos(self, playlist_url):
        """
        Get a list of unique video URLs from a YouTube playlist.
        Args:
            playlist_url (str): The URL of the YouTube playlist.
        Returns:
            list: A list of unique video URLs in the playlist.
        """

        cmd = [
            'yt-dlp',
            '--flat-playlist',
            '--print',
            'id',
            '--no-warnings',
            playlist_url
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        video_ids = list(set(result.stdout.strip().split('\n')))  # Remove duplicates
        return [f'https://www.youtube.com/watch?v={video_id}' for video_id in video_ids if video_id]

    def merge_captions(self, caption_files):
        """
        Merge multiple caption files into a single file.
        Args:
            caption_files (list): A list of paths to caption files.
        """

        merged_content = []
        for file in caption_files:
            with open(file, 'r', encoding='utf-8') as f:
                content = f.read()
                merged_content.append(content)
                merged_content.append('\n\n' + '-'*50 + '\n\n')

        merged_file_path = os.path.join(self.output_dir, 'merged_captions.txt')
        with open(merged_file_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(merged_content))

        logger.info(f"Merged captions saved to: {merged_file_path}")

    def process_playlist(self, playlist_url):
        """
        Process a YouTube playlist to download captions for all videos.
        Args:
            playlist_url (str): The URL of the YouTube playlist.
        Returns:
            list: A list of paths to the downloaded caption files.
        """

        video_urls = self.get_playlist_videos(playlist_url)
        total_videos = len(video_urls)
        logger.info(f"Found {total_videos} unique videos in the playlist.")

        successful_downloads = 0
        failed_downloads = 0
        caption_files = []

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(self.download_captions, url) for url in video_urls]
            for future in as_completed(futures):
                result = future.result()
                if result:
                    caption_files.append(result)
                    successful_downloads += 1
                else:
                    failed_downloads += 1
                logger.info(f"Processed {successful_downloads + failed_downloads}/{total_videos} videos. "
                      f"Successful: {successful_downloads}, Failed: {failed_downloads}")

        logger.info(f"\nDownload summary for playlist {playlist_url}:")
        logger.info(f"Total videos in playlist: {total_videos}")
        logger.info(f"Successfully downloaded: {successful_downloads}")
        logger.info(f"Failed to download: {failed_downloads}")

        return caption_files

# def main():
#     mode = input("Enter 'v' for single video or 'p' for playlist(s): ").lower()

#     if mode == 'v':
#         video_url = input("Enter the YouTube video URL: ")
#         output_dir = input("Enter the output directory for captions: ")

#         if not os.path.exists(output_dir):
#             os.makedirs(output_dir)

#         downloader = YouTubeCaptionDownloader(output_dir)
#         result = downloader.download_captions(video_url)
#         if result:
#             logger.info("Caption downloaded successfully.")
#         else:
#             logger.info("Failed to download caption.")

#     elif mode == 'p':
#         output_dir = input("Enter the output directory for captions: ")

#         if not os.path.exists(output_dir):
#             os.makedirs(output_dir)

#         multiple_playlists = input("Do you want to include multiple playlists? (yes/no): ").lower() == 'yes'

#         if multiple_playlists:
#             num_playlists = int(input("Enter the number of playlists: "))
#             playlist_urls = []
#             for i in range(num_playlists):
#                 playlist_url = input(f"Enter playlist URL {i+1}: ")
#                 playlist_urls.append(playlist_url)
#         else:
#             playlist_urls = [input("Enter the YouTube playlist URL: ")]

#         downloader = YouTubeCaptionDownloader(output_dir)
#         all_caption_files = []

#         for playlist_url in playlist_urls:
#             caption_files = downloader.process_playlist(playlist_url)
#             all_caption_files.extend(caption_files)

#         if all_caption_files:
#             merge_option = input("Do you want to merge all the successfully downloaded captions into a single file? (yes/no): ").lower()
#             if merge_option == 'yes':
#                 downloader.merge_captions(all_caption_files)
#         else:
#             logger.info("No captions were downloaded successfully from any playlist.")

#     else:
#         logger.info("Invalid mode selected. Please run the script again and choose 'v' or 'p'.")

# if __name__ == "__main__":
#     main()
