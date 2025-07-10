from .cleanup import cleanup_old_posts
from .daily import daily_poster
from .monthly_new_releases import monthly_game_post
from .weekly import weekly_poster


def start_tasks(bot):
    # Inject the bot instance into each task module
    import tasks.cleanup
    import tasks.daily
    import tasks.monthly_new_releases
    import tasks.weekly

    tasks.daily.bot = bot
    tasks.weekly.bot = bot
    tasks.cleanup.bot = bot
    tasks.monthly_new_releases.bot = bot

    # Start tasks if not already running
    if not daily_poster.is_running():
        daily_poster.start()
    if not weekly_poster.is_running():
        weekly_poster.start()
    if not cleanup_old_posts.is_running():
        cleanup_old_posts.start()
    if not monthly_game_post.is_running():
        monthly_game_post.start()
