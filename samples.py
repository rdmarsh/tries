# ---------------------------------------------------------------------------
# samples.py
# Standalone sample data for build_tries.py
# ---------------------------------------------------------------------------

SAMPLE_HOSTS = [
    "acmefw01.domain.local",
    "acmefw02.domain.local",
    "acmefw01-oob.domain.local",
    "acmefw02-oob.domain.local",
    "acmesw01.domain.local",
    "acmesw02.domain.local",
    "acmeweb01.domain.local",
    "localhost.localdomain",
    r"ACME\\acmesrv01.domain.local",
    r"ACME\\acmesrv02.domain.local",
]

SAMPLE_IPS = [
    "10.0.0.1",
    "10.0.0.2",
    "10.0.1.20",
    "10.0.1.21",
    "10.0.2.20",
    "10.0.2.21",
    "10.20.30.40",
    "192.168.0.1",
    "192.168.1.1",
    "192.168.1.2",
    "172.16.5.100",
    "8.8.8.8",
]

SAMPLE_PATHS = [
    "/usr/local/bin",
    "/usr/local/sbin",
    "/usr/local/share",
    "/usr/bin",
    "/usr/sbin",
    "/usr/share",
    "/opt/tools",
    "/opt/scripts",
    "/etc/nginx",
    "/etc/ssh",
    "/var/log",
    "/var/tmp",
    "/var/www",
    "/var/www/html",
]

SAMPLE_URLS = [
    "http://example.com/about",
    "https://example.com",
    "https://example.com/about",
    "https://example.com/login",
    "https://example.com/admin",
    "https://acme.local",
    "https://acme.local/app",
    "https://acme.local/app/api",
    "https://portal.example.net",
    "https://portal.example.net/customers",
    "https://portal.example.net/customers/acme",
]

SAMPLE_EMAILS = [
    "alice@example.com",
    "fred@example.com",
    "bob@acme.local",
    "root@localhost",
    "ops@internal.syd.acme",
    "alerts+prod@company.net",
]

SAMPLE_NATO = [
    "acme",
    "brav",
    "char",
    "delt",
    "echo",
    "foxt",
    "gamm",
    "hote",
    "indi",
    "juli",
    "kilo",
    "lima",
    "mang",
    "nove",
    "osca",
    "papa",
    "quar",
    "rome",
    "sier",
    "tang",
    "umbr",
    "vict",
    "whis",
    "xeno",
    "yank",
    "zulu",
]

# dictionary for easy merging
SAMPLES = {
    "hosts": SAMPLE_HOSTS,
    "ips": SAMPLE_IPS,
    "paths": SAMPLE_PATHS,
    "urls": SAMPLE_URLS,
    "emails": SAMPLE_EMAILS,
    "nato": SAMPLE_NATO,
}
