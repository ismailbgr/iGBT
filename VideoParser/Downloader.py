from pytube import YouTube


class YouTubeDownloader:
    """A class to download YouTube videos

    Attributes
    ----------
    url : str
        The URL of the YouTube video to download
        video : YouTube
        The YouTube object of the video to download

    Methods
    -------
    download(filepath=None)
        Downloads the video to the specified filepath
    """

    def __init__(self, url, celery_task=None):
        self.url = url
        self.video = YouTube(url)
        self.celery_task = celery_task

    def download(self, filepath=None):
        if self.celery_task is not None:
            self.celery_task.update_state(state="STARTED")

        if filepath is None:
            filepath = self.video.title + ".mp4"
        stream = self.video.streams.get_lowest_resolution()
        stream.download(output_path=".", filename=filepath)
