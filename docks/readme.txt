Welcome to YouTube downloader! YouTube Downloader is a simple and accessible application written in Python using the wxPython library.
It is designed specifically for screen reader users, offering a user-friendly interface and support for downloading both audio and video from YouTube. The app provides real-time progress feedback through beeps and optional status messages.
This app uses yt-dlp to handle the download and conversion of media from YouTube. For audio files, it uses FFmpeg via yt-dlp's post-processing features.
Progress updates are monitored with yt-dlp's hook system. The app generates optional beeps using Python’s built-in winsound module to indicate download progress.

Features
The interface is easy to navigate and fully operable with a keyboard, making it accessible to screen reader users. Users can enable progress beeps that indicate the current download progress.
They can also customize the beep interval to occur every 1%, 5%, or 10%. Downloads can be saved to a custom folder of your choice.
The app supports several video formats including MP4, AVI, and MKV. It also supports audio formats such as MP3, WAV, FLAC, OGG, and M4A.
There is also an option to download entire playlists or channels when available. Additionally, you can choose whether the download status is shown in the bottom status bar or displayed as a label on the main screen.

Requirements
This application requires Python 3.7 or higher. You will also need the wxPython and yt-dlp Python packages, which can be installed using the provided requirements.txt file.
Additionally, if you plan to download audio formats like MP3 or WAV, you will need to have FFmpeg installed and added to your system’s PATH. FFmpeg is used internally by yt-dlp to convert downloaded audio files into your selected format.

How to use.
To use the app, first launch it and paste a YouTube video or playlist URL into the input field. Then, select your desired format from the dropdown menu. If you'd like to download an entire playlist or channel, you can check the box labeled Download full playlist/channel if available.
You can quickly jump to the URL input field by pressing Alt+D. Pressing the Escape key will close the application immediately. These shortcuts are included to enhance usability, particularly for screen reader users who rely on efficient keyboard navigation.
Next, choose a folder where you'd like the file to be saved, or simply leave the field empty to use the default ./dl folder. Once you're ready, click the Download button and wait for the process to complete.
If no custom path is provided, all downloaded files will be saved into a folder named dl in the same directory as the app. This provides a simple and predictable location for your downloads.
If progress beeps are enabled, you'll hear audio feedback during the download. You can monitor the current status either in the bottom status bar or through the on-screen label, depending on your settings.

License
This project is released as free and open-source software under the MIT License. You are welcome to modify, distribute, or build upon it as long as the license terms are followed.

Enjoy, and happy downloading!