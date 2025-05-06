# Scrapy settings for chileansupermarkets project

BOT_NAME = "chileansupermarkets"

SPIDER_MODULES = ["chileansupermarkets.spiders"]
NEWSPIDER_MODULE = "chileansupermarkets.spiders"

# Configuración de User-Agent
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'

# Obedece robots.txt por defecto
ROBOTSTXT_OBEY = True

# Configure maximum concurrent requests performing to the same domain
CONCURRENT_REQUESTS_PER_DOMAIN = 16

# Configure a delay for requests for the same website
DOWNLOAD_DELAY = 1
RANDOMIZE_DOWNLOAD_DELAY = True

# Deshabilitar cookies
COOKIES_ENABLED = False

# Configurar pipeline
ITEM_PIPELINES = {
   "chileansupermarkets.pipelines.ChileansupermarketsPipeline": 300,
}

# Habilitar la depuración de respuestas HTTP
HTTPERROR_ALLOW_ALL = True

# Aumentar el tiempo de espera
DOWNLOAD_TIMEOUT = 180

# Reintentos para errores HTTP
RETRY_ENABLED = True
RETRY_TIMES = 3
RETRY_HTTP_CODES = [500, 502, 503, 504, 408, 429]

# Configuración para evitar baneo
CONCURRENT_REQUESTS = 16
DOWNLOAD_MAXSIZE = 0
AJAXCRAWL_ENABLED = True

# Middlewares
DOWNLOADER_MIDDLEWARES = {
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
    'scrapy.downloadermiddlewares.retry.RetryMiddleware': 90,
    'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 110,
}

# Configuración de logs
LOG_LEVEL = 'INFO'
LOG_FORMAT = '%(asctime)s [%(name)s] %(levelname)s: %(message)s'
