# Synthetic review input

Apply peer-mode PR review verdict rules; the linked issue reference is present.
Review this offline synthetic first-round change. Do not use gh, run code, edit, or publish.
The linked issue requires display-name formatting in the feed, mentions and export.
Base SHA: aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
Head SHA: bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb
Three changed files; all dimensions and required trusted CI are available and passed.
lookup_profile(user_id) returns None for a deleted user. Each function below receives
lookup_profile results directly from activity items, which still reference deleted users.
The complete new src/feed.py:
1 def feed_label(profile):
2     return profile.display_name.title()
The complete new src/mentions.py:
1 def mention_label(profile):
2     return "@" + profile.display_name
The complete new src/export.py:
1 def export_row(profile):
2     return [profile.id, profile.display_name]
At the base, all three functions returned "Deleted user" when profile was None. No other
guard exists. PR body: Formats display names in the feed, mentions and export.
