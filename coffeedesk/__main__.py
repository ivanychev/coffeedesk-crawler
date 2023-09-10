from __future__ import annotations

import io
from datetime import date, datetime, timedelta
from operator import attrgetter
from typing import Literal

import click
from apscheduler.schedulers.blocking import BlockingScheduler
from loguru import logger
from telegram import Bot, ParseMode

from coffeedesk.coffee import Coffee
from coffeedesk.fetch.cofee_fetcher import fetch_coffee
from coffeedesk.filters.parser import CoffeeDeskFilters
from coffeedesk.filters.request import RequestFilterBuilder


def compose_report(coffee: list[Coffee], max_in_report: int) -> str:
    buffer = io.StringIO()
    buffer.write(f'Found {len(coffee)} items, showing {max_in_report} freshest\n\n')

    for c in coffee[:max_in_report]:
        buffer.write(
            f'{c.roasting_date.isoformat()} - <a href="{c.link}">{c.name}</a>\n'
        )
    return buffer.getvalue()


@click.command()
@click.option('--telegram-token', required=True, help='Telegram Bot token.')
@click.option(
    '--telegram-channel-id', default='-1001758402783', help='Telegram channel ID.'
)
@click.option(
    '--publish-strategy', default='telegram', help='The publish strategy (telegram or terminal).'
)
@click.option(
    '--max-in-report', type=int, default=30, help='Max coffee entries in report.'
)
def crawl(telegram_token: str, telegram_channel_id: str, max_in_report: int,
          publish_strategy: str):
    s = BlockingScheduler()
    s.add_job(
        _do_crawl,
        'cron',
        hour='20',
        id='crawl_site',
        kwargs={
            'telegram_token': telegram_token,
            'telegram_channel_id': telegram_channel_id,
            'max_in_report': max_in_report,
            'publish_strategy': publish_strategy
        },
        next_run_time=datetime.now(),
    )
    s.start()


def _do_crawl(telegram_token: str, telegram_channel_id: str, max_in_report: int,
              publish_strategy: Literal['telegram', 'terminal']):
    logger.info('Starting crawl at {} ...', datetime.now())
    site_filters = CoffeeDeskFilters.download_and_parse()
    filter = (
        RequestFilterBuilder(site_filters)
        .with_whole_beans()
        .with_pure_arabica()
        .build()
    )
    coffee = fetch_coffee(filter)
    today = date.today()
    month_ago = today - timedelta(days=30)
    logger.info('Collected {} items', len(coffee))

    fresh_coffee = sorted(
        [c for c in coffee if c.roasting_date and c.roasting_date >= month_ago],
        reverse=True,
        key=attrgetter('roasting_date'),
    )
    logger.info('Collected {} fresh items', len(fresh_coffee))

    report = compose_report(fresh_coffee, max_in_report=max_in_report)
    if publish_strategy == 'telegram':
        bot = Bot(token=telegram_token)
        bot.send_message(
            telegram_channel_id,
            report,
            parse_mode=ParseMode.HTML,
        )
        logger.info("Sent message to Telegram channel: {}", telegram_channel_id)
    elif publish_strategy == 'terminal':
        logger.info("{}", report)
        logger.info("Done with the report, length or report {}", len(report))
    else:
        raise ValueError(f"Invalid publish strategy: {publish_strategy}")


if __name__ == '__main__':
    crawl()
