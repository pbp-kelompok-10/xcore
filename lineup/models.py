from django.db import models
from django.conf import settings

# --- COUNTRY CHOICES ---
COUNTRY_CHOICES = [
    ('jp', 'Japan'),
    ('ir', 'Iran'),
    ('kr', 'South Korea'),
    ('au', 'Australia'),
    ('sa', 'Saudi Arabia'),
    ('uz', 'Uzbekistan'),
    ('jo', 'Jordan'),
    ('iq', 'Iraq'),
    ('ae', 'United Arab Emirates'),
    ('qa', 'Qatar'),
    ('cn', 'China'),
    ('om', 'Oman'),
    ('id', 'Indonesia'),
    ('bh', 'Bahrain'),
    ('kw', 'Kuwait'),
    ('th', 'Thailand'),
    ('kp', 'North Korea'),
    ('ps', 'Palestine'),
    ('sy', 'Syria'),
    ('vn', 'Vietnam'),
    ('my', 'Malaysia'),
    ('lb', 'Lebanon'),
    ('np', 'Nepal'),
    ('bd', 'Bangladesh'),
    ('mm', 'Myanmar'),
    ('mv', 'Maldives'),
    ('af', 'Afghanistan'),
    ('ph', 'Philippines'),
    ('hk', 'Hong Kong'),
    ('tm', 'Turkmenistan'),
    ('kg', 'Kyrgyzstan'),
    ('tj', 'Tajikistan'),
    ('tw', 'Chinese Taipei'),
    ('ye', 'Yemen'),
    ('bn', 'Brunei'),
    ('la', 'Laos'),
    ('lk', 'Sri Lanka'),
    ('kh', 'Cambodia'),
    ('bt', 'Bhutan'),
    ('gu', 'Guam'),
    ('mn', 'Mongolia'),
    ('pk', 'Pakistan'),
    ('tl', 'Timor-Leste'),
    ('mo', 'Macau'),
    ('sg', 'Singapore'),
    ('in', 'India')
]


class Team(models.Model):
    code = models.CharField(max_length=3, choices=COUNTRY_CHOICES, unique=True)
    name = models.CharField(max_length=100, unique=True, editable=False)

    def save(self, *args, **kwargs):
        for code, country in COUNTRY_CHOICES:
            if self.code == code:
                self.name = country
                break
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Player(models.Model):
    nama = models.CharField(max_length=100)
    asal = models.CharField(max_length=100)
    umur = models.PositiveIntegerField()
    nomor = models.PositiveIntegerField()
    tim = models.ForeignKey(Team, related_name='players', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('nomor', 'tim')
        ordering = ['nomor']

    def __str__(self):
        return f"{self.nama} ({self.tim.name})"


# --- LINEUP MODEL ---
class Lineup(models.Model):
    match = models.ForeignKey('scoreboard.Match', on_delete=models.CASCADE, related_name='lineups')
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    players = models.ManyToManyField(Player, related_name='lineups')

    class Meta:
        unique_together = ('match', 'team')

    def __str__(self):
        return f"Lineup for {self.team.name} in {self.match}"
