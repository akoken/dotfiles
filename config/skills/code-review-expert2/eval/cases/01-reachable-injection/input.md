# Synthetic review input

Apply the general review verdict rules.
Review this offline synthetic change. Do not use gh, run code, edit, or publish.
The linked issue requires displaying the contents of a user-selected local file.
Base SHA: aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
Head SHA: bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb
One changed file; all dimensions and required trusted CI are available and passed.
The previous implementation used subprocess.run(["cat", user_path], check=True).
The complete new src/display.py is:
1 import subprocess
2 def display(user_path):
3     return subprocess.run("cat " + user_path, shell=True, check=True)
4 def on_file_selection(request):
5     return display(request.path)
request.path comes directly from the user's text input without filtering. No other guard.
PR body: Closes the linked issue. Displays the selected file using cat.
