import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lamdabotweb.settings")
django.setup()

from memeviewer.models import MemeSourceImage, MemeSourceImageInContext, MemeTemplate, MemeTemplateInContext, \
    MemeContext, Meem

imset = MemeSourceImage.objects.filter(accepted=True)
progress = imset.count()
for i in imset:
    cs = i.contexts.all()
    if len(cs) == 0:
        cs = MemeContext.objects.all()
    for c in cs:
        tc, _ = MemeSourceImageInContext.objects.get_or_create(context=c, image=i)
        tc.random_usages = Meem.objects.filter(source_images__contains='"%s"' % i.name, context_link=c).count()
        tc.save()
    print(progress)
    progress -= 1

imset = MemeTemplate.objects.filter(accepted=True)
progress = imset.count()
for i in imset:
    cs = i.contexts.all()
    if len(cs) == 0:
        cs = MemeContext.objects.all()
    for c in cs:
        tc, _ = MemeTemplateInContext.objects.get_or_create(context=c, image=i)
        tc.random_usages = i.meem_set.filter(context_link=c).count()
        tc.save()
    print(progress)
    progress -= 1
