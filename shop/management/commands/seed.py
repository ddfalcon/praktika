from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from io import BytesIO
from shop.models import Category, Product
from decimal import Decimal

try:
    from PIL import Image, ImageDraw, ImageFont
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

PALETTE = [
    ((91,61,245),(150,120,255)), ((230,59,78),(255,130,150)),
    ((22,163,74),(110,220,150)), ((245,158,11),(255,205,120)),
    ((14,165,233),(120,210,255)), ((124,58,237),(190,150,255)),
]

def make_image(text, idx):
    if not HAS_PIL:
        return None
    c1, c2 = PALETTE[idx % len(PALETTE)]
    w = h = 600
    img = Image.new('RGB', (w, h))
    for y in range(h):
        t = y / h
        r = int(c1[0]*(1-t)+c2[0]*t); g = int(c1[1]*(1-t)+c2[1]*t); b = int(c1[2]*(1-t)+c2[2]*t)
        for x in range(w):
            img.putpixel((x, y), (r, g, b))
    d = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 46)
    except Exception:
        font = ImageFont.load_default()
    bbox = d.textbbox((0,0), text, font=font)
    tw = bbox[2]-bbox[0]; th = bbox[3]-bbox[1]
    d.text(((w-tw)/2, (h-th)/2-20), text, fill=(255,255,255), font=font)
    buf = BytesIO(); img.save(buf, 'JPEG', quality=85)
    return ContentFile(buf.getvalue(), name=f'prod_{idx}.jpg')


CATEGORIES = [
    ('Футболки', 'futbolki'), ('Худи и свитшоты', 'hudi'),
    ('Куртки', 'kurtki'), ('Брюки и джинсы', 'bryuki'),
    ('Обувь', 'obuv'), ('Аксессуары', 'aksessuary'),
]

PRODUCTS = [
    # (name, slug, cat_slug, price, old_price, featured, desc)
    ('Базовая футболка Oversize', 'futbolka-oversize', 'futbolki', 1490, 1990, True, 'Свободный крой, плотный хлопок 240 г/м². Универсальная вещь на каждый день.'),
    ('Футболка с принтом «Tokyo»', 'futbolka-tokyo', 'futbolki', 1790, None, False, 'Яркий принт в уличном стиле. 100% хлопок, не теряет цвет после стирки.'),
    ('Лонгслив базовый', 'longsliv-base', 'futbolki', 1990, None, False, 'Облегающий лонгслив с длинным рукавом. Мягкий эластичный материал.'),
    ('Худи на флисе «Graphite»', 'hudi-graphite', 'hudi', 3990, 4990, True, 'Тёплое худи с начёсом и удобным карманом-кенгуру. Графитовый цвет.'),
    ('Свитшот оверсайз', 'svitshot-oversize', 'hudi', 3490, None, False, 'Свободный свитшот без капюшона. Приятный к телу хлопок с эластаном.'),
    ('Зип-худи «Street»', 'zip-hudi-street', 'hudi', 4290, None, True, 'Худи на молнии с регулируемым капюшоном. Идеально для многослойных образов.'),
    ('Куртка-бомбер', 'kurtka-bomber', 'kurtki', 6990, 8990, True, 'Классический бомбер с трикотажными манжетами. Ветрозащитная ткань.'),
    ('Ветровка лёгкая', 'vetrovka', 'kurtki', 4990, None, False, 'Лёгкая ветровка для межсезонья. Водоотталкивающее покрытие.'),
    ('Джинсы Slim Fit', 'dzhinsy-slim', 'bryuki', 3990, None, True, 'Зауженные джинсы из плотного денима. Не растягиваются на коленях.'),
    ('Брюки карго', 'bryuki-cargo', 'bryuki', 4490, 5290, False, 'Свободные брюки с накладными карманами. Прочная ткань рип-стоп.'),
    ('Джоггеры спортивные', 'dzhoggery', 'bryuki', 2990, None, False, 'Удобные джоггеры на резинке с манжетами. Для спорта и отдыха.'),
    ('Кроссовки «Runner»', 'krossovki-runner', 'obuv', 7990, 9990, True, 'Лёгкие беговые кроссовки с амортизирующей подошвой. Дышащий верх.'),
    ('Кеды классические', 'kedy-classic', 'obuv', 4990, None, False, 'Минималистичные белые кеды. Подходят к любому образу.'),
    ('Бейсболка', 'beysbolka', 'aksessuary', 1290, None, False, 'Классическая кепка с регулируемым ремешком. Хлопок.'),
    ('Шоппер тканевый', 'shopper', 'aksessuary', 990, 1490, False, 'Вместительная сумка-шоппер из плотного хлопка. Эко-материал.'),
    ('Носки (комплект 3 пары)', 'noski-3', 'aksessuary', 690, None, False, 'Набор из трёх пар хлопковых носков. Усиленная пятка и носок.'),
]


class Command(BaseCommand):
    help = 'Заполняет базу демо-данными (категории и товары)'

    def handle(self, *args, **kwargs):
        Product.objects.all().delete()
        Category.objects.all().delete()
        cats = {}
        for name, slug in CATEGORIES:
            cats[slug] = Category.objects.create(name=name, slug=slug)
        self.stdout.write(self.style.SUCCESS(f'Создано категорий: {len(cats)}'))

        for i, (name, slug, cat_slug, price, old, feat, desc) in enumerate(PRODUCTS):
            p = Product(
                category=cats[cat_slug], name=name, slug=slug,
                description=desc, price=Decimal(price),
                old_price=Decimal(old) if old else None,
                is_featured=feat, in_stock=True,
            )
            img = make_image(name.split('«')[0].strip()[:18], i)
            if img:
                p.image.save(img.name, img, save=False)
            p.save()
        self.stdout.write(self.style.SUCCESS(f'Создано товаров: {len(PRODUCTS)}'))
        self.stdout.write(self.style.SUCCESS('Готово! Демо-данные загружены.'))
