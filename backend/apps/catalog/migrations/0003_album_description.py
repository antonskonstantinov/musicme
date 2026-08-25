from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0002_song_lyrics"),
    ]

    operations = [
        migrations.AddField(
            model_name="album",
            name="description",
            field=models.TextField(
                blank=True,
                default="",
                help_text="Необязательно. Краткое описание альбома (до 500 символов).",
                max_length=500,
                verbose_name="Описание",
            ),
        ),
    ]
