from fetcher import ChannelFetcher


if __name__ == '__main__':
    channel_ids = [
        # enter desired YouTube channel IDs here
    ]
    for _id in channel_ids:
        fetcher = ChannelFetcher(_id)
        fetcher.run()

