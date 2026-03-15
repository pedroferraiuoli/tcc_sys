from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("experiments", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="experiment",
            name="batch_code",
            field=models.CharField(
                blank=True,
                db_index=True,
                default="",
                help_text="Identifica experimentos criados em uma mesma execução em lote.",
                max_length=32,
                verbose_name="código do lote",
            ),
        ),
    ]
