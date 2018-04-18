import sys
from django.core.management import BaseCommand
from memeviewer.models import MemeSourceImage, MemeSourceImageInContext, MemeTemplate, MemeTemplateInContext, \
    MemeContext


class Command(BaseCommand):

    def handle(self, *args, **options):
        imset = MemeSourceImage.objects.filter(accepted=True)
        progress = imset.count()

        for i in imset:
            cs = i.contexts.all()
            if len(cs) == 0:
                cs = MemeContext.objects.all()
            for c in cs:
                tc, _ = MemeSourceImageInContext.objects.get_or_create(context=c, image=i)
                # tc.random_usages = Meem.objects.filter(source_images__contains='"%s"' % i.name, context_link=c).count()
                # tc.save()
            progress -= 1
            print('Updating source images:', progress, '\r', end='')
            sys.stdout.flush()
        print('')

        imset = MemeTemplate.objects.filter(accepted=True)
        progress = imset.count()
        for i in imset:
            cs = i.contexts.all()
            if len(cs) == 0:
                cs = MemeContext.objects.all()
            for c in cs:
                tc, _ = MemeTemplateInContext.objects.get_or_create(context=c, image=i)
                # tc.random_usages = i.meem_set.filter(context_link=c).count()
                # tc.save()
            progress -= 1
            print('Updating templates:', progress, '\r', end='')
            sys.stdout.flush()
        print('')
