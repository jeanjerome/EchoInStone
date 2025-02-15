from pytest_bdd import scenarios, given, when, then
from EchoInStone.capture.downloader_factory import get_downloader
from EchoInStone.capture.youtube_downloader import YouTubeDownloader
from EchoInStone.capture.podcast_downloader import PodcastDownloader
from EchoInStone.capture.audio_downloader import AudioDownloader

# Load scenarios from the feature file
# This function loads BDD scenarios defined in the specified feature file.
scenarios('../downloader.feature')

# Shared variables
# Global variables to store the URL being tested and the selected downloader.
url = ""
downloader = None

@given('the URL is a YouTube URL')
def youtube_url():
    global url
    # Set the URL to a valid YouTube video URL for testing purposes.
    url = 'https://www.youtube.com/watch?v=plZRCMx_Jd8'

@given('the URL is a Podcast URL')
def podcast_url():
    global url
    # Set the URL to a valid podcast feed URL for testing purposes.
    url = 'https://radiofrance-podcast.net/podcast09/rss_13957.xml'

@given('the URL is an MP3 URL')
def mp3_url():
    global url
    # Set the URL to a direct MP3 file URL for testing purposes.
    url = 'https://media.radiofrance-podcast.net/podcast09/25425-13.02.2025-ITEMA_24028677-2025C53905E0006-NET_MFC_D378B90D-D570-44E9-AB5A-F0CC63B05A14-21.mp3'

@when('the downloader is selected')
def select_downloader():
    global downloader
    # Select the appropriate downloader based on the URL.
    downloader = get_downloader(url, output_dir='test_output')

@then('the YouTube downloader should be returned')
def check_youtube_downloader():
    # Verify that the selected downloader is an instance of YouTubeDownloader.
    assert isinstance(downloader, YouTubeDownloader)

@then('the Podcast downloader should be returned')
def check_podcast_downloader():
    # Verify that the selected downloader is an instance of PodcastDownloader.
    assert isinstance(downloader, PodcastDownloader)

@then('the Audio downloader should be returned')
def check_audio_downloader():
    # Verify that the selected downloader is an instance of AudioDownloader.
    assert isinstance(downloader, AudioDownloader)
