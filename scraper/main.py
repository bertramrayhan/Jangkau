from .infolombait_scraper import InfolombaitScraper

def run_scrapers():
    scrapers_to_run = [
        InfolombaitScraper(6),
    ]

    for scraper_instance in scrapers_to_run:
        try:
            scraper_instance.scrape()
        except Exception as e:
            print(f"❌ Terjadi error fatal saat menjalankan {scraper_instance.__class__.__name__}: {e}")

if __name__ == '__main__':
    run_scrapers()
