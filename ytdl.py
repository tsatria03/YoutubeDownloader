import wx
import os
import threading
import winsound
from yt_dlp import YoutubeDL

FORMATS = ["mp4", "avi", "mkv", "mp3", "wav", "flac", "ogg", "m4a"]
BEEP_INTERVALS = ["1%", "5%", "10%"]

class YouTubeDownloader(wx.Frame):
    def __init__(self):
        super().__init__(None, title="YouTube Downloader", size=(500, 500))
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        # YouTube URL input
        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        self.url_label = wx.StaticText(panel, label="YouTube URL:")
        self.url_input = wx.TextCtrl(panel)
        self.url_input.SetHint("Paste the YouTube video or playlist link here...")
        hbox1.Add(self.url_label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        hbox1.Add(self.url_input, 1, wx.ALL | wx.EXPAND, 5)
        vbox.Add(hbox1, 0, wx.EXPAND)
        self.Bind(wx.EVT_MENU, lambda e: self.url_input.SetFocus())
        self.SetAcceleratorTable(wx.AcceleratorTable([(wx.ACCEL_ALT, ord('D'), wx.ID_ANY)]))

        # Format selection
        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        self.format_label = wx.StaticText(panel, label="Format:")
        self.format_combo = wx.ComboBox(panel, choices=FORMATS, style=wx.CB_READONLY)
        self.format_combo.SetSelection(0)
        hbox2.Add(self.format_label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        hbox2.Add(self.format_combo, 1, wx.ALL | wx.EXPAND, 5)
        vbox.Add(hbox2, 0, wx.EXPAND)

        # Playlist option (unchecked by default)
        self.playlist_checkbox = wx.CheckBox(panel, label="Download full playlist/channel if available")
        self.playlist_checkbox.SetValue(False)
        vbox.Add(self.playlist_checkbox, 0, wx.ALL, 5)

        # Save location
        hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        self.path_label = wx.StaticText(panel, label="Save to:")
        self.path_input = wx.TextCtrl(panel)
        self.browse_button = wx.Button(panel, label="Browse")
        hbox3.Add(self.path_label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        hbox3.Add(self.path_input, 1, wx.ALL | wx.EXPAND, 5)
        hbox3.Add(self.browse_button, 0, wx.ALL, 5)
        vbox.Add(hbox3, 0, wx.EXPAND)
        self.Bind(wx.EVT_MENU, lambda e: self.path_input.SetFocus())
        self.browse_button.Bind(wx.EVT_BUTTON, self.on_browse)

        # Beep controls
        self.beep_checkbox = wx.CheckBox(panel, label="Enable progress beeps")
        self.beep_checkbox.SetValue(True)
        vbox.Add(self.beep_checkbox, 0, wx.ALL, 5)

        hbox4 = wx.BoxSizer(wx.HORIZONTAL)
        self.beep_label = wx.StaticText(panel, label="Beep Interval:")
        self.beep_interval_combo = wx.ComboBox(panel, choices=BEEP_INTERVALS, style=wx.CB_READONLY)
        self.beep_interval_combo.SetSelection(0)  # 1% default
        hbox4.Add(self.beep_label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        hbox4.Add(self.beep_interval_combo, 1, wx.ALL | wx.EXPAND, 5)
        vbox.Add(hbox4, 0, wx.EXPAND)

        # Where to show status messages
        self.status_display_checkbox = wx.CheckBox(panel, label="Show status in bottom status bar")
        self.status_display_checkbox.SetValue(True)
        vbox.Add(self.status_display_checkbox, 0, wx.ALL, 5)

        # Progress bar
        self.progress = wx.Gauge(panel, range=100, style=wx.GA_HORIZONTAL)
        vbox.Add(self.progress, 0, wx.EXPAND | wx.ALL, 5)

        # Optional status label (shown only if checkbox is off)
        self.status_label = wx.StaticText(panel, label="")
        vbox.Add(self.status_label, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        # Download and Exit buttons
        self.download_button = wx.Button(panel, label="Download")
        self.download_button.Bind(wx.EVT_BUTTON, self.start_download)
        vbox.Add(self.download_button, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 5)

        self.exit_button = wx.Button(panel, label="Exit")
        self.exit_button.Bind(wx.EVT_BUTTON, lambda e: self.Close())
        vbox.Add(self.exit_button, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 5)

        self.Bind(wx.EVT_CHAR_HOOK, self.on_key)

        panel.SetSizer(vbox)

        # Real status bar
        self.statusbar = self.CreateStatusBar()

        self.Centre()
        self.Show()

        self.last_beep_percent = -1
        self.download_path = ""

    def show_status(self, message):
        if self.status_display_checkbox.IsChecked():
            self.statusbar.SetStatusText(message)
        else:
            self.status_label.SetLabel(message)

    def on_browse(self, event):
        with wx.DirDialog(self, "Choose download folder", "", wx.DD_DEFAULT_STYLE) as dlg:
            if dlg.ShowModal() == wx.ID_OK:
                self.path_input.SetValue(dlg.GetPath())

    def on_key(self, event):
        if event.GetKeyCode() == wx.WXK_ESCAPE:
            self.Close()
        else:
            event.Skip()

    def start_download(self, event):
        url = self.url_input.GetValue()
        fmt = self.format_combo.GetValue()
        raw_path = self.path_input.GetValue()

        if not url.strip():
            self.show_status("Please enter a YouTube URL.")
            return

        # Use default ./dl path if empty
        if not raw_path.strip():
            raw_path = os.path.join(os.getcwd(), "dl")
            self.path_input.SetValue(raw_path)

        if not os.path.exists(raw_path):
            os.makedirs(raw_path)

        self.download_path = raw_path
        self.progress.SetValue(0)
        self.last_beep_percent = -1
        self.show_status("Starting download...")
        threading.Thread(target=self.download_video, args=(url, fmt, raw_path), daemon=True).start()

    def download_video(self, url, fmt, path):
        def hook(d):
            if d['status'] == 'downloading':
                percent = d.get('_percent_str', '').replace('%', '').strip()
                try:
                    percent_float = float(percent)
                    wx.CallAfter(self.progress.SetValue, int(percent_float))
                    self.handle_beep(int(percent_float))
                except:
                    pass

        use_playlist = self.playlist_checkbox.IsChecked()
        outtmpl = os.path.join(
            path,
            '%(playlist_title)s/%(title)s.%(ext)s' if use_playlist else '%(title)s.%(ext)s'
        )

        opts = {
            'format': 'bestaudio/best' if fmt in ['mp3', 'wav', 'flac', 'ogg', 'm4a'] else 'bestvideo+bestaudio',
            'outtmpl': outtmpl,
            'progress_hooks': [hook],
            'ignoreerrors': True,
            'quiet': True,
            'noplaylist': not use_playlist
        }

        if fmt in ['mp3', 'wav', 'flac', 'ogg', 'm4a']:
            opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': fmt,
                'preferredquality': '192',
            }]

        try:
            with YoutubeDL(opts) as ydl:
                ydl.download([url])
            wx.CallAfter(self.download_complete)
        except Exception as e:
            wx.CallAfter(self.show_status, f"Download failed: {e}")

    def download_complete(self):
        msg = f"Download complete! Saved to: {self.download_path}"
        self.show_status(msg)
        if self.beep_checkbox.IsChecked():
            winsound.Beep(1500, 200)

    def handle_beep(self, percent):
        if not self.beep_checkbox.IsChecked():
            return
        try:
            interval = int(self.beep_interval_combo.GetValue().replace('%', ''))
        except:
            interval = 5
        if percent // interval > self.last_beep_percent // interval:
            self.last_beep_percent = percent
            freq = 400 + int((1600 * percent) / 100)
            winsound.Beep(freq, 75)

if __name__ == "__main__":
    app = wx.App(False)
    frame = YouTubeDownloader()
    app.MainLoop()
