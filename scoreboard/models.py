from django.db import models
import uuid

class Match(models.Model):
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

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    home_team_code = models.CharField(max_length=3, choices=COUNTRY_CHOICES)
    away_team_code = models.CharField(max_length=3, choices=COUNTRY_CHOICES)
    home_team = models.CharField(max_length=100, editable=False)
    away_team = models.CharField(max_length=100, editable=False)

    home_score = models.PositiveIntegerField(default=0)
    away_score = models.PositiveIntegerField(default=0)
    match_date = models.DateTimeField()
    stadium = models.CharField(max_length=100)
    round = models.IntegerField(blank=True, null=True)
    group = models.CharField(max_length=20, blank=True, null=True)
    status = models.CharField(
        max_length=10,
        choices=[
            ('upcoming', 'Upcoming'),
            ('live', 'Live'),
            ('finished', 'Finished'),
        ],
        default='upcoming'
    )

    def save(self, *args, **kwargs):
        code_to_country = dict(self.COUNTRY_CHOICES)
        self.home_team = code_to_country.get(self.home_team_code, self.home_team_code)
        self.away_team = code_to_country.get(self.away_team_code, self.away_team_code)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.home_team} vs {self.away_team}"
